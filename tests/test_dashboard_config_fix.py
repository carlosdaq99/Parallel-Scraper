#!/usr/bin/env python3
"""
Test script to verify dashboard interval configuration fix and real-time scaling reflection.

This test validates:
1. Dashboard update intervals are consistent (no conflicting values)
2. Worker count changes are properly reflected in dashboard metrics
3. Both active workers and target workers are tracked correctly
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)


def test_dashboard_interval_consistency():
    """Test that dashboard update intervals are consistent across modules."""
    print("=== Testing Dashboard Interval Configuration ===")

    # Import config
    try:
        from config import ScraperConfig

        config_interval = ScraperConfig.DASHBOARD_UPDATE_INTERVAL
        print(f"✓ Config DASHBOARD_UPDATE_INTERVAL: {config_interval} seconds")
    except Exception as e:
        print(f"✗ Failed to import config: {e}")
        return False

    # Test real_time_monitor fallback
    try:
        # Temporarily remove config import to test fallback
        original_config = sys.modules.get("config")
        if "config" in sys.modules:
            del sys.modules["config"]

        # Clear real_time_monitor from cache if already imported
        if "real_time_monitor" in sys.modules:
            del sys.modules["real_time_monitor"]

        # Import real_time_monitor without config
        import real_time_monitor

        fallback_interval = real_time_monitor.ScraperConfig.DASHBOARD_UPDATE_INTERVAL
        print(f"✓ Real-time monitor fallback interval: {fallback_interval} seconds")

        # Restore config
        if original_config:
            sys.modules["config"] = original_config

        # Check consistency
        if config_interval == fallback_interval:
            print("✓ Dashboard intervals are CONSISTENT")
            return True
        else:
            print(
                f"✗ Dashboard intervals are INCONSISTENT: config={config_interval}, fallback={fallback_interval}"
            )
            return False

    except Exception as e:
        print(f"✗ Failed to test fallback interval: {e}")
        return False


def test_worker_count_tracking():
    """Test that worker count changes are properly tracked in unified metrics."""
    print("\n=== Testing Worker Count Tracking ===")

    try:
        from unified_metrics import UnifiedMetrics
        from adaptive_scaling_engine import (
            set_current_worker_count,
            get_current_worker_count,
        )

        # Create mock worker context
        class MockWorkerManager:
            def __init__(self):
                self.active_workers = [1, 2, 3]  # 3 busy workers

        class MockTaskQueue:
            def qsize(self):
                return 10  # 10 tasks in queue

        class MockWorkerContext:
            def __init__(self):
                self.worker_manager = MockWorkerManager()
                self.task_queue = MockTaskQueue()
                self.max_workers = 100
                self.completed_tasks = [1] * 50  # 50 completed
                self.failed_tasks = [1] * 5  # 5 failed

        # Test initial state
        initial_target = get_current_worker_count()
        print(f"✓ Initial target worker count: {initial_target}")

        # Create unified metrics instance
        worker_context = MockWorkerContext()
        metrics = UnifiedMetrics(worker_context)

        # Test metrics collection before scaling
        unified_data = metrics.collect_metrics()
        print(f"✓ Active workers (target): {unified_data.get('active_workers')}")
        print(f"✓ Busy workers (actual): {unified_data.get('busy_workers')}")
        print(
            f"✓ Worker utilization: {unified_data.get('worker_utilization_percent', 0):.1f}%"
        )

        # Simulate scaling up
        print("\n--- Simulating scale-up to 75 workers ---")
        set_current_worker_count(75)
        new_target = get_current_worker_count()
        print(f"✓ New target worker count: {new_target}")

        # Test metrics collection after scaling
        unified_data_after = metrics.collect_metrics()
        print(
            f"✓ Active workers (target) after scaling: {unified_data_after.get('active_workers')}"
        )
        print(
            f"✓ Busy workers (actual) after scaling: {unified_data_after.get('busy_workers')}"
        )
        print(
            f"✓ Worker utilization after scaling: {unified_data_after.get('worker_utilization_percent', 0):.1f}%"
        )

        # Verify the scaling was reflected
        if unified_data_after.get("active_workers") == 75:
            print("✓ Worker count changes are PROPERLY REFLECTED in metrics")
            return True
        else:
            print(
                f"✗ Worker count changes NOT reflected: expected 75, got {unified_data_after.get('active_workers')}"
            )
            return False

    except Exception as e:
        print(f"✗ Failed to test worker count tracking: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_dashboard_metrics_integration():
    """Test that dashboard properly receives updated metrics."""
    print("\n=== Testing Dashboard Metrics Integration ===")

    try:
        from unified_metrics import get_metrics_for_dashboard
        from adaptive_scaling_engine import set_current_worker_count

        # Create mock worker context
        class MockWorkerManager:
            def __init__(self):
                self.active_workers = [1, 2, 3, 4]  # 4 busy workers

        class MockTaskQueue:
            def qsize(self):
                return 15  # 15 tasks in queue

        class MockWorkerContext:
            def __init__(self):
                self.worker_manager = MockWorkerManager()
                self.task_queue = MockTaskQueue()
                self.max_workers = 100
                self.completed_tasks = [1] * 75  # 75 completed
                self.failed_tasks = [1] * 3  # 3 failed

        worker_context = MockWorkerContext()

        # Set target worker count
        set_current_worker_count(60)

        # Get dashboard metrics
        dashboard_data = get_metrics_for_dashboard(worker_context)

        print(f"✓ Dashboard active workers: {dashboard_data.get('active_workers')}")
        print(
            f"✓ Dashboard worker utilization: {dashboard_data.get('worker_utilization', 0):.1f}%"
        )
        print(f"✓ Dashboard queue length: {dashboard_data.get('queue_length')}")
        print(f"✓ Dashboard success rate: {dashboard_data.get('success_rate', 0):.1%}")

        # Verify dashboard shows target worker count
        if dashboard_data.get("active_workers") == 60:
            print("✓ Dashboard CORRECTLY shows target worker count")
            return True
        else:
            print(
                f"✗ Dashboard shows incorrect worker count: expected 60, got {dashboard_data.get('active_workers')}"
            )
            return False

    except Exception as e:
        print(f"✗ Failed to test dashboard metrics integration: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all dashboard configuration tests."""
    print("Dashboard Configuration Fix Validation")
    print("=====================================\n")

    tests = [
        test_dashboard_interval_consistency,
        test_worker_count_tracking,
        test_dashboard_metrics_integration,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            results.append(False)

    print(f"\n=== Test Results ===")
    print(f"Passed: {sum(results)}/{len(results)}")
    print(f"Failed: {len(results) - sum(results)}/{len(results)}")

    if all(results):
        print("✓ ALL TESTS PASSED - Dashboard configuration fix is working correctly!")
        return True
    else:
        print(
            "✗ Some tests failed - Dashboard configuration needs further investigation"
        )
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
