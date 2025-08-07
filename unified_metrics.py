#!/usr/bin/env python3
"""
Unified Data Collection System

This module provides a unified way to collect performance metrics that both the
dashboard and scaling engine can use consistently.
"""

import time
import os
import sys

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from resource_monitor import get_system_resources

    SYSTEM_MONITORING_AVAILABLE = True
except ImportError:
    SYSTEM_MONITORING_AVAILABLE = False

try:
    from adaptive_scaling_engine import get_current_worker_count

    ADAPTIVE_SCALING_AVAILABLE = True
except ImportError:
    ADAPTIVE_SCALING_AVAILABLE = False


class UnifiedMetrics:
    """Unified metrics collection for both dashboard and scaling engine"""

    def __init__(self, worker_context=None):
        self.worker_context = worker_context
        self.start_time = time.time()
        self.last_metrics = {}

    def collect_unified_metrics(self) -> dict:
        """Collect metrics in a format that both dashboard and scaling engine can use"""

        current_time = time.time()
        elapsed_time = current_time - self.start_time

        # Initialize with defaults
        metrics = {
            # Core performance metrics
            "success_rate": 1.0,
            "avg_processing_time": 2.0,
            "total_processed": 0,
            "total_failed": 0,
            # Worker metrics (consistent format)
            "current_workers": 50,  # From scaling engine
            "active_workers": 0,  # Actually busy workers
            "max_workers": 50,  # Pool size
            # Queue metrics
            "queue_size": 0,
            "queue_length": 0,  # Same as queue_size but for dashboard compatibility
            # System metrics
            "cpu_usage_percent": 30.0,
            "memory_usage_mb": 512.0,
            "memory_usage_percent": 50.0,
            # Calculated metrics
            "pages_per_second": 0.0,
            "worker_utilization": 0.0,  # As decimal (0-1.0)
            "worker_utilization_percent": 0.0,  # As percentage (0-100%) for dashboard
            "queue_to_worker_ratio": 0.0,
            "resource_capacity": 0.5,
            "performance_score": 0.8,
            # Browser metrics
            "browser_pool_size": 0,
            "browser_pool_recommendation": 2,
            # Timestamps
            "timestamp": current_time,
            "elapsed_time": elapsed_time,
        }

        # Collect real data from worker context if available
        if self.worker_context:
            self._collect_worker_context_data(metrics)
        else:
            # Use scaling engine data as fallback
            from main_self_contained import get_current_workers

            current_workers = get_current_workers()
            metrics["current_workers"] = current_workers
            metrics["max_workers"] = current_workers

            # Get target worker count from adaptive scaling engine (fallback path)
            if ADAPTIVE_SCALING_AVAILABLE:
                try:
                    target_workers = get_current_worker_count()
                    metrics["active_workers"] = (
                        target_workers  # Use target workers as active_workers for dashboard
                    )
                except Exception as e:
                    metrics["active_workers"] = (
                        current_workers  # Fallback to current_workers
                    )
            else:
                metrics["active_workers"] = current_workers

        # Collect system resources if available
        if SYSTEM_MONITORING_AVAILABLE:
            self._collect_system_resources(metrics)

        # Collect adaptive scaling data if available
        if ADAPTIVE_SCALING_AVAILABLE:
            self._collect_adaptive_scaling_data(metrics)

        # Calculate derived metrics
        self._calculate_derived_metrics(metrics)

        # Store for future reference
        self.last_metrics = metrics.copy()

        return metrics

    def _collect_worker_context_data(self, metrics: dict):
        """Collect data from active worker context"""
        try:
            # Basic counts
            completed_count = (
                len(self.worker_context.completed_tasks)
                if hasattr(self.worker_context, "completed_tasks")
                else 0
            )
            failed_count = (
                len(self.worker_context.failed_tasks)
                if hasattr(self.worker_context, "failed_tasks")
                else 0
            )
            total_processed = completed_count + failed_count

            # Worker counts - both active and target
            active_workers = 0  # Currently busy workers
            target_workers = 50  # Target worker count from scaling engine
            max_workers = 50

            # Get currently active (busy) workers
            if hasattr(self.worker_context, "worker_manager") and hasattr(
                self.worker_context.worker_manager, "active_workers"
            ):
                active_workers = len(self.worker_context.worker_manager.active_workers)

            # Get target worker count from adaptive scaling engine
            if ADAPTIVE_SCALING_AVAILABLE:
                try:
                    target_workers = get_current_worker_count()
                except Exception as e:
                    target_workers = 50  # Fallback value
            else:
                target_workers = 50  # Fallback if adaptive scaling not available

            if hasattr(self.worker_context, "max_workers"):
                max_workers = self.worker_context.max_workers

            # Queue size
            queue_size = 0
            if hasattr(self.worker_context, "task_queue"):
                queue_size = self.worker_context.task_queue.qsize()

            # Update metrics
            metrics.update(
                {
                    "total_processed": total_processed,
                    "total_failed": failed_count,
                    "active_workers": target_workers,  # Show target workers for scaling visibility
                    "busy_workers": active_workers,  # Show actually busy workers
                    "max_workers": max_workers,
                    "queue_size": queue_size,
                    "queue_length": queue_size,  # Dashboard compatibility
                }
            )

            # Calculate success rate
            if total_processed > 0:
                metrics["success_rate"] = completed_count / total_processed

            # Calculate processing time and rate
            if total_processed > 0 and metrics["elapsed_time"] > 0:
                metrics["pages_per_second"] = total_processed / metrics["elapsed_time"]
                # Estimate average processing time
                if active_workers > 0:
                    estimated_time = active_workers / (
                        total_processed / metrics["elapsed_time"]
                    )
                    metrics["avg_processing_time"] = min(10.0, max(0.5, estimated_time))

        except Exception as e:
            print(f"Warning: Error collecting worker context data: {e}")

    def _collect_system_resources(self, metrics: dict):
        """Collect system resource data"""
        try:
            resources = get_system_resources()
            if resources:
                metrics.update(
                    {
                        "cpu_usage_percent": resources.get("cpu_percent", 30.0),
                        "memory_usage_mb": resources.get("memory_mb", 512.0),
                        "memory_usage_percent": resources.get("memory_percent", 50.0),
                    }
                )
        except Exception as e:
            print(f"Warning: Error collecting system resources: {e}")

    def _collect_adaptive_scaling_data(self, metrics: dict):
        """Collect adaptive scaling status and data"""
        try:
            from adaptive_scaling_engine import get_scaling_status

            scaling_status = get_scaling_status()

            # Extract relevant data for dashboard
            metrics["scaling_status"] = (
                "Active" if scaling_status.get("scaling_active", False) else "Inactive"
            )
            metrics["auto_tuning_active"] = scaling_status.get("scaling_active", False)

            # Get recent scaling decisions
            recent_decisions = scaling_status.get("recent_scaling_decisions", [])
            if recent_decisions:
                last_decision = recent_decisions[-1]
                action = last_decision.get("action", "No action")
                reason = last_decision.get("reason", "")
                metrics["last_scaling_action"] = (
                    f"{action}: {reason}" if reason else action
                )
            else:
                metrics["last_scaling_action"] = "No recent actions"

            # Pattern detection - simplified
            decisions_count = scaling_status.get("scaling_decisions_made", 0)
            if decisions_count > 5:
                metrics["pattern_detected"] = "Performance tracking"
            else:
                metrics["pattern_detected"] = "Monitoring"

            # Config updates
            metrics["config_updates"] = decisions_count

            # Set availability flag
            metrics["has_adaptive_data"] = True

        except Exception as e:
            print(f"Warning: Error collecting adaptive scaling data: {e}")
            # Set defaults
            metrics["scaling_status"] = "Unknown"
            metrics["auto_tuning_active"] = False
            metrics["last_scaling_action"] = "Data unavailable"
            metrics["pattern_detected"] = "Unknown"
            metrics["config_updates"] = 0
            metrics["has_adaptive_data"] = False

    def _calculate_derived_metrics(self, metrics: dict):
        """Calculate derived metrics consistently"""

        # Worker utilization (both formats) - busy workers vs target workers
        if metrics["active_workers"] > 0:  # active_workers is now target_workers
            # Calculate how busy the target workforce is
            utilization_decimal = (
                metrics.get("busy_workers", 0) / metrics["active_workers"]
            )
            utilization_decimal = min(1.0, utilization_decimal)  # Cap at 100%
            metrics["worker_utilization"] = (
                utilization_decimal  # 0-1.0 for scaling engine
            )
            metrics["worker_utilization_percent"] = (
                utilization_decimal * 100
            )  # 0-100% for dashboard

        # Queue to worker ratio - queue vs target workers
        if metrics["active_workers"] > 0:  # active_workers is now target_workers
            metrics["queue_to_worker_ratio"] = (
                metrics["queue_size"] / metrics["active_workers"]
            )

        # Resource capacity
        cpu_capacity = max(0, (90 - metrics["cpu_usage_percent"]) / 90)
        memory_capacity = max(0, (85 - metrics["memory_usage_percent"]) / 85)
        metrics["resource_capacity"] = min(cpu_capacity, memory_capacity)

        # Performance score
        base_score = metrics["success_rate"]
        if metrics["avg_processing_time"] > 0:
            time_factor = min(1.0, 2.0 / metrics["avg_processing_time"])
            metrics["performance_score"] = (base_score + time_factor) / 2.0
        else:
            metrics["performance_score"] = base_score

        # Browser pool recommendation based on target workers
        target_worker_count = metrics.get(
            "active_workers", 50
        )  # active_workers is now target_workers

        # For 6-browser pool: recommend full capacity when >=85 workers (85/17 = 5 browsers minimum)
        # This ensures we utilize the configured 6-browser pool efficiently
        if target_worker_count >= 85:
            recommended_browsers = 6  # Use full configured capacity
        else:
            recommended_browsers = min(6, max(1, target_worker_count // 17))

        metrics["browser_pool_recommendation"] = recommended_browsers

        # Try to get current browser pool size
        try:
            from optimization_utils import _browser_pool
            from config import OptimizationConfig

            actual_pool_size = len(_browser_pool)
            configured_pool_size = OptimizationConfig.BROWSER_POOL_SIZE

            metrics["browser_pool_size"] = actual_pool_size

            # Enhanced status information
            if actual_pool_size == 0:
                if target_worker_count > 0:
                    # Show expected pool size when empty but workers are expected
                    expected_size = max(1, target_worker_count // 17)
                    metrics["browser_pool_status"] = f"Empty (expects {expected_size})"
                else:
                    metrics["browser_pool_status"] = (
                        f"Empty (config: {configured_pool_size})"
                    )
            else:
                metrics["browser_pool_status"] = (
                    f"Active ({actual_pool_size}/{configured_pool_size})"
                )

        except (ImportError, NameError, AttributeError):
            # Fallback: use target worker count for estimation
            fallback_size = max(1, target_worker_count // 17)
            metrics["browser_pool_size"] = 0  # Show 0 since we can't access actual pool
            metrics["browser_pool_status"] = f"Estimated (expects {fallback_size})"

    def get_scaling_engine_format(self) -> dict:
        """Get metrics in the format expected by the scaling engine"""
        unified = self.collect_unified_metrics()

        return {
            "success_rate": unified["success_rate"],
            "avg_processing_time": unified["avg_processing_time"],
            "queue_size": unified["queue_size"],
            "cpu_usage_percent": unified["cpu_usage_percent"],
            "memory_usage_mb": unified["memory_usage_mb"],
            "current_workers": unified["current_workers"],
        }

    def get_dashboard_format(self) -> dict:
        """Get metrics in the format expected by the dashboard"""
        unified = self.collect_unified_metrics()

        # Return all metrics but ensure dashboard-friendly formats
        dashboard_metrics = unified.copy()
        dashboard_metrics["worker_utilization"] = unified[
            "worker_utilization"  # Use decimal form (0-1.0) for .1% formatting
        ]  # Dashboard will convert with .1% format specifier

        return dashboard_metrics


# Global instance for shared use
_unified_metrics = None


def get_unified_metrics(worker_context=None) -> UnifiedMetrics:
    """Get or create the global unified metrics instance"""
    global _unified_metrics
    if _unified_metrics is None:
        _unified_metrics = UnifiedMetrics(worker_context)
    elif worker_context and _unified_metrics.worker_context != worker_context:
        # Update worker context if provided
        _unified_metrics.worker_context = worker_context
    return _unified_metrics


def get_metrics_for_scaling_engine(worker_context=None) -> dict:
    """Get metrics formatted for the scaling engine"""
    unified = get_unified_metrics(worker_context)
    return unified.get_scaling_engine_format()


def get_metrics_for_dashboard(worker_context=None) -> dict:
    """Get metrics formatted for the dashboard"""
    unified = get_unified_metrics(worker_context)
    return unified.get_dashboard_format()
