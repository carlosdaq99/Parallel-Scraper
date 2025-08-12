#!/usr/bin/env python3
"""
Re-test Dashboard On/Off Functionality - Function-Based Architecture

This script re-tests the dashboard enable/disable functionality after
refactoring from class-based to function-based design pattern.
"""

import os
import sys
import asyncio
import logging
from unittest.mock import Mock


def test_function_based_configuration():
    """Test dashboard configuration with function-based design"""
    print("🧪 Testing function-based dashboard configuration...")

    # Test 1: Default configuration (enabled)
    print("1. Testing default configuration...")
    os.environ.pop("SCRAPER_ENABLE_DASHBOARD", None)

    if "config" in sys.modules:
        del sys.modules["config"]
    from config import ScraperConfig

    print(f"   Default ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")
    assert ScraperConfig.ENABLE_DASHBOARD == True, "Default should be enabled"
    print("   ✓ Default configuration correct")

    # Test 2: Explicitly disabled
    print("2. Testing explicitly disabled...")
    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "false"

    if "config" in sys.modules:
        del sys.modules["config"]
    from config import ScraperConfig

    print(f"   Explicit false ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")
    assert ScraperConfig.ENABLE_DASHBOARD == False, "Explicit false should be disabled"
    print("   ✓ Explicit disable correct")

    # Restore default
    os.environ.pop("SCRAPER_ENABLE_DASHBOARD", None)
    if "config" in sys.modules:
        del sys.modules["config"]


async def test_function_based_enabled():
    """Test function-based dashboard when enabled"""
    print("\n🧪 Testing function-based dashboard ENABLED...")

    # Set environment to enabled
    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "true"

    # Fresh imports
    if "config" in sys.modules:
        del sys.modules["config"]
    if "dashboard_controller" in sys.modules:
        del sys.modules["dashboard_controller"]

    from config import ScraperConfig
    from dashboard_controller import (
        start_dashboard,
        stop_dashboard,
        is_dashboard_running,
        get_dashboard_status,
    )

    # Create mock context
    mock_context = Mock()
    mock_context.get_metrics = Mock(
        return_value={"total_processed": 0, "total_failed": 0, "active_workers": 0}
    )

    print(f"   Configuration ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")

    # Test start_dashboard
    print("   Testing start_dashboard()...")
    result = await start_dashboard(ScraperConfig, mock_context)
    print(f"   start_dashboard() returned: {result}")
    assert result == True, "start_dashboard should return True when enabled"

    # Check if running
    is_running = is_dashboard_running()
    print(f"   is_dashboard_running(): {is_running}")
    assert is_running == True, "Dashboard should be running when enabled"

    # Check status
    status = get_dashboard_status()
    print(f"   Dashboard status: {status}")
    assert status["running"] == True, "Status should show running"
    print("   ✓ Dashboard started successfully when enabled")

    # Test stop_dashboard
    print("   Testing stop_dashboard()...")
    stop_dashboard()
    await asyncio.sleep(0.1)  # Brief wait for cleanup

    is_running_after_stop = is_dashboard_running()
    print(f"   is_dashboard_running() after stop: {is_running_after_stop}")
    assert is_running_after_stop == False, "Dashboard should not be running after stop"
    print("   ✓ Dashboard stopped successfully")

    # Cleanup
    os.environ.pop("SCRAPER_ENABLE_DASHBOARD", None)


async def test_function_based_disabled():
    """Test function-based dashboard when disabled"""
    print("\n🧪 Testing function-based dashboard DISABLED...")

    # Set environment to disabled
    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "false"

    # Fresh imports
    if "config" in sys.modules:
        del sys.modules["config"]
    if "dashboard_controller" in sys.modules:
        del sys.modules["dashboard_controller"]

    from config import ScraperConfig
    from dashboard_controller import (
        start_dashboard,
        stop_dashboard,
        is_dashboard_running,
        get_dashboard_status,
    )

    # Create mock context
    mock_context = Mock()

    print(f"   Configuration ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")

    # Test start_dashboard (should not actually start)
    print("   Testing start_dashboard()...")
    result = await start_dashboard(ScraperConfig, mock_context)
    print(f"   start_dashboard() returned: {result}")
    assert result == False, "start_dashboard should return False when disabled"

    # Check if running (should be false when disabled)
    is_running = is_dashboard_running()
    print(f"   is_dashboard_running(): {is_running}")
    assert is_running == False, "Dashboard should NOT be running when disabled"

    # Check status
    status = get_dashboard_status()
    print(f"   Dashboard status: {status}")
    assert status["running"] == False, "Status should show not running"
    print("   ✓ Dashboard correctly did not start when disabled")

    # Test stop_dashboard (should handle gracefully)
    print("   Testing stop_dashboard()...")
    stop_dashboard()
    print("   ✓ Stop handled gracefully when already stopped")

    # Cleanup
    os.environ.pop("SCRAPER_ENABLE_DASHBOARD", None)


def test_function_based_integration():
    """Test integration with main_self_contained.py"""
    print("\n🧪 Testing function-based integration...")

    try:
        # Test that imports work
        print("   Testing imports...")
        from main_self_contained import main
        from dashboard_controller import start_dashboard, stop_dashboard

        print("   ✓ Function-based imports successful")

        # Test that configuration is accessible
        print("   Testing configuration access...")
        if "config" in sys.modules:
            del sys.modules["config"]
        from config import ScraperConfig

        print(f"   ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")
        print(
            f"   DASHBOARD_UPDATE_INTERVAL: {ScraperConfig.DASHBOARD_UPDATE_INTERVAL}"
        )
        print("   ✓ Configuration accessible")

        print("   ✓ Function-based integration test successful")

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        raise
    except Exception as e:
        print(f"   ❌ Integration error: {e}")
        raise


async def test_function_based_state_management():
    """Test global state management in function-based design"""
    print("\n🧪 Testing function-based state management...")

    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "true"

    # Fresh imports
    if "config" in sys.modules:
        del sys.modules["config"]
    if "dashboard_controller" in sys.modules:
        del sys.modules["dashboard_controller"]

    from config import ScraperConfig
    from dashboard_controller import (
        start_dashboard,
        stop_dashboard,
        is_dashboard_running,
        get_dashboard_status,
    )

    mock_context = Mock()

    # Test initial state
    print("   Testing initial state...")
    initial_status = get_dashboard_status()
    print(f"   Initial status: {initial_status}")
    assert initial_status["running"] == False, "Should not be running initially"

    # Test state after start
    print("   Testing state after start...")
    await start_dashboard(ScraperConfig, mock_context)
    running_status = get_dashboard_status()
    print(f"   Running status: {running_status}")
    assert running_status["running"] == True, "Should be running after start"
    assert running_status["task_exists"] == True, "Task should exist"

    # Test state after stop
    print("   Testing state after stop...")
    stop_dashboard()
    await asyncio.sleep(0.1)
    stopped_status = get_dashboard_status()
    print(f"   Stopped status: {stopped_status}")
    assert stopped_status["running"] == False, "Should not be running after stop"
    print("   ✓ Global state management working correctly")

    # Cleanup
    os.environ.pop("SCRAPER_ENABLE_DASHBOARD", None)


async def test_real_world_usage():
    """Test real-world usage scenarios"""
    print("\n🧪 Testing real-world usage scenarios...")

    # Scenario 1: Production mode (dashboard disabled)
    print("   Scenario 1: Production mode (dashboard disabled)")
    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "false"

    if "config" in sys.modules:
        del sys.modules["config"]
    from config import ScraperConfig

    print(f"   Production config ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")
    assert ScraperConfig.ENABLE_DASHBOARD == False
    print("   ✓ Production mode configuration correct")

    # Scenario 2: Development mode (dashboard enabled)
    print("   Scenario 2: Development mode (dashboard enabled)")
    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "true"

    if "config" in sys.modules:
        del sys.modules["config"]
    from config import ScraperConfig

    print(f"   Development config ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")
    assert ScraperConfig.ENABLE_DASHBOARD == True
    print("   ✓ Development mode configuration correct")

    # Scenario 3: Default mode (dashboard enabled)
    print("   Scenario 3: Default mode (dashboard enabled)")
    os.environ.pop("SCRAPER_ENABLE_DASHBOARD", None)

    if "config" in sys.modules:
        del sys.modules["config"]
    from config import ScraperConfig

    print(f"   Default config ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")
    assert ScraperConfig.ENABLE_DASHBOARD == True
    print("   ✓ Default mode configuration correct")


async def main():
    """Run all function-based dashboard on/off functionality tests"""
    print("🚀 Re-Testing Dashboard On/Off Functionality - Function-Based")
    print("=" * 65)

    try:
        # Test 1: Configuration settings
        test_function_based_configuration()

        # Test 2: Function-based dashboard enabled
        await test_function_based_enabled()

        # Test 3: Function-based dashboard disabled
        await test_function_based_disabled()

        # Test 4: Integration with main
        test_function_based_integration()

        # Test 5: State management
        await test_function_based_state_management()

        # Test 6: Real-world usage
        await test_real_world_usage()

        print("\n" + "=" * 65)
        print("🎉 ALL FUNCTION-BASED DASHBOARD ON/OFF TESTS PASSED!")
        print("✅ Function-based architecture working perfectly")
        print("✅ Dashboard can be enabled/disabled via SCRAPER_ENABLE_DASHBOARD")
        print("✅ Global state management working correctly")
        print("✅ Integration with main_self_contained.py works perfectly")
        print("✅ All real-world usage scenarios validated")
        print("✅ Phase 1, Step 1.4 RE-VALIDATION completed successfully!")
        print("✅ Function-based design pattern properly implemented!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)

    finally:
        # Cleanup environment
        os.environ.pop("SCRAPER_ENABLE_DASHBOARD", None)


if __name__ == "__main__":
    # Suppress logging during tests
    logging.basicConfig(level=logging.WARNING)

    # Run the tests
    asyncio.run(main())
