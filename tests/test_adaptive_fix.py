#!/usr/bin/env python3
"""
Test script to validate the adaptive scaling data fix
"""

try:
    # Simulate the exact flow in main_self_contained.py
    from auto_tuning_engine import initialize_auto_tuning, get_auto_tuning_engine
    from real_time_monitor import RealTimeMonitor

    print("=== Testing Adaptive Scaling Data Fix ===")
    print()

    # Step 1: Initialize auto-tuning engine (as done in main_self_contained.py)
    print("Step 1: Initializing auto-tuning engine...")
    try:
        auto_engine = initialize_auto_tuning()
        print(f"✅ Auto-tuning engine initialized: {type(auto_engine).__name__}")
        print(f"   Engine: {auto_engine}")
        print(f"   Patterns detected: {auto_engine.patterns_detected}")
        print(f"   Pattern history length: {len(auto_engine.pattern_history)}")
    except Exception as e:
        print(f"❌ Auto-tuning initialization failed: {e}")
        raise

    print()

    # Step 2: Verify engine can be retrieved
    print("Step 2: Testing engine retrieval...")
    retrieved_engine = get_auto_tuning_engine()
    if retrieved_engine is not None:
        print(f"✅ Engine retrieval successful: {retrieved_engine is auto_engine}")
    else:
        print("❌ Engine retrieval failed - returned None")
        exit(1)

    print()

    # Step 3: Test real-time monitor with the engine
    print("Step 3: Testing real-time monitor...")
    monitor = RealTimeMonitor(5)
    metrics = monitor._collect_current_metrics()

    print(f"   Auto-tuning active: {metrics.auto_tuning_active}")
    print(f"   Has adaptive data: {metrics.has_adaptive_data}")
    print(f"   Pattern detected: {metrics.pattern_detected}")
    print(f"   Last scaling action: {metrics.last_scaling_action}")

    print()

    # Step 4: Results
    if metrics.has_adaptive_data:
        print("🎉 SUCCESS: Adaptive data is now available!")
        print(
            "   The 'Adaptive scaling data not yet available' message should no longer appear"
        )
    else:
        print("❌ ISSUE: Still showing adaptive data not available")
        print("   Need to investigate further...")

    print()
    print("=== Test Complete ===")

except Exception as e:
    print(f"❌ ERROR during test: {e}")
    import traceback

    traceback.print_exc()
