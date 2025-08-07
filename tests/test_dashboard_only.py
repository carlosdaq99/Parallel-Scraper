#!/usr/bin/env python3
"""
Test Real-Time Dashboard in Isolation

Quick test to verify dashboard displays properly without interference from worker logs.
"""

import asyncio
import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from real_time_monitor import start_real_time_monitor


async def test_dashboard():
    """Test the dashboard display in isolation"""

    print("🔄 Starting dashboard test...")

    # Create monitor with shorter update interval for testing
    monitor = start_real_time_monitor(update_interval=3)

    print("✅ Monitor created, starting dashboard...")

    # Start dashboard in background
    dashboard_task = asyncio.create_task(monitor.run_dashboard())

    print("🚀 Dashboard task started, will run for 15 seconds...")

    # Let it run for 15 seconds to see if dashboard appears
    await asyncio.sleep(15)

    print("⏹️  Stopping dashboard...")
    monitor.stop_dashboard()

    # Wait for dashboard task to complete
    try:
        await asyncio.wait_for(dashboard_task, timeout=5)
    except asyncio.TimeoutError:
        dashboard_task.cancel()

    print("✅ Dashboard test complete!")


if __name__ == "__main__":
    asyncio.run(test_dashboard())
