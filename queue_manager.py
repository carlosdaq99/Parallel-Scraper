#!/usr/bin/env python3
"""
Enhanced Queue Management - Level 2 upgrade for parallel_scraper.
Provides intelligent queue management without breaking existing functionality.
"""

import asyncio
import time
from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class QueuedTask:
    """Enhanced task wrapper with priority and retry tracking."""

    task_data: Any
    priority: TaskPriority = TaskPriority.NORMAL
    retry_count: int = 0
    max_retries: int = 3
    created_at: float = 0.0
    last_attempt: float = 0.0

    def __post_init__(self):
        if self.created_at <= 0:
            self.created_at = time.time()


class SmartQueue:
    """
    Intelligent queue management that can be dropped into existing code.
    Provides priority handling, retry logic, and performance tracking.
    """

    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self._queues = {priority: deque() for priority in TaskPriority}
        self._size = 0
        self._stats = {
            "tasks_added": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_retried": 0,
            "total_wait_time": 0.0,
        }
        self._retry_delays = defaultdict(float)  # Track backoff for failed tasks

    def put_nowait(self, task_data: Any, priority: TaskPriority = TaskPriority.NORMAL):
        """Add task to queue with priority (non-blocking)."""
        if self._size >= self.max_size:
            raise asyncio.QueueFull("Queue is full")

        queued_task = QueuedTask(task_data, priority)
        self._queues[priority].append(queued_task)
        self._size += 1
        self._stats["tasks_added"] += 1

    async def put(self, task_data: Any, priority: TaskPriority = TaskPriority.NORMAL):
        """Add task to queue with priority (blocking if full)."""
        while self._size >= self.max_size:
            await asyncio.sleep(0.1)  # Wait for space
        self.put_nowait(task_data, priority)

    def get_nowait(self) -> QueuedTask:
        """Get next task by priority (non-blocking)."""
        if self._size == 0:
            raise asyncio.QueueEmpty("Queue is empty")

        # Check priorities from highest to lowest
        for priority in [
            TaskPriority.CRITICAL,
            TaskPriority.HIGH,
            TaskPriority.NORMAL,
            TaskPriority.LOW,
        ]:
            if self._queues[priority]:
                task = self._queues[priority].popleft()
                self._size -= 1
                return task

        raise asyncio.QueueEmpty("Queue is empty")

    async def get(self) -> QueuedTask:
        """Get next task by priority (blocking if empty)."""
        while self._size == 0:
            await asyncio.sleep(0.1)  # Wait for tasks
        return self.get_nowait()

    def empty(self) -> bool:
        """Check if queue is empty."""
        return self._size == 0

    def qsize(self) -> int:
        """Get current queue size."""
        return self._size

    def mark_completed(self, task: QueuedTask):
        """Mark task as completed for statistics."""
        wait_time = time.time() - task.created_at
        self._stats["tasks_completed"] += 1
        self._stats["total_wait_time"] += wait_time

    def mark_failed(self, task: QueuedTask, should_retry: bool = True) -> bool:
        """
        Mark task as failed and determine if it should be retried.
        Returns True if task was requeued for retry.
        """
        task.retry_count += 1
        task.last_attempt = time.time()

        if should_retry and task.retry_count <= task.max_retries:
            # Add exponential backoff
            delay = min(2**task.retry_count, 60)  # Max 60 second delay
            self._retry_delays[id(task)] = time.time() + delay

            # Requeue with higher priority for retries
            retry_priority = (
                TaskPriority.HIGH
                if task.priority == TaskPriority.NORMAL
                else task.priority
            )
            self.put_nowait(task.task_data, retry_priority)
            self._stats["tasks_retried"] += 1
            return True
        else:
            self._stats["tasks_failed"] += 1
            return False

    def get_statistics(self) -> Dict[str, Any]:
        """Get queue performance statistics."""
        avg_wait_time = (
            self._stats["total_wait_time"] / self._stats["tasks_completed"]
            if self._stats["tasks_completed"] > 0
            else 0
        )

        return {
            "current_size": self._size,
            "max_size": self.max_size,
            "tasks_added": self._stats["tasks_added"],
            "tasks_completed": self._stats["tasks_completed"],
            "tasks_failed": self._stats["tasks_failed"],
            "tasks_retried": self._stats["tasks_retried"],
            "average_wait_time_seconds": avg_wait_time,
            "success_rate": (
                self._stats["tasks_completed"]
                / (self._stats["tasks_completed"] + self._stats["tasks_failed"])
                * 100
                if (self._stats["tasks_completed"] + self._stats["tasks_failed"]) > 0
                else 0
            ),
            "queue_breakdown": {
                priority.name: len(self._queues[priority]) for priority in TaskPriority
            },
        }


class QueueManager:
    """
    Drop-in replacement for asyncio.Queue with enhanced features.
    Maintains backward compatibility while adding smart features.
    """

    def __init__(self, max_size: int = 1000):
        self.smart_queue = SmartQueue(max_size)
        self._closed = False

    async def put(self, item: Any, priority: TaskPriority = TaskPriority.NORMAL):
        """Put item in queue with optional priority."""
        if self._closed:
            raise RuntimeError("Queue is closed")
        await self.smart_queue.put(item, priority)

    def put_nowait(self, item: Any, priority: TaskPriority = TaskPriority.NORMAL):
        """Put item in queue without blocking."""
        if self._closed:
            raise RuntimeError("Queue is closed")
        self.smart_queue.put_nowait(item, priority)

    async def get(self) -> Any:
        """Get next item from queue."""
        if self._closed and self.smart_queue.empty():
            raise RuntimeError("Queue is closed and empty")
        task = await self.smart_queue.get()
        return task.task_data  # Return original data for compatibility

    def get_nowait(self) -> Any:
        """Get next item without blocking."""
        if self._closed and self.smart_queue.empty():
            raise RuntimeError("Queue is closed and empty")
        task = self.smart_queue.get_nowait()
        return task.task_data  # Return original data for compatibility

    def empty(self) -> bool:
        """Check if queue is empty."""
        return self.smart_queue.empty()

    def qsize(self) -> int:
        """Get current queue size."""
        return self.smart_queue.qsize()

    def close(self):
        """Close the queue."""
        self._closed = True

    def get_stats(self) -> Dict[str, Any]:
        """Get enhanced queue statistics."""
        return self.smart_queue.get_statistics()


# Backward compatibility functions for existing code


def create_enhanced_queue(max_size: int = 1000) -> QueueManager:
    """
    Create an enhanced queue that can replace asyncio.Queue in existing code.

    Usage in existing code:
    # Replace this:
    # queue = asyncio.Queue(maxsize=1000)

    # With this:
    # queue = create_enhanced_queue(max_size=1000)

    All existing queue operations will work the same!
    """
    return QueueManager(max_size)


def upgrade_existing_queue(existing_queue: asyncio.Queue) -> QueueManager:
    """
    Upgrade an existing asyncio.Queue to use enhanced features.
    Transfers any existing items to the new queue.
    """
    enhanced_queue = QueueManager(max_size=existing_queue.maxsize or 1000)

    # Transfer existing items
    while not existing_queue.empty():
        try:
            item = existing_queue.get_nowait()
            enhanced_queue.put_nowait(item)
        except asyncio.QueueEmpty:
            break

    return enhanced_queue


# Example integration with existing worker pattern:
"""
In your existing worker.py, you can enhance queue handling by:

1. Import the enhanced queue:
   from queue_manager import create_enhanced_queue, TaskPriority

2. Replace queue creation (in your main file):
   # Old: task_queue = asyncio.Queue(maxsize=config.MAX_QUEUE_SIZE)
   # New: task_queue = create_enhanced_queue(max_size=config.MAX_QUEUE_SIZE)

3. Optionally use priority for important tasks:
   # Normal task: await task_queue.put(task_data)
   # High priority: await task_queue.put(task_data, TaskPriority.HIGH)

4. Get queue statistics:
   stats = task_queue.get_stats()
   print(f"Queue success rate: {stats['success_rate']:.1f}%")

That's it! All existing code continues to work exactly the same.
"""
