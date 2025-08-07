#!/usr/bin/env python3
"""
Debug Dashboard Metrics Issues

This script specifically tests the dashboard metric calculation to identify
why worker utilization shows 10000% and other values are incorrect.
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from real_time_monitor import RealTimeMonitor
import time


class MockWorkerContext:
    """Mock worker context to test dashboard calculations"""

    def __init__(self):
        self.completed_tasks = []
        self.failed_tasks = []
        self.max_workers = 50

        # Create mock worker manager
        self.worker_manager = MockWorkerManager()

        # Create mock task queue
        self.task_queue = MockQueue()

        # Add some mock tasks to simulate load
        for i in range(10):
            self.completed_tasks.append(f"task_{i}")

        # Add some failed tasks
        for i in range(2):
            self.failed_tasks.append(f"failed_task_{i}")


class MockWorkerManager:
    """Mock worker manager"""

    def __init__(self):
        # Simulate some active workers (workers currently busy)
        self.active_workers = [f"worker_{i}" for i in range(5)]  # 5 busy workers


class MockQueue:
    """Mock queue"""

    def qsize(self):
        return 32  # Return 32 items in queue (mentioned in feedback)


def test_dashboard_calculations():
    """Test the dashboard metric calculations to find bugs"""

    print("🔧 Testing Dashboard Metric Calculations")
    print("=" * 50)

    # Create mock context to simulate running system
    mock_context = MockWorkerContext()

    # Create monitor with mock context
    monitor = RealTimeMonitor(worker_context=mock_context)
    monitor.start_time = time.time() - 60  # Started 60 seconds ago

    # Collect metrics using the same logic as the dashboard
    metrics = monitor._collect_current_metrics()

    print("📊 COLLECTED METRICS:")
    print(f"   Total Completed: {len(mock_context.completed_tasks)}")
    print(f"   Total Failed: {len(mock_context.failed_tasks)}")
    print(f"   Total Processed: {metrics.total_processed}")
    print(f"   Busy Workers: {len(mock_context.worker_manager.active_workers)}")
    print(f"   Max Workers: {mock_context.max_workers}")
    print(f"   Queue Size: {mock_context.task_queue.qsize()}")
    print()

    print("🧮 CALCULATED DASHBOARD VALUES:")
    print(f"   Success Rate: {metrics.success_rate:.1%}")
    print(f"   Active Workers: {metrics.active_workers}")
    print(f"   Queue Length: {metrics.queue_length}")
    print(f"   Pages/Second: {metrics.pages_per_second}")
    print(f"   Avg Processing Time: {metrics.avg_processing_time}")
    print()

    print("⚠️  SCALING DECISION METRICS:")
    print(f"   Worker Utilization: {metrics.worker_utilization}% (SHOULD be 0-100%)")
    print(f"   Queue/Worker Ratio: {metrics.queue_to_worker_ratio:.1f}:1")
    print(f"   Resource Capacity: {metrics.resource_capacity}")
    print(f"   Performance Score: {metrics.performance_score}")
    print(f"   Browser Pool Size: {metrics.browser_pool_size}")
    print(f"   Browser Pool Rec: {metrics.browser_pool_recommendation}")
    print()

    print("🔍 DETAILED CALCULATIONS:")
    total_worker_pool_size = mock_context.max_workers
    busy_workers = len(mock_context.worker_manager.active_workers)
    queue_depth = mock_context.task_queue.qsize()

    print(f"   Total Pool Size: {total_worker_pool_size}")
    print(f"   Busy Workers: {busy_workers}")
    print(f"   Queue Depth: {queue_depth}")

    # Calculate worker utilization the same way as the dashboard
    if total_worker_pool_size > 0 and queue_depth is not None:
        calculated_utilization = min(
            100.0, (busy_workers / total_worker_pool_size) * 100
        )
        calculated_ratio = queue_depth / total_worker_pool_size

        print(f"   Calculated Utilization: {calculated_utilization}% (should be 10%)")
        print(f"   Calculated Ratio: {calculated_ratio:.2f}:1 (should be 0.64:1)")

        # Check if there's a bug in the calculation
        if calculated_utilization != metrics.worker_utilization:
            print(
                f"   ❌ BUG FOUND: Expected {calculated_utilization}%, got {metrics.worker_utilization}%"
            )
        else:
            print(f"   ✅ Utilization calculation is correct")

        if abs(calculated_ratio - metrics.queue_to_worker_ratio) > 0.01:
            print(
                f"   ❌ BUG FOUND: Expected {calculated_ratio:.2f}, got {metrics.queue_to_worker_ratio:.2f}"
            )
        else:
            print(f"   ✅ Queue/Worker ratio calculation is correct")


if __name__ == "__main__":
    test_dashboard_calculations()
