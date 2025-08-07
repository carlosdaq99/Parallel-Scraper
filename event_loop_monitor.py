#!/usr/bin/env python3
"""
Event Loop Monitor - Async performance monitoring for adaptive scaling
Provides event loop health monitoring and performance tracking.

Features:
- Event loop lag detection and measurement
- Slow callback identification
- Task count monitoring
- Async performance metrics for scaling decisions
- Integration with existing optimization systems
"""

import asyncio
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from collections import deque

# Configure logging
logger = logging.getLogger(__name__)

# Event loop monitoring state
_monitoring_active = False
_performance_history = deque(maxlen=200)
_slow_callbacks = deque(maxlen=50)
_monitor_task = None


@dataclass
class EventLoopMetrics:
    """Event loop performance metrics snapshot."""

    timestamp: float
    loop_lag_ms: float
    active_task_count: int
    pending_callbacks: int
    slow_callbacks_count: int
    is_saturated: bool
    health_score: float
    recommendations: List[str]


@dataclass
class SlowCallback:
    """Information about slow/blocking callback."""

    timestamp: float
    duration_ms: float
    callback_name: str
    severity: str  # 'warning', 'critical'


class EventLoopPerformanceMonitor:
    """
    Event loop performance monitoring for adaptive scaling decisions.

    Tracks async performance metrics to help determine when scaling
    is needed due to event loop congestion.
    """

    def __init__(
        self, lag_threshold_ms: float = 50.0, slow_callback_threshold_ms: float = 100.0
    ):
        """
        Initialize event loop monitor.

        Args:
            lag_threshold_ms: Maximum acceptable event loop lag
            slow_callback_threshold_ms: Threshold for slow callback detection
        """
        self.lag_threshold_ms = lag_threshold_ms
        self.slow_callback_threshold_ms = slow_callback_threshold_ms
        self.last_measurement_time = time.time()
        self.callback_start_times = {}

        # Performance tracking
        self.total_measurements = 0
        self.lag_violations = 0
        self.slow_callback_count = 0

    async def start_monitoring(self, interval_seconds: float = 2.0) -> None:
        """
        Start event loop monitoring.

        Args:
            interval_seconds: Monitoring collection interval
        """
        global _monitoring_active, _monitor_task

        if _monitoring_active:
            logger.warning("Event loop monitoring already active")
            return

        _monitoring_active = True
        self.last_measurement_time = time.time()

        # Start monitoring task
        _monitor_task = asyncio.create_task(self._monitoring_loop(interval_seconds))
        logger.info(f"Event loop monitoring started (interval: {interval_seconds}s)")

    async def stop_monitoring(self) -> None:
        """Stop event loop monitoring."""
        global _monitoring_active, _monitor_task

        if not _monitoring_active:
            return

        _monitoring_active = False

        if _monitor_task:
            _monitor_task.cancel()
            try:
                await _monitor_task
            except asyncio.CancelledError:
                pass

        logger.info("Event loop monitoring stopped")

    async def _monitoring_loop(self, interval_seconds: float) -> None:
        """Main monitoring loop collecting metrics."""
        while _monitoring_active:
            try:
                metrics = await self.collect_event_loop_metrics()
                _performance_history.append(metrics)

                # Log critical issues
                if metrics.is_saturated:
                    logger.warning(
                        f"Event loop saturated - lag: {metrics.loop_lag_ms:.1f}ms"
                    )

                await asyncio.sleep(interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in event loop monitoring: {e}")
                await asyncio.sleep(interval_seconds)

    async def collect_event_loop_metrics(self) -> EventLoopMetrics:
        """Collect current event loop performance metrics."""
        current_time = time.time()

        # Measure event loop lag
        lag_start = time.perf_counter()
        await asyncio.sleep(0)  # Yield control to measure lag
        lag_end = time.perf_counter()
        loop_lag_ms = (lag_end - lag_start) * 1000

        # Get task information
        all_tasks = asyncio.all_tasks()
        active_task_count = len([t for t in all_tasks if not t.done()])

        # Estimate pending callbacks (simplified)
        try:
            loop = asyncio.get_running_loop()
            # This is a rough approximation - actual implementation would need loop internals
            pending_callbacks = len(getattr(loop, "_callbacks", []))
        except Exception:
            pending_callbacks = 0

        # Check if loop is saturated
        is_saturated = (
            loop_lag_ms > self.lag_threshold_ms
            or active_task_count > 100  # Arbitrary threshold
            or pending_callbacks > 50
        )

        # Calculate health score
        health_score = self._calculate_event_loop_health_score(
            loop_lag_ms, active_task_count, pending_callbacks
        )

        # Generate recommendations
        recommendations = self._generate_performance_recommendations(
            loop_lag_ms, active_task_count, is_saturated
        )

        # Update tracking counters
        self.total_measurements += 1
        if loop_lag_ms > self.lag_threshold_ms:
            self.lag_violations += 1

        return EventLoopMetrics(
            timestamp=current_time,
            loop_lag_ms=loop_lag_ms,
            active_task_count=active_task_count,
            pending_callbacks=pending_callbacks,
            slow_callbacks_count=len(_slow_callbacks),
            is_saturated=is_saturated,
            health_score=health_score,
            recommendations=recommendations,
        )

    def _calculate_event_loop_health_score(
        self, lag_ms: float, task_count: int, pending_callbacks: int
    ) -> float:
        """Calculate event loop health score (0.0 to 1.0)."""
        # Lag component (0.5 weight)
        lag_score = max(0, 1.0 - (lag_ms / (self.lag_threshold_ms * 2))) * 0.5

        # Task count component (0.3 weight)
        task_score = max(0, 1.0 - (task_count / 200)) * 0.3

        # Pending callbacks component (0.2 weight)
        callback_score = max(0, 1.0 - (pending_callbacks / 100)) * 0.2

        return max(0.0, min(lag_score + task_score + callback_score, 1.0))

    def _generate_performance_recommendations(
        self, lag_ms: float, task_count: int, is_saturated: bool
    ) -> List[str]:
        """Generate performance recommendations based on metrics."""
        recommendations = []

        if lag_ms > self.lag_threshold_ms:
            if lag_ms > self.lag_threshold_ms * 2:
                recommendations.append(
                    "CRITICAL: Event loop lag excessive - consider scaling down"
                )
            else:
                recommendations.append("WARNING: Event loop lag high - monitor closely")

        if task_count > 100:
            recommendations.append("High task count - may need to reduce worker load")

        if is_saturated:
            recommendations.append(
                "Event loop saturated - recommend scaling down workers"
            )
        elif lag_ms < self.lag_threshold_ms * 0.5 and task_count < 50:
            recommendations.append("Event loop healthy - can potentially scale up")

        if not recommendations:
            recommendations.append("Event loop performance normal")

        return recommendations

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get event loop performance summary."""
        if not _performance_history:
            return {"status": "No performance data available"}

        recent_metrics = list(_performance_history)[-10:]  # Last 10 measurements

        # Calculate averages
        avg_lag = sum(m.loop_lag_ms for m in recent_metrics) / len(recent_metrics)
        avg_tasks = sum(m.active_task_count for m in recent_metrics) / len(
            recent_metrics
        )
        avg_health = sum(m.health_score for m in recent_metrics) / len(recent_metrics)

        # Count issues
        saturated_count = sum(1 for m in recent_metrics if m.is_saturated)
        lag_violations = sum(
            1 for m in recent_metrics if m.loop_lag_ms > self.lag_threshold_ms
        )

        return {
            "monitoring_active": _monitoring_active,
            "total_measurements": self.total_measurements,
            "recent_measurements": len(recent_metrics),
            "averages": {
                "loop_lag_ms": avg_lag,
                "active_task_count": avg_tasks,
                "health_score": avg_health,
            },
            "issues": {
                "saturated_measurements": saturated_count,
                "lag_violations": lag_violations,
                "total_lag_violations": self.lag_violations,
                "violation_rate": (
                    (self.lag_violations / self.total_measurements)
                    if self.total_measurements > 0
                    else 0
                ),
            },
            "latest_metrics": recent_metrics[-1] if recent_metrics else None,
        }

    def get_scaling_recommendation(self) -> Dict[str, Any]:
        """Get scaling recommendation based on event loop performance."""
        if len(_performance_history) < 3:
            return {
                "recommendation": "maintain",
                "confidence": 0.3,
                "reason": "Insufficient event loop performance data",
            }

        # Analyze recent performance
        recent_metrics = list(_performance_history)[-5:]  # Last 5 measurements

        # Check for consistent problems
        saturated_count = sum(1 for m in recent_metrics if m.is_saturated)
        high_lag_count = sum(
            1 for m in recent_metrics if m.loop_lag_ms > self.lag_threshold_ms
        )
        avg_health = sum(m.health_score for m in recent_metrics) / len(recent_metrics)

        # Make scaling decision
        if saturated_count >= 3 or high_lag_count >= 4:
            return {
                "recommendation": "scale_down",
                "confidence": 0.8,
                "reason": f"Event loop consistently saturated ({saturated_count}/5 measurements)",
            }
        elif avg_health > 0.8 and high_lag_count == 0:
            return {
                "recommendation": "scale_up",
                "confidence": 0.6,
                "reason": f"Event loop healthy (avg health: {avg_health:.2f})",
            }
        else:
            return {
                "recommendation": "maintain",
                "confidence": 0.7,
                "reason": f"Event loop performance stable (health: {avg_health:.2f})",
            }


# Global monitor instance
_global_monitor = None


def get_event_loop_monitor() -> EventLoopPerformanceMonitor:
    """Get or create global event loop monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = EventLoopPerformanceMonitor()
    return _global_monitor


async def start_event_loop_monitoring(interval_seconds: float = 2.0) -> None:
    """Start global event loop monitoring."""
    monitor = get_event_loop_monitor()
    await monitor.start_monitoring(interval_seconds)


async def stop_event_loop_monitoring() -> None:
    """Stop global event loop monitoring."""
    monitor = get_event_loop_monitor()
    await monitor.stop_monitoring()


def get_event_loop_performance_summary() -> Dict[str, Any]:
    """Get event loop performance summary."""
    monitor = get_event_loop_monitor()
    return monitor.get_performance_summary()


def get_event_loop_scaling_recommendation() -> Dict[str, Any]:
    """Get scaling recommendation based on event loop performance."""
    monitor = get_event_loop_monitor()
    return monitor.get_scaling_recommendation()


async def measure_current_event_loop_lag() -> float:
    """Measure current event loop lag in milliseconds."""
    lag_start = time.perf_counter()
    await asyncio.sleep(0)  # Yield control
    lag_end = time.perf_counter()
    return (lag_end - lag_start) * 1000


def is_event_loop_monitoring_active() -> bool:
    """Check if event loop monitoring is currently active."""
    return _monitoring_active


def log_slow_callback(callback_name: str, duration_ms: float) -> None:
    """Log a slow callback for analysis."""
    severity = "critical" if duration_ms > 500 else "warning"

    slow_callback = SlowCallback(
        timestamp=time.time(),
        duration_ms=duration_ms,
        callback_name=callback_name,
        severity=severity,
    )

    _slow_callbacks.append(slow_callback)

    if severity == "critical":
        logger.warning(
            f"Critical slow callback: {callback_name} took {duration_ms:.1f}ms"
        )


def get_slow_callbacks_summary() -> Dict[str, Any]:
    """Get summary of slow callbacks detected."""
    if not _slow_callbacks:
        return {"status": "No slow callbacks detected"}

    recent_callbacks = list(_slow_callbacks)[-10:]

    return {
        "total_slow_callbacks": len(_slow_callbacks),
        "recent_callbacks": len(recent_callbacks),
        "critical_callbacks": len(
            [c for c in recent_callbacks if c.severity == "critical"]
        ),
        "warning_callbacks": len(
            [c for c in recent_callbacks if c.severity == "warning"]
        ),
        "latest_callbacks": [
            {
                "name": c.callback_name,
                "duration_ms": c.duration_ms,
                "severity": c.severity,
                "timestamp": c.timestamp,
            }
            for c in recent_callbacks
        ],
    }
