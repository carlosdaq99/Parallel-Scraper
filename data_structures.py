"""
Data structures module for parallel scraper system.

Contains dataclasses for tasks, node information, and worker context
that manage the state and coordination of the parallel web scraping process.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional
from datetime import datetime
import asyncio
import logging

# Import config with fallback
try:
    from config import ScraperConfig

    WORKER_SHUTDOWN_TIMEOUT = ScraperConfig.WORKER_SHUTDOWN_TIMEOUT
    MAX_CONCURRENT_PAGES = ScraperConfig.MAX_CONCURRENT_PAGES
except ImportError:
    from config import ScraperConfig

    WORKER_SHUTDOWN_TIMEOUT = ScraperConfig.WORKER_SHUTDOWN_TIMEOUT
    MAX_CONCURRENT_PAGES = ScraperConfig.MAX_CONCURRENT_PAGES


class WorkerManager:
    """Manages dynamic hierarchical worker spawning with limits"""

    def __init__(self, max_workers: int = MAX_CONCURRENT_PAGES):
        self.max_workers = max_workers
        self.active_workers: Set[str] = set()
        self.worker_queue = asyncio.Queue()  # Queue for waiting workers
        self.lock = asyncio.Lock()

    async def register_worker(self, worker_id: str) -> bool:
        """Register a new worker if under limits, otherwise queue it"""
        async with self.lock:
            if len(self.active_workers) < self.max_workers:
                self.active_workers.add(worker_id)
                return True
            else:
                # Queue the worker to wait for a slot
                await self.worker_queue.put(worker_id)
                return False

    async def unregister_worker(self, worker_id: str):
        """Unregister a completed worker and activate next queued worker"""
        async with self.lock:
            self.active_workers.discard(worker_id)

            # Activate next queued worker if any
            if not self.worker_queue.empty():
                next_worker = await self.worker_queue.get()
                self.active_workers.add(next_worker)
                return next_worker
            return None

    async def get_active_count(self) -> int:
        """Get current active worker count"""
        async with self.lock:
            return len(self.active_workers)

    def get_queued_count(self) -> int:
        """Get current queued worker count"""
        return self.worker_queue.qsize()


@dataclass
class NodeInfo:
    """Enhanced class to store information about a tree node"""

    label: str
    path: str
    depth: int
    worker_id: str = ""
    parent_worker_id: str = ""
    is_leaf: bool = False
    subfolders: List[str] = field(default_factory=list)
    guid: str = ""  # GUID from data-id attribute if available

    def to_dict(self) -> Dict:
        """Convert NodeInfo to dictionary for JSON serialization"""
        result = {
            "label": self.label,
            "path": self.path,
            "depth": self.depth,
            "worker_id": self.worker_id,
            "parent_worker_id": self.parent_worker_id,
            "is_leaf": self.is_leaf,
            "subfolders": self.subfolders,
        }

        # Only include GUID if it exists (not empty)
        if self.guid:
            result["guid"] = self.guid

        return result


@dataclass
class Task:
    """Task definition for queue-based worker system"""

    worker_id: str
    node_info: NodeInfo
    priority: int  # Lower number = higher priority (breadth-first)
    retry_count: int = 0
    parent_task_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __lt__(self, other):
        """For priority queue ordering - prioritize by depth (breadth-first)"""
        return self.priority < other.priority

    def to_dict(self) -> Dict:
        """Convert Task to dictionary for logging and debugging"""
        return {
            "worker_id": self.worker_id,
            "node_info": self.node_info.to_dict(),
            "priority": self.priority,
            "retry_count": self.retry_count,
            "parent_task_id": self.parent_task_id,
            "created_at": self.created_at.isoformat(),
        }


class ParallelWorkerContext:
    """Enhanced worker context with CONCURRENT task management and hierarchical worker spawning"""

    def __init__(self, max_workers: int, logger: logging.Logger):
        self.max_workers = max_workers
        self.task_queue = asyncio.Queue()
        self.completed_tasks: Dict[str, NodeInfo] = {}
        self.failed_tasks: Dict[str, Exception] = {}
        self.active_tasks: Set[str] = set()
        self.lock = asyncio.Lock()
        self.shutdown_flag = False
        self.logger = logger

        # Hierarchical worker management
        self.worker_manager = WorkerManager(max_workers)

        # Statistics
        self.total_tasks_created = 0
        self.total_tasks_completed = 0
        self.total_tasks_failed = 0
        self.total_retries = 0

        # Concurrency control
        self.semaphore = asyncio.Semaphore(max_workers)

        # Timing
        self.start_time = datetime.now()
        self.worker_shutdown_timeout = WORKER_SHUTDOWN_TIMEOUT

        self.logger.info(f"ParallelWorkerContext initialized: {max_workers} workers")

    async def submit_task(self, task: Task) -> bool:
        """Submit a task to the async queue with logging"""
        async with self.lock:
            if self.shutdown_flag:
                self.logger.warning(
                    f"Task submission rejected - shutdown in progress: {task.worker_id}"
                )
                return False

            await self.task_queue.put(task)
            self.active_tasks.add(task.worker_id)
            self.total_tasks_created += 1

            self.logger.debug(
                f"Task submitted: {task.worker_id} (priority: {task.priority})"
            )
            return True

    async def mark_task_completed(self, task_id: str, result: NodeInfo):
        """Mark task as completed and store result"""
        async with self.lock:
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)

            self.completed_tasks[task_id] = result
            self.total_tasks_completed += 1

            # Signal task completion for queue.join() pattern
            self.task_queue.task_done()

            self.logger.debug(f"Task completed: {task_id} -> {result.label}")

    async def mark_task_failed(self, task_id: str, error: Exception):
        """Mark task as failed and store error"""
        async with self.lock:
            if task_id in self.active_tasks:
                self.active_tasks.remove(task_id)

            self.failed_tasks[task_id] = error
            self.total_tasks_failed += 1

            # Signal task completion even for failures
            self.task_queue.task_done()

            self.logger.error(f"Task failed: {task_id} -> {error}")

    def signal_shutdown(self):
        """Signal all workers to begin shutdown"""
        self.shutdown_flag = True
        self.logger.info("Shutdown signal sent to all workers")

    def get_statistics(self) -> Dict:
        """Get current system statistics for monitoring"""
        runtime = (datetime.now() - self.start_time).total_seconds()

        return {
            "runtime_seconds": runtime,
            "total_tasks_created": self.total_tasks_created,
            "total_tasks_completed": self.total_tasks_completed,
            "total_tasks_failed": self.total_tasks_failed,
            "total_retries": self.total_retries,
            "active_tasks": len(self.active_tasks),
            "queue_size": self.task_queue.qsize(),
            "completion_rate": (
                self.total_tasks_completed / max(self.total_tasks_created, 1)
            )
            * 100,
        }

    def is_queue_empty(self) -> bool:
        """Check if the queue is empty"""
        return self.task_queue.empty()

    def has_active_tasks(self) -> bool:
        """Check if there are any active tasks"""
        return len(self.active_tasks) > 0

    def should_shutdown(self) -> bool:
        """Check if the worker should shutdown"""
        return self.shutdown_flag
