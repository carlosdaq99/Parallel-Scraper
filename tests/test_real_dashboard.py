#!/usr/bin/env python3
"""Test main application with dashboard to verify all sections work"""

import sys
import os
import asyncio
import signal
import time

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Set environment for testing
os.environ["SCRAPER_MONITOR_ENABLED"] = "true"
os.environ["SCRAPER_MONITOR_INTERVAL"] = "3"  # Faster updates for testing
os.environ["SCRAPER_MAX_WORKERS"] = "3"  # Small worker pool
os.environ["SCRAPER_START_URL"] = (
    "https://httpbin.org/links/5"  # Simple test page with few links
)

from main_self_contained import main as run_scraper


async def test_main_application_dashboard():
    """Test the main application with dashboard for 30 seconds"""
    print("🚀 Testing main application with real-time dashboard...")
    print("This will run the actual scraper with a small workload")
    print(
        "Dashboard will show real worker activity, system resources, and adaptive scaling"
    )
    print("Test will run for 30 seconds then stop automatically\n")

    # Set up to run scraper for limited time
    test_duration = 30  # seconds

    # Create a task to run the scraper
    scraper_task = asyncio.create_task(run_scraper())

    # Wait for test duration or scraper completion
    try:
        await asyncio.wait_for(scraper_task, timeout=test_duration)
    except asyncio.TimeoutError:
        print(f"\n⏰ Test completed after {test_duration} seconds")
        scraper_task.cancel()
        try:
            await scraper_task
        except asyncio.CancelledError:
            pass

    # Cleanup - no URLs file to remove

    print("\n✅ Dashboard test with main application completed!")
    print("You should have seen:")
    print("  - Performance metrics with real success rates and processing counts")
    print("  - System resources showing CPU and memory usage percentages")
    print("  - Adaptive scaling showing worker management decisions")
    print("  - Performance trends tracking metrics over time")


if __name__ == "__main__":
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        print("\n🛑 Test interrupted by user")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    try:
        asyncio.run(test_main_application_dashboard())
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
