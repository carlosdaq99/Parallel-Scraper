#!/usr/bin/env python3
"""
Resource Monitor - System-level resource tracking for adaptive scaling
Provides comprehensive resource monitoring and snapshot capabilities.

Builds on existing optimization functions and extends with system-level monitoring.
Used for making informed scaling decisions based on resource availability.

Features:
- System resource tracking (CPU, memory, disk)
- Browser instance monitoring
- Queue size and worker tracking
- Performance statistics and history
- Integration with existing optimization metrics
"""

import time
import json
import psutil
from typing import Dict, Any, Optional, List
from dataclasses import asdict
from dataclasses import dataclass, asdict
from collections import deque
from datetime import datetime
from pathlib import Path

# Import existing optimization metrics functions
from optimization_utils import get_optimization_metrics
from advanced_optimization_utils import collect_advanced_metrics

# Resource monitoring history
_resource_history = deque(maxlen=500)
_system_stats = {
    "start_time": time.time(),
    "peak_memory_mb": 0,
    "peak_cpu_percent": 0,
    "peak_browser_instances": 0,
    "total_snapshots": 0,
}


@dataclass
class ResourceSnapshot:
    """Comprehensive resource snapshot for scaling decisions."""

    timestamp: float
    datetime_str: str

    # System resources
    memory_usage_mb: float
    memory_available_mb: float
    memory_percent: float
    cpu_percent: float
    cpu_count: int

    # Browser and worker tracking
    browser_instances: int
    active_workers: int
    completed_tasks: int
    failed_tasks: int
    queue_size: int

    # Performance metrics
    success_rate: float
    avg_processing_time_ms: float
    pages_processed: int

    # System health indicators
    disk_usage_percent: float
    network_io_mb: float
    load_average: Optional[float]

    # Optimization metrics integration
    optimization_health_score: float
    circuit_breaker_failures: int


class SystemResourceMonitor:
    """
    Comprehensive system resource monitoring for adaptive scaling decisions.

    Integrates with existing optimization metrics and provides system-level
    resource tracking for informed scaling decisions.
    """

    def __init__(self, history_size: int = 500, enable_logging: bool = True):
        """
        Initialize system resource monitor.

        Args:
            history_size: Number of snapshots to retain in history
            enable_logging: Whether to enable file logging of snapshots
        """
        self.history_size = history_size
        self.enable_logging = enable_logging
        self.start_time = time.time()

        # Performance counters
        self.counters = {
            "total_tasks_completed": 0,
            "total_tasks_failed": 0,
            "snapshots_taken": 0,
            "last_snapshot_time": 0,
        }

        # Create logs directory if logging enabled
        if self.enable_logging:
            self.logs_dir = Path("logs")
            self.logs_dir.mkdir(exist_ok=True)

    def update_task_counters(self, completed: int = 0, failed: int = 0) -> None:
        """
        Update task completion counters.

        Args:
            completed: Number of newly completed tasks
            failed: Number of newly failed tasks
        """
        self.counters["total_tasks_completed"] += completed
        self.counters["total_tasks_failed"] += failed

    def take_comprehensive_snapshot(
        self, active_workers: int = 0, queue_size: int = 0
    ) -> ResourceSnapshot:
        """
        Take a comprehensive resource snapshot including system and optimization metrics.

        Args:
            active_workers: Current number of active workers
            queue_size: Current size of work queue

        Returns:
            ResourceSnapshot containing all relevant metrics
        """
        current_time = time.time()

        # Get system resource information
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(
            interval=1.0
        )  # Use 1 second for accurate reading

        # Disk usage (cross-platform path)
        try:
            import os

            if os.name == "nt":  # Windows
                disk = psutil.disk_usage("C:\\")
            else:  # Unix-like systems
                disk = psutil.disk_usage("/")
        except Exception:
            # Fallback for disk usage
            class MockDisk:
                percent = 0.0

            disk = MockDisk()

        # Network I/O (simplified)
        try:
            net_io = psutil.net_io_counters()
            network_io_mb = (net_io.bytes_sent + net_io.bytes_recv) / 1024 / 1024
        except Exception:
            network_io_mb = 0.0

        # Load average (Unix-like systems)
        try:
            load_avg = psutil.getloadavg()[0] if hasattr(psutil, "getloadavg") else None
        except Exception:
            load_avg = None

        # Count browser instances
        browser_count = self._count_browser_instances()

        # Get optimization metrics
        opt_metrics = self._get_integrated_optimization_metrics()

        # Calculate success rate
        total_tasks = (
            self.counters["total_tasks_completed"] + self.counters["total_tasks_failed"]
        )
        success_rate = (
            (self.counters["total_tasks_completed"] / total_tasks)
            if total_tasks > 0
            else 1.0
        )

        # Create comprehensive snapshot
        snapshot = ResourceSnapshot(
            timestamp=current_time,
            datetime_str=datetime.now().isoformat(),
            # System resources
            memory_usage_mb=memory.used / 1024 / 1024,
            memory_available_mb=memory.available / 1024 / 1024,
            memory_percent=memory.percent,
            cpu_percent=cpu_percent,
            cpu_count=psutil.cpu_count(),
            # Browser and worker tracking
            browser_instances=browser_count,
            active_workers=active_workers,
            completed_tasks=self.counters["total_tasks_completed"],
            failed_tasks=self.counters["total_tasks_failed"],
            queue_size=queue_size,
            # Performance metrics
            success_rate=success_rate,
            avg_processing_time_ms=opt_metrics.get("avg_processing_time_ms", 0),
            pages_processed=opt_metrics.get("pages_processed", 0),
            # System health indicators
            disk_usage_percent=disk.percent,
            network_io_mb=network_io_mb,
            load_average=load_avg,
            # Optimization metrics integration
            optimization_health_score=self._calculate_optimization_health_score(
                opt_metrics
            ),
            circuit_breaker_failures=opt_metrics.get("circuit_breaker_failures", 0),
        )

        # Update global statistics
        _system_stats["peak_memory_mb"] = max(
            _system_stats["peak_memory_mb"], snapshot.memory_usage_mb
        )
        _system_stats["peak_cpu_percent"] = max(
            _system_stats["peak_cpu_percent"], snapshot.cpu_percent
        )
        _system_stats["peak_browser_instances"] = max(
            _system_stats["peak_browser_instances"], snapshot.browser_instances
        )
        _system_stats["total_snapshots"] += 1

        # Store in history
        _resource_history.append(snapshot)
        self.counters["snapshots_taken"] += 1
        self.counters["last_snapshot_time"] = current_time

        # Log if enabled
        if self.enable_logging:
            self._log_snapshot(snapshot)

        return snapshot

    def _count_browser_instances(self) -> int:
        """Count current browser instances running on the system."""
        try:
            browser_count = 0
            for process in psutil.process_iter(["name", "cmdline"]):
                try:
                    process_name = (
                        process.info["name"].lower() if process.info["name"] else ""
                    )
                    if any(
                        browser in process_name
                        for browser in ["chrome", "chromium", "firefox", "edge"]
                    ):
                        browser_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            return browser_count
        except Exception:
            return 0

    def _get_integrated_optimization_metrics(self) -> Dict[str, Any]:
        """Get metrics from existing optimization functions."""
        try:
            # Get base optimization metrics
            opt_metrics = get_optimization_metrics()

            # Try to get advanced metrics as well
            try:
                advanced_metrics = collect_advanced_metrics()
                opt_metrics.update(advanced_metrics)
            except Exception:
                pass  # Advanced metrics optional

            return opt_metrics
        except Exception:
            # Return default metrics if functions unavailable
            return {
                "avg_processing_time_ms": 0,
                "pages_processed": 0,
                "success_rate": 1.0,
                "circuit_breaker_failures": 0,
                "memory_usage_mb": 0,
            }

    def _calculate_optimization_health_score(
        self, opt_metrics: Dict[str, Any]
    ) -> float:
        """Calculate optimization health score based on integrated metrics."""
        success_rate = opt_metrics.get("success_rate", 1.0)
        circuit_failures = opt_metrics.get("circuit_breaker_failures", 0)

        # Simple health calculation
        health_score = success_rate * (1.0 - min(circuit_failures / 10, 0.5))
        return max(0.0, min(health_score, 1.0))

    def _log_snapshot(self, snapshot: ResourceSnapshot) -> None:
        """Log snapshot to file for historical analysis."""
        try:
            log_file = self.logs_dir / "resource_snapshots.jsonl"
            with open(log_file, "a", encoding="utf-8") as f:
                json.dump(asdict(snapshot), f)
                f.write("\n")
        except Exception:
            pass  # Silent fail for logging

    def get_current_resource_status(self) -> Dict[str, Any]:
        """Get current resource status and performance statistics."""
        if not _resource_history:
            return {"status": "No snapshots available"}

        latest = _resource_history[-1]
        runtime = time.time() - self.start_time

        return {
            "current_snapshot": asdict(latest),
            "runtime_seconds": runtime,
            "runtime_formatted": f"{runtime/60:.1f} minutes",
            "peak_memory_mb": _system_stats["peak_memory_mb"],
            "peak_cpu_percent": _system_stats["peak_cpu_percent"],
            "peak_browser_instances": _system_stats["peak_browser_instances"],
            "total_snapshots": _system_stats["total_snapshots"],
            "snapshot_rate_per_minute": (
                (self.counters["snapshots_taken"] / (runtime / 60))
                if runtime > 60
                else 0
            ),
            "history_size": len(_resource_history),
        }

    def analyze_resource_trends(self, lookback_minutes: int = 10) -> Dict[str, Any]:
        """
        Analyze resource trends over specified time period.

        Args:
            lookback_minutes: How many minutes to look back for trend analysis

        Returns:
            Dictionary containing trend analysis results
        """
        if len(_resource_history) < 5:
            return {"status": "Insufficient data for trend analysis"}

        # Filter recent history
        cutoff_time = time.time() - (lookback_minutes * 60)
        recent_snapshots = [s for s in _resource_history if s.timestamp >= cutoff_time]

        if len(recent_snapshots) < 3:
            return {"status": f"Insufficient data in last {lookback_minutes} minutes"}

        # Calculate trends
        memory_trend = self._calculate_metric_trend(
            [s.memory_usage_mb for s in recent_snapshots]
        )
        cpu_trend = self._calculate_metric_trend(
            [s.cpu_percent for s in recent_snapshots]
        )
        success_rate_trend = self._calculate_metric_trend(
            [s.success_rate for s in recent_snapshots]
        )
        browser_trend = self._calculate_metric_trend(
            [s.browser_instances for s in recent_snapshots]
        )

        return {
            "analysis_period_minutes": lookback_minutes,
            "snapshots_analyzed": len(recent_snapshots),
            "trends": {
                "memory_usage_mb": memory_trend,
                "cpu_percent": cpu_trend,
                "success_rate": success_rate_trend,
                "browser_instances": browser_trend,
            },
            "latest_values": {
                "memory_usage_mb": recent_snapshots[-1].memory_usage_mb,
                "cpu_percent": recent_snapshots[-1].cpu_percent,
                "success_rate": recent_snapshots[-1].success_rate,
                "browser_instances": recent_snapshots[-1].browser_instances,
            },
        }

    def _calculate_metric_trend(self, values: List[float]) -> Dict[str, Any]:
        """Calculate trend for a list of metric values."""
        if len(values) < 2:
            return {"direction": "stable", "change": 0.0, "confidence": 0.0}

        # Simple trend calculation
        start_val = values[0]
        end_val = values[-1]
        change = end_val - start_val
        change_percent = (change / start_val * 100) if start_val != 0 else 0

        # Determine direction
        if abs(change_percent) < 5:
            direction = "stable"
        elif change_percent > 0:
            direction = "increasing"
        else:
            direction = "decreasing"

        # Simple confidence based on consistency
        if len(values) >= 5:
            mid_point = len(values) // 2
            first_half_avg = sum(values[:mid_point]) / mid_point
            second_half_avg = sum(values[mid_point:]) / (len(values) - mid_point)
            consistency = 1.0 - abs(
                (second_half_avg - first_half_avg) / (first_half_avg + 1)
            )
            confidence = max(0.3, min(consistency, 1.0))
        else:
            confidence = 0.5

        return {
            "direction": direction,
            "change": change,
            "change_percent": change_percent,
            "confidence": confidence,
        }

    def get_scaling_resource_recommendation(self) -> Dict[str, Any]:
        """
        Get resource-based scaling recommendation.

        Returns:
            Dictionary with scaling recommendation based on resource analysis
        """
        if not _resource_history:
            return {
                "recommendation": "maintain",
                "reason": "No resource data available",
            }

        latest = _resource_history[-1]

        # Resource-based scaling logic
        scale_down_reasons = []
        scale_up_reasons = []

        # Memory pressure
        if latest.memory_percent > 85:
            scale_down_reasons.append(
                f"High memory usage: {latest.memory_percent:.1f}%"
            )
        elif latest.memory_percent < 60:
            scale_up_reasons.append(f"Low memory usage: {latest.memory_percent:.1f}%")

        # CPU pressure
        if latest.cpu_percent > 90:
            scale_down_reasons.append(f"High CPU usage: {latest.cpu_percent:.1f}%")
        elif latest.cpu_percent < 50:
            scale_up_reasons.append(f"Low CPU usage: {latest.cpu_percent:.1f}%")

        # Success rate
        if latest.success_rate < 0.8:
            scale_down_reasons.append(f"Low success rate: {latest.success_rate:.2f}")
        elif latest.success_rate > 0.95:
            scale_up_reasons.append(f"High success rate: {latest.success_rate:.2f}")

        # Browser instance stress
        if latest.browser_instances > 20:  # Arbitrary threshold
            scale_down_reasons.append(f"High browser count: {latest.browser_instances}")

        # Circuit breaker failures
        if latest.circuit_breaker_failures > 5:
            scale_down_reasons.append(
                f"Circuit breaker active: {latest.circuit_breaker_failures} failures"
            )

        # Make recommendation
        if len(scale_down_reasons) >= 2:
            recommendation = "scale_down"
            confidence = 0.8
            reason = "; ".join(scale_down_reasons)
        elif len(scale_up_reasons) >= 2 and len(scale_down_reasons) == 0:
            recommendation = "scale_up"
            confidence = 0.7
            reason = "; ".join(scale_up_reasons)
        else:
            recommendation = "maintain"
            confidence = 0.6
            reason = "Resource levels within acceptable parameters"

        return {
            "recommendation": recommendation,
            "confidence": confidence,
            "reason": reason,
            "current_resources": {
                "memory_percent": latest.memory_percent,
                "cpu_percent": latest.cpu_percent,
                "success_rate": latest.success_rate,
                "browser_instances": latest.browser_instances,
            },
        }

    def print_resource_status(self) -> None:
        """Print current resource status to console."""
        status = self.get_current_resource_status()
        if "current_snapshot" not in status:
            print("No resource data available")
            return

        snapshot = status["current_snapshot"]
        # Convert snapshot to dict if it's a NamedTuple
        if hasattr(snapshot, "_asdict"):
            snapshot = snapshot._asdict()
        elif not isinstance(snapshot, dict):
            # If it's not a dict or NamedTuple, convert attributes to dict
            snapshot = {
                "memory_usage_mb": getattr(snapshot, "memory_usage_mb", 0),
                "memory_percent": getattr(snapshot, "memory_percent", 0),
                "cpu_percent": getattr(snapshot, "cpu_percent", 0),
                "browser_instances": getattr(snapshot, "browser_instances", 0),
                "active_workers": getattr(snapshot, "active_workers", 0),
                "queue_size": getattr(snapshot, "queue_size", 0),
                "success_rate": getattr(snapshot, "success_rate", 0),
                "completed_tasks": getattr(snapshot, "completed_tasks", 0),
                "failed_tasks": getattr(snapshot, "failed_tasks", 0),
                "optimization_health_score": getattr(
                    snapshot, "optimization_health_score", 0
                ),
            }

        print("\n=== System Resource Status ===")
        print(f"Runtime: {status.get('runtime_formatted', 'Unknown')}")
        print(
            f"Memory: {snapshot.get('memory_usage_mb', 0):.1f} MB ({snapshot.get('memory_percent', 0):.1f}%)"
        )
        print(f"CPU: {snapshot.get('cpu_percent', 0):.1f}%")
        print(f"Browser instances: {snapshot.get('browser_instances', 0)}")
        print(f"Active workers: {snapshot.get('active_workers', 0)}")
        print(f"Queue size: {snapshot.get('queue_size', 0)}")
        print(f"Success rate: {snapshot.get('success_rate', 0):.2f}")
        print(f"Completed tasks: {snapshot.get('completed_tasks', 0)}")
        print(f"Failed tasks: {snapshot.get('failed_tasks', 0)}")
        print(
            f"Optimization health: {snapshot.get('optimization_health_score', 0):.2f}"
        )

        # Show scaling recommendation
        recommendation = self.get_scaling_resource_recommendation()
        print(f"\nScaling recommendation: {recommendation['recommendation'].upper()}")
        print(f"Confidence: {recommendation['confidence']:.2f}")
        print(f"Reason: {recommendation['reason']}")


def get_resource_monitor() -> SystemResourceMonitor:
    """Get or create a global resource monitor instance."""
    if not hasattr(get_resource_monitor, "_instance"):
        get_resource_monitor._instance = SystemResourceMonitor()
    return get_resource_monitor._instance


def take_quick_resource_snapshot() -> Dict[str, Any]:
    """Take a quick resource snapshot without full SystemResourceMonitor setup."""
    monitor = get_resource_monitor()
    snapshot = monitor.take_comprehensive_snapshot()
    return asdict(snapshot)


def get_system_resources() -> Dict[str, Any]:
    """Get current system resources for dashboard display."""
    try:
        import psutil

        # Get basic system metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(
            interval=1.0
        )  # Use 1 second for accurate reading

        return {
            "cpu_percent": round(cpu_percent, 1),
            "memory_mb": round(memory.used / 1024 / 1024, 1),
            "memory_available_mb": round(memory.available / 1024 / 1024, 1),
            "memory_percent": round(memory.percent, 1),
            "cpu_count": psutil.cpu_count(),
        }
    except Exception as e:
        print(f"Error getting system resources: {e}")
        return None
