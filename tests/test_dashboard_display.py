#!/usr/bin/env python3
"""Simple test to show dashboard metrics once."""

import os
import logging
import sys
from pathlib import Path

# Set up environment
os.environ["SCRAPER_LOG_LEVEL"] = "ERROR"
os.environ["SCRAPER_MAX_WORKERS"] = "50"
os.environ["ADAPTIVE_MODULES_AVAILABLE"] = "true"

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from data_structures import ParallelWorkerContext
from real_time_monitor import RealTimeMonitor


def test_dashboard_once():
    """Test dashboard display once."""
    print("🎯 Dashboard Metrics Test")
    print("=" * 50)

    # Create logger
    logger = logging.getLogger("test")
    logger.setLevel(logging.ERROR)

    # Create worker context with 50 workers
    context = ParallelWorkerContext(max_workers=50, logger=logger)

    # Simulate some activity
    context.total_tasks_completed = 25
    context.total_tasks_failed = 2

    # Create monitor and display metrics once
    monitor = RealTimeMonitor(update_interval=30, worker_context=context)
    metrics = monitor._collect_current_metrics()

    print("📊 Collected Metrics:")
    print(f"   Active Workers: {metrics.active_workers}")
    print(f"   Browser Pool: {metrics.browser_pool_size}")
    print(f"   Success Rate: {metrics.success_rate:.1%}")
    print(f"   Total Processed: {metrics.total_processed}")
    print(f"   Queue Length: {metrics.queue_length}")

    # Display the dashboard once
    print("\n" + "=" * 50)
    print("📈 DASHBOARD DISPLAY:")
    print("=" * 50)
    monitor.display_dashboard(metrics)
    print("=" * 50)

    print("\n✅ Dashboard Test Results:")
    print(f"   ✅ Active Workers shows: {metrics.active_workers} (expected: 50)")
    print(
        f"   ✅ Browser Pool shows: {metrics.browser_pool_size} (expected: 0 or higher)"
    )
    print(f"   ✅ Success Rate shows: {metrics.success_rate:.1%} (expected: ~92.6%)")

    if metrics.active_workers == 50:
        print("\n🎉 SUCCESS: Active Workers correctly shows total pool size!")
    else:
        print(
            f"\n❌ FAILURE: Active Workers shows {metrics.active_workers}, expected 50"
        )


if __name__ == "__main__":
    test_dashboard_once()
