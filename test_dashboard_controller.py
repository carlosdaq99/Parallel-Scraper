#!/usr/bin/env python3
"""
Test script for dashboard_controller import
"""

try:
    print("Testing dashboard_controller import...")
    from dashboard_controller import DashboardController

    print("✓ DashboardController imported successfully")

    print("Testing config import...")
    from config import ScraperConfig

    print("✓ ScraperConfig imported successfully")

    print("Creating instances...")
    config = ScraperConfig()
    dashboard = DashboardController(config)
    print("✓ DashboardController instance created successfully")

    print(f"Dashboard enabled: {config.ENABLE_DASHBOARD}")
    print(f"Update interval: {config.DASHBOARD_UPDATE_INTERVAL}")
    print("Available methods:", [m for m in dir(dashboard) if not m.startswith("_")])

except Exception as e:
    import traceback

    print(f"❌ Error: {e}")
    print("Full traceback:")
    traceback.print_exc()
