#!/usr/bin/env python3
"""
Step 2: Core Adaptive Scaling Engine - Function-based Implementation

This module provides adaptive worker scaling functionality using the enhanced intelligence
layer from Step 1. Converts the class-based optimization/phase_3 logic into functions.

Features:
- Performance-based scaling with trend analysis
- Resource availability monitoring with safety limits
- Dynamic scaling decisions with confidence scoring
- Integration with enhanced intelligence layer
- Function-based architecture for consistency

Author: AI Assistant
Date: August 2025
"""

import asyncio
import time

try:
    from config import ScraperConfig
except ImportError:
    # Fallback for standalone execution
    class ScraperConfig:
        SCALING_MONITOR_INTERVAL = 20.0
        ADAPTIVE_SCALING_INTERVAL = 30.0


try:
    from config import (
        get_enhanced_config as get_dynamic_config,
    )  # Alias for compatibility

    ENHANCED_CONFIG_AVAILABLE = True
except ImportError:
    ENHANCED_CONFIG_AVAILABLE = False


import statistics
import psutil
import os
from collections import deque
from dataclasses import dataclass, asdict
from typing import Dict, Any
from datetime import datetime

# Import from our enhanced intelligence layer (conditional)
try:
    from enhanced_metrics import collect_predictive_metrics
    from resource_monitor import take_quick_resource_snapshot
    from event_loop_monitor import get_event_loop_monitor

    ENHANCED_MODULES_AVAILABLE = True
except ImportError:
    ENHANCED_MODULES_AVAILABLE = False


# Global state for adaptive scaling engine
_performance_history: deque = deque(maxlen=100)
_scaling_history: deque = deque(maxlen=50)
_last_scaling_time: float = 0.0
_current_worker_count: int = 50  # Start with proactive scaling initial value
_scaling_config: Dict[str, Any] = {}


def initialize_adaptive_scaling() -> Dict[str, Any]:
    """Initialize the adaptive scaling system. Alias for initialize_scaling_config."""
    return initialize_scaling_config()


# Initialize default scaling configuration
def initialize_scaling_config() -> Dict[str, Any]:
    """Initialize proactive adaptive scaling configuration for maximum output."""
    return {
        # Proactive Worker Range Configuration (20-200, starting at 50)
        "min_workers": 20,  # Minimum workers for baseline performance
        "max_workers": 200,  # Maximum workers for peak load (updated from 100)
        "initial_workers": 50,  # Starting worker count for immediate capacity
        # Proactive Performance Thresholds (aggressive scaling up)
        "scale_up_success_rate_threshold": 0.90,  # Scale up more aggressively
        "scale_down_success_rate_threshold": 0.80,  # More conservative scale down
        "scale_up_response_time_threshold": 1.5,  # Scale up faster on slower response
        "scale_down_response_time_threshold": 6.0,  # More tolerant before scaling down
        # Safe Resource Thresholds (stay within limits)
        "max_memory_usage_percent": 85.0,
        "max_cpu_usage_percent": 90.0,
        "scale_down_memory_threshold": 60.0,
        "scale_down_cpu_threshold": 70.0,
        # Proactive Scaling Behavior (centralized configuration)
        "scale_up_increment": 10,  # Scale up by 10 workers (matches enhanced config)
        "scale_down_increment": 5,  # Scale down by 5 workers (matches enhanced config)
        "scaling_cooldown_seconds": 45.0,  # Shorter cooldown for responsiveness
        # Monitoring Intervals (more frequent monitoring)
        "monitoring_interval": ScraperConfig.SCALING_MONITOR_INTERVAL,  # Check every 20 seconds
        "optimization_interval": 180.0,  # Optimize every 3 minutes
        # Proactive Safety Limits
        "emergency_scale_down_threshold": 95.0,  # CPU/Memory %
        "max_scale_up_per_interval": 10,  # Allow larger scale ups
        "max_scale_down_per_interval": 5,  # Control scale downs
        # Performance History
        "performance_history_size": 100,
        "trend_analysis_window_minutes": 15,
    }


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics for scaling decisions."""

    timestamp: float
    pages_per_second: float = 0.0
    avg_page_load_time: float = 0.0
    success_rate: float = 1.0
    error_rate: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    browser_pool_utilization: float = 0.0
    worker_utilization: float = 0.0
    queue_depth: int = 0
    active_connections: int = 0
    network_io_mb_per_sec: float = 0.0
    disk_io_mb_per_sec: float = 0.0
    resource_blocking_efficiency: float = 0.0
    cache_hit_ratio: float = 0.0

    def calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-1, higher is better)."""
        # Weighted scoring components
        success_weight = 0.3
        speed_weight = 0.25
        efficiency_weight = 0.2
        resource_weight = 0.15
        stability_weight = 0.1

        # Success score
        success_score = self.success_rate

        # Speed score (inverse of page load time, normalized to 0-1)
        speed_score = max(0, min(1, 1 - (self.avg_page_load_time / 30.0)))

        # Efficiency score (combination of resource blocking and cache hits)
        efficiency_score = (
            self.resource_blocking_efficiency + self.cache_hit_ratio
        ) / 2.0

        # Resource utilization score (optimal around 70-80%)
        optimal_utilization = 0.75
        utilization_avg = (
            self.browser_pool_utilization + self.worker_utilization
        ) / 2.0
        resource_score = (
            1.0 - abs(utilization_avg - optimal_utilization) / optimal_utilization
        )

        # Stability score (low error rate)
        stability_score = 1.0 - self.error_rate

        # Calculate weighted final score
        final_score = (
            success_score * success_weight
            + speed_score * speed_weight
            + efficiency_score * efficiency_weight
            + resource_score * resource_weight
            + stability_score * stability_weight
        )

        return max(0, min(1, final_score))


@dataclass
class ResourceAvailability:
    """System resource availability metrics for scaling decisions."""

    timestamp: float
    total_memory_gb: float = 0.0
    available_memory_gb: float = 0.0
    memory_usage_percent: float = 0.0
    cpu_count: int = 0
    cpu_usage_percent: float = 0.0
    cpu_load_avg: float = 0.0
    disk_free_gb: float = 0.0
    disk_usage_percent: float = 0.0
    network_bandwidth_mbps: float = 0.0
    active_processes: int = 0
    system_load_level: str = "normal"  # low, normal, high, critical

    def calculate_scaling_capacity(self) -> float:
        """Calculate how much scaling headroom is available (0-1)."""
        memory_headroom = max(0, (100 - self.memory_usage_percent) / 100)
        cpu_headroom = max(0, (100 - self.cpu_usage_percent) / 100)
        disk_headroom = max(0, (100 - self.disk_usage_percent) / 100)

        # Weighted average with memory being most important
        capacity = memory_headroom * 0.5 + cpu_headroom * 0.3 + disk_headroom * 0.2

        return max(0, min(1, capacity))

    def is_safe_to_scale_up(self) -> bool:
        """Determine if it's safe to scale up workers."""
        return (
            self.memory_usage_percent < 80
            and self.cpu_usage_percent < 85
            and self.disk_usage_percent < 90
            and self.system_load_level in ["low", "normal"]
        )

    def requires_scale_down(self) -> bool:
        """Determine if we must scale down due to resource pressure."""
        return (
            self.memory_usage_percent > 90
            or self.cpu_usage_percent > 95
            or self.disk_usage_percent > 95
            or self.system_load_level == "critical"
        )


@dataclass
class ScalingDecision:
    """Represents a scaling decision with reasoning."""

    timestamp: float
    action: str  # "scale_up", "scale_down", "no_change"
    current_workers: int
    target_workers: int
    reasoning: str
    confidence: float
    performance_score: float
    resource_capacity: float
    safety_override: bool = False


def get_scaling_config() -> Dict[str, Any]:
    """Get the current scaling configuration, integrating with enhanced config manager."""
    global _scaling_config
    if not _scaling_config:
        _scaling_config = initialize_scaling_config()

        # INTEGRATION: Override with enhanced config manager values if available
        if ENHANCED_CONFIG_AVAILABLE:
            try:
                enhanced_config = get_dynamic_config()
                if enhanced_config:
                    # Override scaling increments with centralized config
                    if "worker_scale_increment" in enhanced_config:
                        _scaling_config["scale_up_increment"] = enhanced_config[
                            "worker_scale_increment"
                        ]
                    if "worker_scale_decrement" in enhanced_config:
                        _scaling_config["scale_down_increment"] = enhanced_config[
                            "worker_scale_decrement"
                        ]

                    print(
                        f"🔧 ADAPTIVE SCALING: Integrated enhanced config - "
                        f"scale_up_increment={_scaling_config['scale_up_increment']}, "
                        f"scale_down_increment={_scaling_config['scale_down_increment']}"
                    )
            except Exception as e:
                print(
                    f"WARNING: ADAPTIVE SCALING: Failed to integrate enhanced config: {e}"
                )

    return _scaling_config


def update_scaling_config(updates: Dict[str, Any]) -> None:
    """Update scaling configuration with new values."""
    global _scaling_config
    config = get_scaling_config()
    config.update(updates)
    _scaling_config = config


def collect_performance_metrics() -> PerformanceMetrics:
    """
    Collect comprehensive performance metrics from enhanced intelligence layer.

    Returns:
        PerformanceMetrics object with current system performance
    """
    current_time = time.time()

    # Get enhanced metrics from Step 1
    try:
        enhanced_metrics = collect_predictive_metrics()

        # Extract performance data
        pages_per_second = enhanced_metrics.get("performance_efficiency", {}).get(
            "pages_per_second", 0.0
        )
        success_rate = enhanced_metrics.get("success_count", 0) / max(
            1, enhanced_metrics.get("pages_processed", 1)
        )
        error_rate = enhanced_metrics.get("error_count", 0) / max(
            1, enhanced_metrics.get("pages_processed", 1)
        )
        memory_usage_mb = enhanced_metrics.get("memory_usage_mb", 0.0)

        # Get additional system metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Calculate derived metrics
        avg_page_load_time = enhanced_metrics.get("processing_time_ms", 0) / 1000.0
        browser_pool_utilization = min(
            1.0, enhanced_metrics.get("browser_pool_size", 0) / 10.0
        )
        worker_utilization = min(
            1.0,
            enhanced_metrics.get("active_workers", 0)
            / max(1, get_current_worker_count()),
        )

        return PerformanceMetrics(
            timestamp=current_time,
            pages_per_second=pages_per_second,
            avg_page_load_time=avg_page_load_time,
            success_rate=success_rate,
            error_rate=error_rate,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_percent,
            browser_pool_utilization=browser_pool_utilization,
            worker_utilization=worker_utilization,
            queue_depth=enhanced_metrics.get("queue_size", 0),
            active_connections=enhanced_metrics.get("browser_instances", 0),
            resource_blocking_efficiency=enhanced_metrics.get(
                "resource_block_rate", 0.0
            ),
            cache_hit_ratio=enhanced_metrics.get("cache_hits", 0)
            / max(
                1,
                enhanced_metrics.get("cache_hits", 0)
                + enhanced_metrics.get("cache_misses", 1),
            ),
        )

    except Exception:
        # Fallback to basic metrics if enhanced metrics fail
        return PerformanceMetrics(
            timestamp=current_time,
            pages_per_second=0.0,
            avg_page_load_time=1.0,
            success_rate=0.9,
            cpu_usage_percent=psutil.cpu_percent(interval=0.1),
            memory_usage_mb=psutil.virtual_memory().used / 1024 / 1024,
        )


def collect_resource_availability() -> ResourceAvailability:
    """
    Collect system resource availability metrics.

    Returns:
        ResourceAvailability object with current system resources
    """
    current_time = time.time()

    try:
        # Get system resource information
        memory = psutil.virtual_memory()
        cpu_count = psutil.cpu_count()
        cpu_percent = psutil.cpu_percent(interval=0.1)

        # Disk usage (cross-platform)
        try:
            if os.name == "nt":  # Windows
                disk = psutil.disk_usage("C:\\")
            else:  # Unix-like systems
                disk = psutil.disk_usage("/")
        except Exception:

            class MockDisk:
                total = 1024**3  # 1GB fallback
                free = 512**3  # 512MB fallback
                percent = 50.0

            disk = MockDisk()

        # Load average (Unix-like systems)
        try:
            load_avg = (
                psutil.getloadavg()[0]
                if hasattr(psutil, "getloadavg")
                else cpu_percent / 100.0
            )
        except Exception:
            load_avg = cpu_percent / 100.0

        # Determine system load level
        system_load_level = "normal"
        if memory.percent > 90 or cpu_percent > 90:
            system_load_level = "critical"
        elif memory.percent > 80 or cpu_percent > 80:
            system_load_level = "high"
        elif memory.percent < 50 and cpu_percent < 50:
            system_load_level = "low"

        return ResourceAvailability(
            timestamp=current_time,
            total_memory_gb=memory.total / 1024**3,
            available_memory_gb=memory.available / 1024**3,
            memory_usage_percent=memory.percent,
            cpu_count=cpu_count,
            cpu_usage_percent=cpu_percent,
            cpu_load_avg=load_avg,
            disk_free_gb=disk.free / 1024**3,
            disk_usage_percent=disk.percent,
            network_bandwidth_mbps=100.0,  # Default assumption
            active_processes=len(psutil.pids()),
            system_load_level=system_load_level,
        )

    except Exception:
        # Fallback minimal resource info
        return ResourceAvailability(
            timestamp=current_time,
            total_memory_gb=16.0,  # Reasonable default
            available_memory_gb=8.0,
            memory_usage_percent=50.0,
            cpu_count=4,
            cpu_usage_percent=25.0,
            system_load_level="normal",
        )


def analyze_performance_trends_for_scaling(
    lookback_minutes: int = 15,
) -> Dict[str, Any]:
    """
    Analyze performance trends from history to inform scaling decisions.

    Args:
        lookback_minutes: How far back to look for trend analysis

    Returns:
        Dictionary with trend analysis results
    """
    if len(_performance_history) < 3:
        return {
            "status": "insufficient_data",
            "trend_direction": "stable",
            "confidence": 0.0,
            "recommendation": "no_change",
        }

    # Get recent performance data
    cutoff_time = time.time() - (lookback_minutes * 60)
    recent_metrics = [m for m in _performance_history if m.timestamp > cutoff_time]

    if len(recent_metrics) < 2:
        return {
            "status": "insufficient_recent_data",
            "trend_direction": "stable",
            "confidence": 0.0,
            "recommendation": "no_change",
        }

    # Calculate trends
    performance_scores = [m.calculate_performance_score() for m in recent_metrics]
    success_rates = [m.success_rate for m in recent_metrics]
    response_times = [m.avg_page_load_time for m in recent_metrics]

    # Linear trend analysis
    def calculate_trend(values):
        if len(values) < 2:
            return 0.0
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    performance_trend = calculate_trend(performance_scores)
    success_trend = calculate_trend(success_rates)
    response_time_trend = calculate_trend(response_times)

    # Determine overall trend direction
    if performance_trend > 0.05 and success_trend > 0.02:
        trend_direction = "improving"
        recommendation = "scale_up" if performance_trend > 0.1 else "maintain"
    elif performance_trend < -0.05 or success_trend < -0.02:
        trend_direction = "declining"
        recommendation = "scale_down" if performance_trend < -0.1 else "maintain"
    else:
        trend_direction = "stable"
        recommendation = "maintain"

    # Calculate confidence based on data consistency
    performance_variance = (
        statistics.variance(performance_scores) if len(performance_scores) > 1 else 0.0
    )
    confidence = max(0.0, min(1.0, 1.0 - performance_variance))

    return {
        "status": "analyzed",
        "trend_direction": trend_direction,
        "performance_trend": performance_trend,
        "success_trend": success_trend,
        "response_time_trend": response_time_trend,
        "confidence": confidence,
        "recommendation": recommendation,
        "data_points": len(recent_metrics),
        "analysis_window_minutes": lookback_minutes,
    }


def make_scaling_decision_simple(metrics_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simplified scaling decision function for testing and simple use cases.

    Args:
        metrics_dict: Dictionary with performance metrics

    Returns:
        Dictionary with scaling decision
    """
    try:
        # Convert simple metrics to structured format
        performance_metrics = PerformanceMetrics(
            timestamp=time.time(),
            success_rate=metrics_dict.get("success_rate", 1.0),
            avg_page_load_time=metrics_dict.get(
                "avg_processing_time", 2.0
            ),  # Convert to seconds
            error_rate=metrics_dict.get("error_rate", 0.0),
            worker_utilization=metrics_dict.get("worker_utilization", 0.0),
            queue_depth=metrics_dict.get("queue_length", 0),
            pages_per_second=metrics_dict.get("throughput", 0.0),
            cpu_usage_percent=metrics_dict.get("cpu_usage_percent", 50.0),
            memory_usage_mb=metrics_dict.get("memory_usage_mb", 500.0),
        )

        resource_availability = ResourceAvailability(
            timestamp=time.time(),
            cpu_usage_percent=metrics_dict.get("cpu_usage_percent", 50.0),
            memory_usage_percent=metrics_dict.get("memory_usage_percent", 50.0),
            available_memory_gb=2.0,  # Convert MB to GB approximation
            disk_usage_percent=50.0,
            network_bandwidth_mbps=30.0,
        )

        trend_analysis = {
            "performance_trend": "stable",
            "resource_trend": "stable",
            "recommendation": "no_change",  # Required field
            "confidence": 0.8,
            "trend_direction": "stable",
        }

        # Make the actual scaling decision
        decision = make_scaling_decision(
            performance_metrics, resource_availability, trend_analysis
        )

        # Convert to simple dictionary format
        return {
            "action": decision.action,
            "target_workers": decision.target_workers,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
        }

    except Exception as e:
        # Return safe default decision
        return {
            "action": "no_change",
            "target_workers": metrics_dict.get("active_workers", 5),
            "confidence": 0.0,
            "reasoning": f"Error in decision making: {str(e)}",
        }


def make_scaling_decision(
    performance_metrics: PerformanceMetrics,
    resource_availability: ResourceAvailability,
    trend_analysis: Dict[str, Any],
) -> ScalingDecision:
    """
    Make an intelligent scaling decision based on all available data.

    Args:
        performance_metrics: Current performance metrics
        resource_availability: Current resource availability
        trend_analysis: Performance trend analysis results

    Returns:
        ScalingDecision with recommended action
    """
    config = get_scaling_config()
    current_workers = get_current_worker_count()
    current_time = time.time()

    # Check cooldown period
    time_since_last_scaling = current_time - _last_scaling_time
    if time_since_last_scaling < config["scaling_cooldown_seconds"]:
        return ScalingDecision(
            timestamp=current_time,
            action="no_change",
            current_workers=current_workers,
            target_workers=current_workers,
            reasoning=f"Cooldown period active ({time_since_last_scaling:.1f}s remaining)",
            confidence=1.0,
            performance_score=performance_metrics.calculate_performance_score(),
            resource_capacity=resource_availability.calculate_scaling_capacity(),
        )

    # Emergency scale down check
    if resource_availability.requires_scale_down():
        target_workers = max(
            config["min_workers"],
            current_workers - config["max_scale_down_per_interval"],
        )
        return ScalingDecision(
            timestamp=current_time,
            action="scale_down",
            current_workers=current_workers,
            target_workers=target_workers,
            reasoning="Emergency scale down due to resource pressure",
            confidence=1.0,
            performance_score=performance_metrics.calculate_performance_score(),
            resource_capacity=resource_availability.calculate_scaling_capacity(),
            safety_override=True,
        )

    # Calculate performance and resource scores
    performance_score = performance_metrics.calculate_performance_score()
    resource_capacity = resource_availability.calculate_scaling_capacity()

    # Determine scaling action based on multiple factors
    scale_up_signals = 0
    scale_down_signals = 0
    reasoning_parts = []

    # Performance-based signals
    if performance_metrics.success_rate >= config["scale_up_success_rate_threshold"]:
        scale_up_signals += 1
        reasoning_parts.append(
            f"High success rate ({performance_metrics.success_rate:.2f})"
        )
    elif (
        performance_metrics.success_rate <= config["scale_down_success_rate_threshold"]
    ):
        scale_down_signals += 1
        reasoning_parts.append(
            f"Low success rate ({performance_metrics.success_rate:.2f})"
        )

    # Response time signals
    if (
        performance_metrics.avg_page_load_time
        <= config["scale_up_response_time_threshold"]
    ):
        scale_up_signals += 1
        reasoning_parts.append(
            f"Fast response time ({performance_metrics.avg_page_load_time:.1f}s)"
        )
    elif (
        performance_metrics.avg_page_load_time
        >= config["scale_down_response_time_threshold"]
    ):
        scale_down_signals += 1
        reasoning_parts.append(
            f"Slow response time ({performance_metrics.avg_page_load_time:.1f}s)"
        )

    # Resource availability signals
    if resource_availability.is_safe_to_scale_up() and resource_capacity > 0.3:
        scale_up_signals += 1
        reasoning_parts.append(f"Resources available ({resource_capacity:.1%})")
    elif resource_capacity < 0.2:
        scale_down_signals += 1
        reasoning_parts.append(f"Low resource availability ({resource_capacity:.1%})")

    # Trend analysis signals
    if (
        trend_analysis["recommendation"] == "scale_up"
        and trend_analysis["confidence"] > 0.6
    ):
        scale_up_signals += 1
        reasoning_parts.append(
            f"Positive performance trend ({trend_analysis['trend_direction']})"
        )
    elif (
        trend_analysis["recommendation"] == "scale_down"
        and trend_analysis["confidence"] > 0.6
    ):
        scale_down_signals += 1
        reasoning_parts.append(
            f"Negative performance trend ({trend_analysis['trend_direction']})"
        )

    # Make final decision
    if scale_up_signals > scale_down_signals and scale_up_signals >= 2:
        action = "scale_up"
        target_workers = min(
            config["max_workers"], current_workers + config["scale_up_increment"]
        )
        confidence = min(1.0, scale_up_signals / 4.0)
    elif scale_down_signals > scale_up_signals and scale_down_signals >= 2:
        action = "scale_down"
        target_workers = max(
            config["min_workers"], current_workers - config["scale_down_increment"]
        )
        confidence = min(1.0, scale_down_signals / 4.0)
    else:
        action = "no_change"
        target_workers = current_workers
        confidence = 0.8
        reasoning_parts.append("Balanced signals - maintaining current level")

    reasoning = (
        "; ".join(reasoning_parts) if reasoning_parts else "No clear scaling signals"
    )

    return ScalingDecision(
        timestamp=current_time,
        action=action,
        current_workers=current_workers,
        target_workers=target_workers,
        reasoning=reasoning,
        confidence=confidence,
        performance_score=performance_score,
        resource_capacity=resource_capacity,
    )


def execute_scaling_decision(decision: ScalingDecision) -> bool:
    """
    Execute a scaling decision by updating worker count.

    Args:
        decision: The scaling decision to execute

    Returns:
        bool: True if scaling was successful, False otherwise
    """
    global _current_worker_count, _last_scaling_time

    if decision.action == "no_change":
        return True

    # Validate target worker count
    config = get_scaling_config()
    if not (config["min_workers"] <= decision.target_workers <= config["max_workers"]):
        return False

    # Update global state
    old_count = _current_worker_count
    _current_worker_count = decision.target_workers
    _last_scaling_time = decision.timestamp

    # Store decision in history
    _scaling_history.append(decision)

    # Log the scaling action
    print(
        f"🔄 Scaling {decision.action}: {old_count} → {decision.target_workers} workers"
    )
    print(f"   Reason: {decision.reasoning}")
    print(f"   Confidence: {decision.confidence:.2f}")

    return True


def get_current_worker_count() -> int:
    """Get the current worker count."""
    global _current_worker_count
    if _current_worker_count <= 0:
        _current_worker_count = get_scaling_config()["initial_workers"]
    return _current_worker_count


def set_current_worker_count(count: int) -> None:
    """Set the current worker count."""
    global _current_worker_count
    config = get_scaling_config()
    _current_worker_count = max(
        config["min_workers"], min(config["max_workers"], count)
    )


def get_scaling_status() -> Dict[str, Any]:
    """
    Get comprehensive status of the adaptive scaling engine.

    Returns:
        Dictionary with current scaling status and metrics
    """
    current_time = time.time()
    config = get_scaling_config()

    # Get latest metrics if available
    latest_performance = None
    latest_resources = None

    try:
        latest_performance = collect_performance_metrics()
        latest_resources = collect_resource_availability()
    except Exception:
        pass

    # Calculate runtime
    runtime_seconds = current_time - _last_scaling_time if _last_scaling_time > 0 else 0

    status = {
        "timestamp": current_time,
        "datetime": datetime.now().isoformat(),
        "runtime_seconds": runtime_seconds,
        "runtime_formatted": f"{runtime_seconds/60:.1f} minutes",
        # Current state
        "current_workers": get_current_worker_count(),
        "min_workers": config["min_workers"],
        "max_workers": config["max_workers"],
        "scaling_active": True,
        # Recent performance
        "latest_performance": (
            asdict(latest_performance) if latest_performance else None
        ),
        "latest_resources": asdict(latest_resources) if latest_resources else None,
        # History stats
        "performance_history_size": len(_performance_history),
        "scaling_decisions_made": len(_scaling_history),
        "last_scaling_time": _last_scaling_time,
        "time_since_last_scaling": (
            current_time - _last_scaling_time if _last_scaling_time > 0 else 0
        ),
        # Configuration
        "config": config.copy(),
    }

    # Add recent scaling decisions
    if _scaling_history:
        status["recent_scaling_decisions"] = [
            asdict(decision) for decision in list(_scaling_history)[-5:]
        ]

    return status


def run_adaptive_scaling_cycle() -> ScalingDecision:
    """
    Run a complete adaptive scaling cycle.

    Returns:
        ScalingDecision made in this cycle
    """
    # Collect current metrics
    performance_metrics = collect_performance_metrics()
    resource_availability = collect_resource_availability()

    # Store performance metrics in history
    _performance_history.append(performance_metrics)

    # Analyze trends
    trend_analysis = analyze_performance_trends_for_scaling()

    # Make scaling decision
    decision = make_scaling_decision(
        performance_metrics, resource_availability, trend_analysis
    )

    # Execute the decision
    execute_scaling_decision(decision)

    return decision


async def start_adaptive_scaling_monitor(interval_seconds: float = None) -> None:
    """
    Start the adaptive scaling monitor that runs scaling cycles continuously.

    Args:
        interval_seconds: How often to run scaling cycles
    """
    if interval_seconds is None:
        interval_seconds = ScraperConfig.ADAPTIVE_SCALING_INTERVAL

    print(f"🚀 Starting adaptive scaling monitor (interval: {interval_seconds}s)")

    cycle_count = 0
    try:
        while True:
            cycle_count += 1
            print(f"\n📊 Scaling Cycle #{cycle_count}")

            try:
                decision = run_adaptive_scaling_cycle()

                if decision.action != "no_change":
                    print(
                        f"   🔄 Action: {decision.action} ({decision.confidence:.2f} confidence)"
                    )
                    print(f"   📈 Performance Score: {decision.performance_score:.3f}")
                    print(f"   💾 Resource Capacity: {decision.resource_capacity:.1%}")
                else:
                    print(f"   ✅ Maintaining {decision.current_workers} workers")

            except Exception as e:
                print(f"   ❌ Scaling cycle failed: {e}")

            await asyncio.sleep(interval_seconds)

    except KeyboardInterrupt:
        print(f"\n🛑 Adaptive scaling monitor stopped after {cycle_count} cycles")
    except Exception as e:
        print(f"\n💥 Adaptive scaling monitor crashed: {e}")


def print_scaling_status() -> None:
    """Print current adaptive scaling status to console."""
    status = get_scaling_status()

    print("\n" + "=" * 80)
    print("ADAPTIVE SCALING ENGINE STATUS")
    print("=" * 80)

    print(f"Runtime: {status['runtime_formatted']}")
    print(
        f"Current Workers: {status['current_workers']} (range: {status['min_workers']}-{status['max_workers']})"
    )
    print(f"Scaling Decisions Made: {status['scaling_decisions_made']}")
    print(f"Performance History: {status['performance_history_size']} entries")

    # Show latest performance if available
    if status["latest_performance"]:
        perf = status["latest_performance"]
        print("\nLatest Performance:")
        print(f"  Success Rate: {perf['success_rate']:.1%}")
        print(f"  Avg Response Time: {perf['avg_page_load_time']:.2f}s")
        print(f"  Performance Score: {perf.get('performance_score', 'N/A')}")

    # Show latest resources if available
    if status["latest_resources"]:
        res = status["latest_resources"]
        print("\nSystem Resources:")
        print(f"  Memory Usage: {res['memory_usage_percent']:.1f}%")
        print(f"  CPU Usage: {res['cpu_usage_percent']:.1f}%")
        print(f"  System Load: {res['system_load_level']}")

    # Show recent decisions
    if status.get("recent_scaling_decisions"):
        print("\nRecent Scaling Decisions:")
        for decision in status["recent_scaling_decisions"][-3:]:
            action_emoji = {"scale_up": "⬆️", "scale_down": "⬇️", "no_change": "➡️"}
            emoji = action_emoji.get(decision["action"], "❓")
            action = decision["action"]
            confidence = decision["confidence"]
            reasoning = decision["reasoning"][:60]
            print(f"  {emoji} {action} ({confidence:.2f}) - {reasoning}...")


# Initialize the scaling engine
def initialize_adaptive_scaling_engine() -> Dict[str, Any]:
    """Initialize the adaptive scaling engine with default configuration."""
    global _scaling_config, _current_worker_count

    if not _scaling_config:
        _scaling_config = initialize_scaling_config()

    if _current_worker_count <= 0:
        _current_worker_count = _scaling_config["initial_workers"]

    print("🎯 Adaptive Scaling Engine initialized")
    print(
        f"   Workers: {_current_worker_count} (range: {_scaling_config['min_workers']}-{_scaling_config['max_workers']})"
    )
    print(f"   Monitoring interval: {_scaling_config['monitoring_interval']}s")

    return {
        "status": "initialized",
        "initial_workers": _current_worker_count,
        "config": _scaling_config.copy(),
    }
