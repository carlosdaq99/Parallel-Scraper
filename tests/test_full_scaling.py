#!/usr/bin/env python3
"""
Test full scaling integration
"""
import sys
import asyncio

sys.path.append(".")


async def test_full_scaling():
    print("🔧 Testing full scaling integration...")

    try:
        from main_self_contained import (
            SelfContainedScrapingManager,
            perform_adaptive_scaling_check,
        )

        # Create manager
        manager = SelfContainedScrapingManager()

        # Get real performance data
        print("📊 Getting real performance data...")
        perf_data = await manager.get_current_performance_data()
        print(f"Performance data: {perf_data}")

        # Test scaling with this data
        print("\n🚀 Testing adaptive scaling...")
        await perform_adaptive_scaling_check(perf_data)

        # Test scaling with high queue (should trigger scale-up)
        print("\n🚀 Testing with high queue (should scale up)...")
        high_load_data = {
            "success_rate": 1.0,
            "avg_processing_time": 1.5,  # Fast response
            "queue_length": 50,  # High queue
            "cpu_usage_percent": 40.0,  # Low CPU
            "memory_usage_mb": 400.0,  # Low memory
        }
        await perform_adaptive_scaling_check(high_load_data)

        # Test scaling with poor performance (should scale down)
        print("\n🚀 Testing with poor performance (should scale down)...")
        poor_perf_data = {
            "success_rate": 0.6,  # Poor success rate
            "avg_processing_time": 8.0,  # Slow response
            "queue_length": 5,  # Low queue
            "cpu_usage_percent": 90.0,  # High CPU
            "memory_usage_mb": 900.0,  # High memory
        }
        await perform_adaptive_scaling_check(poor_perf_data)

        print("\n✅ Full scaling integration test completed!")

    except Exception as e:
        print(f"❌ Full scaling test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_full_scaling())
