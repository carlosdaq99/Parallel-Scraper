#!/usr/bin/env python3
"""
TEST: Fixed Scaling Engine Integration
Tests the scaling issues with a minimal working version
"""

import asyncio
import time
from data_structures import ParallelWorkerContext, WorkerManager
from real_time_monitor import start_real_time_monitor, DashboardMetrics
from adaptive_scaling_engine import (
    make_scaling_decision_simple,
    get_current_worker_count,
)


async def test_real_time_scaling():
    """Test real-time scaling with proper worker context"""

    print("🧪 REAL-TIME SCALING TEST")
    print("=" * 80)
    print("Testing real dashboard with simulated worker activity")
    print()

    # Create worker context with proper structure
    worker_context = ParallelWorkerContext(max_workers=50)

    # Simulate some active workers
    for i in range(25):  # 50% utilization
        worker_context.worker_manager.assign_worker(f"worker_{i}")

    # Start real-time monitor with worker context
    print("🖥️  Starting real-time dashboard...")
    monitor_task = start_real_time_monitor(worker_context)

    # Let it run for a few seconds to show data
    await asyncio.sleep(5)

    print("\n✅ Real-time dashboard test completed")

    # Clean up
    if monitor_task:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    asyncio.run(test_real_time_scaling())
