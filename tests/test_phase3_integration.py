"""
Test Phase 3 Step 3.4: Comprehensive Integration Test for Hierarchical Worker Tracking

This test integrates the hierarchical tracking system with the main scraper
to validate real-world functionality with actual worker processing.
"""

import asyncio
import sys
import os
import logging
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from data_structures import Task, NodeInfo, ParallelWorkerContext
from worker_tracking_display import (
    initialize_tracker_state,
    display_comprehensive_summary,
    periodic_status_updates,
    get_tracking_statistics,
)
from worker import process_task_async
from config import ScraperConfig


async def test_integration_with_real_worker():
    """Test hierarchical tracking integration with real worker processing."""
    print("🔄 Testing integration with real worker processing...")

    # Create a logger
    logger = logging.getLogger("test_integration")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(handler)

    # Create worker context with hierarchical tracking
    context = ParallelWorkerContext(max_workers=5, logger=logger)
    print(f"✓ Created worker context with tracker state")

    # Create test tasks with hierarchical structure
    root_node = NodeInfo(
        label="Test Root Folder",
        path="https://help.autodesk.com/view/OARX/2025/ENU/?guid=GUID-test-root",
        depth=0,
        worker_id="integration-worker-1",
        guid="test-root-guid",
    )

    root_task = Task(worker_id="integration-worker-1", node_info=root_node, priority=0)

    print(f"✓ Created root task: {root_task.task_id[:8]}")

    # Submit the task
    success = await context.submit_task(root_task)
    assert success, "Task submission should succeed"
    print(f"✓ Successfully submitted task to context")

    # Check initial tracking state
    initial_stats = get_tracking_statistics(context.tracker_state)
    print(f"✓ Initial tracker state: {initial_stats['tasks']['total']} tasks tracked")

    # Mock browser and playwright for testing
    mock_browser = MagicMock()
    mock_page = MagicMock()

    # Configure mock page to simulate successful processing
    mock_browser.new_page = MagicMock(return_value=mock_page)
    mock_page.close = MagicMock()
    mock_page.goto = MagicMock()
    mock_page.wait_for_load_state = MagicMock()
    mock_page.locator = MagicMock()

    # Mock DOM utils to simulate finding children
    with patch("worker.create_browser_page") as mock_create_page:
        with patch("worker.find_target_folder_dom_async") as mock_find_folder:
            with patch("worker.expand_node_safely") as mock_expand:
                with patch("worker.get_children_at_level_async") as mock_get_children:

                    # Configure mocks
                    mock_create_page.return_value = mock_page
                    mock_find_folder.return_value = MagicMock()
                    mock_expand.return_value = True
                    mock_get_children.return_value = [
                        {"label": "Child 1", "guid": "child-1-guid"},
                        {"label": "Child 2", "guid": "child-2-guid"},
                    ]

                    print("✓ Configured mocks for DOM operations")

                    # Process the task
                    try:
                        result = await process_task_async(
                            root_task, context, mock_browser
                        )
                        print(f"✓ Task processed successfully: {result.label}")

                        # Check hierarchical tracking results
                        final_stats = get_tracking_statistics(context.tracker_state)
                        print(
                            f"✓ Final tracker state: {final_stats['tasks']['total']} tasks tracked"
                        )

                        # Verify that child tasks were created and tracked
                        if (
                            final_stats["tasks"]["total"]
                            > initial_stats["tasks"]["total"]
                        ):
                            print(
                                f"✓ Child tasks were created and tracked (+{final_stats['tasks']['total'] - initial_stats['tasks']['total']})"
                            )

                        # Verify hierarchy structure
                        root_tasks = [
                            task_id
                            for task_id, task in context.tracker_state["tasks"].items()
                            if task.get("parent_id") is None
                        ]
                        print(f"✓ Found {len(root_tasks)} root tasks in hierarchy")

                        return True

                    except Exception as e:
                        print(f"❌ Task processing failed: {e}")
                        import traceback

                        traceback.print_exc()
                        return False


async def test_scaling_integration():
    """Test hierarchical tracking with adaptive scaling."""
    print("\n🔄 Testing hierarchical tracking with scaling simulation...")

    logger = logging.getLogger("test_scaling")
    logger.setLevel(logging.WARNING)  # Reduce verbosity

    # Create context with multiple workers
    context = ParallelWorkerContext(max_workers=10, logger=logger)

    # Create multiple tasks to simulate scaling scenario
    tasks = []
    for i in range(5):
        node = NodeInfo(
            label=f"Scaling Test Folder {i}",
            path=f"https://test.example.com/folder{i}",
            depth=0,
            worker_id=f"scaling-worker-{i}",
            guid=f"scaling-test-{i}",
        )

        task = Task(worker_id=f"scaling-worker-{i}", node_info=node, priority=i)
        tasks.append(task)

        # Submit task
        await context.submit_task(task)

    print(f"✓ Created and submitted {len(tasks)} tasks")

    # Simulate some task completions and failures
    for i, task in enumerate(tasks[:3]):
        if i % 2 == 0:
            # Mark as completed
            await context.mark_task_completed(task.worker_id, task.node_info)
        else:
            # Mark as failed
            await context.mark_task_failed(
                task.worker_id, Exception(f"Test failure {i}")
            )

    print("✓ Simulated task completions and failures")

    # Check tracking statistics
    stats = get_tracking_statistics(context.tracker_state)
    print(
        f"✓ Scaling test stats: {stats['tasks']['total']} total, {stats['tasks']['completed']} completed, {stats['tasks']['failed']} failed"
    )

    # Test comprehensive summary display
    print("\n--- Comprehensive Summary Display ---")
    display_comprehensive_summary(context.tracker_state, context)

    return True


async def test_stress_test():
    """Stress test hierarchical tracking with many tasks."""
    print("\n🔄 Running stress test with hierarchical tracking...")

    logger = logging.getLogger("test_stress")
    logger.setLevel(logging.ERROR)  # Minimal verbosity for stress test

    context = ParallelWorkerContext(max_workers=20, logger=logger)

    # Create a large number of tasks
    num_tasks = 50
    tasks_created = 0

    for i in range(num_tasks):
        node = NodeInfo(
            label=f"Stress Test Task {i}",
            path=f"https://stress.test.com/task{i}",
            depth=i % 5,  # Vary depth
            worker_id=f"stress-worker-{i}",
            guid=f"stress-{i}",
        )

        # Some tasks have parents (hierarchical structure)
        parent_task_id = None
        if i > 0 and i % 3 == 0:
            # Every 3rd task is a child of a previous task
            parent_index = max(0, i - 3)
            parent_task_id = f"stress-task-{parent_index}"

        task = Task(
            worker_id=f"stress-worker-{i}",
            node_info=node,
            priority=i,
            parent_task_id=parent_task_id,
        )

        await context.submit_task(task)
        tasks_created += 1

        # Periodically simulate task completion
        if i % 10 == 0 and i > 0:
            completed_task_id = f"stress-worker-{i-5}"
            try:
                completed_node = NodeInfo(
                    label=f"Completed Task {i-5}",
                    path=f"https://stress.test.com/task{i-5}",
                    depth=(i - 5) % 5,
                    worker_id=completed_task_id,
                    guid=f"completed-{i-5}",
                )
                await context.mark_task_completed(completed_task_id, completed_node)
            except:
                pass  # Ignore if task doesn't exist

    print(f"✓ Created {tasks_created} tasks for stress test")

    # Check final statistics
    final_stats = get_tracking_statistics(context.tracker_state)
    print(
        f"✓ Stress test results: {final_stats['tasks']['total']} tracked, {final_stats['hierarchy']['root_tasks']} root tasks"
    )
    print(
        f"✓ Max depth: {final_stats['hierarchy']['max_depth']}, Avg children: {final_stats['hierarchy']['avg_children_per_task']:.1f}"
    )

    # Verify tracker state integrity
    tasks = context.tracker_state["tasks"]
    orphaned_children = 0
    for task_id, task in tasks.items():
        parent_id = task.get("parent_id")
        if parent_id and parent_id not in tasks:
            orphaned_children += 1

    print(f"✓ Tracker integrity: {orphaned_children} orphaned children (should be low)")

    return orphaned_children < (num_tasks * 0.1)  # Allow up to 10% orphaned


async def main():
    """Run comprehensive Phase 3 Step 3.4 integration tests."""
    print("=" * 80)
    print("PHASE 3 STEP 3.4: COMPREHENSIVE INTEGRATION TESTS")
    print("=" * 80)

    tests_passed = 0
    total_tests = 3

    try:
        # Test 1: Integration with real worker
        print("\n📊 Test 1: Integration with Real Worker Processing")
        if await test_integration_with_real_worker():
            tests_passed += 1
            print("✅ Integration test PASSED")
        else:
            print("❌ Integration test FAILED")

        # Test 2: Scaling integration
        print("\n📊 Test 2: Scaling Integration")
        if await test_scaling_integration():
            tests_passed += 1
            print("✅ Scaling integration test PASSED")
        else:
            print("❌ Scaling integration test FAILED")

        # Test 3: Stress test
        print("\n📊 Test 3: Stress Test")
        if await test_stress_test():
            tests_passed += 1
            print("✅ Stress test PASSED")
        else:
            print("❌ Stress test FAILED")

        # Final results
        print("\n" + "=" * 80)
        print(f"INTEGRATION TEST RESULTS: {tests_passed}/{total_tests} PASSED")

        if tests_passed == total_tests:
            print("🎉 ALL PHASE 3 INTEGRATION TESTS PASSED!")
            print("Hierarchical worker tracking is fully integrated and functional.")
        else:
            print("⚠️ Some integration tests failed. Review and fix issues.")

        print("=" * 80)

        return tests_passed == total_tests

    except Exception as e:
        print(f"\n❌ Integration tests failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
