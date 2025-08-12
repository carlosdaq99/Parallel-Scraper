#!/usr/bin/env python3
"""
Test script for dashboard on/off functionality - Phase 1, Step 1.4

This script tests the dashboard enable/disable functionality through the
SCRAPER_ENABLE_DASHBOARD environment variable and configuration system.
"""

import os
import sys
import asyncio
import logging
from unittest.mock import Mock


def test_dashboard_configuration():
    """Test dashboard configuration settings"""
    print("🧪 Testing dashboard configuration settings...")

    # Test 1: Default configuration (enabled)
    print("1. Testing default configuration...")
    os.environ.pop("SCRAPER_ENABLE_DASHBOARD", None)  # Remove any existing env var

    # Reload config to get fresh settings
    if "config" in sys.modules:
        del sys.modules["config"]
    from config import ScraperConfig

    print(f"   Default ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")
    assert ScraperConfig.ENABLE_DASHBOARD == True, "Default should be enabled"
    print("   ✓ Default configuration correct")

    # Test 2: Explicitly enabled
    print("2. Testing explicitly enabled...")
    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "true"

    if "config" in sys.modules:
        del sys.modules["config"]
    from config import ScraperConfig

    print(f"   Explicit true ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")
    assert ScraperConfig.ENABLE_DASHBOARD == True, "Explicit true should be enabled"
    print("   ✓ Explicit enable correct")

    # Test 3: Explicitly disabled
    print("3. Testing explicitly disabled...")
    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "false"

    if "config" in sys.modules:
        del sys.modules["config"]
    from config import ScraperConfig

    print(f"   Explicit false ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")
    assert ScraperConfig.ENABLE_DASHBOARD == False, "Explicit false should be disabled"
    print("   ✓ Explicit disable correct")

    # Test 4: Case insensitive
    print("4. Testing case insensitive...")
    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "FALSE"

    if "config" in sys.modules:
        del sys.modules["config"]
    from config import ScraperConfig

    print(f"   Uppercase FALSE ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")
    assert ScraperConfig.ENABLE_DASHBOARD == False, "Uppercase FALSE should be disabled"
    print("   ✓ Case insensitive correct")

    # Restore default for other tests
    os.environ.pop("SCRAPER_ENABLE_DASHBOARD", None)
    if "config" in sys.modules:
        del sys.modules["config"]


async def test_dashboard_controller_enabled():
    """Test DashboardController when dashboard is enabled"""
    print("\n🧪 Testing DashboardController with dashboard ENABLED...")

    # Set environment to enabled
    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "true"

    # Fresh imports
    if "config" in sys.modules:
        del sys.modules["config"]
    if "dashboard_controller" in sys.modules:
        del sys.modules["dashboard_controller"]

    from config import ScraperConfig
    from dashboard_controller import DashboardController

    # Create mock context
    mock_context = Mock()
    mock_context.get_metrics = Mock(
        return_value={"total_processed": 0, "total_failed": 0, "active_workers": 0}
    )

    # Test dashboard controller
    controller = DashboardController(ScraperConfig)
    print(
        f"   Controller created with ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}"
    )

    # Test start_dashboard
    print("   Testing start_dashboard...")
    await controller.start_dashboard(mock_context)

    # Check if running (should be true when enabled)
    is_running = controller.is_running()
    print(f"   Dashboard is_running(): {is_running}")
    assert is_running == True, "Dashboard should be running when enabled"
    print("   ✓ Dashboard started successfully when enabled")

    # Test stop_dashboard
    print("   Testing stop_dashboard...")
    controller.stop_dashboard()
    await asyncio.sleep(0.1)  # Brief wait for cleanup

    is_running_after_stop = controller.is_running()
    print(f"   Dashboard is_running() after stop: {is_running_after_stop}")
    assert is_running_after_stop == False, "Dashboard should not be running after stop"
    print("   ✓ Dashboard stopped successfully")

    # Cleanup
    os.environ.pop("SCRAPER_ENABLE_DASHBOARD", None)


async def test_dashboard_controller_disabled():
    """Test DashboardController when dashboard is disabled"""
    print("\n🧪 Testing DashboardController with dashboard DISABLED...")

    # Set environment to disabled
    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "false"

    # Fresh imports
    if "config" in sys.modules:
        del sys.modules["config"]
    if "dashboard_controller" in sys.modules:
        del sys.modules["dashboard_controller"]

    from config import ScraperConfig
    from dashboard_controller import DashboardController

    # Create mock context
    mock_context = Mock()

    # Test dashboard controller
    controller = DashboardController(ScraperConfig)
    print(
        f"   Controller created with ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}"
    )

    # Test start_dashboard (should not actually start)
    print("   Testing start_dashboard...")
    await controller.start_dashboard(mock_context)

    # Check if running (should be false when disabled)
    is_running = controller.is_running()
    print(f"   Dashboard is_running(): {is_running}")
    assert is_running == False, "Dashboard should NOT be running when disabled"
    print("   ✓ Dashboard correctly did not start when disabled")

    # Test stop_dashboard (should handle gracefully)
    print("   Testing stop_dashboard...")
    controller.stop_dashboard()
    print("   ✓ Stop handled gracefully when already stopped")

    # Cleanup
    os.environ.pop("SCRAPER_ENABLE_DASHBOARD", None)


async def test_configuration_switching():
    """Test switching configuration during runtime"""
    print("\n🧪 Testing configuration switching...")

    # Start with enabled
    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "true"
    if "config" in sys.modules:
        del sys.modules["config"]
    if "dashboard_controller" in sys.modules:
        del sys.modules["dashboard_controller"]

    from config import ScraperConfig
    from dashboard_controller import DashboardController

    print(f"   Initial config ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")

    # Create controllers with different configs
    enabled_controller = DashboardController(ScraperConfig)

    # Switch to disabled config
    os.environ["SCRAPER_ENABLE_DASHBOARD"] = "false"
    if "config" in sys.modules:
        del sys.modules["config"]
    from config import ScraperConfig as DisabledConfig

    disabled_controller = DashboardController(DisabledConfig)
    print(f"   Switched config ENABLE_DASHBOARD: {DisabledConfig.ENABLE_DASHBOARD}")

    # Test that each controller respects its config
    mock_context = Mock()

    print("   Testing enabled controller...")
    await enabled_controller.start_dashboard(mock_context)
    assert enabled_controller.is_running() == True, "Enabled controller should start"
    enabled_controller.stop_dashboard()
    print("   ✓ Enabled controller worked correctly")

    print("   Testing disabled controller...")
    await disabled_controller.start_dashboard(mock_context)
    assert (
        disabled_controller.is_running() == False
    ), "Disabled controller should not start"
    print("   ✓ Disabled controller worked correctly")

    # Cleanup
    os.environ.pop("SCRAPER_ENABLE_DASHBOARD", None)


def test_integration_with_main():
    """Test integration points with main_self_contained.py"""
    print("\n🧪 Testing integration with main_self_contained.py...")

    try:
        # Test that imports work
        print("   Testing imports...")
        from main_self_contained import main
        from dashboard_controller import DashboardController

        print("   ✓ Imports successful")

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

        print("   ✓ Integration test successful")

    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        raise
    except Exception as e:
        print(f"   ❌ Integration error: {e}")
        raise


async def main():
    """Run all dashboard on/off functionality tests"""
    print("🚀 Starting Dashboard On/Off Functionality Tests")
    print("=" * 60)

    try:
        # Test 1: Configuration settings
        test_dashboard_configuration()

        # Test 2: DashboardController with enabled dashboard
        await test_dashboard_controller_enabled()

        # Test 3: DashboardController with disabled dashboard
        await test_dashboard_controller_disabled()

        # Test 4: Configuration switching
        await test_configuration_switching()

        # Test 5: Integration with main
        test_integration_with_main()

        print("\n" + "=" * 60)
        print("🎉 ALL DASHBOARD ON/OFF FUNCTIONALITY TESTS PASSED!")
        print("✅ Dashboard can be enabled/disabled via SCRAPER_ENABLE_DASHBOARD")
        print("✅ DashboardController respects configuration settings")
        print("✅ Proper behavior when enabled vs disabled")
        print("✅ Integration with main_self_contained.py works correctly")
        print("✅ Phase 1, Step 1.4 completed successfully!")

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
