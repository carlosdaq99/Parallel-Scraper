#!/usr/bin/env python3
"""Quick dashboard test to show final working metrics."""

import os
import asyncio
import logging
import time
import sys
from pathlib import Path

# Set up environment
os.environ["SCRAPER_LOG_LEVEL"] = "ERROR"
os.environ["SCRAPER_MAX_WORKERS"] = "50"  # Default production size
os.environ["ADAPTIVE_MODULES_AVAILABLE"] = "true"

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from data_structures import ParallelWorkerContext
from real_time_monitor import RealTimeMonitor


async def test_final_dashboard():
    """Test the final dashboard display."""
    print("🎯 Final Dashboard Test - Worker Pool Metrics")
    print("=" * 60)

    # Create logger
    logger = logging.getLogger("test")
    logger.setLevel(logging.ERROR)

    # Create worker context with 50 workers (production size)
    context = ParallelWorkerContext(max_workers=50, logger=logger)

    # Simulate some activity
    context.total_tasks_completed = 15
    context.total_tasks_failed = 1

    # Start dashboard
    monitor = RealTimeMonitor(update_interval=5, worker_context=context)

    print("📊 Starting dashboard display for 15 seconds...")
    print("Look for:")
    print("  - Active Workers: 50 (not 0)")
    print("  - Browser Pool: 0 or higher")
    print("  - Success Rate: ~93.8%")
    print("\n" + "=" * 60)

    # Run dashboard for 15 seconds
    task = asyncio.create_task(monitor.start())
    await asyncio.sleep(15)

    # Stop dashboard
    monitor.stop()
    try:
        await task
    except asyncio.CancelledError:
        pass

    print("\n🎉 Final Dashboard Test Completed!")
    print("✅ Active Workers should show 50 (total pool size)")
    print("✅ Browser Pool should show actual browser count")


if __name__ == "__main__":
    try:
        asyncio.run(test_final_dashboard())
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
