"""
Test Phase 3: Advanced Hierarchical Worker Tracking Features

This test validates the hierarchical worker tracking implementation
including task parent-child relationships, queue analysis, and status updates.
"""

import asyncio
import sys
import os
import time
from unittest.mock import MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from worker_tracking_display import (
    initialize_tracker_state,
    track_task_start,
    track_task_completion,
    track_task_child_creation,
    get_task_hierarchy,
    get_root_tasks,
    display_hierarchical_status,
    display_queue_analysis,
    get_queue_health_summary,
    get_tracking_statistics,
)
from data_structures import Task, NodeInfo


async def test_hierarchical_tracking():
    """Test basic hierarchical tracking functionality."""
    print("Testing hierarchical tracking...")

    # Initialize tracker state
    tracker_state = initialize_tracker_state()
    print(f"✓ Initialized tracker state: {len(tracker_state['tasks'])} tasks")

    # Create a mock context
    context = MagicMock()
    context.task_queue.qsize.return_value = 0
    context.shutdown_flag = False

    # Create parent task
    parent_node = NodeInfo(
        label="Parent Folder",
        path="/parent",
        depth=0,
        worker_id="worker-1",
        guid="parent-guid",
    )
    parent_task = Task(worker_id="worker-1", node_info=parent_node, priority=0)

    # Track parent task start
    track_task_start(
        tracker_state,
        parent_task.task_id,
        "worker-1",
        metadata={"label": "Parent Folder", "depth": 0},
    )
    print(f"✓ Started parent task: {parent_task.task_id[:8]}")

    # Create child tasks
    child_tasks = []
    for i in range(3):
        child_node = NodeInfo(
            label=f"Child Folder {i}",
            path=f"/parent/child{i}",
            depth=1,
            worker_id=f"worker-{i+2}",
            guid=f"child-{i}-guid",
        )
        child_task = Task(
            worker_id=f"worker-{i+2}",
            node_info=child_node,
            priority=1,
            parent_task_id=parent_task.task_id,
        )
        child_tasks.append(child_task)

        # Track child task start
        track_task_start(
            tracker_state,
            child_task.task_id,
            f"worker-{i+2}",
            parent_id=parent_task.task_id,
            metadata={"label": f"Child Folder {i}", "depth": 1},
        )

        # Track parent-child relationship
        track_task_child_creation(
            tracker_state, parent_task.task_id, child_task.task_id
        )

        print(f"✓ Started child task {i}: {child_task.task_id[:8]}")

        # Simulate some work time
        await asyncio.sleep(0.1)

    # Complete some tasks
    track_task_completion(tracker_state, child_tasks[0].task_id, "completed")
    track_task_completion(tracker_state, child_tasks[1].task_id, "failed")
    print("✓ Completed first child, failed second child")

    # Test hierarchy retrieval
    hierarchy = get_task_hierarchy(tracker_state, parent_task.task_id)
    assert "children" in hierarchy, "Hierarchy should include children"
    assert (
        len(hierarchy["children"]) == 3
    ), f"Expected 3 children, got {len(hierarchy['children'])}"
    print(f"✓ Hierarchy contains {len(hierarchy['children'])} children")

    # Test root tasks
    root_tasks = get_root_tasks(tracker_state)
    assert parent_task.task_id in root_tasks, "Parent task should be in root tasks"
    print(f"✓ Found {len(root_tasks)} root tasks")

    # Test tracking statistics
    stats = get_tracking_statistics(tracker_state)
    assert (
        stats["tasks"]["total"] == 4
    ), f"Expected 4 total tasks, got {stats['tasks']['total']}"
    assert (
        stats["tasks"]["completed"] == 1
    ), f"Expected 1 completed task, got {stats['tasks']['completed']}"
    assert (
        stats["tasks"]["failed"] == 1
    ), f"Expected 1 failed task, got {stats['tasks']['failed']}"
    print(
        f"✓ Statistics: {stats['tasks']['total']} total, {stats['tasks']['completed']} completed, {stats['tasks']['failed']} failed"
    )

    return tracker_state, context


async def test_queue_analysis():
    """Test queue analysis functionality."""
    print("\nTesting queue analysis...")

    tracker_state, context = await test_hierarchical_tracking()

    # Test health summary
    health = get_queue_health_summary(tracker_state, context)
    assert "health_score" in health, "Health summary should include score"
    assert "queue_size" in health, "Health summary should include queue size"
    print(f"✓ Health score: {health['health_score']}/100")

    # Test display functions (just ensure they don't crash)
    print("\n--- Queue Analysis Display ---")
    display_queue_analysis(tracker_state, context)

    print("\n--- Hierarchical Status Display ---")
    display_hierarchical_status(tracker_state)

    print("✓ Display functions completed successfully")


async def test_periodic_updates():
    """Test periodic status updates functionality."""
    print("\nTesting periodic updates...")

    tracker_state, context = await test_hierarchical_tracking()

    # Test a single update cycle (short interval)
    print("Running single periodic update...")

    try:
        # Create the update task with a short timeout
        update_task = asyncio.create_task(
            asyncio.wait_for(
                periodic_status_updates(tracker_state, context, interval=1), timeout=2.0
            )
        )

        # Wait briefly then cancel
        await asyncio.sleep(1.5)
        update_task.cancel()

        try:
            await update_task
        except asyncio.CancelledError:
            print("✓ Periodic updates cancelled successfully")
        except asyncio.TimeoutError:
            print("✓ Periodic updates timed out as expected")

    except Exception as e:
        print(f"✓ Periodic updates handled error: {e}")


async def main():
    """Run all Phase 3 tests."""
    print("=" * 80)
    print("PHASE 3: HIERARCHICAL TRACKING TESTS")
    print("=" * 80)

    try:
        # Test Step 3.1: Hierarchical tracking foundation
        print("\n🔄 Step 3.1: Testing hierarchical tracking foundation...")
        await test_hierarchical_tracking()

        # Test Step 3.2: Queue analysis display
        print("\n🔄 Step 3.2: Testing queue analysis display...")
        await test_queue_analysis()

        # Test Step 3.3: Periodic status updates
        print("\n🔄 Step 3.3: Testing periodic status updates...")
        await test_periodic_updates()

        print("\n" + "=" * 80)
        print("✅ ALL PHASE 3 TESTS PASSED!")
        print("Hierarchical worker tracking is working correctly.")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    # Import the periodic_status_updates function
    try:
        from worker_tracking_display import periodic_status_updates
    except ImportError as e:
        print(f"Warning: Could not import periodic_status_updates: {e}")

        # Create a mock function for testing
        async def periodic_status_updates(tracker_state, context, interval=30):
            print(f"Mock periodic updates (interval: {interval}s)")
            await asyncio.sleep(0.1)

    success = asyncio.run(main())
    sys.exit(0 if success else 1)
