#!/usr/bin/env python3
"""
Simple test to debug the scaling issue
"""
import sys
import asyncio

sys.path.append(".")

# Test imports first
print("🔧 Testing imports...")
try:
    from main_self_contained import update_worker_count, get_current_workers

    print("✅ Core functions imported")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test basic scaling
print("\n🔧 Testing basic scaling...")
try:
    current = get_current_workers()
    print(f"Current workers: {current}")

    print("\nTesting update_worker_count(55)...")
    update_worker_count(55, "Debug test scaling up")

    new_current = get_current_workers()
    print(f"New current workers: {new_current}")

    if new_current != current:
        print("✅ Worker count changed successfully!")
    else:
        print("❌ Worker count did not change")

except Exception as e:
    print(f"❌ Scaling test failed: {e}")
    import traceback

    traceback.print_exc()

print("\n🔧 Test complete")
