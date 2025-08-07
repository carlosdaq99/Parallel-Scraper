#!/usr/bin/env python3
"""
Performance Metrics and Adaptive Scaling Test Script

This script creates a minimal version of main_self_contained.py focused exclusively on:
1. Performance data extraction
2. Adaptive scaling decisions
3. Metrics collection debugging

All worker activity output is silenced to focus only on the metrics and scaling system.
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

# Import necessary modules
try:
    from data_structures import ParallelWorkerContext
    from playwright.async_api import async_playwright
    from real_time_monitor import start_real_time_monitor
    from adaptive_scaling_engine import (
        initialize_adaptive_scaling,
        get_current_worker_count,
        set_current_worker_count,
        run_adaptive_scaling_cycle,
        make_scaling_decision_simple,
    )
    from optimization_utils import (
        create_optimized_browser,
        initialize_optimization_state,
    )
except ImportError as e:
    print(f"Failed to import required modules: {e}")
    print("Available adaptive scaling functions:")
    try:
        import adaptive_scaling_engine

        print(
            [func for func in dir(adaptive_scaling_engine) if not func.startswith("_")]
        )
    except:
        pass
    sys.exit(1)

# Configuration
START_URL = "https://example.com"  # Simple test URL
MAX_TEST_PAGES = 5
INITIAL_WORKERS = 2
METRICS_REPORT_INTERVAL = 10  # Report metrics every 10 seconds
TEST_DURATION = 60  # Run test for 60 seconds


class MetricsTestLogger:
    """Custom logger that only shows metrics and scaling information"""

    def __init__(self):
        self.start_time = time.time()

    def log_metrics(self, message: str):
        """Log metrics-related information"""
        elapsed = time.time() - self.start_time
        print(f"[{elapsed:6.1f}s] METRICS: {message}")

    def log_scaling(self, message: str):
        """Log scaling-related information"""
        elapsed = time.time() - self.start_time
        print(f"[{elapsed:6.1f}s] SCALING: {message}")

    def log_error(self, message: str):
        """Log error information"""
        elapsed = time.time() - self.start_time
        print(f"[{elapsed:6.1f}s] ERROR: {message}")


async def silent_worker(worker_id: str, context: ParallelWorkerContext, browser):
    """Simplified worker that generates performance data without detailed output"""
    try:
        # Simulate different performance characteristics
        if "slow" in worker_id:
            await asyncio.sleep(2.0)  # Slow worker
        elif "error" in worker_id:
            if time.time() % 10 < 2:  # Periodic errors
                raise Exception("Simulated error")
            await asyncio.sleep(1.0)
        else:
            await asyncio.sleep(0.5)  # Normal worker

        # Simulate task completion
        await context.mark_task_completed(worker_id, None)

    except Exception as e:
        await context.mark_task_failed(worker_id, e)


async def collect_performance_data(context: ParallelWorkerContext) -> dict:
    """Collect performance data for adaptive scaling analysis"""
    try:
        total_completed = len(context.completed_tasks)
        total_failed = len(context.failed_tasks)
        total_processed = total_completed + total_failed

        success_rate = total_completed / max(total_processed, 1)
        queue_depth = context.task_queue.qsize()
        active_worker_count = len(context.worker_manager.active_workers)

        # Calculate average processing time (simulated)
        current_time = time.time()
        avg_processing_time = (
            1.0 + (current_time % 10) * 0.5
        )  # Variable processing time

        return {
            "success_rate": success_rate,
            "avg_processing_time": avg_processing_time,
            "total_processed": total_processed,
            "total_completed": total_completed,
            "total_failed": total_failed,
            "active_workers": active_worker_count,
            "queue_depth": queue_depth,
            "timestamp": current_time,
        }

    except Exception as e:
        return {"error": str(e)}


async def main():
    """Main test function focused on metrics and scaling"""
    logger = MetricsTestLogger()

    print("=" * 80)
    print("PERFORMANCE METRICS & ADAPTIVE SCALING TEST")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Test Duration: {TEST_DURATION} seconds")
    print(f"Initial Workers: {INITIAL_WORKERS}")
    print(f"Target URL: {START_URL}")
    print()

    # Initialize systems
    logger.log_metrics("Initializing optimization state...")
    initialize_optimization_state()

    logger.log_scaling("Initializing adaptive scaling...")
    initialize_adaptive_scaling()

    # Suppress worker-related logging
    worker_logger = logging.getLogger()
    worker_logger.setLevel(logging.ERROR)  # Only show errors

    async with async_playwright() as playwright:
        try:
            logger.log_metrics("Creating optimized browser...")
            browser = await create_optimized_browser(playwright)

            if not browser:
                logger.log_error("Failed to create browser")
                return

            # Create worker context
            context = ParallelWorkerContext(
                max_workers=INITIAL_WORKERS, logger=worker_logger
            )
            logger.log_metrics(f"Created worker context with {INITIAL_WORKERS} workers")

            # Start real-time monitoring
            logger.log_metrics("Starting real-time monitoring...")
            monitor = start_real_time_monitor(
                update_interval=5,  # Faster updates for testing
                worker_context=context,
            )
            monitoring_task = asyncio.create_task(monitor.run_dashboard())

            # Start test workers
            workers = []
            worker_types = ["normal_1", "normal_2", "slow_1", "error_1"]

            for i, worker_type in enumerate(worker_types[:INITIAL_WORKERS]):
                logger.log_metrics(f"Starting worker: {worker_type}")
                worker = asyncio.create_task(
                    silent_worker(worker_type, context, browser)
                )
                workers.append(worker)

            # Main monitoring loop
            start_time = time.time()
            last_metrics_time = start_time
            last_scaling_time = start_time
            metrics_history = []

            logger.log_metrics("Starting metrics collection loop...")

            while time.time() - start_time < TEST_DURATION:
                current_time = time.time()

                # Collect and report metrics
                if current_time - last_metrics_time >= METRICS_REPORT_INTERVAL:
                    performance_data = await collect_performance_data(context)
                    metrics_history.append(performance_data)

                    if "error" not in performance_data:
                        logger.log_metrics(
                            f"Success Rate: {performance_data['success_rate']:.2%}, "
                            f"Avg Time: {performance_data['avg_processing_time']:.2f}s, "
                            f"Processed: {performance_data['total_processed']}, "
                            f"Active Workers: {performance_data['active_workers']}, "
                            f"Queue: {performance_data['queue_depth']}"
                        )
                    else:
                        logger.log_error(
                            f"Metrics collection failed: {performance_data['error']}"
                        )

                    last_metrics_time = current_time

                # Perform adaptive scaling check
                if (
                    current_time - last_scaling_time >= 15
                ):  # Check scaling every 15 seconds
                    if metrics_history:
                        latest_metrics = metrics_history[-1]
                        if "error" not in latest_metrics:
                            logger.log_scaling("Performing adaptive scaling check...")
                            old_workers = get_current_worker_count()

                            try:
                                # Use the actual scaling system
                                scaling_decision = make_scaling_decision_simple(
                                    latest_metrics
                                )
                                new_workers = scaling_decision.get(
                                    "new_worker_count", old_workers
                                )

                                if new_workers != old_workers:
                                    set_current_worker_count(new_workers)
                                    logger.log_scaling(
                                        f"Scaling decision: {old_workers} -> {new_workers} workers "
                                        f"(Success: {latest_metrics['success_rate']:.2%}, "
                                        f"Time: {latest_metrics['avg_processing_time']:.2f}s)"
                                    )
                                else:
                                    logger.log_scaling(
                                        f"No scaling needed (Workers: {old_workers}, "
                                        f"Success: {latest_metrics['success_rate']:.2%}, "
                                        f"Time: {latest_metrics['avg_processing_time']:.2f}s)"
                                    )

                            except Exception as e:
                                logger.log_error(f"Adaptive scaling failed: {e}")

                    last_scaling_time = current_time

                # Keep some workers active by restarting completed ones
                for i, worker in enumerate(workers):
                    if worker.done():
                        worker_type = worker_types[i % len(worker_types)]
                        logger.log_metrics(
                            f"Restarting completed worker: {worker_type}"
                        )
                        workers[i] = asyncio.create_task(
                            silent_worker(
                                f"{worker_type}_{int(current_time)}", context, browser
                            )
                        )

                await asyncio.sleep(1)  # Main loop interval

            # Test completed
            logger.log_metrics("Test duration completed, shutting down...")

            # Cancel monitoring
            monitoring_task.cancel()
            try:
                await monitoring_task
            except asyncio.CancelledError:
                pass

            # Cancel workers
            for worker in workers:
                if not worker.done():
                    worker.cancel()

            await asyncio.gather(*workers, return_exceptions=True)

            # Final metrics summary
            print()
            print("=" * 80)
            print("FINAL METRICS SUMMARY")
            print("=" * 80)

            if metrics_history:
                final_metrics = metrics_history[-1]
                if "error" not in final_metrics:
                    print(f"Total Metrics Collected: {len(metrics_history)}")
                    print(f"Final Success Rate: {final_metrics['success_rate']:.2%}")
                    print(
                        f"Final Processing Time: {final_metrics['avg_processing_time']:.2f}s"
                    )
                    print(f"Total Tasks Processed: {final_metrics['total_processed']}")
                    print(f"Final Worker Count: {get_current_worker_count()}")

                    # Check if metrics were successfully collected
                    if len(metrics_history) >= 3:
                        logger.log_metrics(
                            "SUCCESS: Metrics collection is working properly!"
                        )
                    else:
                        logger.log_error(
                            "WARNING: Very few metrics collected - possible collection issue"
                        )

                else:
                    logger.log_error("Final metrics collection failed")
            else:
                logger.log_error("CRITICAL: No metrics were collected during the test!")

            await browser.close()

        except Exception as e:
            logger.log_error(f"Test failed: {e}")
            import traceback

            traceback.print_exc()

    print(f"\\nTest completed at: {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(main())
