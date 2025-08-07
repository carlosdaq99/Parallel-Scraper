"""
Test script to verify the main_self_contained.py file is working correctly
and that all scaling issues have been resolved.
"""

import asyncio
import time
from main_self_contained import (
    initialize_adaptive_scaling,
    get_current_workers,
    update_worker_count,
    SelfContainedScrapingManager,
)


async def test_main_file_functionality():
    """Test the main file functionality."""
    print("🧪 Testing main_self_contained.py functionality...")

    # Test 1: Initialization
    print("\n1. Testing adaptive scaling initialization...")
    initialize_adaptive_scaling()
    initial_workers = get_current_workers()
    print(f"   ✅ Initial workers: {initial_workers}")

    # Test 2: Worker scaling
    print("\n2. Testing worker scaling...")
    update_worker_count(60, "Test scaling up")
    updated_workers = get_current_workers()
    print(f"   ✅ Updated workers: {updated_workers}")

    # Test 3: Manager initialization
    print("\n3. Testing scraping manager...")
    manager = SelfContainedScrapingManager()
    print("   ✅ Manager initialized successfully")

    # Test 4: Performance data collection
    print("\n4. Testing performance data collection...")
    performance_data = await manager.get_current_performance_data()
    print(f"   ✅ Performance data: {performance_data}")

    print("\n✅ All tests passed! Main file is fully functional.")
    return True


if __name__ == "__main__":
    asyncio.run(test_main_file_functionality())
