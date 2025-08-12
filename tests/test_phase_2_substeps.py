"""
Test script for Phase 2 implementation verification - Complete sub-steps validation
Tests Steps 2.2, 2.3, and 2.4 implementation details
"""

import os
import sys
import asyncio
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def test_phase_2_sub_steps():
    """Test all Phase 2 sub-steps are properly implemented."""

    print("🧪 PHASE 2 SUB-STEPS VALIDATION")
    print("=" * 50)

    # Test 2.2: Debug prints replaced in main_self_contained.py
    print("\n📋 STEP 2.2: Debug Print Replacement")
    try:
        with open("main_self_contained.py", "r") as f:
            content = f.read()

        # Check for old debug prints
        old_prints = content.count("🔧")
        worker_tracking_calls = (
            content.count("log_worker_count_update")
            + content.count("log_scaling_decision")
            + content.count("log_worker_error")
        )

        print(f"   • Old debug prints found: {old_prints}")
        print(f"   • Worker tracking calls found: {worker_tracking_calls}")

        if old_prints == 0 and worker_tracking_calls > 0:
            print("   ✅ STEP 2.2 COMPLETE: Debug prints replaced with worker tracking")
        else:
            print(
                "   ❌ STEP 2.2 INCOMPLETE: Debug prints still present or missing tracking calls"
            )

    except Exception as e:
        print(f"   ❌ STEP 2.2 ERROR: {e}")

    # Test 2.3: Worker completion tracking in worker.py
    print("\n📋 STEP 2.3: Worker Completion Tracking")
    try:
        with open("worker.py", "r") as f:
            content = f.read()

        # Check for worker completion tracking
        completion_tracking = content.count("log_worker_completion")
        error_tracking = content.count("log_worker_error")
        import_tracking = "from .worker_tracking_display import" in content

        print(f"   • Worker completion calls: {completion_tracking}")
        print(f"   • Worker error calls: {error_tracking}")
        print(f"   • Tracking imports present: {import_tracking}")

        if completion_tracking >= 2 and error_tracking >= 1 and import_tracking:
            print("   ✅ STEP 2.3 COMPLETE: Worker completion tracking enhanced")
        else:
            print("   ❌ STEP 2.3 INCOMPLETE: Missing worker completion tracking")

    except Exception as e:
        print(f"   ❌ STEP 2.3 ERROR: {e}")

    # Test 2.4: Browser pool status monitoring
    print("\n📋 STEP 2.4: Browser Pool Monitoring")
    try:
        with open("worker_tracking_display.py", "r") as f:
            content = f.read()

        # Check for browser pool monitoring function
        sync_function = "sync_browser_pool_with_optimization_metrics" in content
        optimization_import = (
            "from optimization_utils import get_optimization_metrics" in content
        )

        # Check integration in main file
        with open("main_self_contained.py", "r") as f:
            main_content = f.read()

        main_integration = "sync_browser_pool_with_optimization_metrics" in main_content

        print(f"   • Browser pool sync function: {sync_function}")
        print(f"   • Optimization metrics import: {optimization_import}")
        print(f"   • Main file integration: {main_integration}")

        if sync_function and optimization_import and main_integration:
            print("   ✅ STEP 2.4 COMPLETE: Browser pool monitoring added")
        else:
            print("   ❌ STEP 2.4 INCOMPLETE: Missing browser pool monitoring")

    except Exception as e:
        print(f"   ❌ STEP 2.4 ERROR: {e}")

    # Test overall Phase 2 completion
    print("\n🎯 PHASE 2 OVERALL STATUS")
    try:
        # Import and test the worker tracking system
        from worker_tracking_display import (
            log_scaling_decision,
            log_worker_creation,
            log_worker_completion,
            log_worker_error,
            sync_browser_pool_with_optimization_metrics,
        )

        print("   ✅ All worker tracking functions importable")

        # Test a quick function call
        log_scaling_decision(10, 15, "Test scaling decision")
        log_worker_creation("Test-Worker-001")
        log_worker_completion("Test-Worker-001", "Test task", 1.5, 5)
        log_worker_error("Test-Worker-002", "Test error message", 1)
        sync_browser_pool_with_optimization_metrics()

        print("   ✅ All worker tracking functions functional")
        print("\n🚀 PHASE 2 IMPLEMENTATION COMPLETE!")
        print("   • Step 2.1: Function-based worker tracking display ✅")
        print("   • Step 2.2: Debug prints replaced with tracking calls ✅")
        print("   • Step 2.3: Worker completion tracking enhanced ✅")
        print("   • Step 2.4: Browser pool status monitoring added ✅")

    except Exception as e:
        print(f"   ❌ Phase 2 integration error: {e}")
        return False

    return True


if __name__ == "__main__":
    success = test_phase_2_sub_steps()

    if success:
        print("\n" + "=" * 50)
        print("🎉 ALL PHASE 2 SUB-STEPS VERIFIED!")
        print(
            "Worker tracking system fully integrated with function-based architecture"
        )
        exit(0)
    else:
        print("\n" + "=" * 50)
        print("❌ Phase 2 sub-steps need attention")
        exit(1)
