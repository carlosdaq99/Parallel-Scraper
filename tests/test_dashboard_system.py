#!/usr/bin/env python3
"""Test system resources in dashboard"""

import sys
import os
import asyncio

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from real_time_monitor import demo_dashboard
from data_structures import ParallelWorkerContext


async def test_dashboard_system_resources():
    """Test dashboard with system resources working"""
    print("Testing dashboard with system resources...")

    # Create basic worker context
    context = ParallelWorkerContext()

    # Simulate some completed and failed tasks
    for i in range(10):
        await context.mark_task_completed(
            f"worker_{i}", f"https://example.com/page_{i}"
        )
        if i % 3 == 0:  # Add some failures
            await context.mark_task_failed(f"worker_{i}_fail", Exception("Test error"))

    print(
        f"Tasks created - Completed: {len(context.completed_tasks)}, Failed: {len(context.failed_tasks)}"
    )

    # Start monitoring for a short time
    monitor_task = asyncio.create_task(
        start_dashboard_monitoring(context, update_interval=3)
    )

    # Let it run for 6 seconds (2 updates)
    await asyncio.sleep(6)

    monitor_task.cancel()

    try:
        await monitor_task
    except asyncio.CancelledError:
        pass

    print("Dashboard test completed!")


if __name__ == "__main__":
    asyncio.run(test_dashboard_system_resources())
