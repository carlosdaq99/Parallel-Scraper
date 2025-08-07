#!/usr/bin/env python3
"""Test dashboard briefly"""

import sys
import os
import asyncio

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from real_time_monitor import RealTimeMonitor


async def test_dashboard_brief():
    """Test dashboard briefly to check adaptive scaling"""
    print("Testing dashboard with adaptive scaling...")

    monitor = RealTimeMonitor(update_interval=3)

    # Run 2 updates
    for i in range(2):
        print(f"\n=== Update {i+1} ===")
        await monitor._update_display()
        if i < 1:  # Don't wait after last update
            await asyncio.sleep(3)

    print("\nTest completed!")


if __name__ == "__main__":
    asyncio.run(test_dashboard_brief())
