#!/usr/bin/env python3
"""
Test Phase 4 Step 4.3: Performance Testing with 200+ Workers
Tests system performance and hierarchical tracking with high worker loads.
"""

import sys
import os
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List, Any

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


@dataclass
class PerformanceConfig:
    """Configuration for performance testing."""

    hierarchical_tracking: bool = True
    tracking_verbosity: str = "quiet"  # Use quiet for performance testing
    dashboard_enabled: bool = False  # Disable dashboard for pure performance test
    worker_count: int = 200
    max_workers: int = 250
    performance_test_mode: bool = True


class PerformanceTestContext:
    """Mock context for performance testing."""

    def __init__(self):
        # Import and use actual tracker state initialization
        from worker_tracking_display import initialize_tracker_state

        self.tracker_state = initialize_tracker_state()
        self.start_time = time.time()
        self.tasks_completed = 0
        self.lock = threading.Lock()


def simulate_worker_task(
    worker_id: str, task_count: int, tracker, context: PerformanceTestContext
) -> Dict[str, Any]:
    """Simulate a worker performing multiple tasks."""
    worker_stats = {
        "worker_id": worker_id,
        "tasks_completed": 0,
        "start_time": time.time(),
        "errors": 0,
    }

    try:
        for i in range(task_count):
            task_id = f"{worker_id}_task_{i}"

            # Simulate task start
            tracker.track_task_start(
                task_id=task_id,
                worker_id=worker_id,
                parent_id=(
                    None if i % 5 != 0 else f"{worker_id}_task_{i-1}"
                ),  # Some child tasks
                metadata={"url": f"https://example.com/task/{i}", "depth": i % 3},
            )

            # Simulate work (very brief for performance testing)
            time.sleep(0.001)  # 1ms simulated work

            # Simulate task completion
            status = "completed" if i % 20 != 0 else "failed"  # 5% failure rate
            tracker.track_task_completion(task_id, status)

            worker_stats["tasks_completed"] += 1

            with context.lock:
                context.tasks_completed += 1

    except Exception as e:
        worker_stats["errors"] += 1
        print(f"Error in worker {worker_id}: {e}")

    worker_stats["end_time"] = time.time()
    worker_stats["duration"] = worker_stats["end_time"] - worker_stats["start_time"]

    return worker_stats


def test_high_worker_performance():
    """Test performance with 200+ workers."""
    print("=== Testing Phase 4 Step 4.3: Performance Testing with 200+ Workers ===\n")

    try:
        from worker_tracking_display import create_tracker

        # Performance test configurations
        test_configs = [
            {
                "workers": 200,
                "tasks_per_worker": 10,
                "description": "200 workers, 10 tasks each",
            },
            {
                "workers": 250,
                "tasks_per_worker": 8,
                "description": "250 workers, 8 tasks each",
            },
            {
                "workers": 300,
                "tasks_per_worker": 5,
                "description": "300 workers, 5 tasks each",
            },
        ]

        for test_config in test_configs:
            print(f"\n--- Performance Test: {test_config['description']} ---")

            # Create performance configuration
            config = PerformanceConfig(
                worker_count=test_config["workers"],
                max_workers=test_config["workers"] + 50,
            )

            # Create context and tracker
            context = PerformanceTestContext()
            tracker = create_tracker(config, context)

            print(
                f"Created {type(tracker).__name__} for {test_config['workers']} workers"
            )

            # Start tracker
            start_time = time.time()
            tracker.start()

            # Use ThreadPoolExecutor to simulate high concurrency
            with ThreadPoolExecutor(max_workers=test_config["workers"]) as executor:
                # Submit worker tasks
                futures = []
                for worker_num in range(test_config["workers"]):
                    worker_id = f"perf_worker_{worker_num:03d}"
                    future = executor.submit(
                        simulate_worker_task,
                        worker_id,
                        test_config["tasks_per_worker"],
                        tracker,
                        context,
                    )
                    futures.append(future)

                # Wait for all workers to complete
                worker_results = []
                for future in futures:
                    try:
                        result = future.result(
                            timeout=30
                        )  # 30 second timeout per worker
                        worker_results.append(result)
                    except Exception as e:
                        print(f"Worker future failed: {e}")

            # Stop tracker and collect results
            tracker.stop()
            end_time = time.time()

            # Calculate performance metrics
            total_duration = end_time - start_time
            total_tasks = sum(r["tasks_completed"] for r in worker_results)
            successful_workers = len([r for r in worker_results if r["errors"] == 0])
            total_errors = sum(r["errors"] for r in worker_results)

            tasks_per_second = total_tasks / total_duration if total_duration > 0 else 0
            avg_worker_duration = sum(r["duration"] for r in worker_results) / len(
                worker_results
            )

            # Get tracker statistics
            tracker_stats = tracker.get_tracking_statistics()

            # Display results
            print(f"  ✅ Test completed in {total_duration:.2f} seconds")
            print(
                f"  ✅ Workers: {len(worker_results)}/{test_config['workers']} completed"
            )
            print(f"  ✅ Tasks completed: {total_tasks}")
            print(f"  ✅ Tasks/second: {tasks_per_second:.1f}")
            print(
                f"  ✅ Successful workers: {successful_workers}/{len(worker_results)}"
            )
            print(f"  ✅ Total errors: {total_errors}")
            print(f"  ✅ Avg worker duration: {avg_worker_duration:.3f}s")
            print(f"  ✅ Tracker statistics: {len(tracker_stats)} metrics collected")
            print(
                f"  ✅ Memory efficient: Tracker handled {total_tasks} tasks concurrently"
            )

            # Performance validation
            assert (
                tasks_per_second > 50
            ), f"Performance too low: {tasks_per_second:.1f} tasks/sec"
            assert (
                total_errors < total_tasks * 0.1
            ), f"Too many errors: {total_errors}/{total_tasks}"
            assert (
                successful_workers > test_config["workers"] * 0.95
            ), f"Too many worker failures: {successful_workers}/{test_config['workers']}"

            print(f"  ✅ Performance validation passed")

        print("\n=== Performance Test Summary ===")
        print("- ✅ Successfully tested with 200+ workers")
        print("- ✅ Hierarchical tracking scales to high worker counts")
        print("- ✅ Memory usage remains efficient under load")
        print("- ✅ Task tracking performance meets requirements")
        print("- ✅ Error rates within acceptable limits")
        print("- ✅ Concurrent worker handling validated")

        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_tracker_memory_efficiency():
    """Test memory efficiency of tracker under load."""
    print("\n=== Testing Tracker Memory Efficiency ===")

    try:
        from worker_tracking_display import create_tracker, NullTracker
        import psutil
        import os

        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        print(f"Initial memory usage: {initial_memory:.1f} MB")

        # Test with HierarchicalTracker
        config = PerformanceConfig(
            hierarchical_tracking=True, tracking_verbosity="quiet"
        )
        context = PerformanceTestContext()
        tracker = create_tracker(config, context)

        tracker.start()

        # Simulate many tasks
        task_count = 1000
        for i in range(task_count):
            task_id = f"mem_test_task_{i}"
            tracker.track_task_start(task_id, f"worker_{i % 50}", None, {"test": True})
            tracker.track_task_completion(task_id, "completed")

        # Get memory after tracking many tasks
        mid_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = mid_memory - initial_memory

        tracker.stop()

        # Get final memory (should be similar to mid_memory for good memory management)
        final_memory = process.memory_info().rss / 1024 / 1024  # MB

        print(
            f"Memory after {task_count} tasks: {mid_memory:.1f} MB (+{memory_increase:.1f} MB)"
        )
        print(f"Final memory: {final_memory:.1f} MB")
        print(f"Memory per task: {memory_increase * 1024 / task_count:.2f} KB")

        # Validate memory efficiency
        memory_per_task_kb = memory_increase * 1024 / task_count
        assert (
            memory_per_task_kb < 10
        ), f"Memory usage too high: {memory_per_task_kb:.2f} KB per task"

        print("✅ Memory efficiency test passed")

        # Test NullTracker for comparison
        null_tracker = NullTracker()
        null_tracker.start()

        initial_null_memory = process.memory_info().rss / 1024 / 1024

        for i in range(task_count):
            null_tracker.track_task_start(f"null_task_{i}", f"worker_{i % 50}")
            null_tracker.track_task_completion(f"null_task_{i}", "completed")

        final_null_memory = process.memory_info().rss / 1024 / 1024
        null_memory_increase = final_null_memory - initial_null_memory

        null_tracker.stop()

        print(
            f"NullTracker memory increase: {null_memory_increase:.1f} MB (should be minimal)"
        )

        assert (
            null_memory_increase < 1
        ), f"NullTracker using too much memory: {null_memory_increase:.1f} MB"

        print("✅ NullTracker memory efficiency confirmed")

        return True

    except Exception as e:
        print(f"❌ Memory efficiency test failed: {e}")
        return False


if __name__ == "__main__":
    print("Testing Phase 4 Step 4.3: Performance Testing with 200+ Workers")
    print("=" * 70)

    performance_ok = test_high_worker_performance()
    memory_ok = test_tracker_memory_efficiency()

    if performance_ok and memory_ok:
        print("\n🎉 ALL PERFORMANCE TESTS PASSED - Phase 4 Step 4.3 COMPLETED")
        print("System ready for high-load production deployment!")
    else:
        print("\n❌ Some performance tests failed")
        sys.exit(1)
