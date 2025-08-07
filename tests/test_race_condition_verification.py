#!/usr/bin/env python3
"""
Race Condition Verification Test

This test verifies the hypothesis that the completion monitoring in main_self_contained.py
has a race condition where it exits before workers can register and start processing tasks.
"""

import asyncio
import sys
import time
from pathlib import Path

# Add the current directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Add parent directory to path for imports
    parent_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(parent_dir))

    from config import ScraperConfig
    from data_structures import NodeInfo, Task, ParallelWorkerContext
    import logging

    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


async def test_race_condition():
    """Test the race condition in completion monitoring."""

    print("\n=== Race Condition Verification Test ===")

    # Set up logging
    logger = logging.getLogger("test")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)

    # Create worker context
    max_workers = 3
    worker_context = ParallelWorkerContext(max_workers, logger)

    print(f"📊 Initial state:")
    print(f"   • Queue empty: {worker_context.task_queue.empty()}")
    print(f"   • Active workers: {len(worker_context.worker_manager.active_workers)}")

    # Add some test tasks
    test_tasks = []
    for i in range(2):
        node_info = NodeInfo(
            label=f"TestFolder_{i}",
            path="/test",
            depth=0,
            worker_id=f"test_worker_{i}",
            guid="",
        )
        task = Task(worker_id=f"test_worker_{i}", node_info=node_info, priority=0)
        await worker_context.task_queue.put(task)
        test_tasks.append(task)

    print(f"\n📊 After adding {len(test_tasks)} tasks:")
    print(f"   • Queue empty: {worker_context.task_queue.empty()}")
    print(f"   • Queue size: {worker_context.task_queue.qsize()}")
    print(f"   • Active workers: {len(worker_context.worker_manager.active_workers)}")

    # Simulate the main loop's completion check (THE BUG)
    completion_condition = (
        worker_context.task_queue.empty()
        and not worker_context.worker_manager.active_workers
    )

    print(f"\n🚨 RACE CONDITION CHECK:")
    print(f"   • Queue empty: {worker_context.task_queue.empty()}")
    print(f"   • Active workers: {len(worker_context.worker_manager.active_workers)}")
    print(f"   • Completion condition: {completion_condition}")

    if not worker_context.task_queue.empty() and completion_condition:
        print("❌ BUG CONFIRMED: Queue has tasks but completion condition is True!")
        print("   This means main loop would exit before workers can process tasks")
        return False

    # Now simulate worker registration with some delay
    print(f"\n⏱️  Simulating worker registration timing...")

    async def mock_worker_startup(worker_id: str, delay: float):
        await asyncio.sleep(delay)  # Startup delay
        success = await worker_context.worker_manager.register_worker(worker_id)
        print(f"   • Worker {worker_id} registered after {delay}s: {success}")
        return success

    # Start mock workers with different startup delays
    worker_tasks = [
        asyncio.create_task(mock_worker_startup(f"Worker-{i}", i * 0.1))
        for i in range(max_workers)
    ]

    # Monitor the race condition timing
    start_time = time.time()
    batch_delay = ScraperConfig.WORKER_STARTUP_BATCH_DELAY  # This is what main uses

    print(f"   • Configured WORKER_BATCH_DELAY: {batch_delay}s")
    print(f"   • Waiting {batch_delay}s (same as main_self_contained.py)...")

    await asyncio.sleep(batch_delay)

    elapsed = time.time() - start_time
    print(f"\n📊 After {elapsed:.2f}s delay (same as main):")
    print(f"   • Queue empty: {worker_context.task_queue.empty()}")
    print(f"   • Active workers: {len(worker_context.worker_manager.active_workers)}")

    # Check the problematic condition again
    completion_condition_after_delay = (
        worker_context.task_queue.empty()
        and not worker_context.worker_manager.active_workers
    )

    print(f"   • Completion condition: {completion_condition_after_delay}")

    if not worker_context.task_queue.empty() and completion_condition_after_delay:
        print("❌ RACE CONDITION CONFIRMED!")
        print("   Main loop exits before workers register, causing 0 tasks processed")
        return False

    # Wait for all workers to register
    await asyncio.gather(*worker_tasks)

    print(f"\n📊 After all workers registered:")
    print(f"   • Queue empty: {worker_context.task_queue.empty()}")
    print(f"   • Active workers: {len(worker_context.worker_manager.active_workers)}")

    completion_condition_final = (
        worker_context.task_queue.empty()
        and not worker_context.worker_manager.active_workers
    )

    print(f"   • Completion condition: {completion_condition_final}")

    if not completion_condition_final:
        print("✅ Workers registered successfully, condition now correct")
        return True
    else:
        print("❌ Issue persists even after registration")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_race_condition())
    if not result:
        print("\n🎯 DIAGNOSIS: Race condition confirmed in main_self_contained.py")
        print("   • Main loop checks completion before workers can register")
        print("   • 1-second delay is insufficient for worker startup")
        print("   • Workers timeout because main loop exits prematurely")
        sys.exit(1)
    else:
        print("\n✅ Race condition test passed")
        sys.exit(0)
