#!/usr/bin/env python3
"""
Simple Metrics and Dashboard Test Script

This script creates a minimal test to check if:
1. Performance metrics can be collected
2. Dashboard monitoring works
3. Data flows correctly from metrics to dashboard

Focus on debugging the core issue: dashboard showing placeholders instead of real data.
"""

import asyncio
import time
import logging
import sys
import os
from datetime import datetime

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import only essential modules
try:
    from data_structures import ParallelWorkerContext
    from real_time_monitor import start_real_time_monitor
    from adaptive_scaling_engine import (
        get_current_worker_count,
        set_current_worker_count,
    )
except ImportError as e:
    print(f"Failed to import required modules: {e}")
    sys.exit(1)

# Test configuration
TEST_DURATION = 30  # 30 second test
METRICS_INTERVAL = 5  # Report every 5 seconds


async def simulate_worker_activity(context: ParallelWorkerContext, worker_id: str):
    """Simulate worker activity with realistic performance data"""
    try:
        # Simulate work being done
        await asyncio.sleep(1.0)

        # Mark as completed
        await context.mark_task_completed(
            worker_id, f"https://example.com/page_{worker_id}"
        )

    except Exception as e:
        await context.mark_task_failed(worker_id, e)


async def collect_test_metrics(context: ParallelWorkerContext) -> dict:
    """Collect metrics to test if data extraction works"""
    try:
        # Basic metrics collection
        total_completed = len(context.completed_tasks)
        total_failed = len(context.failed_tasks)
        total_processed = total_completed + total_failed
        active_workers = len(context.worker_manager.active_workers)
        queue_size = context.task_queue.qsize()

        return {
            "timestamp": time.time(),
            "total_completed": total_completed,
            "total_failed": total_failed,
            "total_processed": total_processed,
            "active_workers": active_workers,
            "queue_size": queue_size,
            "success_rate": total_completed / max(total_processed, 1),
        }

    except Exception as e:
        return {"error": str(e)}


async def main():
    """Main test function to check metrics and dashboard"""

    print("=" * 60)
    print("METRICS & DASHBOARD TEST")
    print("=" * 60)
    print(f"Start Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Test Duration: {TEST_DURATION} seconds")
    print()

    # Suppress worker logging for clarity
    logger = logging.getLogger()
    logger.setLevel(logging.ERROR)

    try:
        # Create worker context
        context = ParallelWorkerContext(max_workers=2, logger=logger)
        print(f"[OK] Created worker context")

        # Start real-time monitoring
        print("[TEST] Starting real-time monitoring...")
        monitor = start_real_time_monitor(
            update_interval=3,  # Fast updates for testing
            worker_context=context,
        )

        if monitor is None:
            print("[ERROR] Failed to start monitor")
            return

        print(f"[OK] Monitor created: {type(monitor).__name__}")

        # Start the dashboard
        print("[TEST] Starting dashboard...")
        monitoring_task = asyncio.create_task(monitor.run_dashboard())

        # Initial metrics check
        initial_metrics = await collect_test_metrics(context)
        if "error" in initial_metrics:
            print(
                f"[ERROR] Initial metrics collection failed: {initial_metrics['error']}"
            )
            return
        else:
            print(f"[OK] Initial metrics collected: {initial_metrics}")

        # Add some test URLs to the queue
        test_urls = [
            "https://example.com/1",
            "https://example.com/2",
            "https://example.com/3",
        ]

        for url in test_urls:
            await context.task_queue.put(url)
        print(f"[OK] Added {len(test_urls)} test URLs to queue")

        # Start some simulated workers
        workers = []
        for i in range(2):
            worker = asyncio.create_task(
                simulate_worker_activity(context, f"test_worker_{i}")
            )
            workers.append(worker)
        print(f"[OK] Started {len(workers)} test workers")

        # Monitor metrics collection for test duration
        start_time = time.time()
        last_metrics_time = start_time
        metrics_collected = []

        print(f"[TEST] Monitoring metrics collection for {TEST_DURATION} seconds...")

        while time.time() - start_time < TEST_DURATION:
            current_time = time.time()

            # Collect metrics periodically
            if current_time - last_metrics_time >= METRICS_INTERVAL:
                metrics = await collect_test_metrics(context)
                metrics_collected.append(metrics)

                if "error" in metrics:
                    print(f"[ERROR] Metrics collection failed: {metrics['error']}")
                else:
                    print(
                        f"[METRICS] Completed: {metrics['total_completed']}, "
                        f"Failed: {metrics['total_failed']}, "
                        f"Active: {metrics['active_workers']}, "
                        f"Queue: {metrics['queue_size']}"
                    )

                last_metrics_time = current_time

            # Keep some workers running
            for i, worker in enumerate(workers):
                if worker.done():
                    workers[i] = asyncio.create_task(
                        simulate_worker_activity(
                            context, f"test_worker_{i}_{int(current_time)}"
                        )
                    )

            await asyncio.sleep(1)

        print(f"\\n[TEST] Test duration completed")

        # Stop monitoring
        print("[TEST] Stopping dashboard...")
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass

        # Stop workers
        for worker in workers:
            if not worker.done():
                worker.cancel()
        await asyncio.gather(*workers, return_exceptions=True)

        # Final analysis
        print("\\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)

        if metrics_collected:
            print(f"Total metrics samples collected: {len(metrics_collected)}")

            # Check if metrics changed over time (indicating data flow)
            if len(metrics_collected) >= 2:
                first = metrics_collected[0]
                last = metrics_collected[-1]

                if "error" not in first and "error" not in last:
                    completed_change = (
                        last["total_completed"] - first["total_completed"]
                    )
                    processed_change = (
                        last["total_processed"] - first["total_processed"]
                    )

                    print(f"Tasks completed during test: {completed_change}")
                    print(f"Tasks processed during test: {processed_change}")

                    if completed_change > 0:
                        print("[SUCCESS] ✓ Performance data is being collected!")
                        print("[SUCCESS] ✓ Metrics system is working!")
                    else:
                        print(
                            "[WARNING] No task completion detected - workers may not be running"
                        )

                    # Check if dashboard should have data
                    print(f"\\nDashboard should show:")
                    print(f"  - Success rate: {last['success_rate']:.1%}")
                    print(f"  - Total processed: {last['total_processed']}")
                    print(f"  - Active workers: {last['active_workers']}")

                else:
                    print("[ERROR] Metrics contained errors")
            else:
                print("[ERROR] Not enough metrics samples collected")
        else:
            print("[CRITICAL] No metrics were collected at all!")

        print(
            f"\\nCurrent worker count from scaling engine: {get_current_worker_count()}"
        )

    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback

        traceback.print_exc()

    print(f"\\nTest completed at: {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
