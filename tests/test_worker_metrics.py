#!/usr/bin/env python3
"""Test the corrected worker pool metrics display."""

import os
import asyncio
import logging
import sys
from pathlib import Path

# Set up environment for testing
os.environ["SCRAPER_LOG_LEVEL"] = "INFO"
os.environ["SCRAPER_MAX_WORKERS"] = "50"  # Default 50 workers like production
os.environ["SCRAPER_BROWSER_HEADLESS"] = "true"
os.environ["ADAPTIVE_MODULES_AVAILABLE"] = "true"

# Add the current directory to the path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import modules after setting environment
from main_self_contained import main
from real_time_monitor import RealTimeMonitor


async def test_worker_metrics():
    """Test worker pool metrics collection and display."""
    print("🧪 Testing Worker Pool Metrics")
    print("=" * 60)

    # Start the main scraper in the background
    main_task = asyncio.create_task(main())

    # Wait a bit for workers to initialize
    await asyncio.sleep(2)

    # Test metrics collection directly
    from main_self_contained import _scraper_context

    if _scraper_context and _scraper_context.worker_context:
        context = _scraper_context.worker_context

        print(f"📊 Worker Context Analysis:")
        print(f"   Total Worker Pool Size: {context.max_workers}")
        print(f"   Busy Workers: {len(context.worker_manager.active_workers)}")
        print(f"   Queue Size: {context.task_queue.qsize()}")
        print(f"   Total Tasks Completed: {context.total_tasks_completed}")

        # Test browser pool access
        try:
            from optimization_utils import _browser_pool

            print(f"   Browser Pool Size: {len(_browser_pool)}")
        except (ImportError, NameError):
            print(f"   Browser Pool Size: Not available")

        # Test dashboard metrics
        monitor = RealTimeMonitor(update_interval=30, worker_context=context)
        metrics = monitor._collect_current_metrics()

        print(f"\n📈 Dashboard Metrics:")
        print(
            f"   Active Workers: {metrics.active_workers} (should be {context.max_workers})"
        )
        print(f"   Browser Pool: {metrics.browser_pool_size}")
        print(f"   Success Rate: {metrics.success_rate:.1%}")
        print(f"   Total Processed: {metrics.total_processed}")
        print(f"   Queue Length: {metrics.queue_length}")

        # Success validation
        if metrics.active_workers == context.max_workers:
            print(
                f"\n✅ SUCCESS: Active Workers shows total pool size ({context.max_workers})"
            )
        else:
            print(
                f"\n❌ FAILURE: Active Workers shows {metrics.active_workers}, expected {context.max_workers}"
            )

        if metrics.browser_pool_size is not None:
            print(
                f"✅ SUCCESS: Browser Pool shows {metrics.browser_pool_size} browsers"
            )
        else:
            print(f"⚠️  WARNING: Browser Pool not available")
    else:
        print("❌ No worker context available")

    # Cancel the main task
    main_task.cancel()
    try:
        await main_task
    except asyncio.CancelledError:
        pass


def main_sync():
    """Run the async test function."""
    try:
        asyncio.run(test_worker_metrics())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    main_sync()
