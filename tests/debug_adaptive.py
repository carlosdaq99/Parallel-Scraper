#!/usr/bin/env python3
"""
Debug script to understand why auto_tuning_active is False
"""

try:
    from auto_tuning_engine import initialize_auto_tuning, get_auto_tuning_engine
    from real_time_monitor import RealTimeMonitor, ADAPTIVE_MODULES_AVAILABLE

    print("=== Debug: Real-Time Monitor Auto-Tuning Detection ===")
    print()

    # Initialize engine
    print("Initializing auto-tuning engine...")
    auto_engine = initialize_auto_tuning()
    print(f"✅ Engine initialized: {auto_engine}")

    # Check if modules are available
    print(f"ADAPTIVE_MODULES_AVAILABLE: {ADAPTIVE_MODULES_AVAILABLE}")

    # Manual test of the logic in real_time_monitor
    print("\nManual test of auto-tuning detection logic:")
    if ADAPTIVE_MODULES_AVAILABLE:
        print("✅ Adaptive modules are available")
        try:
            engine = get_auto_tuning_engine()
            print(f"   get_auto_tuning_engine() returned: {engine}")

            if engine is None:
                print("   Engine is None, trying to initialize...")
                engine = initialize_auto_tuning()
                print(f"   After initialization: {engine}")

            if engine:
                print(
                    "   ✅ Engine is available - should set auto_tuning_active = True"
                )
                print(f"   Engine type: {type(engine)}")
                print(
                    f"   Engine has patterns_detected: {hasattr(engine, 'patterns_detected')}"
                )
                print(
                    f"   patterns_detected value: {getattr(engine, 'patterns_detected', 'Not found')}"
                )
                print(
                    f"   Engine has pattern_history: {hasattr(engine, 'pattern_history')}"
                )
                print(
                    f"   pattern_history length: {len(getattr(engine, 'pattern_history', []))}"
                )
            else:
                print("   ❌ Engine is None - auto_tuning_active will be False")

        except Exception as e:
            print(f"   ❌ Exception in auto-tuning detection: {e}")
            import traceback

            traceback.print_exc()
    else:
        print("❌ Adaptive modules not available")

    print("\nNow testing real monitor...")
    monitor = RealTimeMonitor(5)
    metrics = monitor._collect_current_metrics()

    print(f"Final results:")
    print(f"   auto_tuning_active: {metrics.auto_tuning_active}")
    print(f"   has_adaptive_data: {metrics.has_adaptive_data}")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback

    traceback.print_exc()
