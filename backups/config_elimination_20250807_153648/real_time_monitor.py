#!/usr/bin/env python3
"""
Real-Time Monitoring Dashboard for Parallel Scraper

Displays adaptive scaling system metrics in the terminal with real-time updates
during scraping operations. Shows system health, performance, and scaling decisions.
"""

import time
import asyncio
import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass
from contextlib import contextmanager

try:
    from config import ScraperConfig
except ImportError:
    # Fallback for standalone execution
    class ScraperConfig:
        DASHBOARD_UPDATE_INTERVAL = 10.0  # Match config.py value
        DASHBOARD_DEMO_INTERVAL = 5.0
        TERMINAL_OUTPUT_SUPPRESSION = 0.5
        TREND_ANALYSIS_MIN_SAMPLES = 2
        TREND_ANALYSIS_HISTORY_SIZE = 10


# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from resource_monitor import get_system_resources
    from auto_tuning_engine import (
        get_tuned_parameters,
        get_auto_tuning_engine,
        initialize_auto_tuning,
    )
    from enhanced_config_manager import get_dynamic_config

    ADAPTIVE_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Note: Some adaptive modules not available: {e}")
    ADAPTIVE_MODULES_AVAILABLE = False


@dataclass
class DashboardMetrics:
    """Holds all metrics for dashboard display with availability tracking"""

    timestamp: str

    # Performance metrics (with availability flags)
    success_rate: Optional[float] = None
    avg_processing_time: Optional[float] = None
    total_processed: Optional[int] = None
    errors_count: Optional[int] = None

    # Worker metrics
    active_workers: Optional[int] = None
    queue_length: Optional[int] = None
    browser_pool_size: Optional[int] = None
    browser_pool_status: Optional[str] = None  # Status info for browser pool

    # System metrics
    cpu_usage: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    memory_usage_percent: Optional[float] = None

    # Scaling decision metrics (NEW - all factors used in scaling decisions)
    pages_per_second: Optional[float] = None
    worker_utilization: Optional[float] = None
    resource_capacity: Optional[float] = None
    performance_score: Optional[float] = None
    queue_to_worker_ratio: Optional[float] = None
    browser_pool_recommendation: Optional[int] = None

    # Trend analysis metrics
    success_rate_trend: Optional[str] = None
    response_time_trend: Optional[str] = None
    resource_trend: Optional[str] = None
    scaling_recommendation: Optional[str] = None
    trend_cpu_direction: Optional[str] = None
    trend_memory_direction: Optional[str] = None

    # Adaptive scaling metrics
    scaling_status: Optional[str] = None
    auto_tuning_active: bool = False
    last_scaling_action: Optional[str] = None
    pattern_detected: Optional[str] = None
    config_updates: Optional[int] = None

    # Availability flags
    has_performance_data: bool = False
    has_system_data: bool = False
    has_worker_data: bool = False
    has_adaptive_data: bool = False


class RealTimeMonitor:
    """Real-time terminal dashboard for adaptive scaling system"""

    def __init__(self, update_interval: int = None, worker_context=None):
        """Initialize the real-time monitor

        Args:
            update_interval: Update interval in seconds (default 10)
            worker_context: Active worker context for real metrics collection
        """
        self.update_interval = (
            update_interval or ScraperConfig.DASHBOARD_UPDATE_INTERVAL
        )
        self.worker_context = worker_context
        self.is_running = False
        self.start_time = time.time()
        self.total_updates = 0
        self.last_metrics = None

        # Dashboard configuration
        self.dashboard_width = 80
        self.use_colors = True

        # Performance tracking
        self.performance_history = []
        self.max_history = 20  # Keep last 20 data points

    def _clear_screen(self):
        """Clear terminal screen using ANSI escape codes"""
        # \033[H moves cursor to top-left. \033[J clears from cursor to end of screen.
        print("\033[H\033[J", end="")

    @contextmanager
    def _suppress_logging(self):
        """Temporarily suppress all logging output to prevent interference with dashboard display"""
        # Get the root logger
        root_logger = logging.getLogger()
        original_level = root_logger.level

        # Store original handlers and their levels
        original_handlers = []
        for handler in root_logger.handlers:
            original_handlers.append((handler, handler.level))
            # Temporarily set handler level to CRITICAL to suppress INFO/DEBUG logs
            handler.setLevel(logging.CRITICAL)

        try:
            yield
        finally:
            # Restore original handler levels
            for handler, level in original_handlers:
                handler.setLevel(level)

    def _get_color_code(self, color: str) -> str:
        """Get ANSI color code if colors are enabled"""
        if not self.use_colors:
            return ""

        colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "yellow": "\033[93m",
            "blue": "\033[94m",
            "magenta": "\033[95m",
            "cyan": "\033[96m",
            "white": "\033[97m",
            "reset": "\033[0m",
            "bold": "\033[1m",
        }
        return colors.get(color, "")

    def _format_value(self, value: Any, value_type: str = "default") -> str:
        """Format values with appropriate colors and formatting"""
        reset = self._get_color_code("reset")

        if value_type == "success_rate":
            if value >= 0.95:
                color = self._get_color_code("green")
            elif value >= 0.85:
                color = self._get_color_code("yellow")
            else:
                color = self._get_color_code("red")
            return f"{color}{value:.1%}{reset}"

        elif value_type == "cpu_usage":
            if value <= 50:
                color = self._get_color_code("green")
            elif value <= 80:
                color = self._get_color_code("yellow")
            else:
                color = self._get_color_code("red")
            return f"{color}{value:.1f}%{reset}"

        elif value_type == "memory":
            if value <= 500:
                color = self._get_color_code("green")
            elif value <= 800:
                color = self._get_color_code("yellow")
            else:
                color = self._get_color_code("red")
            return f"{color}{value:.0f}MB{reset}"

        elif value_type == "memory_percent":
            if value <= 60:
                color = self._get_color_code("green")
            elif value <= 80:
                color = self._get_color_code("yellow")
            else:
                color = self._get_color_code("red")
            return f"{color}{value:.1f}%{reset}"

        elif value_type == "processing_time":
            if value <= 2.0:
                color = self._get_color_code("green")
            elif value <= 5.0:
                color = self._get_color_code("yellow")
            else:
                color = self._get_color_code("red")
            return f"{color}{value:.2f}s{reset}"

        elif value_type == "status":
            if "scaling up" in str(value).lower():
                color = self._get_color_code("green")
            elif "scaling down" in str(value).lower():
                color = self._get_color_code("yellow")
            elif "stable" in str(value).lower():
                color = self._get_color_code("blue")
            else:
                color = self._get_color_code("white")
            return f"{color}{value}{reset}"

        elif value_type == "pattern":
            if "peak_load" in str(value).lower():
                color = self._get_color_code("red")
            elif "low_activity" in str(value).lower():
                color = self._get_color_code("blue")
            elif "high_performance" in str(value).lower():
                color = self._get_color_code("green")
            else:
                color = self._get_color_code("cyan")
            return f"{color}{value}{reset}"

        else:
            return str(value)

    async def _trigger_browser_pool_scaling(
        self, current_size: int, recommended_size: int
    ):
        """Trigger browser pool scaling if there's a significant difference"""
        try:
            if recommended_size > current_size:
                # Import here to avoid circular imports
                from optimization_utils import scale_browser_pool_to_target
                from playwright.async_api import async_playwright

                async with async_playwright() as p:
                    await scale_browser_pool_to_target(p, recommended_size)

        except Exception as e:
            print(f"Failed to trigger browser pool scaling: {e}")

    def _collect_current_metrics(self) -> DashboardMetrics:
        """Collect current system metrics for dashboard display using UNIFIED METRICS"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        # Initialize metrics with None values
        metrics = DashboardMetrics(timestamp=timestamp)

        try:
            # Try to use unified metrics system for consistent data
            try:
                from unified_metrics import get_metrics_for_dashboard

                unified_data = get_metrics_for_dashboard(self.worker_context)
                print(
                    f"🔧 Dashboard using UNIFIED metrics: worker_util={unified_data.get('worker_utilization', 'N/A')}%, queue={unified_data.get('queue_length', 'N/A')}"
                )

                # Map unified data to dashboard metrics
                metrics.success_rate = unified_data.get("success_rate")
                metrics.avg_processing_time = unified_data.get("avg_processing_time")
                metrics.total_processed = unified_data.get("total_processed")
                metrics.errors_count = unified_data.get("total_failed")
                metrics.active_workers = unified_data.get("active_workers")
                metrics.queue_length = unified_data.get("queue_length")
                metrics.browser_pool_size = unified_data.get("browser_pool_size")
                metrics.browser_pool_status = unified_data.get(
                    "browser_pool_status", "Unknown"
                )
                metrics.pages_per_second = unified_data.get("pages_per_second")
                metrics.worker_utilization = unified_data.get(
                    "worker_utilization"
                )  # Already in percentage
                metrics.queue_to_worker_ratio = unified_data.get(
                    "queue_to_worker_ratio"
                )
                metrics.resource_capacity = unified_data.get("resource_capacity")
                metrics.performance_score = unified_data.get("performance_score")
                metrics.browser_pool_recommendation = unified_data.get(
                    "browser_pool_recommendation"
                )
                metrics.cpu_usage = unified_data.get("cpu_usage_percent")
                metrics.memory_usage_mb = unified_data.get("memory_usage_mb")
                metrics.memory_usage_percent = unified_data.get("memory_usage_percent")

                # Map adaptive scaling fields (FIX: Data Mapping Disconnect)
                metrics.scaling_status = unified_data.get("scaling_status")
                metrics.auto_tuning_active = unified_data.get(
                    "auto_tuning_active", False
                )
                metrics.last_scaling_action = unified_data.get("last_scaling_action")
                metrics.pattern_detected = unified_data.get("pattern_detected")
                metrics.config_updates = unified_data.get("config_updates", 0)

                # Mark as having adaptive data if data is available
                if unified_data.get("has_adaptive_data", False):
                    metrics.has_adaptive_data = True

                # Mark as having data
                if metrics.total_processed and metrics.total_processed > 0:
                    metrics.has_performance_data = True
                if metrics.active_workers is not None:
                    metrics.has_worker_data = True
                if metrics.cpu_usage is not None:
                    metrics.has_system_data = True

                # FIXED: Add adaptive modules logic BEFORE the return statement
                # Advanced adaptive modules (only if available)
                if ADAPTIVE_MODULES_AVAILABLE:
                    # Try to get auto-tuning status
                    try:
                        engine = get_auto_tuning_engine()
                        # If engine doesn't exist, try to initialize it
                        if engine is None:
                            engine = initialize_auto_tuning()

                        if engine:
                            metrics.auto_tuning_active = True
                            # Get recent patterns if available (corrected attribute name)
                            if (
                                hasattr(engine, "patterns_detected")
                                and engine.patterns_detected
                            ):
                                # patterns_detected is a dict, get the latest pattern type
                                pattern_types = list(engine.patterns_detected.keys())
                                if pattern_types:
                                    metrics.pattern_detected = pattern_types[-1]

                            # Get recent actions from pattern_history if available
                            if (
                                hasattr(engine, "pattern_history")
                                and engine.pattern_history
                            ):
                                last_pattern = engine.pattern_history[-1]
                                if hasattr(last_pattern, "pattern_type"):
                                    metrics.last_scaling_action = (
                                        last_pattern.pattern_type[:30]
                                    )

                            # Mark that we have adaptive data since auto-tuning engine is active
                            metrics.has_adaptive_data = True
                    except Exception as e:
                        # Log auto-tuning detection errors if needed for debugging
                        pass

                    # Try to get configuration status
                    try:
                        config = get_dynamic_config()
                        if config and hasattr(config, "update_count"):
                            metrics.config_updates = config.update_count
                            metrics.has_adaptive_data = True
                    except Exception as e:
                        # Log dynamic config detection errors if needed for debugging
                        pass

                return metrics

            except ImportError:
                print("🔧 Dashboard falling back to legacy metrics collection")
                pass
            # Always try to collect basic metrics from worker context (no adaptive modules needed)
            if self.worker_context:
                # Get actual metrics from running workers
                total_completed = len(self.worker_context.completed_tasks)
                total_failed = len(self.worker_context.failed_tasks)
                total_processed = total_completed + total_failed
                busy_workers = len(
                    self.worker_context.worker_manager.active_workers
                )  # Currently busy workers
                total_worker_pool_size = (
                    self.worker_context.max_workers
                )  # Total pool size available
                queue_depth = self.worker_context.task_queue.qsize()

                # Calculate success rate
                if total_processed > 0:
                    metrics.success_rate = total_completed / total_processed
                else:
                    metrics.success_rate = 0.0  # Show 0% instead of None

                # Set available metrics - show TOTAL workers count for real-time tracking
                metrics.total_processed = total_processed
                metrics.errors_count = total_failed

                # Get the actual current worker pool size from adaptive scaling system
                try:
                    from main_self_contained import get_current_workers

                    metrics.active_workers = (
                        get_current_workers()
                    )  # Show total worker pool size
                except ImportError:
                    # Fall back to busy workers if adaptive scaling not available
                    metrics.active_workers = (
                        busy_workers  # Show actually busy workers count
                    )

                metrics.queue_length = queue_depth

                # Basic processing metrics - calculate proper averages
                if total_processed > 0 and hasattr(self, "start_time"):
                    elapsed_time = time.time() - self.start_time
                    if elapsed_time > 0:
                        # Calculate pages per second rate
                        metrics.pages_per_second = total_processed / elapsed_time

                        # Estimate average processing time from throughput
                        if busy_workers > 0:
                            # Estimate: processing_time = workers / throughput
                            estimated_avg_time = busy_workers / (
                                total_processed / elapsed_time
                            )
                            metrics.avg_processing_time = min(
                                10.0, max(0.5, estimated_avg_time)
                            )  # Cap between 0.5-10 seconds
                else:
                    metrics.avg_processing_time = None

                # Try to get browser pool size from optimization_utils
                # Scale browser pool with worker count for efficiency
                current_pool_size = 0  # Default value

                # For 6-browser pool: recommend full capacity when >=85 workers (85/17 = 5 browsers minimum)
                if total_worker_pool_size >= 85:
                    optimal_browsers = 6  # Use full configured capacity
                else:
                    optimal_browsers = min(6, max(1, total_worker_pool_size // 17))

                try:
                    from optimization_utils import _browser_pool, OptimizationConfig

                    current_pool_size = len(_browser_pool)
                    # Use consistent recommendation logic with configured pool size
                    if total_worker_pool_size >= 85:
                        optimal_browsers = (
                            OptimizationConfig.BROWSER_POOL_SIZE
                        )  # Use full configured capacity
                    else:
                        optimal_browsers = min(
                            OptimizationConfig.BROWSER_POOL_SIZE,
                            max(1, total_worker_pool_size // 17),
                        )  # ~17 workers per browser

                    # Store browser scaling recommendation
                    if current_pool_size < optimal_browsers:
                        optimal_browsers = max(
                            1, min(6, (total_worker_pool_size + 16) // 17)
                        )
                        metrics.scaling_recommendation = (
                            f"Suggest {optimal_browsers} browsers for "
                            f"{total_worker_pool_size} workers"
                        )

                except (ImportError, NameError, AttributeError) as e:
                    # Fallback: estimate browser pool size based on worker count
                    current_pool_size = max(1, total_worker_pool_size // 17)

                metrics.browser_pool_size = current_pool_size
                metrics.browser_pool_recommendation = optimal_browsers

                # Calculate scaling decision metrics
                if total_worker_pool_size > 0 and queue_depth is not None:
                    metrics.worker_utilization = min(
                        100.0, (busy_workers / total_worker_pool_size)
                    )
                    metrics.queue_to_worker_ratio = queue_depth / total_worker_pool_size

                    # Estimate pages per second based on recent activity
                    if total_processed > 0 and hasattr(self, "start_time"):
                        elapsed_time = time.time() - self.start_time
                        if elapsed_time > 0:
                            metrics.pages_per_second = total_processed / elapsed_time

                # Calculate performance score (used in scaling decisions)
                if metrics.success_rate is not None:
                    base_score = metrics.success_rate
                    if (
                        metrics.avg_processing_time is not None
                        and metrics.avg_processing_time > 0
                    ):
                        # Lower processing time = higher score
                        time_factor = min(1.0, 2.0 / metrics.avg_processing_time)
                        metrics.performance_score = (base_score + time_factor) / 2.0
                    else:
                        metrics.performance_score = base_score
                metrics.cpu_usage = None
                metrics.memory_usage_mb = None

                # Mark as having performance data if we got meaningful values
                if total_processed > 0 or busy_workers > 0 or queue_depth > 0:
                    metrics.has_performance_data = True

                # Mark as having worker data if we have worker context
                metrics.has_worker_data = True

                # Calculate trend directions for scaling decisions
                if (
                    len(self.performance_history)
                    >= ScraperConfig.TREND_ANALYSIS_MIN_SAMPLES
                ):
                    recent_history = self.performance_history[
                        -ScraperConfig.TREND_ANALYSIS_MIN_SAMPLES :
                    ]  # Last N samples

                    # CPU trend direction
                    if (
                        recent_history[0].get("cpu_usage") is not None
                        and recent_history[-1].get("cpu_usage") is not None
                    ):
                        if (
                            recent_history[-1]["cpu_usage"]
                            > recent_history[0]["cpu_usage"] + 1.0  # 1% threshold
                        ):
                            metrics.trend_cpu_direction = "↗️ Rising"
                        elif (
                            recent_history[-1]["cpu_usage"]
                            < recent_history[0]["cpu_usage"] - 1.0  # 1% threshold
                        ):
                            metrics.trend_cpu_direction = "↘️ Falling"
                        else:
                            metrics.trend_cpu_direction = "→ Stable"

                    # Memory trend direction
                    if (
                        recent_history[0].get("memory_usage_percent") is not None
                        and recent_history[-1].get("memory_usage_percent") is not None
                    ):
                        if (
                            recent_history[-1]["memory_usage_percent"]
                            > recent_history[0]["memory_usage_percent"]
                            + 1.0  # 1% threshold
                        ):
                            metrics.trend_memory_direction = "↗️ Rising"
                        elif (
                            recent_history[-1]["memory_usage_percent"]
                            < recent_history[0]["memory_usage_percent"]
                            - 1.0  # 1% threshold
                        ):
                            metrics.trend_memory_direction = "↘️ Falling"
                        else:
                            metrics.trend_memory_direction = "→ Stable"

        except Exception as e:
            print(f"Error collecting metrics: {e}")

        return metrics

    def _draw_dashboard_header(self):
        """Draw the dashboard header"""
        bold = self._get_color_code("bold")
        cyan = self._get_color_code("cyan")
        reset = self._get_color_code("reset")

        header = f"{bold}{cyan}{'='*self.dashboard_width}{reset}"
        title = f"{bold}{cyan}       ADAPTIVE SCRAPER SYSTEM - REAL-TIME MONITOR        {reset}"
        start_time_str = f"{bold}Uptime: {time.time() - self.start_time:.0f}s"
        updates_str = f"Updates: {self.total_updates}"
        interval_str = f"Interval: {self.update_interval}s{reset}"
        uptime = f"{start_time_str} | {updates_str} | {interval_str}"

        print(header)
        print(title)
        print(f"{bold}{cyan}{'='*self.dashboard_width}{reset}")
        print(f"{uptime:^{self.dashboard_width}}")
        print()

    def _draw_performance_section(self, metrics: DashboardMetrics):
        """Draw the performance metrics section"""
        blue = self._get_color_code("blue")
        bold = self._get_color_code("bold")
        reset = self._get_color_code("reset")
        gray = self._get_color_code("white")

        print(f"{bold}{blue}📊 PERFORMANCE METRICS{reset}")
        print(f"{'─'*self.dashboard_width}")

        if metrics.has_performance_data:
            # Core performance metrics
            success_rate = (
                self._format_value(metrics.success_rate, "success_rate")
                if metrics.success_rate is not None
                else "N/A"
            )
            proc_time = (
                self._format_value(metrics.avg_processing_time, "processing_time")
                if metrics.avg_processing_time is not None
                else "N/A"
            )

            print(
                f"Success Rate:      {success_rate:>20} | Avg Process Time: {proc_time:>15}"
            )
            print(
                f"Total Processed:   {metrics.total_processed or 0:>10} | Error Count:      {metrics.errors_count or 0:>10}"
            )
        else:
            print(
                f"{gray}Performance data not yet available (scraper starting up...){reset}"
            )

        if metrics.has_worker_data:
            print(
                f"Active Workers:    {metrics.active_workers or 0:>10} | Queue Length:     {metrics.queue_length or 0:>10}"
            )
            # Format browser pool info with status
            browser_info = f"{metrics.browser_pool_size or 0}"
            if metrics.browser_pool_status:
                browser_info += f" {metrics.browser_pool_status}"
            print(
                f"Browser Pool:      {browser_info:>15} | Timestamp:        {metrics.timestamp:>10}"
            )
        else:
            if (
                not metrics.has_performance_data
            ):  # Only show this if we didn't show performance data
                print(f"{gray}Worker data not yet available{reset}")
                print(f"Timestamp:         {metrics.timestamp:>30}")
        print()

    def _draw_system_section(self, metrics: DashboardMetrics):
        """Draw the system resources section"""
        green = self._get_color_code("green")
        bold = self._get_color_code("bold")
        reset = self._get_color_code("reset")
        gray = self._get_color_code("white")

        print(f"{bold}{green}💻 SYSTEM RESOURCES{reset}")
        print(f"{'─'*self.dashboard_width}")

        if metrics.has_system_data:
            cpu_usage = (
                self._format_value(metrics.cpu_usage, "cpu_usage")
                if metrics.cpu_usage is not None
                else "N/A"
            )
            memory_usage_percent = (
                self._format_value(metrics.memory_usage_percent, "memory_percent")
                if metrics.memory_usage_percent is not None
                else "N/A"
            )
            memory_usage_mb = (
                self._format_value(metrics.memory_usage_mb, "memory")
                if metrics.memory_usage_mb is not None
                else "N/A"
            )
            print(
                f"CPU Usage:         {cpu_usage:>20} | Memory Usage:     {memory_usage_percent:>15}"
            )
            print(
                f"Memory Available:  {memory_usage_mb:>20} | Load Metrics:               ✅"
            )
        else:
            print(f"{gray}System resource monitoring not available{reset}")
        print()

    def _draw_adaptive_section(self, metrics: DashboardMetrics):
        """Draw the adaptive scaling section"""
        magenta = self._get_color_code("magenta")
        bold = self._get_color_code("bold")
        reset = self._get_color_code("reset")
        gray = self._get_color_code("white")

        print(f"{bold}{magenta}🎯 ADAPTIVE SCALING{reset}")
        print(f"{'─'*self.dashboard_width}")

        if metrics.has_adaptive_data:
            scaling_status = (
                self._format_value(metrics.scaling_status, "status")
                if metrics.scaling_status
                else "Monitoring"
            )
            pattern = (
                self._format_value(metrics.pattern_detected, "pattern")
                if metrics.pattern_detected
                else "None"
            )
            auto_tuning = "✅ Active" if metrics.auto_tuning_active else "❌ Inactive"

            print(f"Scaling Status:    {scaling_status}")
            print(
                f"Pattern Detected:  {pattern:>20} | Auto-Tuning:     {auto_tuning:>15}"
            )

            if metrics.last_scaling_action:
                print(f"Last Action:       {metrics.last_scaling_action}")
            else:
                print("Last Action:       No recent actions")

            print(f"Config Updates:    {metrics.config_updates or 0:>10}")
        else:
            print(f"{gray}Adaptive scaling data not yet available{reset}")
            print(
                f"{gray}(Auto-tuning engine needs time to gather performance data){reset}"
            )
        print()

    def _draw_scaling_decisions_section(self, metrics: DashboardMetrics):
        """Draw the scaling decisions metrics section"""
        cyan = self._get_color_code("cyan")
        bold = self._get_color_code("bold")
        reset = self._get_color_code("reset")
        gray = self._get_color_code("white")

        print(f"{bold}{cyan}⚖️ SCALING DECISION METRICS{reset}")
        print(f"{'─'*self.dashboard_width}")

        # Performance Factors
        if metrics.pages_per_second is not None:
            pages_per_sec = f"{metrics.pages_per_second:.2f} pages/sec"
        else:
            pages_per_sec = "N/A"

        if metrics.performance_score is not None:
            perf_score = f"{metrics.performance_score:.2f}/1.0"
        else:
            perf_score = "N/A"

        print(
            f"Pages/Second:      {pages_per_sec:>15} | Performance Score: {perf_score:>15}"
        )

        # Resource Factors
        if metrics.worker_utilization is not None:
            worker_util = f"{metrics.worker_utilization:.1%}"
        else:
            worker_util = "N/A"

        if metrics.resource_capacity is not None:
            resource_cap = f"{metrics.resource_capacity:.1%}"
        else:
            resource_cap = "N/A"

        print(
            f"Worker Utilization: {worker_util:>14} | Resource Capacity: {resource_cap:>14}"
        )

        # Queue and Browser Factors
        if metrics.queue_to_worker_ratio is not None:
            queue_ratio = f"{metrics.queue_to_worker_ratio:.2f}:1"
        else:
            queue_ratio = "N/A"

        if metrics.browser_pool_recommendation is not None:
            browser_rec = f"{metrics.browser_pool_recommendation} browsers"
        else:
            browser_rec = "N/A"

        print(
            f"Queue/Worker Ratio: {queue_ratio:>14} | Browser Pool Rec:  {browser_rec:>14}"
        )

        # Trend Analysis
        if (
            metrics.trend_cpu_direction is not None
            and metrics.trend_memory_direction is not None
        ):
            cpu_trend = f"CPU {metrics.trend_cpu_direction}"
            memory_trend = f"Memory {metrics.trend_memory_direction}"
        else:
            cpu_trend = "N/A"
            memory_trend = "N/A"

        print(
            f"CPU Trend:         {cpu_trend:>15} | Memory Trend:      {memory_trend:>15}"
        )

        print(
            f"{gray}(These metrics drive scaling decisions - ≥2 signals required for scaling){reset}"
        )
        print()

    def _draw_trend_section(self, metrics: DashboardMetrics):
        """Draw the performance trend section"""
        yellow = self._get_color_code("yellow")
        bold = self._get_color_code("bold")
        reset = self._get_color_code("reset")
        gray = self._get_color_code("white")

        print(
            f"{bold}{yellow}📈 PERFORMANCE TRENDS (Last {len(self.performance_history)} samples){reset}"
        )
        print(f"{'─'*self.dashboard_width}")

        if len(self.performance_history) > 1:
            # Check if we have valid performance data in history
            valid_samples = [
                h for h in self.performance_history if h.get("success_rate") is not None
            ]

            if valid_samples:
                # Calculate trends
                recent_success = [
                    h["success_rate"]
                    for h in valid_samples[-5:]
                    if h["success_rate"] is not None
                ]
                recent_cpu = [
                    h["cpu_usage"]
                    for h in valid_samples[-5:]
                    if h["cpu_usage"] is not None
                ]
                recent_processing = [
                    h["avg_processing_time"]
                    for h in valid_samples[-5:]
                    if h["avg_processing_time"] is not None
                ]

                if recent_success:
                    # Use CURRENT success rate (latest reading) not historical average
                    current_success = recent_success[-1]  # Latest/current success rate
                    avg_success = sum(recent_success) / len(
                        recent_success
                    )  # Historical average

                    success_trend = (
                        "📈"
                        if len(recent_success) > 1
                        and recent_success[-1] > recent_success[-2]
                        else "📉" if len(recent_success) > 1 else "━"
                    )
                    # Show CURRENT rate prominently, avg in smaller text
                    print(
                        f"Current Success:   {current_success:.1%} {success_trend} | Avg (5): {avg_success:.1%}",
                        end="",
                    )

                if recent_cpu:
                    # Use CURRENT CPU usage from real-time metrics (not historical data)
                    current_cpu = (
                        metrics.cpu_usage
                        if metrics.cpu_usage is not None
                        else recent_cpu[-1]
                    )
                    avg_cpu = sum(recent_cpu) / len(recent_cpu)
                    cpu_trend = (
                        "📈"
                        if len(recent_cpu) > 1 and recent_cpu[-1] > recent_cpu[-2]
                        else "📉" if len(recent_cpu) > 1 else "━"
                    )
                    if recent_success:
                        print(
                            f"\nCurrent CPU:       {current_cpu:.1f}% {cpu_trend} | Avg (5): {avg_cpu:.1f}%"
                        )
                    else:
                        print(
                            f"Current CPU:       {current_cpu:.1f}% {cpu_trend} | Avg (5): {avg_cpu:.1f}%"
                        )

                if recent_processing:
                    avg_processing = sum(recent_processing) / len(recent_processing)
                    print(
                        f"Avg Process Time:  {avg_processing:.2f}s     | Valid Samples:    {len(valid_samples)}"
                    )
                else:
                    print(f"Valid Samples:     {len(valid_samples)}")
            else:
                print(f"{gray}No valid performance data for trend analysis yet{reset}")
        else:
            print(f"{gray}Collecting trend data... (need more samples){reset}")
        print()

    def _draw_dashboard_footer(self):
        """Draw the dashboard footer"""
        cyan = self._get_color_code("cyan")
        bold = self._get_color_code("bold")
        reset = self._get_color_code("reset")

        print(f"{bold}{cyan}{'='*self.dashboard_width}{reset}")
        print(
            f"{bold}Next update in {self.update_interval} seconds... (Press Ctrl+C to stop){reset}"
        )
        print(f"{bold}{cyan}{'='*self.dashboard_width}{reset}")

    def display_dashboard(self, metrics: DashboardMetrics):
        """Display the complete dashboard"""
        self._clear_screen()

        # Draw all sections
        self._draw_dashboard_header()
        self._draw_performance_section(metrics)
        self._draw_system_section(metrics)
        self._draw_adaptive_section(metrics)
        self._draw_scaling_decisions_section(metrics)
        self._draw_trend_section(metrics)
        self._draw_dashboard_footer()

        self.last_metrics = metrics
        self.total_updates += 1

    def _update_performance_history(self, metrics: DashboardMetrics):
        """Update performance history for trend analysis without displaying dashboard"""
        # Update performance history (only store data that's actually available)
        history_entry = {
            "timestamp": metrics.timestamp,
            "success_rate": metrics.success_rate,
            "cpu_usage": metrics.cpu_usage,
            "memory_usage_percent": metrics.memory_usage_percent,
            "avg_processing_time": metrics.avg_processing_time,
            "active_workers": metrics.active_workers,
        }

        # Only add to history if we have some valid data
        if any(v is not None for v in history_entry.values() if v != metrics.timestamp):
            self.performance_history.append(history_entry)

        # Limit history size to configuration parameter
        max_history = getattr(ScraperConfig, "TREND_ANALYSIS_HISTORY_SIZE", 10)
        if len(self.performance_history) > max_history:
            self.performance_history = self.performance_history[-max_history:]

    async def run_dashboard(self):
        """Run the dashboard in a loop"""
        self.is_running = True
        last_display_time = 0
        last_trend_collection = 0

        try:
            while self.is_running:
                current_time = time.time()

                # Collect trend data at faster interval (even when not displaying)
                if (
                    current_time - last_trend_collection
                    >= ScraperConfig.TREND_COLLECTION_INTERVAL
                ):
                    metrics = self._collect_current_metrics()
                    # Update performance history for trend analysis
                    self._update_performance_history(metrics)
                    last_trend_collection = current_time

                # Display dashboard at slower interval
                if current_time - last_display_time >= self.update_interval:
                    # Temporarily suppress logging during dashboard display
                    with self._suppress_logging():
                        # Clear screen before displaying new metrics
                        self._clear_screen()

                        # Collect current metrics (fresh data for display)
                        metrics = self._collect_current_metrics()
                        self.display_dashboard(metrics)

                        # Add a small delay to ensure dashboard is visible
                        await asyncio.sleep(ScraperConfig.TERMINAL_OUTPUT_SUPPRESSION)

                    last_display_time = current_time

                # Sleep for trend collection interval to avoid busy waiting
                await asyncio.sleep(ScraperConfig.TREND_COLLECTION_INTERVAL)

        except KeyboardInterrupt:
            print(
                f"\n{self._get_color_code('yellow')}Dashboard stopped by user{self._get_color_code('reset')}"
            )
        except Exception as e:
            print(
                f"\n{self._get_color_code('red')}Dashboard error: {e}{self._get_color_code('reset')}"
            )
        finally:
            self.is_running = False

    def stop_dashboard(self):
        """Stop the dashboard"""
        self.is_running = False


# Convenience functions for integration
_monitor_instance: Optional[RealTimeMonitor] = None


def start_real_time_monitor(
    update_interval: int = None, worker_context=None
) -> RealTimeMonitor:
    """Start the real-time monitor dashboard

    Args:
        update_interval: Update interval in seconds
        worker_context: Optional worker context for live metrics

    Returns:
        RealTimeMonitor instance
    """
    global _monitor_instance

    if _monitor_instance is None:
        _monitor_instance = RealTimeMonitor(
            update_interval or ScraperConfig.DASHBOARD_UPDATE_INTERVAL, worker_context
        )

    return _monitor_instance


def stop_real_time_monitor():
    """Stop the real-time monitor dashboard"""
    global _monitor_instance

    if _monitor_instance:
        _monitor_instance.stop_dashboard()
        _monitor_instance = None


async def run_monitor_dashboard(update_interval: int = None):
    """Run the monitor dashboard (async)"""
    monitor = start_real_time_monitor(
        update_interval or ScraperConfig.DASHBOARD_UPDATE_INTERVAL
    )
    await monitor.run_dashboard()


# Demo/test function
async def demo_dashboard():
    """Demo the dashboard with sample data"""
    print("🚀 Starting Real-Time Monitor Dashboard Demo...")
    print(
        f"Update interval: {ScraperConfig.DASHBOARD_DEMO_INTERVAL} seconds (demo mode)"
    )
    print("Press Ctrl+C to stop\n")

    monitor = RealTimeMonitor(
        update_interval=ScraperConfig.DASHBOARD_DEMO_INTERVAL
    )  # Faster updates for demo

    try:
        await monitor.run_dashboard()
    except KeyboardInterrupt:
        print("\nDemo stopped by user")


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_dashboard())
