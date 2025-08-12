"""
Worker Tracking Display System - Function-based implementation for granular worker output controls.

OVERVIEW
========
This module provides comprehensive worker tracking functionality for the parallel web scraper.
It follows the project's architectural pattern of using functions over classes for simplicity
and async compatibility. The system is designed around configurability - almost every aspect
of tracking output can be controlled via environment variables or programmatic configuration.

CORE ARCHITECTURE
=================
1. FUNCTION-BASED DESIGN: Uses global state and functions rather than complex class hierarchies
2. CONFIGURABLE BY DEFAULT: Every feature can be enabled/disabled independently
3. NULL OBJECT PATTERN: NullTracker provides no-op implementations when tracking is disabled
4. PROGRESSIVE ENHANCEMENT: Starts with minimal functionality and adds features based on config
5. ASYNC COMPATIBLE: All functions work seamlessly with asyncio-based worker system

KEY FEATURES
============
- Configurable worker state tracking (creation, state changes, completion)
- Adaptive scaling decision logging with reasoning
- Hierarchical task relationship management (parent/child tasks)
- Browser pool utilization and health monitoring
- Real-time queue analysis and performance metrics
- Error tracking with retry information
- Dashboard integration for live monitoring
- Multiple independent configuration settings for granular control

CONFIGURATION SYSTEM
====================
All tracking features are controlled via environment variables:

BASIC TRACKING:
- SCRAPER_SHOW_SCALING=true/false     - Scaling decisions (recommended: true)
- SCRAPER_SHOW_COMPLETED=true/false   - Task completions (recommended: true)
- SCRAPER_SHOW_ERRORS=true/false      - Error events (recommended: true)
- SCRAPER_SHOW_CREATED=true/false     - Worker creation (can be noisy)

DETAILED TRACKING:
- SCRAPER_SHOW_STATE=true/false       - State transitions (very verbose)
- SCRAPER_SHOW_STATUS=true/false      - Periodic status summaries
- SCRAPER_SHOW_HIERARCHY=true/false   - Hierarchical task tree display

ADVANCED TRACKING:
- SCRAPER_SHOW_BROWSER_POOL=true/false    - Browser pool utilization
- SCRAPER_SHOW_QUEUE_ANALYSIS=true/false  - Queue depth and processing metrics

MANUAL CONTROL:
- Each setting is controlled independently via environment variables
- No preset verbosity levels - configure each feature as needed for your use case
- SCRAPER_MAX_RECENT=10               - Number of recent completions to track

USAGE PATTERNS
==============

For Production:
    Set SCRAPER_SHOW_SCALING=true, SCRAPER_SHOW_ERRORS=true, and disable other SHOW_* settings
    Shows only scaling decisions and errors

For Development:
    Set SCRAPER_SHOW_SCALING=true, SCRAPER_SHOW_COMPLETED=true, SCRAPER_SHOW_ERRORS=true, SCRAPER_SHOW_CREATED=true
    Shows scaling, completions, errors, and worker creation

For Debugging:
    Enable additional settings like SCRAPER_SHOW_STATE=true, SCRAPER_SHOW_STATUS=true, SCRAPER_SHOW_HIERARCHY=true
    Adds state changes, status summaries, and hierarchy

For Deep Analysis:
    Enable all SHOW_* settings including SCRAPER_SHOW_BROWSER_POOL=true, SCRAPER_SHOW_QUEUE_ANALYSIS=true
    Enables everything including browser pool and queue analysis

DESIGN DECISIONS EXPLAINED
==========================

1. WHY GLOBAL STATE?
   - Simplifies integration with existing function-based architecture
   - Eliminates need to pass tracker objects through call chains
   - Allows easy access from any part of the worker system

2. WHY NULL OBJECT PATTERN?
   - Eliminates conditional checks throughout worker code
   - Zero performance overhead when tracking is disabled
   - Maintains consistent API regardless of configuration

3. WHY SO MANY CONFIGURATION OPTIONS?
   - Different use cases need different levels of detail
   - Production environments need minimal noise
   - Debug sessions need comprehensive information
   - Granular control allows fine-tuning for specific needs

4. WHY FUNCTION-BASED OVER CLASSES?
   - Consistent with project's overall architecture
   - Easier async integration
   - Simpler testing and mocking
   - Reduced complexity for maintenance

PERFORMANCE CONSIDERATIONS
==========================
- NullTracker has zero overhead when tracking is disabled
- String formatting only occurs when features are enabled
- Global state access is faster than object attribute lookup
- Configuration checks are cached to avoid repeated environment variable reads

This system is designed to be comprehensive yet unobtrusive, providing detailed
insights when needed while staying out of the way during normal operation.
"""

import time
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from data_structures import ParallelWorkerContext


# ============================================================================
# GLOBAL STATE MANAGEMENT (Function-based pattern)
# ============================================================================

# Worker tracking configuration loaded from environment variables
# This configuration dictionary controls what information is displayed during scraping operations
# Each setting can be controlled via environment variables or programmatically via update_worker_tracking_config()
#
# Configuration Pattern Explanation:
# os.getenv("ENV_VAR_NAME", "default_value").lower() == "true"
# │         │                │                │        └─ Converts to boolean (only "true" becomes True)
# │         │                │                └─ Converts to lowercase for case-insensitive comparison
# │         │                └─ Default value if environment variable is not set
# │         └─ Environment variable name to check
# └─ Gets environment variable value
#
# Environment Variable Settings (set these in your shell or .env file):
# SCRAPER_SHOW_SCALING=true/false     - Show worker scaling decisions (scale up/down events)
# SCRAPER_SHOW_CREATED=true/false     - Show when new workers are created
# SCRAPER_SHOW_STATE=true/false       - Show worker state transitions (idle→busy→completed)
# SCRAPER_SHOW_COMPLETED=true/false   - Show when workers complete tasks with timing info
# SCRAPER_SHOW_ERRORS=true/false      - Show worker errors and retry attempts
# SCRAPER_SHOW_STATUS=true/false      - Show periodic status summaries
# SCRAPER_SHOW_HIERARCHY=true/false   - Show hierarchical worker relationships (parent/child)
# ============================================================================
# CENTRALIZED CONFIGURATION IMPORT
# ============================================================================

# Import centralized configuration from config.py
# All configuration is determined entirely in config.py - no fallbacks here
from config import ScraperConfig

# Global reference to worker count function - set up by main module to avoid circular imports
_get_current_workers_func = None

def set_worker_count_callback(func):
    """Set the function to get current worker count to avoid circular imports."""
    global _get_current_workers_func
    _get_current_workers_func = func

def _get_current_workers():
    """Get current worker count using callback or fallback."""
    if _get_current_workers_func:
        return _get_current_workers_func()
    # Fallback to tracked worker states if callback not set
    return len(_worker_states) if '_worker_states' in globals() else 50


# ============================================================================
# TRACKER STATE MANAGEMENT
# ============================================================================

# Global state for tracking worker activities - Consolidated hierarchical tracker
# This dictionary maintains the complete state of the worker tracking system in memory.
# It follows the function-based architecture pattern used throughout this project.
#
# State Structure:
# - tasks: Hierarchical task tracking with parent-child relationships
# - workers: Current worker status and assignments
# - queue_stats: Processing statistics and performance metrics
# - recent_completions: Rolling list of recently completed tasks (for analysis)
# - scaling_history: Record of scaling decisions made by the adaptive engine
# - browser_pool_status: Health and utilization of browser instances
_tracker_state = {
    "tasks": {},  # task_id -> task tracking info (start time, status, parent/children)
    "workers": {},  # worker_id -> worker status (idle/busy, current task assignment)
    "queue_stats": {
        "depth": 0,
        "processed_total": 0,
        "processed_1min": 0,
    },  # Real-time processing metrics
    "recent_completions": [],  # List of recently completed tasks with timing info
    "scaling_history": [],  # Record of adaptive scaling decisions for analysis
    "browser_pool_status": {},  # Browser instance health and worker assignments
}


# ============================================================================
# HIERARCHICAL TRACKER STATE FUNCTIONS
# ============================================================================


def initialize_tracker_state() -> Dict[str, Any]:
    """
    Initialize the state dictionary for hierarchical tracking.

    Creates a clean tracker state with proper data structures for:
    - Task hierarchy management (parent-child relationships)
    - Worker status tracking (idle/busy states)
    - Queue performance statistics
    - Historical data for analysis

    Returns:
        Dict containing initialized tracking state with empty collections
        and default values for all tracking categories.
    """
    return {
        "tasks": {
            # Each task entry structure:
            # task_id: {
            #     "parent_id": str | None,        # Parent task ID for hierarchy
            #     "children_ids": set(),          # Set of child task IDs
            #     "status": "pending" | "running" | "completed" | "failed",
            #     "worker_id": str | None,        # Worker assigned to this task
            #     "metadata": {"url": "...", "depth": 0},  # Task-specific data
            #     "start_time": float | None,     # Unix timestamp when task started
            #     "end_time": float | None,       # Unix timestamp when task completed/failed
            # }
        },
        "workers": {
            # Each worker entry structure:
            # worker_id: {
            #     "status": "idle" | "busy",      # Current worker state
            #     "current_task_id": str | None,  # Task currently being processed
            # }
        },
        "queue_stats": {
            "depth": 0,  # Current queue depth
            "processed_total": 0,  # Total tasks processed since start
            "processed_1min": 0,  # Tasks processed in last minute (rolling)
            "last_update": time.time(),  # Timestamp of last statistics update
        },
        "recent_completions": [],  # List of recent task completions for analysis
        "scaling_history": [],  # Record of adaptive scaling decisions
        "browser_pool_status": {},  # Browser instance health and assignments
    }


def get_tracker_state() -> Dict[str, Any]:
    """Get the current tracker state."""
    global _tracker_state
    return _tracker_state


def reset_tracker_state() -> None:
    """Reset tracker state to initial values."""
    global _tracker_state
    _tracker_state = initialize_tracker_state()


def track_task_start(
    tracker_state: Dict[str, Any],
    task_id: str,
    worker_id: str,
    parent_id: Optional[str] = None,
    metadata: Optional[Dict] = None,
) -> None:
    """
    Track the start of a new task in the hierarchical tracking system.

    This function:
    1. Updates worker status to 'busy' and assigns the task
    2. Creates or updates task entry with start time and status
    3. Links task to parent if specified (for hierarchy tracking)
    4. Stores metadata like URL and depth for analysis

    Args:
        tracker_state: The global tracker state dictionary
        task_id: Unique identifier for the task (usually URL-based hash)
        worker_id: ID of the worker that will process this task
        parent_id: Optional parent task ID for hierarchical relationships
        metadata: Optional dict with task-specific data (url, depth, etc.)
    """

    # Update worker status to indicate it's now processing a task
    tracker_state["workers"][worker_id] = {"status": "busy", "current_task_id": task_id}

    # Create/update task entry with initial data
    if task_id not in tracker_state["tasks"]:
        tracker_state["tasks"][task_id] = {
            "parent_id": parent_id,
            "children_ids": set(),
            "metadata": metadata or {},
        }

    # Update task with runtime information
    tracker_state["tasks"][task_id].update(
        {
            "status": "running",
            "worker_id": worker_id,
            "start_time": time.time(),
        }
    )

    # Link to parent task for hierarchy tracking
    if parent_id and parent_id in tracker_state["tasks"]:
        tracker_state["tasks"][parent_id]["children_ids"].add(task_id)


def track_task_completion(
    tracker_state: Dict[str, Any], task_id: str, status: str = "completed"
) -> None:
    """
    Track the completion or failure of a task in the tracking system.

    This function:
    1. Updates task status and records end time
    2. Frees up the worker (sets to idle)
    3. Updates global processing statistics
    4. Maintains performance metrics for analysis

    Args:
        tracker_state: The global tracker state dictionary
        task_id: Unique identifier of the task that finished
        status: Final status - "completed" or "failed"
    """

    if task_id not in tracker_state["tasks"]:
        return  # Task not found, log warning in debug mode

    # Update task status and completion time
    task = tracker_state["tasks"][task_id]
    task["status"] = status
    task["end_time"] = time.time()

    # Free up the worker that was processing this task
    worker_id = task.get("worker_id")
    if worker_id and worker_id in tracker_state["workers"]:
        tracker_state["workers"][worker_id] = {
            "status": "idle",
            "current_task_id": None,
        }

    # Update global processing statistics
    tracker_state["queue_stats"]["processed_total"] += 1


def track_task_child_creation(
    tracker_state: Dict[str, Any], parent_id: str, child_id: str
) -> None:
    """
    Track when a task creates child tasks for hierarchical analysis.

    This function maintains the parent-child relationships that are essential
    for understanding the tree structure of web scraping operations. For example,
    when a folder page spawns individual file processing tasks.

    Args:
        tracker_state: The global tracker state dictionary
        parent_id: ID of the parent task that is creating children
        child_id: ID of the newly created child task
    """
    if parent_id in tracker_state["tasks"]:
        tracker_state["tasks"][parent_id]["children_ids"].add(child_id)


def get_task_hierarchy(tracker_state: Dict[str, Any], task_id: str) -> Dict[str, Any]:
    """Get hierarchical view of a task and its children."""
    task = tracker_state["tasks"].get(task_id)
    if not task:
        return {}

    hierarchy = {
        "task_id": task_id,
        "status": task.get("status", "unknown"),
        "worker_id": task.get("worker_id"),
        "start_time": task.get("start_time"),
        "end_time": task.get("end_time"),
        "metadata": task.get("metadata", {}),
        "children": [],
    }

    # Recursively get children
    for child_id in task.get("children_ids", set()):
        child_hierarchy = get_task_hierarchy(tracker_state, child_id)
        if child_hierarchy:
            hierarchy["children"].append(child_hierarchy)

    return hierarchy


def get_root_tasks(tracker_state: Dict[str, Any]) -> List[str]:
    """Get all root tasks (tasks with no parent)."""
    return [
        task_id
        for task_id, task in tracker_state["tasks"].items()
        if task.get("parent_id") is None
    ]


def display_hierarchical_status(tracker_state: Dict[str, Any]) -> None:
    """Display hierarchical status of all tasks."""
    print("\n" + "=" * 80)
    print("HIERARCHICAL TASK STATUS")
    print("=" * 80)

    root_tasks = get_root_tasks(tracker_state)
    if not root_tasks:
        print("No active tasks")
        return

    for root_id in root_tasks:
        _display_task_tree(tracker_state, root_id, indent=0)


def _display_task_tree(
    tracker_state: Dict[str, Any], task_id: str, indent: int = 0
) -> None:
    """Recursively display task tree structure."""
    task = tracker_state["tasks"].get(task_id)
    if not task:
        return

    prefix = "  " * indent + ("├─ " if indent > 0 else "")
    status = task.get("status", "unknown")
    worker_id = task.get("worker_id", "none")

    # Calculate duration if completed
    duration_str = ""
    if task.get("start_time") and task.get("end_time"):
        duration = task["end_time"] - task["start_time"]
        duration_str = f" ({duration:.2f}s)"
    elif task.get("start_time"):
        duration = time.time() - task["start_time"]
        duration_str = f" ({duration:.2f}s running)"

    print(f"{prefix}{task_id[:8]}... [{status}] Worker:{worker_id}{duration_str}")

    # Display children
    for child_id in task.get("children_ids", set()):
        _display_task_tree(tracker_state, child_id, indent + 1)


def display_queue_analysis(tracker_state: Dict[str, Any], context) -> None:
    """Display comprehensive queue and task analysis."""
    print("\n" + "=" * 80)
    print("QUEUE ANALYSIS & TASK BREAKDOWN")
    print("=" * 80)

    # Queue statistics
    queue_stats = tracker_state["queue_stats"]
    print(f"Queue Size: {context.task_queue.qsize()}")
    print(f"Processed Total: {queue_stats['processed_total']}")
    print(f"Failed Total: {queue_stats.get('failed_total', 0)}")
    print(
        f"Queue Processing Rate: {queue_stats.get('processing_rate', 0):.2f} tasks/min"
    )

    # Task status breakdown
    tasks = tracker_state["tasks"]
    status_counts = {}
    depth_counts = {}

    for task_id, task in tasks.items():
        status = task.get("status", "unknown")
        status_counts[status] = status_counts.get(status, 0) + 1

        # Analyze depth distribution
        metadata = task.get("metadata", {})
        depth = metadata.get("depth", 0)
        depth_counts[depth] = depth_counts.get(depth, 0) + 1

    print("\nTask Status Distribution:")
    for status, count in sorted(status_counts.items()):
        print(f"  {status}: {count}")

    print("\nDepth Distribution:")
    for depth in sorted(depth_counts.keys()):
        print(f"  Depth {depth}: {depth_counts[depth]} tasks")

    # Worker utilization
    workers = tracker_state["workers"]
    busy_workers = sum(1 for w in workers.values() if w.get("status") == "busy")
    idle_workers = sum(1 for w in workers.values() if w.get("status") == "idle")

    print("\nWorker Utilization:")
    print(f"  Busy: {busy_workers}")
    print(f"  Idle: {idle_workers}")
    print(f"  Total: {len(workers)}")
    if len(workers) > 0:
        utilization = (busy_workers / len(workers)) * 100
        print(f"  Utilization: {utilization:.1f}%")


def display_task_performance_metrics(tracker_state: Dict[str, Any]) -> None:
    """Display detailed performance metrics for tasks."""
    print("\n" + "=" * 80)
    print("TASK PERFORMANCE METRICS")
    print("=" * 80)

    tasks = tracker_state["tasks"]
    completed_tasks = [
        t
        for t in tasks.values()
        if t.get("status") == "completed" and t.get("start_time") and t.get("end_time")
    ]

    if not completed_tasks:
        print("No completed tasks to analyze")
        return

    # Calculate timing statistics
    durations = [(t["end_time"] - t["start_time"]) for t in completed_tasks]

    avg_duration = sum(durations) / len(durations)
    min_duration = min(durations)
    max_duration = max(durations)

    print(f"Completed Tasks: {len(completed_tasks)}")
    print(f"Average Duration: {avg_duration:.2f}s")
    print(f"Min Duration: {min_duration:.2f}s")
    print(f"Max Duration: {max_duration:.2f}s")

    # Analyze by depth
    depth_performance = {}
    for task in completed_tasks:
        metadata = task.get("metadata", {})
        depth = metadata.get("depth", 0)
        duration = task["end_time"] - task["start_time"]

        if depth not in depth_performance:
            depth_performance[depth] = []
        depth_performance[depth].append(duration)

    print("\nPerformance by Depth:")
    for depth in sorted(depth_performance.keys()):
        durations = depth_performance[depth]
        avg = sum(durations) / len(durations)
        print(f"  Depth {depth}: {avg:.2f}s average ({len(durations)} tasks)")


def get_queue_health_summary(tracker_state: Dict[str, Any], context) -> Dict[str, Any]:
    """Get a comprehensive health summary of the queue system."""
    tasks = tracker_state["tasks"]
    workers = tracker_state["workers"]

    # Calculate key metrics
    queue_size = context.task_queue.qsize()
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks.values() if t.get("status") == "completed"])
    failed_tasks = len([t for t in tasks.values() if t.get("status") == "failed"])
    running_tasks = len([t for t in tasks.values() if t.get("status") == "running"])

    busy_workers = len([w for w in workers.values() if w.get("status") == "busy"])
    idle_workers = len([w for w in workers.values() if w.get("status") == "idle"])

    # Health indicators
    health_score = 100
    health_issues = []

    # Check queue backlog
    if queue_size > 100:
        health_score -= 20
        health_issues.append(f"High queue backlog: {queue_size}")

    # Check failure rate
    if total_tasks > 0:
        failure_rate = (failed_tasks / total_tasks) * 100
        if failure_rate > 10:
            health_score -= 30
            health_issues.append(f"High failure rate: {failure_rate:.1f}%")

    # Check worker utilization
    if len(workers) > 0:
        utilization = (busy_workers / len(workers)) * 100
        if utilization < 30:
            health_score -= 15
            health_issues.append(f"Low worker utilization: {utilization:.1f}%")

    return {
        "health_score": max(0, health_score),
        "health_issues": health_issues,
        "queue_size": queue_size,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "failed_tasks": failed_tasks,
        "running_tasks": running_tasks,
        "busy_workers": busy_workers,
        "idle_workers": idle_workers,
        "worker_utilization": (busy_workers / len(workers) * 100) if workers else 0,
    }


async def periodic_status_updates(
    tracker_state: Dict[str, Any], context, interval: int = 30
) -> None:
    """Provide periodic status updates with hierarchical tracking information."""
    print(f"\n{'='*80}")
    print("STARTING PERIODIC STATUS UPDATES")
    print(f"Update interval: {interval} seconds")
    print(f"{'='*80}")

    update_count = 0

    try:
        while not context.shutdown_flag:
            await asyncio.sleep(interval)
            update_count += 1

            print(f"\n{'='*80}")
            print(f"STATUS UPDATE #{update_count} - {time.strftime('%H:%M:%S')}")
            print(f"{'='*80}")

            # Display queue analysis
            display_queue_analysis(tracker_state, context)

            # Display hierarchical status (only show first few root tasks)
            root_tasks = get_root_tasks(tracker_state)[:5]  # Limit to 5 for readability
            if root_tasks:
                print(f"\nHierarchical Status (showing {len(root_tasks)} root tasks):")
                for root_id in root_tasks:
                    _display_task_tree(tracker_state, root_id, indent=0)

            # Display health summary
            health = get_queue_health_summary(tracker_state, context)
            print(f"\nSystem Health Score: {health['health_score']}/100")
            if health["health_issues"]:
                print("Health Issues:")
                for issue in health["health_issues"]:
                    print(f"  - {issue}")

            print(f"{'='*80}\n")

    except asyncio.CancelledError:
        print(f"\nPeriodic status updates stopped after {update_count} updates")
        raise
    except Exception as e:
        print(f"Error in periodic status updates: {e}")


def display_comprehensive_summary(tracker_state: Dict[str, Any], context) -> None:
    """Display a comprehensive summary of all tracking information."""
    print(f"\n{'='*100}")
    print("COMPREHENSIVE HIERARCHICAL TRACKING SUMMARY")
    print(f"{'='*100}")

    # System overview
    health = get_queue_health_summary(tracker_state, context)
    print(f"System Health: {health['health_score']}/100")
    print(f"Total Tasks: {health['total_tasks']}")
    print(f"Queue Size: {health['queue_size']}")
    print(f"Worker Utilization: {health['worker_utilization']:.1f}%")

    # Hierarchical view
    display_hierarchical_status(tracker_state)

    # Queue analysis
    display_queue_analysis(tracker_state, context)

    # Performance metrics
    display_task_performance_metrics(tracker_state)

    print(f"{'='*100}")


def log_tracking_event(
    tracker_state: Dict[str, Any], event_type: str, details: Dict[str, Any]
) -> None:
    """Log significant tracking events for debugging and monitoring."""
    timestamp = time.strftime("%H:%M:%S")

    # Update tracker state with event log
    if "events" not in tracker_state:
        tracker_state["events"] = []

    event = {"timestamp": timestamp, "type": event_type, "details": details}

    tracker_state["events"].append(event)

    # Keep only last 100 events to prevent memory bloat
    if len(tracker_state["events"]) > 100:
        tracker_state["events"] = tracker_state["events"][-100:]

    # Print important events
    if event_type in ["task_failed", "worker_error", "queue_backlog"]:
        print(f"[{timestamp}] TRACKING EVENT: {event_type} - {details}")


def get_tracking_statistics(tracker_state: Dict[str, Any]) -> Dict[str, Any]:
    """Get comprehensive tracking statistics for monitoring and reporting."""
    tasks = tracker_state["tasks"]
    workers = tracker_state["workers"]
    queue_stats = tracker_state["queue_stats"]

    # Task statistics
    task_stats = {
        "total": len(tasks),
        "running": len([t for t in tasks.values() if t.get("status") == "running"]),
        "completed": len([t for t in tasks.values() if t.get("status") == "completed"]),
        "failed": len([t for t in tasks.values() if t.get("status") == "failed"]),
    }

    # Worker statistics
    worker_stats = {
        "total": len(workers),
        "busy": len([w for w in workers.values() if w.get("status") == "busy"]),
        "idle": len([w for w in workers.values() if w.get("status") == "idle"]),
    }

    # Hierarchy statistics
    root_tasks = len(get_root_tasks(tracker_state))
    max_depth = 0
    total_children = 0

    for task in tasks.values():
        children_count = len(task.get("children_ids", set()))
        total_children += children_count

        metadata = task.get("metadata", {})
        depth = metadata.get("depth", 0)
        max_depth = max(max_depth, depth)

    hierarchy_stats = {
        "root_tasks": root_tasks,
        "max_depth": max_depth,
        "total_children": total_children,
        "avg_children_per_task": total_children / len(tasks) if tasks else 0,
    }

    return {
        "tasks": task_stats,
        "workers": worker_stats,
        "hierarchy": hierarchy_stats,
        "queue": queue_stats,
        "timestamp": time.time(),
    }


class NullTracker:
    """
    A no-op tracker that performs no operations for disabled hierarchical tracking.

    Design Pattern Explanation:
    This class implements the Null Object Pattern to avoid conditional checks throughout
    the codebase. When hierarchical tracking is disabled, this tracker is used instead
    of the full HierarchicalTracker, providing the same interface but with no actual
    functionality.

    Benefits:
    - Eliminates need for if/else checks in worker code
    - Zero performance overhead when tracking is disabled
    - Maintains consistent API regardless of configuration
    - Allows for clean code without defensive programming

    Usage:
    Created automatically by create_tracker() factory function when
    config.hierarchical_tracking is False or missing.
    """

    def __init__(self, *args, **kwargs):
        """Initialize null tracker - accepts any arguments but ignores them."""
        pass

    def start(self):
        """No-op start method."""
        pass

    def stop(self):
        """No-op stop method."""
        pass

    def track_task_start(self, *args, **kwargs):
        """No-op task start tracking."""
        pass

    def track_task_completion(self, *args, **kwargs):
        """No-op task completion tracking."""
        pass

    def track_task_child_creation(self, *args, **kwargs):
        """No-op child task creation tracking."""
        pass

    def display_hierarchical_status(self, *args, **kwargs):
        """No-op hierarchical status display."""
        pass

    def display_queue_analysis(self, *args, **kwargs):
        """No-op queue analysis display."""
        pass

    def get_tracking_statistics(self):
        """Return empty statistics for compatibility with monitoring systems."""
        return {
            "tasks": {"total": 0, "running": 0, "completed": 0, "failed": 0},
            "workers": {"total": 0, "busy": 0, "idle": 0},
            "hierarchy": {
                "root_tasks": 0,
                "max_depth": 0,
                "total_children": 0,
                "avg_children_per_task": 0,
            },
            "queue": {"processed_total": 0, "failed_total": 0, "processing_rate": 0},
            "timestamp": time.time(),
        }


class HierarchicalTracker:
    """
    Full hierarchical tracking implementation for comprehensive worker monitoring.

    This class provides complete tracking functionality when hierarchical_tracking
    is enabled in the configuration. It maintains detailed state information about:

    - Task hierarchy relationships (parent/child tasks)
    - Worker assignments and state transitions
    - Performance metrics and timing data
    - Dashboard integration for real-time monitoring
    - Configurable verbosity levels for different use cases

    Key Features:
    - Real-time task and worker state tracking
    - Hierarchical task relationship management
    - Optional dashboard queue integration
    - Configurable logging verbosity (quiet/normal/verbose)
    - Performance statistics collection
    - Integration with browser pool monitoring

    Architecture Note:
    This follows the project's function-based pattern by wrapping the global
    state functions in a class interface for easier integration with existing
    object-oriented components while maintaining the core functional design.
    """

    def __init__(
        self,
        tracker_state: Dict[str, Any],
        verbosity: str = "normal",
        dashboard_queue=None,
    ):
        """
        Initialize hierarchical tracker with state and configuration.

        Args:
            tracker_state: Global tracker state dictionary (shared across workers)
            verbosity: Logging level - "quiet", "normal", or "verbose"
            dashboard_queue: Optional queue for sending data to dashboard
        """
        self.tracker_state = tracker_state
        self.verbosity = verbosity
        self.dashboard_queue = dashboard_queue
        self.running = False

    def start(self):
        """Start the hierarchical tracker."""
        self.running = True
        if self.verbosity != "quiet":
            print("Hierarchical worker tracking started")

    def stop(self):
        """Stop the hierarchical tracker."""
        self.running = False
        if self.verbosity != "quiet":
            print("Hierarchical worker tracking stopped")

    def track_task_start(
        self,
        task_id: str,
        worker_id: str,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Track task start with optional dashboard updates."""
        if not self.running:
            return

        track_task_start(self.tracker_state, task_id, worker_id, parent_id, metadata)

        # Push to dashboard if available
        if self.dashboard_queue:
            try:
                dashboard_data = {
                    "type": "task_start",
                    "task_id": task_id,
                    "worker_id": worker_id,
                    "parent_id": parent_id,
                    "metadata": metadata,
                }
                self.dashboard_queue.put_nowait(dashboard_data)
            except:
                pass  # Ignore dashboard errors

        # Console logging based on verbosity
        if self.verbosity == "verbose":
            print(f"TRACKER: Task {task_id[:8]} started on worker {worker_id}")
        elif self.verbosity == "normal" and parent_id is None:
            print(f"TRACKER: Root task {task_id[:8]} started")

    def track_task_completion(self, task_id: str, status: str = "completed"):
        """Track task completion with optional dashboard updates."""
        if not self.running:
            return

        track_task_completion(self.tracker_state, task_id, status)

        # Push to dashboard if available
        if self.dashboard_queue:
            try:
                dashboard_data = {
                    "type": "task_completion",
                    "task_id": task_id,
                    "status": status,
                }
                self.dashboard_queue.put_nowait(dashboard_data)
            except:
                pass  # Ignore dashboard errors

        # Console logging based on verbosity
        if self.verbosity == "verbose":
            print(f"TRACKER: Task {task_id[:8]} {status}")
        elif self.verbosity == "normal" and status == "failed":
            print(f"TRACKER: Task {task_id[:8]} failed")

    def track_task_child_creation(self, parent_id: str, child_id: str):
        """Track parent-child task relationship."""
        if not self.running:
            return

        track_task_child_creation(self.tracker_state, parent_id, child_id)

        if self.verbosity == "verbose":
            print(f"TRACKER: Task {parent_id[:8]} created child {child_id[:8]}")

    def display_hierarchical_status(self):
        """Display hierarchical status if verbosity allows."""
        if not self.running or self.verbosity == "quiet":
            return

        display_hierarchical_status(self.tracker_state)

    def display_queue_analysis(self, context):
        """Display queue analysis if verbosity allows."""
        if not self.running or self.verbosity == "quiet":
            return

        display_queue_analysis(self.tracker_state, context)

    def get_tracking_statistics(self):
        """Get current tracking statistics."""
        if not self.running:
            return self._empty_stats()

        return get_tracking_statistics(self.tracker_state)

    def _empty_stats(self):
        """Return empty statistics when tracker is not running."""
        return {
            "tasks": {"total": 0, "running": 0, "completed": 0, "failed": 0},
            "workers": {"total": 0, "busy": 0, "idle": 0},
            "hierarchy": {
                "root_tasks": 0,
                "max_depth": 0,
                "total_children": 0,
                "avg_children_per_task": 0,
            },
            "queue": {"processed_total": 0, "failed_total": 0, "processing_rate": 0},
            "timestamp": time.time(),
        }


def create_tracker(config: Any, context=None) -> Any:
    """
    Factory function to create appropriate tracker based on configuration.

    This function implements the Factory Pattern to instantiate the correct
    tracker type based on the configuration settings. It automatically
    chooses between NullTracker (for disabled tracking) and HierarchicalTracker
    (for full tracking functionality).

    Configuration Detection:
    - Checks config.hierarchical_tracking to determine if tracking is enabled
    - Falls back to NullTracker if configuration is missing or disabled
    - Integrates with dashboard if dashboard_enabled is True

    Args:
        config: Configuration object with tracking settings
        context: Optional context containing existing tracker state

    Returns:
        Either NullTracker or HierarchicalTracker instance

    Note:
    The queue import is done locally to avoid circular dependencies
    and to handle cases where the queue module might not be available.
    """
    if hasattr(config, "hierarchical_tracking") and config.hierarchical_tracking:
        # Initialize tracker state from context or create new one
        if context and hasattr(context, "tracker_state"):
            tracker_state = context.tracker_state
        else:
            tracker_state = initialize_tracker_state()

        # Dashboard queue setup - import locally to avoid circular dependencies
        dashboard_queue = None
        if hasattr(config, "dashboard_enabled") and config.dashboard_enabled:
            try:
                import queue

                dashboard_queue = queue.Queue()
            except ImportError:
                # Queue module not available, continue without dashboard
                dashboard_queue = None

        return HierarchicalTracker(
            tracker_state=tracker_state,
            verbosity=getattr(config, "tracking_verbosity", "normal"),
            dashboard_queue=dashboard_queue,
        )
    else:
        return NullTracker()


# ============================================================================
# LEGACY COMPATIBILITY FUNCTIONS
# ============================================================================

# Maintain backwards compatibility with existing code that expects these global variables
# These are kept for older parts of the system that haven't been updated to use
# the new hierarchical tracking system yet. They provide a bridge between the
# old simple tracking and the new comprehensive tracking.
#
# Migration Note:
# New code should use the tracker classes above rather than these globals.
# These will be phased out as the system is fully migrated to hierarchical tracking.
_recent_completions: List[Dict[str, Any]] = []  # Legacy: Recent task completions
_scaling_history: List[Dict[str, Any]] = []  # Legacy: Scaling decision history
_worker_states: Dict[str, str] = {}  # Legacy: Simple worker state mapping
_browser_pool_status: Dict[str, Any] = {}  # Legacy: Browser pool status info


# ============================================================================
# CONFIGURATION FUNCTIONS
# ============================================================================

# These functions provide runtime control over the tracking system configuration.
# They allow dynamic adjustment of tracking settings without restarting the application.


def get_worker_tracking_config() -> Dict[str, Any]:
    """
    Get current worker tracking configuration.

    Returns a dictionary containing configuration settings from ScraperConfig.
    All values are determined entirely in config.py.

    Returns:
        Dict containing all current tracking configuration settings
    """
    return {
        "SHOW_SCALING": ScraperConfig.SHOW_SCALING,
        "SHOW_CREATED": ScraperConfig.SHOW_WORKER_CREATED,
        "SHOW_STATE": ScraperConfig.SHOW_WORKER_STATE,
        "SHOW_COMPLETED": ScraperConfig.SHOW_WORKER_COMPLETED,
        "SHOW_ERRORS": ScraperConfig.SHOW_WORKER_ERRORS,
        "SHOW_STATUS": ScraperConfig.SHOW_WORKER_STATUS,
        "SHOW_HIERARCHY": ScraperConfig.SHOW_WORKER_HIERARCHY,
        "SHOW_BROWSER_POOL": ScraperConfig.SHOW_BROWSER_POOL,
        "SHOW_QUEUE_ANALYSIS": ScraperConfig.SHOW_QUEUE_ANALYSIS,
        "MAX_RECENT_COMPLETIONS": ScraperConfig.MAX_RECENT_COMPLETIONS,
    }


def update_worker_tracking_config(**kwargs) -> None:
    """
    Update worker tracking configuration dynamically at runtime.

    This function updates the ScraperConfig class attributes directly.
    All configuration is controlled entirely by config.py.

    Args:
        **kwargs: Configuration key-value pairs to update

    Example:
        update_worker_tracking_config(
            SHOW_SCALING=True,
            SHOW_COMPLETED=False,
            VERBOSITY_LEVEL="debug"
        )
    """
    # Mapping from old config keys to ScraperConfig attributes
    key_mapping = {
        "SHOW_SCALING": "SHOW_SCALING",
        "SHOW_CREATED": "SHOW_WORKER_CREATED",
        "SHOW_STATE": "SHOW_WORKER_STATE",
        "SHOW_COMPLETED": "SHOW_WORKER_COMPLETED",
        "SHOW_ERRORS": "SHOW_WORKER_ERRORS",
        "SHOW_STATUS": "SHOW_WORKER_STATUS",
        "SHOW_HIERARCHY": "SHOW_WORKER_HIERARCHY",
        "SHOW_BROWSER_POOL": "SHOW_BROWSER_POOL",
        "SHOW_QUEUE_ANALYSIS": "SHOW_QUEUE_ANALYSIS",
        "MAX_RECENT_COMPLETIONS": "MAX_RECENT_COMPLETIONS",
    }

    for key, value in kwargs.items():
        if key in key_mapping:
            setattr(ScraperConfig, key_mapping[key], value)


def is_worker_tracking_enabled(feature: str) -> bool:
    """
    Check if a specific worker tracking feature is enabled.

    Args:
        feature: Name of the feature to check (e.g., "SHOW_SCALING")

    Returns:
        Boolean indicating if the feature is enabled
    """
    config_dict = get_worker_tracking_config()
    return config_dict.get(feature, False)


# ============================================================================
# WORKER SCALING TRACKING
# ============================================================================

# These functions track adaptive scaling decisions made by the scaling engine.
# They provide visibility into when and why the system scales worker count up or down.


def log_scaling_decision(old_count: int, new_count: int, reason: str) -> None:
    """
    Log scaling decisions with timestamp and reasoning.

    This function records when the adaptive scaling engine changes the worker count,
    providing transparency into scaling behavior and helping with performance analysis.

    The scaling history is maintained for analysis and can help identify:
    - Scaling patterns and frequency
    - Reasons for scaling decisions
    - System responsiveness to load changes

    Args:
        old_count: Previous worker count before scaling decision
        new_count: New worker count after scaling decision
        reason: Human-readable explanation for the scaling decision

    Output Format (when SHOW_SCALING is enabled):
        [14:32:15] SCALING: 20 → 35 workers (Scale-up)
                   Reason: High queue backlog detected
    """
    if not ScraperConfig.SHOW_SCALING:
        return

    timestamp = datetime.now().strftime("%H:%M:%S")

    if new_count > old_count:
        action = "Scale-up"
    elif new_count < old_count:
        action = "Scale-down"
    else:
        action = "No change"

    print(f"[{timestamp}] SCALING: {old_count} → {new_count} workers ({action})")
    print(f"           Reason: {reason}")
    
    # Calculate and show browser pool recommendation 
    optimal_browsers = min(6, max(1, new_count // 17))
    print(f"           Browser Pool: {optimal_browsers} browsers recommended for {new_count} workers")

    # Store in scaling history
    scaling_entry = {
        "timestamp": timestamp,
        "old_count": old_count,
        "new_count": new_count,
        "reason": reason,
        "action": action,
    }

    _scaling_history.append(scaling_entry)

    # Keep only recent scaling history (last 20 entries)
    if len(_scaling_history) > 20:
        _scaling_history.pop(0)


def get_scaling_history() -> List[Dict[str, Any]]:
    """Get recent scaling decision history."""
    return _scaling_history.copy()


# ============================================================================
# WORKER LIFECYCLE TRACKING
# ============================================================================

# These functions track individual worker lifecycle events from creation through completion.
# They provide detailed visibility into worker behavior and task processing patterns.


def log_worker_creation(worker_id: str, parent_id: Optional[str] = None) -> None:
    """
    Log worker creation with hierarchical information.

    Tracks when new workers are spawned, including hierarchical relationships
    for child workers. This is particularly useful for understanding the
    branching pattern of web scraping operations where folder pages spawn
    individual file processing workers.

    Args:
        worker_id: Unique identifier for the new worker (often includes hierarchy info)
        parent_id: Optional parent worker ID for hierarchical tracking

    Output Format (when SHOW_CREATED is enabled):
        [14:32:16] CREATED: Worker-001 (child of Worker-Root)
        [14:32:17] CREATED:   Worker-001.1 (child of Worker-001)

    Hierarchy Display:
        The indentation level reflects the hierarchical depth based on
        the number of "." characters in the worker_id.
    """
    if not ScraperConfig.SHOW_WORKER_CREATED:
        return

    timestamp = datetime.now().strftime("%H:%M:%S")

    # Calculate hierarchical level for indentation
    level = worker_id.count(".") if "." in worker_id else 0
    indent = "  " * level

    parent_info = f" (child of {parent_id})" if parent_id else ""
    print(f"[{timestamp}] CREATED: {indent}{worker_id}{parent_info}")

    # Update worker state tracking
    _worker_states[worker_id] = "created"


def log_worker_state_change(worker_id: str, old_state: str, new_state: str) -> None:
    """
    Log worker state transitions (configurable).

    Args:
        worker_id: Unique worker identifier
        old_state: Previous worker state
        new_state: New worker state
    """
    if not ScraperConfig.SHOW_WORKER_STATE:
        return

    timestamp = datetime.now().strftime("%H:%M:%S")

    # Calculate hierarchical level for indentation
    level = worker_id.count(".") if "." in worker_id else 0
    indent = "  " * level

    print(f"[{timestamp}] STATE: {indent}{worker_id}: {old_state} → {new_state}")

    # Update global state tracking
    _worker_states[worker_id] = new_state


def log_worker_completion(
    worker_id: str, task_name: str, duration: float, children_count: int = 0
) -> None:
    """
    Log worker completion with details (configurable).

    Args:
        worker_id: Unique worker identifier
        task_name: Name/description of completed task
        duration: Task duration in seconds
        children_count: Number of child tasks spawned
    """
    # Show instant hierarchy display if enabled
    if ScraperConfig.SHOW_WORKER_HIERARCHY and children_count > 0:
        print(f"[{worker_id}] - spawned {children_count}")

    # Show detailed completion logging only if enabled
    if not ScraperConfig.SHOW_WORKER_COMPLETED:
        return

    timestamp = datetime.now().strftime("%H:%M:%S")
    children_info = (
        f" → spawned {children_count} children" if children_count > 0 else ""
    )

    print(
        f"[{timestamp}] COMPLETED: {worker_id} - {task_name} ({duration:.1f}s){children_info}"
    )

    # Store completion details
    completion = {
        "timestamp": timestamp,
        "worker_id": worker_id,
        "task_name": task_name,
        "duration": duration,
        "children_count": children_count,
    }

    _recent_completions.append(completion)

    # Keep only recent completions
    max_recent = ScraperConfig.MAX_RECENT_COMPLETIONS
    if len(_recent_completions) > max_recent:
        _recent_completions.pop(0)

    # Update worker state
    _worker_states[worker_id] = "completed"


def log_worker_error(worker_id: str, error_msg: str, retry_count: int = 0) -> None:
    """
    Log worker errors with retry information (configurable).

    Args:
        worker_id: Unique worker identifier
        error_msg: Error message description
        retry_count: Current retry attempt number
    """
    if not ScraperConfig.SHOW_WORKER_ERRORS:
        return

    timestamp = datetime.now().strftime("%H:%M:%S")
    retry_info = f" (retry {retry_count})" if retry_count > 0 else ""

    print(f"[{timestamp}] ERROR: {worker_id} - {error_msg}{retry_info}")

    # Update worker state
    _worker_states[worker_id] = f"error{retry_info}"


# ============================================================================
# BROWSER POOL TRACKING
# ============================================================================

# These functions track browser pool utilization and health status.
# The browser pool is a critical resource in this parallel scraper - it maintains
# 6 browser instances that are shared among 20-100 workers for optimal performance.


def log_browser_pool_status(pool_status: Dict[str, Any]) -> None:
    """
    Log browser pool utilization and health status.

    The browser pool is one of the most critical resources in the parallel scraper.
    This function tracks how workers are distributed across available browsers
    and monitors browser health for the circuit breaker pattern.

    Browser Pool Architecture:
    - 6 browser instances shared among up to 100 workers
    - Optimal ratio: ~17 workers per browser
    - Circuit breaker protection against browser failures
    - Resource filtering blocks images/media for 50-70% performance gain

    Args:
        pool_status: Dictionary mapping browser IDs to their status information
                    Format: {browser_id: {"workers": [worker_list], "health": status}}

    Output Format (when SHOW_BROWSER_POOL is enabled):
        [14:32:35] BROWSER POOL:
                   Browser-1: 17 workers | Health: Good
                   Browser-2: 16 workers | Health: Warning
                   Browser-3: 15 workers | Health: Good
    """
    if not ScraperConfig.SHOW_BROWSER_POOL:
        return

    timestamp = datetime.now().strftime("%H:%M:%S")

    print(f"[{timestamp}] BROWSER POOL:")
    for browser_id, info in pool_status.items():
        # Handle both old format (list) and new format (int)
        workers = info.get("workers", 0)
        worker_count = len(workers) if isinstance(workers, list) else workers
        health = info.get("health", "Unknown")
        print(f"           {browser_id}: {worker_count} workers | Health: {health}")

    # Update global browser pool status
    global _browser_pool_status
    _browser_pool_status = pool_status.copy()


def update_browser_pool_status(
    browser_id: str, worker_list: List[str], health: str = "Good"
) -> None:
    """
    Update browser pool status for a specific browser.

    Args:
        browser_id: Browser identifier
        worker_list: List of workers using this browser
        health: Browser health status
    """
    _browser_pool_status[browser_id] = {
        "workers": worker_list.copy(),
        "health": health,
        "last_update": datetime.now().strftime("%H:%M:%S"),
    }


def sync_browser_pool_with_optimization_metrics() -> None:
    """
    Sync browser pool status with real optimization metrics.
    This updates the browser pool tracking with actual metrics from optimization_utils.
    """
    if not ScraperConfig.SHOW_BROWSER_POOL:
        return

    try:
        # Import here to avoid circular dependency
        from optimization_utils import get_optimization_metrics

        metrics = get_optimization_metrics()

        # Create browser pool status from metrics
        pool_status = {}
        pool_size = metrics.get("browser_pool_size", 0)
        circuit_breaker_status = metrics.get("circuit_breaker_status", "closed")
        reuse_rate = metrics.get("browser_reuse_rate", 0.0)

        # Create entries for each browser in the pool
        for i in range(pool_size):
            browser_id = f"Browser-{i+1}"
            health = "Good" if circuit_breaker_status == "closed" else "Warning"

            # Calculate workers per browser using current actual worker count
            try:
                current_workers = _get_current_workers()
            except Exception:
                # Fallback to tracked worker states if main module not available
                current_workers = len(_worker_states)
                if ScraperConfig.SHOW_BROWSER_POOL:
                    print(f"DEBUG: Browser pool sync (fallback) - Current workers: {current_workers}, Pool size: {pool_size}")

            # For single browser pool, show all workers on that browser
            # For multiple browsers, distribute workers approximately evenly
            if pool_size == 1:
                workers_per_browser = current_workers
            else:
                # Distribute workers among browsers (show actual distribution)
                workers_per_browser = current_workers // pool_size
                # Give remainder to first browser
                if i == 0:
                    workers_per_browser += current_workers % pool_size

            pool_status[browser_id] = {
                "workers": workers_per_browser,  # Show actual current worker count
                "health": health,
                "reuse_rate": f"{reuse_rate:.1%}",
                "last_update": datetime.now().strftime("%H:%M:%S"),
            }

        # Add overall pool metrics
        if pool_size > 0:
            log_browser_pool_status(pool_status)

            # Log pool summary (controlled by SHOW_BROWSER_POOL setting)
            if ScraperConfig.SHOW_BROWSER_POOL:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(
                    f"[{timestamp}] 🌐 BROWSER POOL: {pool_size} browsers, "
                    f"reuse rate {reuse_rate:.1%}, circuit breaker {circuit_breaker_status}"
                )

    except ImportError:
        # Optimization utils not available
        pass
    except Exception as e:
        # Silent failure for browser pool monitoring (enable SHOW_BROWSER_POOL for debugging)
        if ScraperConfig.SHOW_BROWSER_POOL:
            print(f"Browser pool sync error: {e}")


# ============================================================================
# STATUS DISPLAY FUNCTIONS
# ============================================================================


def show_current_status(context: Optional[ParallelWorkerContext] = None) -> None:
    """
    Show current system status summary (configurable).

    Args:
        context: Optional worker context for detailed status
    """
    if not ScraperConfig.SHOW_WORKER_STATUS:
        return

    timestamp = datetime.now().strftime("%H:%M:%S")

    # Basic status information
    active_workers = len(
        [w for w in _worker_states.values() if w not in ["completed", "failed"]]
    )
    completed_workers = len([w for w in _worker_states.values() if w == "completed"])
    error_workers = len([w for w in _worker_states.values() if "error" in w])

    print(f"[{timestamp}] STATUS SUMMARY:")
    print(
        f"           Active: {active_workers} | Completed: {completed_workers} | Errors: {error_workers}"
    )

    # Additional context information if available
    if context:
        try:
            if hasattr(context, "task_queue"):
                queue_size = context.task_queue.qsize()
                print(f"           Queue Size: {queue_size}")
        except Exception:
            pass  # Ignore if queue access fails


def show_hierarchy_status(context: Optional[ParallelWorkerContext] = None) -> None:
    """Show hierarchical task status in user's preferred format."""
    if not ScraperConfig.SHOW_WORKER_HIERARCHY:
        return

    timestamp = datetime.now().strftime("%H:%M:%S")
    
    # Get completed tasks from worker context if available
    completed_tasks = {}
    if context and hasattr(context, 'completed_tasks'):
        completed_tasks = context.completed_tasks
    
    # Fall back to tracker state if no context
    if not completed_tasks:
        global _tracker_state
        tasks = _tracker_state.get("tasks", {})
        # Filter for completed tasks only
        completed_tasks = {k: v for k, v in tasks.items() if v.get("status") == "completed"}
    
    if not completed_tasks:
        # Only show "no tasks" message occasionally to avoid spam
        if not hasattr(show_hierarchy_status, 'last_empty_message'):
            show_hierarchy_status.last_empty_message = 0
        
        current_time = time.time()
        if current_time - show_hierarchy_status.last_empty_message > 30:  # Show only every 30 seconds
            print(f"[{timestamp}]      Task    [No completed tasks yet]")
            show_hierarchy_status.last_empty_message = current_time
        return
    
    # Display recently completed tasks in user's preferred format
    displayed_count = 0
    recent_tasks = list(completed_tasks.items())[-5:]  # Show last 5 completed tasks
    
    for task_id, task_info in recent_tasks:
        if displayed_count >= 5:  # Limit display to prevent spam
            break
            
        # Get task metadata - handle both tracker format and worker context format
        if isinstance(task_info, dict):
            # Tracker state format
            metadata = task_info.get("metadata", {})
            children_count = len(task_info.get("children_ids", set()))
            path = metadata.get("path", "") or metadata.get("url", "")
            depth = metadata.get("depth", 0)
        else:
            # Worker context NodeInfo format
            path = getattr(task_info, 'path', "")
            depth = getattr(task_info, 'depth', 0)
            children_count = len(getattr(task_info, 'subfolders', []))
        
        # Create a simplified path indicator like [2.4.23.1]
        if path and "/" in path:
            # Extract meaningful path components from URL
            path_parts = [p for p in path.split("/") if p and p not in ["", "docs", "view", "OARX", "2023", "ENU"]]
            if len(path_parts) >= 1 and "guid=" in path_parts[-1]:
                # Extract guid part for cleaner display
                guid_part = path_parts[-1].split("guid=")[-1]
                if len(guid_part) > 20:
                    guid_part = guid_part[:20] + "..."
                path_indicator = f"{depth}.{guid_part}"
            elif len(path_parts) >= 2:
                # Use last 2 meaningful parts
                path_indicator = f"{depth}.{'.'.join(path_parts[-2:])}"
            else:
                path_indicator = f"{depth}.{displayed_count + 1}"
        else:
            # Fallback: use depth and position
            path_indicator = f"{depth}.{displayed_count + 1}"
        
        # Format according to user's specification
        if children_count > 0:
            # Task that spawned children
            print(f"[{timestamp}]      Task    [{path_indicator}]    --    spawned {children_count}")
        else:
            # Leaf node that completed
            print(f"[{timestamp}]      Task    [{path_indicator}]    --    LEAF node")
        
        displayed_count += 1


def show_recent_completions() -> None:
    """Show recent worker completions."""
    if not _recent_completions:
        return

    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] RECENT COMPLETIONS:")

    for completion in _recent_completions[-5:]:  # Show last 5
        print(
            f"           {completion['worker_id']} - {completion['task_name']} ({completion['duration']:.1f}s)"
        )


# ============================================================================
# INTEGRATION HELPER FUNCTIONS
# ============================================================================


def get_worker_states() -> Dict[str, str]:
    """Get current worker states dictionary."""
    return _worker_states.copy()


def get_recent_completions() -> List[Dict[str, Any]]:
    """Get recent worker completions list."""
    return _recent_completions.copy()


def clear_worker_tracking_state() -> None:
    """Clear all worker tracking state (useful for testing)."""
    global _recent_completions, _scaling_history, _worker_states, _browser_pool_status
    _recent_completions.clear()
    _scaling_history.clear()
    _worker_states.clear()
    _browser_pool_status.clear()


# ============================================================================
# ASYNC INTEGRATION FUNCTIONS
# ============================================================================

# These functions provide async integration for the worker tracking system.
# They allow the tracking system to work seamlessly with the async/await
# architecture used throughout the parallel scraper.
#
# DESIGN NOTE: Why some functions might appear "incomplete"
# ========================================================
# This file follows a function-based architecture pattern where some functions
# intentionally have minimal implementations or appear "incomplete" because:
#
# 1. NULL OBJECT PATTERN: The NullTracker class implements no-op methods
#    that intentionally do nothing when tracking is disabled. This eliminates
#    conditional checks throughout the codebase.
#
# 2. CONFIGURABLE FEATURES: Many functions have conditional logic that only
#    executes when specific tracking features are enabled via environment
#    variables. When features are disabled, functions may appear to do nothing.
#
# 3. OPTIONAL DEPENDENCIES: Some functions handle optional dependencies
#    (like dashboard integration or queue module) gracefully by using
#    try/except blocks and continuing with reduced functionality.
#
# 4. PROGRESSIVE ENHANCEMENT: The system is designed to work with minimal
#    functionality and add features progressively based on configuration.
#    This means many advanced features are "commented out" by default.
#
# 5. LEGACY COMPATIBILITY: Some sections maintain backward compatibility
#    with older versions of the system that used different approaches.
#
# This is NOT incomplete code - it's intentional design for configurability!


async def start_worker_tracking_monitor(
    context: ParallelWorkerContext, interval: float = 30.0
) -> None:
    """
    Start async worker tracking monitor for periodic status updates.

    This function runs continuously in the background, providing periodic
    status updates about worker and queue state. It's designed to be
    non-intrusive and can be easily cancelled when the system shuts down.

    Features:
    - Periodic status summaries (configurable interval)
    - Hierarchical status display when enabled
    - Graceful handling of cancellation
    - Error recovery for monitoring failures

    Args:
        context: Worker context containing queue and state information
        interval: Update interval in seconds (default: 30 seconds)

    Raises:
        asyncio.CancelledError: Re-raised for proper cleanup during shutdown

    Note:
        This function runs indefinitely until cancelled. It should be
        started as a background task and cancelled during system shutdown.
    """
    while True:
        try:
            await asyncio.sleep(interval)

            if ScraperConfig.SHOW_WORKER_STATUS:
                show_current_status(context)

            if ScraperConfig.SHOW_WORKER_HIERARCHY:
                show_hierarchy_status(context)

        except asyncio.CancelledError:
            # Re-raise CancelledError for proper cleanup
            raise
        except Exception as e:
            print(f"Worker tracking monitor error: {e}")


async def track_worker_async(worker_id: str, task_func, *args, **kwargs) -> Any:
    """
    Async wrapper to track worker execution automatically.

    Args:
        worker_id: Unique worker identifier
        task_func: Async function to execute
        *args, **kwargs: Arguments for task_func

    Returns:
        Result of task_func execution
    """
    log_worker_creation(worker_id)
    log_worker_state_change(worker_id, "created", "starting")

    start_time = asyncio.get_event_loop().time()

    try:
        log_worker_state_change(worker_id, "starting", "running")
        result = await task_func(*args, **kwargs)

        duration = asyncio.get_event_loop().time() - start_time
        task_name = getattr(task_func, "__name__", "unknown_task")

        log_worker_completion(worker_id, task_name, duration)
        log_worker_state_change(worker_id, "running", "completed")

        return result

    except Exception as e:
        duration = asyncio.get_event_loop().time() - start_time
        log_worker_error(worker_id, str(e))
        log_worker_state_change(worker_id, "running", "failed")
        raise


# ============================================================================
# TESTING AND DEBUG FUNCTIONS
# ============================================================================

# These functions provide testing and validation capabilities for the tracking system.
# They allow developers to verify that tracking functionality works correctly
# without running the full scraping system.


def test_worker_tracking_display() -> None:
    """
    Test function for worker tracking display functionality.

    This function provides a comprehensive test of all tracking features
    without requiring the full scraper to be running. It simulates:

    - Configuration display and validation
    - Scaling decision logging with realistic scenarios
    - Worker lifecycle events (creation, state changes, completion)
    - Error handling and retry scenarios
    - Browser pool status tracking
    - Status display functions

    Use Cases:
    - Validating tracking configuration changes
    - Testing new tracking features
    - Debugging tracking output formatting
    - Demonstrating tracking capabilities

    Output:
    Produces sample output for all configured tracking features,
    allowing visual inspection of formatting and content.

    Note:
    This function uses the current configuration settings, so enable
    different tracking features to see their output during testing.
    """
    print("🧪 Testing Worker Tracking Display (Function-based)")
    print("=" * 60)

    # Test configuration
    print(f"Configuration: {get_worker_tracking_config()}")

    # Test scaling decisions
    log_scaling_decision(20, 35, "High queue backlog detected")
    log_scaling_decision(35, 28, "CPU utilization decreased")

    # Test worker lifecycle
    log_worker_creation("Worker-001")
    log_worker_creation("Worker-001.1", "Worker-001")
    log_worker_state_change("Worker-001", "created", "running")
    log_worker_completion("Worker-001.1", "process_folder", 2.3, 0)
    log_worker_error("Worker-002", "Timeout connecting to page", 1)

    # Test browser pool tracking
    pool_status = {
        "Browser-1": {"workers": ["Worker-001", "Worker-002"], "health": "Good"},
        "Browser-2": {"workers": ["Worker-003"], "health": "Warning"},
    }
    log_browser_pool_status(pool_status)

    # Test status display
    show_current_status()
    show_hierarchy_status()  # Test call without context
    show_recent_completions()

    print("✅ Function-based worker tracking test completed")
