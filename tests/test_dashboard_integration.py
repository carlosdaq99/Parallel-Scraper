#!/usr/bin/env python3
"""
Quick test to check if dashboard integration works in main_self_contained
"""

import asyncio
import logging
from real_time_monitor import start_real_time_monitor
from data_structures import ParallelWorkerContext


async def test_dashboard_integration():
    """Test dashboard integration similar to main_self_contained"""
    print("🧪 Testing dashboard integration...")

    # Create basic logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Create a minimal worker context similar to main_self_contained
    worker_context = ParallelWorkerContext(max_workers=50, logger=logger)

    # Start dashboard similar to main_self_contained
    monitor_instance = start_real_time_monitor(
        5, worker_context
    )  # 5 second updates for testing

    print("🖥️ DASHBOARD: Created with 5 second update interval")

    # Run dashboard for 30 seconds
    try:
        asyncio.create_task(monitor_instance.run_dashboard(), name="test_dashboard")
        print("🖥️ DASHBOARD: Task started, should appear in 5 seconds...")

        # Let it run for 30 seconds
        await asyncio.sleep(30)

    except KeyboardInterrupt:
        print("🖥️ DASHBOARD: Test stopped by user")
    except Exception as e:
        print(f"🖥️ DASHBOARD: Error - {e}")
    finally:
        print("🖥️ DASHBOARD: Test completed")


if __name__ == "__main__":
    asyncio.run(test_dashboard_integration())
