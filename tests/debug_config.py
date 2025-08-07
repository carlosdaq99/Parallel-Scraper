#!/usr/bin/env python3
"""
Debug dynamic config
"""
import sys

sys.path.append(".")

print("🔧 Testing dynamic config...")
try:
    from enhanced_config_manager import get_dynamic_config

    config = get_dynamic_config()
    print("Dynamic config values:")
    print(f"  min_workers: {config.get('min_workers', 'NOT SET')}")
    print(f"  max_workers: {config.get('max_workers', 'NOT SET')}")
    print(f"  initial_workers: {config.get('initial_workers', 'NOT SET')}")

    print("\nOther relevant keys:")
    relevant_keys = [k for k in config.keys() if "worker" in k.lower()]
    for key in relevant_keys:
        print(f"  {key}: {config[key]}")

except Exception as e:
    print(f"❌ Config test failed: {e}")
    import traceback

    traceback.print_exc()

print("\n🔧 Testing base config values...")
try:
    from config import ScraperConfig

    print(f"ScraperConfig.MAX_WORKERS: {ScraperConfig.MAX_WORKERS}")
    print(f"ScraperConfig.MIN_WORKERS: {ScraperConfig.MIN_WORKERS}")
    print(f"ScraperConfig.INITIAL_WORKERS: {ScraperConfig.INITIAL_WORKERS}")
except Exception as e:
    print(f"❌ Base config test failed: {e}")

print("\n🔧 Test complete")
