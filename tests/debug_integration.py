#!/usr/bin/env python3
"""
Debug script for integration validation NoneType error
"""

import sys
import os
import time
import asyncio

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def debug_integration_load_test():
    """Debug the integration validation load test"""
    print("🔍 Debugging integration validation load test...")

    # Import required modules
    from auto_tuning_engine import run_auto_tuning_cycle, initialize_auto_tuning
    import main_self_contained

    print("✅ Modules imported successfully")

    # Initialize auto-tuning engine
    try:
        auto_engine = initialize_auto_tuning()
        print("✅ Auto-tuning engine initialized")
    except Exception as e:
        print(f"❌ Auto-tuning initialization failed: {e}")
        return False

    # Initialize main scraper components
    try:
        main_self_contained.initialize_adaptive_scaling()
        print("✅ Main scraper initialized")
    except Exception as e:
        print(f"❌ Main scraper initialization failed: {e}")
        return False

    # Test the problematic load simulation
    print("🧪 Testing load simulation...")

    load_start_time = time.time()
    print(f"   Load start time: {load_start_time} (type: {type(load_start_time)})")

    try:
        for i in range(5):  # Reduced iterations for debugging
            metrics = {
                "success_rate": 0.85 + (i % 10) * 0.01,
                "avg_processing_time": 3.0 + (i % 5) * 0.5,
                "cpu_usage_percent": 60.0 + (i % 20),
                "memory_usage_mb": 500.0 + (i % 30) * 10,
                "active_workers": 8 + (i % 5),
                "queue_length": 5 + (i % 8),
                "error_rate": 0.10 + (i % 5) * 0.01,
            }

            print(f"   Iteration {i}: metrics = {metrics}")

            # Test auto-tuning cycle
            if i % 2 == 0:  # Every 2 iterations for debugging
                print(f"     Running auto-tuning cycle...")
                try:
                    result = run_auto_tuning_cycle(metrics)
                    print(f"     Auto-tuning result: {type(result)}")
                except Exception as e:
                    print(f"     ❌ Auto-tuning failed: {e}")
                    return False

            # Test adaptive scaling
            if i % 1 == 0:  # Every iteration for debugging
                print(f"     Running adaptive scaling check...")
                try:
                    result = asyncio.run(
                        main_self_contained.perform_adaptive_scaling_check(metrics)
                    )
                    print(f"     Adaptive scaling result: {type(result)}")
                except Exception as e:
                    print(f"     ❌ Adaptive scaling failed: {e}")
                    print(f"     Error type: {type(e)}")
                    return False

            time.sleep(0.05)  # Shorter delay for debugging

        load_end_time = time.time()
        print(f"   Load end time: {load_end_time} (type: {type(load_end_time)})")

        if load_start_time is None:
            print("❌ load_start_time is None!")
            return False
        if load_end_time is None:
            print("❌ load_end_time is None!")
            return False

        load_duration = load_end_time - load_start_time
        print(f"   Load duration: {load_duration} (type: {type(load_duration)})")

        print("✅ Load test completed successfully")
        return True

    except Exception as e:
        print(f"❌ Load test failed: {e}")
        print(f"   Error type: {type(e)}")
        return False


if __name__ == "__main__":
    debug_integration_load_test()
