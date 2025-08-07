#!/usr/bin/env python3
"""Quick test of worker metrics display."""

import os
import asyncio
import logging
import sys
from pathlib import Path

# Set up environment
os.environ["SCRAPER_LOG_LEVEL"] = "ERROR"  # Reduce noise
os.environ["SCRAPER_MAX_WORKERS"] = "50"
os.environ["ADAPTIVE_MODULES_AVAILABLE"] = "true"

# Add current directory to path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from data_structures import ParallelWorkerContext, WorkerManager
from real_time_monitor import RealTimeMonitor


def test_metrics_display():
    """Test metrics display without running full scraper."""
    print("🧪 Testing Worker Metrics Display")
    print("=" * 50)

    # Create a mock logger
    logger = logging.getLogger("test")
    logger.setLevel(logging.ERROR)

    # Create worker context with 50 workers
    context = ParallelWorkerContext(max_workers=50, logger=logger)

    print(f"📊 Worker Context Created:")
    print(f"   Max Workers: {context.max_workers}")
    print(f"   Active Workers: {len(context.worker_manager.active_workers)}")
    print(f"   Queue Size: {context.task_queue.qsize()}")

    # Test dashboard metrics
    monitor = RealTimeMonitor(update_interval=30, worker_context=context)
    metrics = monitor._collect_current_metrics()

    print(f"\n📈 Dashboard Metrics:")
    print(f"   Active Workers: {metrics.active_workers}")
    print(f"   Browser Pool: {metrics.browser_pool_size}")
    print(f"   Success Rate: {metrics.success_rate}")
    print(f"   Total Processed: {metrics.total_processed}")
    print(f"   Queue Length: {metrics.queue_length}")

    # Test browser pool
    try:
        from optimization_utils import _browser_pool

        print(f"   Browser Pool Size: {len(_browser_pool)}")
    except Exception as e:
        print(f"   Browser Pool Error: {e}")

    # Validation
    print(f"\n✅ Validation:")
    if metrics.active_workers == 50:
        print(f"   ✅ Active Workers shows total pool size: {metrics.active_workers}")
    else:
        print(f"   ❌ Active Workers wrong: {metrics.active_workers}, expected 50")

    if metrics.browser_pool_size is not None:
        print(f"   ✅ Browser Pool accessible: {metrics.browser_pool_size}")
    else:
        print(f"   ⚠️  Browser Pool not available")


if __name__ == "__main__":
    test_metrics_display()
