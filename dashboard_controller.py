"""
Dashboard Controller for Terminal Output Separation

This module provides function-based dashboard control that manages the real-time
dashboard display independently from terminal output streams. Part of Phase 1
implementation for separating dashboard from worker tracking output.

Follows the project's function-based design pattern for simplicity and async compatibility.
"""

import asyncio
import logging
from typing import Optional
from real_time_monitor import RealTimeMonitor, start_real_time_monitor


# Global state for dashboard management
_dashboard_task: Optional[asyncio.Task] = None
_dashboard_monitor: Optional[RealTimeMonitor] = None
_dashboard_running = False
_logger = logging.getLogger(__name__)


async def start_dashboard(config, context):
    """
    Start dashboard display in background if enabled.

    Args:
        config: ScraperConfig instance containing dashboard settings
        context: ParallelWorkerContext instance for dashboard data

    Returns:
        bool: True if dashboard started, False if disabled/already running
    """
    global _dashboard_task, _dashboard_monitor, _dashboard_running

    if not config.ENABLE_DASHBOARD:
        _logger.info("Dashboard disabled via configuration")
        return False

    if _dashboard_running:
        _logger.warning("Dashboard already running")
        return False

    try:
        _logger.info("Starting dashboard controller")

        # Create the RealTimeMonitor instance
        _dashboard_monitor = start_real_time_monitor(
            config.REAL_TIME_MONITOR_INTERVAL, context
        )

        # Start the dashboard task in background
        _dashboard_running = True
        _dashboard_task = asyncio.create_task(
            _dashboard_monitor.run_dashboard(), name="dashboard_controller"
        )

        _logger.info(
            f"Dashboard controller started with update interval {config.REAL_TIME_MONITOR_INTERVAL} seconds"
        )
        return True

    except Exception as e:
        _logger.error(f"Failed to start dashboard: {e}")
        _dashboard_running = False
        raise


def stop_dashboard():
    """Stop dashboard display and clean up background task."""
    global _dashboard_task, _dashboard_monitor, _dashboard_running

    if not _dashboard_running:
        return

    _logger.info("Stopping dashboard controller")
    _dashboard_running = False

    if _dashboard_task and not _dashboard_task.done():
        _dashboard_task.cancel()

    # Clean up monitor instance
    if _dashboard_monitor:
        _dashboard_monitor.is_running = False
        _dashboard_monitor = None


async def wait_for_dashboard_completion():
    """Wait for dashboard task to complete (useful for clean shutdown)."""
    global _dashboard_task

    if _dashboard_task and not _dashboard_task.done():
        try:
            await _dashboard_task
        except asyncio.CancelledError:
            # Expected when task is cancelled
            raise  # Re-raise CancelledError as required
        except Exception as e:
            _logger.error(f"Dashboard task error during shutdown: {e}")


def is_dashboard_running() -> bool:
    """Check if dashboard is currently running."""
    global _dashboard_task, _dashboard_running
    return _dashboard_running and _dashboard_task and not _dashboard_task.done()


def get_dashboard_status() -> dict:
    """Get current dashboard status information."""
    global _dashboard_task, _dashboard_monitor, _dashboard_running

    return {
        "running": _dashboard_running,
        "task_exists": _dashboard_task is not None,
        "task_done": _dashboard_task.done() if _dashboard_task else True,
        "monitor_exists": _dashboard_monitor is not None,
    }
