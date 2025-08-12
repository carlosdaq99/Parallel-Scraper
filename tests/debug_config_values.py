#!/usr/bin/env python3
"""
Debug script to check current config values and environment variables.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_config_values():
    """Check what config values are currently set."""
    print("Configuration Debug Report")
    print("=" * 50)

    # Check environment variables
    print("Environment Variables:")
    env_vars = [
        "SCRAPER_ENABLE_DASHBOARD",
        "SCRAPER_DASHBOARD_INTERVAL",
        "SCRAPER_ADAPTIVE_SCALING",
    ]

    for var in env_vars:
        value = os.getenv(var, "NOT SET")
        print(f"  {var} = {value}")

    print("\nConfig.py Values:")
    try:
        from config import ScraperConfig

        print(f"  ENABLE_DASHBOARD = {ScraperConfig.ENABLE_DASHBOARD}")
        print(
            f"  DASHBOARD_UPDATE_INTERVAL = {ScraperConfig.DASHBOARD_UPDATE_INTERVAL}"
        )
        print(
            f"  ADAPTIVE_SCALING_INTERVAL = {ScraperConfig.ADAPTIVE_SCALING_INTERVAL}"
        )
    except Exception as e:
        print(f"  Error loading config: {e}")

    print("\nReal-time Monitor Fallback:")
    try:
        # Check if real_time_monitor uses fallback
        import real_time_monitor

        if hasattr(real_time_monitor, "ScraperConfig"):
            print(f"  Using config import: OK")
        else:
            print(f"  Using fallback: hardcoded 10.0 seconds")
    except Exception as e:
        print(f"  Error checking real_time_monitor: {e}")


if __name__ == "__main__":
    check_config_values()
