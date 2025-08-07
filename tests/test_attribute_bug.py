#!/usr/bin/env python3
"""
Test script to verify the attribute access bug in the monitoring system.
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from data_structures import ParallelWorkerContext
import logging


def test_attribute_access():
    """Test attribute access to confirm the bug"""
    print("=== ATTRIBUTE ACCESS TEST ===")

    logger = logging.getLogger("test")
    context = ParallelWorkerContext(4, logger)

    print(f"context.active_tasks exists: {hasattr(context, 'active_tasks')}")
    print(f"context.active_workers exists: {hasattr(context, 'active_workers')}")
    print(f"context.worker_manager exists: {hasattr(context, 'worker_manager')}")

    if hasattr(context, "worker_manager"):
        print(
            f"context.worker_manager.active_workers exists: {hasattr(context.worker_manager, 'active_workers')}"
        )
        print(
            f"context.worker_manager.get_active_count exists: {hasattr(context.worker_manager, 'get_active_count')}"
        )

    print("\n=== SIMULATING MONITOR ACCESS ===")
    try:
        # This is what the monitor tries to do (will fail)
        active_worker_count = len(context.active_workers)
        print(f"SUCCESS: len(context.active_workers) = {active_worker_count}")
    except AttributeError as e:
        print(f"ERROR: len(context.active_workers) failed: {e}")

    try:
        # This is what it should do (will work)
        active_worker_count = await context.worker_manager.get_active_count()
        print(
            f"SUCCESS: await context.worker_manager.get_active_count() = {active_worker_count}"
        )
    except Exception as e:
        print(
            f"NOTE: await context.worker_manager.get_active_count() needs async context: {e}"
        )

    try:
        # Alternative: direct access to worker_manager.active_workers
        active_worker_count = len(context.worker_manager.active_workers)
        print(
            f"SUCCESS: len(context.worker_manager.active_workers) = {active_worker_count}"
        )
    except Exception as e:
        print(f"ERROR: len(context.worker_manager.active_workers) failed: {e}")


if __name__ == "__main__":
    test_attribute_access()
