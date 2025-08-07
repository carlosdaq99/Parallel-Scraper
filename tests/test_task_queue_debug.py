#!/usr/bin/env python3
"""
Task Queue Debug Test

This test tracks exactly what happens with task_done() calls to understand
why queue.join() completes when workers haven't processed any tasks.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

try:
    from config import ScraperConfig
    from data_structures import NodeInfo, Task, ParallelWorkerContext
    import logging

    print("✅ Imports successful")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class DebugQueue(asyncio.Queue):
    """Debug wrapper for asyncio.Queue to track task_done() calls"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.put_count = 0
        self.done_count = 0

    async def put(self, item):
        self.put_count += 1
        print(
            f"🔵 Queue.put() called: item={item.worker_id}, total_puts={self.put_count}"
        )
        await super().put(item)

    def task_done(self):
        self.done_count += 1
        print(
            f"🟢 Queue.task_done() called: total_done={self.done_count}, pending={self.put_count - self.done_count}"
        )
        super().task_done()

    async def join(self):
        print(
            f"🔴 Queue.join() starting: puts={self.put_count}, done={self.done_count}"
        )
        await super().join()
        print(
            f"🟢 Queue.join() completed: puts={self.put_count}, done={self.done_count}"
        )


async def test_task_queue_behavior():
    """Test task queue behavior to understand premature completion."""

    print("\n=== Task Queue Debug Test ===")

    # Set up logging
    logger = logging.getLogger("test")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(handler)

    # Create worker context with debug queue
    max_workers = 3
    worker_context = ParallelWorkerContext(max_workers, logger)

    # Replace the queue with our debug version
    original_queue = worker_context.task_queue
    debug_queue = DebugQueue()
    worker_context.task_queue = debug_queue

    print(f"📊 Initial state:")
    print(f"   • Queue puts: {debug_queue.put_count}")
    print(f"   • Queue done: {debug_queue.done_count}")
    print(f"   • Queue size: {debug_queue.qsize()}")

    # Add test tasks (this calls our debug put())
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
    print(f"   • Queue puts: {debug_queue.put_count}")
    print(f"   • Queue done: {debug_queue.done_count}")
    print(f"   • Queue size: {debug_queue.qsize()}")
    print(f"   • Pending tasks: {debug_queue.put_count - debug_queue.done_count}")

    # Test if join() would complete immediately
    print(f"\n🔴 Testing queue.join() behavior...")

    try:
        # Set a short timeout to see if join() completes immediately
        await asyncio.wait_for(debug_queue.join(), timeout=1.0)
        print("❌ BUG CONFIRMED: queue.join() completed immediately!")
        print("   This means task_done() was called for all tasks without processing")
        return False
    except asyncio.TimeoutError:
        print("✅ queue.join() correctly waiting for tasks to be processed")

    # Simulate what happens when we mark tasks completed
    print(f"\n🟢 Simulating task completion...")
    for i, task in enumerate(test_tasks):
        # Simulate getting a task from queue
        retrieved_task = await debug_queue.get()
        print(f"   Retrieved task: {retrieved_task.worker_id}")

        # Simulate successful processing
        node_info = NodeInfo(
            label=f"ProcessedFolder_{i}",
            path="/processed",
            depth=1,
            worker_id=retrieved_task.worker_id,
            guid="",
        )

        # This should call task_done()
        await worker_context.mark_task_completed(retrieved_task.worker_id, node_info)
        print(f"   Marked {retrieved_task.worker_id} as completed")

    print(f"\n📊 After processing all tasks:")
    print(f"   • Queue puts: {debug_queue.put_count}")
    print(f"   • Queue done: {debug_queue.done_count}")
    print(f"   • Queue size: {debug_queue.qsize()}")
    print(f"   • Pending tasks: {debug_queue.put_count - debug_queue.done_count}")

    # Now join() should complete
    print(f"\n🔴 Testing queue.join() after proper completion...")
    try:
        await asyncio.wait_for(debug_queue.join(), timeout=0.1)
        print("✅ queue.join() completed after proper task processing")
        return True
    except asyncio.TimeoutError:
        print("❌ queue.join() still waiting - something wrong with task_done() logic")
        return False


if __name__ == "__main__":
    result = asyncio.run(test_task_queue_behavior())
    if not result:
        print("\n🎯 DIAGNOSIS: task_done() being called prematurely or incorrectly")
        print("   • Check if task submission itself calls task_done()")
        print("   • Check if task failures call task_done() immediately")
        print("   • This would cause queue.join() to complete before workers start")
        sys.exit(1)
    else:
        print("\n✅ Task queue behavior is correct")
        sys.exit(0)
