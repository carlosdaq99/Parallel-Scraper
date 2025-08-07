#!/usr/bin/env python3
"""Simple test for real-time monitor"""

import asyncio
import sys
from real_time_monitor import RealTimeMonitor


async def test_monitor():
    """Test the monitor for 10 seconds"""
    print("🚀 Testing Real-Time Monitor...")
    monitor = RealTimeMonitor(update_interval=5)  # 5 second intervals for testing

    # Run for 3 updates (15 seconds total)
    for i in range(3):
        print(f"\n=== Update {i+1}/3 ===")
        metrics = monitor._collect_current_metrics()
        monitor.display_dashboard(metrics)
        if i < 2:  # Don't sleep after last update
            await asyncio.sleep(5)

    print("\n✅ Monitor test completed!")


if __name__ == "__main__":
    asyncio.run(test_monitor())
