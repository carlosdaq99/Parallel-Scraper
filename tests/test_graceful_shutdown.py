#!/usr/bin/env python3
"""
Test script to demonstrate graceful shutdown functionality with progress saving.

This test shows how Ctrl+C (SIGINT) is handled gracefully with JSON progress saving.
"""

import asyncio
import signal
import time
import json
import os
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from data_structures import ParallelWorkerContext, NodeInfo


async def simulate_scraping_with_graceful_shutdown():
    """Simulate a scraping session that can be interrupted gracefully."""
    print("🚀 Starting graceful shutdown test...")
    print("   Press Ctrl+C to test graceful shutdown with progress saving")
    print("   The test will automatically stop after 30 seconds\n")

    # Create a simple logger for the test
    import logging

    logger = logging.getLogger("test_graceful_shutdown")
    logger.setLevel(logging.INFO)

    # Create a mock worker context with some test data
    worker_context = ParallelWorkerContext(max_workers=5, logger=logger)

    # Add some simulated completed tasks
    for i in range(5):
        task_id = f"test_task_{i}"
        node_info = NodeInfo(
            label=f"Test Node {i}",
            path=f"/test/path/{i}",
            depth=i + 1,
            is_leaf=(i % 2 == 0),
            subfolders=[f"subfolder_{i}_{j}" for j in range(2)],
        )
        worker_context.completed_tasks[task_id] = node_info

    # Add some simulated failed tasks
    worker_context.failed_tasks["failed_task_1"] = "Connection timeout"
    worker_context.failed_tasks["failed_task_2"] = "Page not found"

    # Set up graceful shutdown handling
    shutdown_event = asyncio.Event()

    def signal_handler():
        print("\n⚠️  Received Ctrl+C - initiating graceful shutdown...")
        shutdown_event.set()

    # Register signal handler
    if hasattr(signal, "SIGINT"):
        try:
            loop = asyncio.get_event_loop()
            loop.add_signal_handler(signal.SIGINT, signal_handler)
            print("✅ Signal handler registered")
        except (OSError, NotImplementedError):
            signal.signal(signal.SIGINT, lambda s, f: signal_handler())
            print("✅ Fallback signal handler registered")

    # Simulate ongoing work that can be interrupted
    start_time = time.time()
    max_duration = 30  # Auto-stop after 30 seconds

    try:
        while not shutdown_event.is_set():
            elapsed = time.time() - start_time

            # Add more completed tasks periodically
            if int(elapsed) % 3 == 0 and int(elapsed) > 0:
                new_task_id = f"dynamic_task_{int(elapsed)}"
                if new_task_id not in worker_context.completed_tasks:
                    node_info = NodeInfo(
                        label=f"Dynamic Node {int(elapsed)}",
                        path=f"/dynamic/path/{int(elapsed)}",
                        depth=1,
                        is_leaf=True,
                        subfolders=[],
                    )
                    worker_context.completed_tasks[new_task_id] = node_info
                    print(f"📁 Added task: {new_task_id}")

            # Auto-stop after max duration
            if elapsed > max_duration:
                print(f"\n⏰ Auto-stopping after {max_duration} seconds...")
                break

            # Show progress
            print(
                f"⚡ Working... ({elapsed:.1f}s) - {len(worker_context.completed_tasks)} completed",
                end="\r",
            )
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n⚠️  Received KeyboardInterrupt in try block")
        shutdown_event.set()

    # Save progress when shutting down
    print(f"\n💾 Saving progress...")
    await save_test_progress(worker_context)

    print(f"✅ Graceful shutdown complete!")
    print(f"   Total runtime: {time.time() - start_time:.1f}s")
    print(f"   Completed tasks: {len(worker_context.completed_tasks)}")
    print(f"   Failed tasks: {len(worker_context.failed_tasks)}")


async def save_test_progress(worker_context):
    """Save test progress to JSON file."""
    try:
        output_file = "test_graceful_shutdown_output.json"

        # Build JSON structure from completed tasks
        json_structure = {}
        for task_id, node_info in worker_context.completed_tasks.items():
            json_structure[task_id] = {
                "label": node_info.label,
                "path": node_info.path,
                "depth": node_info.depth,
                "is_leaf": node_info.is_leaf,
                "subfolders": node_info.subfolders,
                "timestamp": time.time(),
                "status": "completed",
            }

        # Add failed tasks
        failed_structure = {}
        for task_id, error_info in worker_context.failed_tasks.items():
            failed_structure[task_id] = {
                "error": str(error_info),
                "timestamp": time.time(),
                "status": "failed",
            }

        # Create final output with metadata
        final_output = {
            "metadata": {
                "generated_at": time.time(),
                "total_completed": len(json_structure),
                "total_failed": len(failed_structure),
                "interrupted": True,
                "test_mode": True,
                "scraper_version": "graceful_shutdown_test",
            },
            "completed_tasks": json_structure,
            "failed_tasks": failed_structure,
        }

        # Save to file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(final_output, f, indent=2, ensure_ascii=False)

        print(f"💾 Progress saved to: {output_file}")
        return True

    except Exception as e:
        print(f"❌ Failed to save progress: {e}")
        return False


def show_saved_results():
    """Display the saved results file if it exists."""
    output_file = "test_graceful_shutdown_output.json"
    if os.path.exists(output_file):
        print(f"\n📋 Saved results in {output_file}:")
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            print(f"   Metadata: {data['metadata']}")
            print(f"   Completed tasks: {len(data['completed_tasks'])}")
            print(f"   Failed tasks: {len(data['failed_tasks'])}")

            # Show first few completed tasks
            completed_items = list(data["completed_tasks"].items())[:3]
            for task_id, task_data in completed_items:
                print(f"     {task_id}: {task_data['label']} at {task_data['path']}")

            if len(data["completed_tasks"]) > 3:
                print(f"     ... and {len(data['completed_tasks']) - 3} more")

        except Exception as e:
            print(f"❌ Error reading saved file: {e}")
    else:
        print(f"\n❌ No saved results file found: {output_file}")


if __name__ == "__main__":
    print("=== Graceful Shutdown Test ===")
    print("This test demonstrates graceful shutdown with progress saving.")
    print("You can press Ctrl+C at any time to test the shutdown functionality.\n")

    try:
        asyncio.run(simulate_scraping_with_graceful_shutdown())
    except KeyboardInterrupt:
        print("\n⚠️  KeyboardInterrupt caught at main level")
    finally:
        show_saved_results()
        print("\n🏁 Test completed!")
