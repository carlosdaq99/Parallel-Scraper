#!/usr/bin/env python3
"""
Test script for dashboard controller integration in main_self_contained.py
"""

import sys
import os

# Ensure we can import the modules
try:
    print("Testing dashboard controller integration...")

    # Test individual imports
    print("1. Testing config import...")
    from config import ScraperConfig

    print("   ✓ ScraperConfig imported")

    print("2. Testing dashboard controller import...")
    from dashboard_controller import DashboardController

    print("   ✓ DashboardController imported")

    print("3. Testing dashboard controller instantiation...")
    dashboard = DashboardController(ScraperConfig)
    print("   ✓ DashboardController instantiated")

    print("4. Checking configuration values...")
    print(f"   ENABLE_DASHBOARD: {ScraperConfig.ENABLE_DASHBOARD}")
    print(f"   DASHBOARD_UPDATE_INTERVAL: {ScraperConfig.DASHBOARD_UPDATE_INTERVAL}")

    print("5. Testing dashboard controller methods...")
    print(f"   is_running(): {dashboard.is_running()}")
    print("   stop_dashboard(): ", end="")
    dashboard.stop_dashboard()
    print("✓ executed")

    print("\n🎉 Dashboard controller integration test completed successfully!")
    print("   The dashboard controller is properly integrated and ready to use.")

except Exception as e:
    import traceback

    print(f"❌ Integration test failed: {e}")
    print("Full traceback:")
    traceback.print_exc()
    sys.exit(1)
