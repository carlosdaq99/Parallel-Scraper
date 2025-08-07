#!/usr/bin/env python3
"""
Test Integration for Adaptive Scaling in Main Scraper
"""

import sys
import time
import asyncio
from unittest.mock import MagicMock


# Test the integration of adaptive scaling in main_self_contained.py
def test_adaptive_scaling_integration():
    print("🧪 Testing Adaptive Scaling Integration...")

    try:
        # Import the main module
        import main_self_contained

        # Test 1: Check if adaptive scaling functions are available
        print("✅ Test 1: Checking adaptive scaling functions...")
        assert hasattr(
            main_self_contained, "get_current_workers"
        ), "get_current_workers function missing"
        assert hasattr(
            main_self_contained, "update_worker_count"
        ), "update_worker_count function missing"
        assert hasattr(
            main_self_contained, "initialize_adaptive_scaling"
        ), "initialize_adaptive_scaling function missing"
        assert hasattr(
            main_self_contained, "perform_adaptive_scaling_check"
        ), "perform_adaptive_scaling_check function missing"
        print("   ✅ All adaptive scaling functions present")

        # Test 2: Test initialization
        print("✅ Test 2: Testing adaptive scaling initialization...")
        try:
            main_self_contained.initialize_adaptive_scaling()
            print("   ✅ Adaptive scaling initialization successful")
        except Exception as e:
            print(f"   ❌ Initialization failed: {e}")
            return False

        # Test 3: Test worker count functions
        print("✅ Test 3: Testing worker count management...")
        try:
            current_workers = main_self_contained.get_current_workers()
            print(f"   ✅ Current workers: {current_workers}")

            # Test updating worker count
            main_self_contained.update_worker_count(5, "Test update")
            new_count = main_self_contained.get_current_workers()
            print(f"   ✅ Updated worker count: {new_count}")
        except Exception as e:
            print(f"   ❌ Worker count management failed: {e}")
            return False

        # Test 4: Test adaptive scaling check
        print("✅ Test 4: Testing adaptive scaling check...")
        try:
            performance_data = {
                "success_rate": 0.95,
                "avg_processing_time": 2.5,
                "memory_usage": 50,
                "cpu_usage": 30,
            }
            # Run the async function properly
            asyncio.run(
                main_self_contained.perform_adaptive_scaling_check(performance_data)
            )
            print("   ✅ Adaptive scaling check successful")
        except Exception as e:
            print(f"   ❌ Adaptive scaling check failed: {e}")
            return False

        # Test 5: Check imports
        print("✅ Test 5: Checking adaptive scaling imports...")
        try:
            from adaptive_scaling_engine import (
                make_scaling_decision,
                execute_scaling_decision,
            )
            from enhanced_config_manager import (
                initialize_dynamic_config,
                adjust_config_for_performance,
            )

            print("   ✅ All required imports successful")
        except ImportError as e:
            print(f"   ❌ Import failed: {e}")
            return False

        print("🎉 ALL INTEGRATION TESTS PASSED!")
        return True

    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def test_performance_monitoring_integration():
    """Test that performance monitoring works with adaptive scaling"""
    print("\n🧪 Testing Performance Monitoring Integration...")

    try:
        # Test that the monitoring loop structure is correct
        import main_self_contained

        # Mock some data for testing
        performance_data = {
            "success_rate": 0.98,
            "avg_processing_time": 1.5,
            "memory_usage": 40,
            "cpu_usage": 25,
            "error_rate": 0.02,
        }

        # Test the adaptive scaling check with various scenarios
        test_scenarios = [
            {
                "name": "High Performance",
                "data": {
                    "success_rate": 0.98,
                    "avg_processing_time": 1.5,
                    "memory_usage": 40,
                    "cpu_usage": 25,
                },
            },
            {
                "name": "Low Performance",
                "data": {
                    "success_rate": 0.75,
                    "avg_processing_time": 12.0,
                    "memory_usage": 80,
                    "cpu_usage": 85,
                },
            },
            {
                "name": "Normal Performance",
                "data": {
                    "success_rate": 0.90,
                    "avg_processing_time": 5.0,
                    "memory_usage": 60,
                    "cpu_usage": 50,
                },
            },
        ]

        for scenario in test_scenarios:
            print(f"   Testing {scenario['name']} scenario...")
            try:
                # Run the async function properly
                asyncio.run(
                    main_self_contained.perform_adaptive_scaling_check(scenario["data"])
                )
                print(f"   ✅ {scenario['name']} scenario passed")
            except Exception as e:
                print(f"   ❌ {scenario['name']} scenario failed: {e}")
                return False

        print("🎉 PERFORMANCE MONITORING INTEGRATION TESTS PASSED!")
        return True

    except Exception as e:
        print(f"❌ Performance monitoring integration test failed: {e}")
        return False


if __name__ == "__main__":
    print("🚀 Starting Adaptive Scaling Integration Tests...")

    success1 = test_adaptive_scaling_integration()
    success2 = test_performance_monitoring_integration()

    if success1 and success2:
        print("\n🎉 ALL INTEGRATION TESTS SUCCESSFUL!")
        print("✅ Adaptive scaling is properly integrated with main scraper")
        print("✅ Performance monitoring is working with adaptive scaling")
        sys.exit(0)
    else:
        print("\n❌ SOME INTEGRATION TESTS FAILED!")
        sys.exit(1)
