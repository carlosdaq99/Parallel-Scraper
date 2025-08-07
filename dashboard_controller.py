"""
Dashboard Controller for Terminal Output Separation

This module provides the DashboardController class that manages the real-time
dashboard display independently from terminal output streams. Part of Phase 1
implementation for separating dashboard from worker tracking output.
"""

import asyncio
import logging
from typing import Optional
from real_time_monitor import RealTimeMonitor, start_real_time_monitor


class DashboardController:
    """
    Controls the dashboard display independently from terminal output.

    This controller manages the real-time dashboard as a background task,
    allowing it to be enabled/disabled via configuration without affecting
    the main terminal output stream.
    """

    def __init__(self, config):
        """
        Initialize the dashboard controller.

        Args:
            config: ScraperConfig instance containing dashboard settings
        """
        self.config = config
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.monitor_instance: Optional[RealTimeMonitor] = None
        self.logger = logging.getLogger(__name__)

    async def start_dashboard(self, context):
        """
        Start dashboard display in background if enabled.

        Args:
            context: ParallelWorkerContext instance for dashboard data
        """
        if not self.config.ENABLE_DASHBOARD:
            self.logger.info("Dashboard disabled via configuration")
            return

        if self.running:
            self.logger.warning("Dashboard already running")
            return

        try:
            self.logger.info("Starting dashboard controller")

            # Create the RealTimeMonitor instance
            self.monitor_instance = start_real_time_monitor(
                self.config.DASHBOARD_UPDATE_INTERVAL, context
            )

            # Start the dashboard task in background
            self.running = True
            self.task = asyncio.create_task(
                self.monitor_instance.run_dashboard(), name="dashboard_controller"
            )

            self.logger.info(
                f"Dashboard controller started with update interval {self.config.DASHBOARD_UPDATE_INTERVAL} seconds"
            )

        except Exception as e:
            self.logger.error(f"Failed to start dashboard: {e}")
            self.running = False
            raise

    def stop_dashboard(self):
        """Stop dashboard display and clean up background task."""
        if not self.running:
            return

        self.logger.info("Stopping dashboard controller")
        self.running = False

        if self.task and not self.task.done():
            self.task.cancel()

        # Clean up monitor instance
        if self.monitor_instance:
            self.monitor_instance.is_running = False
            self.monitor_instance = None

    async def wait_for_completion(self):
        """Wait for dashboard task to complete (useful for clean shutdown)."""
        if self.task and not self.task.done():
            try:
                await self.task
            except asyncio.CancelledError:
                # Expected when task is cancelled
                raise  # Re-raise CancelledError as required
            except Exception as e:
                self.logger.error(f"Dashboard task error during shutdown: {e}")

    def is_running(self) -> bool:
        """Check if dashboard is currently running."""
        return self.running and self.task and not self.task.done()
