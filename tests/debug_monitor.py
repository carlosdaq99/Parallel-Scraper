#!/usr/bin/env python3
"""
Debug    # Add some completed tasks to simulate activity
    for i in range(10):
        context.completed_tasks[f"task_{i}"] = f"https://example.com/{i}"

    # Add some failed tasks
    for i in range(5):
        context.failed_tasks[f"failed_task_{i}"] = Exception(f"Error {i}")

    # Add tasks to queue
    for i in range(3):
        await context.task_queue.put(f"https://example.com/pending_{i}")

    print("Test setup:")
    print(f"  - Completed tasks: {len(context.completed_tasks)}")
    print(f"  - Failed tasks: {len(context.failed_tasks)}")
    print(f"  - Queue size: {context.task_queue.qsize()}")
    print(f"  - Active workers: {len(context.worker_manager.active_workers)}")hows exactly what the dashboard sees
"""

import asyncio
import logging
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import modules
from data_structures import ParallelWorkerContext
from real_time_monitor import RealTimeMonitor


async def main():
    """Debug test to see what the monitor actually collects"""

    print("=" * 60)
    print("DEBUG MONITOR TEST")
    print("=" * 60)

    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

    # Create worker context with some test data
    context = ParallelWorkerContext(max_workers=2, logger=logger)

    # Add some completed tasks to simulate activity
    for i in range(10):
        context.completed_tasks[f"task_{i}"] = f"https://example.com/{i}"

    # Add some failed tasks
    for i in range(5):
        context.failed_tasks[f"failed_task_{i}"] = Exception(f"Error {i}")

    # Add tasks to queue
    for i in range(3):
        await context.task_queue.put(f"https://example.com/pending_{i}")

    print(f"Test setup:")
    print(f"  - Completed tasks: {len(context.completed_tasks)}")
    print(f"  - Failed tasks: {len(context.failed_tasks)}")
    print(f"  - Queue size: {context.task_queue.qsize()}")
    print(f"  - Active workers: {len(context.worker_manager.active_workers)}")
    print()

    # Create monitor with this context
    monitor = RealTimeMonitor(update_interval=5, worker_context=context)

    # Manually collect metrics to debug
    print("Collecting metrics...")
    metrics = monitor._collect_current_metrics()

    print(f"Raw metrics collected:")
    print(f"  - has_performance_data: {metrics.has_performance_data}")
    print(f"  - has_worker_data: {metrics.has_worker_data}")
    print(f"  - success_rate: {metrics.success_rate}")
    print(f"  - total_processed: {metrics.total_processed}")
    print(f"  - errors_count: {metrics.errors_count}")
    print(f"  - active_workers: {metrics.active_workers}")
    print(f"  - queue_length: {metrics.queue_length}")
    print()

    # Check the condition manually
    condition_values = [
        metrics.success_rate,
        metrics.total_processed,
        metrics.active_workers,
    ]
    print(f"Condition check for has_performance_data:")
    print(
        f"  - success_rate: {metrics.success_rate} (truthy: {bool(metrics.success_rate)})"
    )
    print(
        f"  - total_processed: {metrics.total_processed} (truthy: {bool(metrics.total_processed)})"
    )
    print(
        f"  - active_workers: {metrics.active_workers} (truthy: {bool(metrics.active_workers)})"
    )
    print(f"  - any() result: {any(condition_values)}")
    print()

    # Test a few dashboard updates
    print("Testing dashboard output:")
    print("=" * 60)

    for i in range(3):
        print(f"\\nUpdate {i+1}:")
        monitor._draw_performance_section(metrics)

        if i < 2:
            # Add more data for next iteration
            context.completed_tasks.append(f"https://example.com/new_{i}")
            await context.task_queue.put(f"https://example.com/new_pending_{i}")
            metrics = monitor._collect_current_metrics()

        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
