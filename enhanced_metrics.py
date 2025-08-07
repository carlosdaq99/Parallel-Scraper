#!/usr/bin/env python3
"""
Enhanced Metrics Collection - Extension of existing optimization metrics
Provides sophisticated performance analytics and trend analysis for adaptive scaling.

Builds on existing functions:
- collect_advanced_metrics() from advanced_optimization_utils.py
- get_optimization_metrics() from optimization_utils.py

Features:
- Performance trend analysis with statistical modeling
- Bottleneck identification and scaling recommendations
- Predictive metrics for proactive scaling decisions
- Enhanced timing breakdown and efficiency tracking
"""

import time
import statistics
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from collections import deque
from datetime import datetime

# Import existing optimization metrics functions
from advanced_optimization_utils import collect_advanced_metrics
from optimization_utils import get_optimization_metrics

# Performance history storage
_performance_history = deque(maxlen=1000)
_trend_analysis_cache = {}
_bottleneck_detection_history = deque(maxlen=100)


@dataclass
class TimingBreakdown:
    """Detailed timing metrics breakdown."""

    total_time_ms: float
    page_load_time_ms: float = 0.0
    resource_blocking_time_ms: float = 0.0
    browser_launch_time_ms: float = 0.0
    content_extraction_time_ms: float = 0.0
    cleanup_time_ms: float = 0.0
    queue_wait_time_ms: float = 0.0
    network_time_ms: float = 0.0
    dom_processing_time_ms: float = 0.0
    overhead_time_ms: float = 0.0


@dataclass
class TrendAnalysis:
    """Performance trend analysis results."""

    metric_name: str
    current_value: float
    trend_direction: str  # 'improving', 'degrading', 'stable'
    trend_strength: float  # 0.0 to 1.0
    predicted_next_value: float
    confidence_level: float  # 0.0 to 1.0
    recommendation: str


@dataclass
class BottleneckDetection:
    """Bottleneck identification results."""

    bottleneck_type: str  # 'memory', 'cpu', 'browser_pool', 'network'
    severity: str  # 'low', 'medium', 'high', 'critical'
    impact_score: float  # 0.0 to 1.0
    description: str
    scaling_recommendation: str


@dataclass
class ScalingRecommendation:
    """Scaling decision recommendation."""

    action: str  # 'scale_up', 'scale_down', 'maintain'
    confidence: float  # 0.0 to 1.0
    target_workers: int
    reasoning: str
    expected_improvement: str


def collect_predictive_metrics() -> Dict[str, Any]:
    """
    Collect enhanced metrics with predictive analysis.

    Extends existing metrics with trend analysis and scaling recommendations.
    """
    # Get base metrics from existing functions
    base_metrics_obj = collect_advanced_metrics()
    optimization_metrics = get_optimization_metrics()

    # Convert AdvancedMetrics dataclass to dictionary
    from dataclasses import asdict

    base_metrics = asdict(base_metrics_obj)

    # Combine base metrics
    combined_metrics = {**base_metrics, **optimization_metrics}

    # Add timestamp for trend analysis
    combined_metrics["timestamp"] = time.time()
    combined_metrics["datetime"] = datetime.now().isoformat()

    # Store in history for trend analysis
    _performance_history.append(combined_metrics)

    # Add enhanced analytics
    enhanced_metrics = combined_metrics.copy()

    # Get scaling recommendation and convert to dict
    scaling_rec = calculate_scaling_recommendation(combined_metrics)
    scaling_rec_dict = (
        asdict(scaling_rec)
        if hasattr(scaling_rec, "__dataclass_fields__")
        else {
            "action": getattr(scaling_rec, "action", "maintain"),
            "confidence": getattr(scaling_rec, "confidence", 0.5),
            "target_workers": getattr(scaling_rec, "target_workers", 1),
            "reasoning": getattr(scaling_rec, "reasoning", "No analysis available"),
            "expected_improvement": getattr(
                scaling_rec, "expected_improvement", "Unknown"
            ),
        }
    )

    enhanced_metrics.update(
        {
            "trend_analysis": analyze_performance_trends(),
            "bottleneck_detection": identify_current_bottlenecks(combined_metrics),
            "scaling_recommendation": scaling_rec_dict,
            "performance_efficiency": calculate_performance_efficiency(
                combined_metrics
            ),
            "system_health_score": calculate_system_health_score(combined_metrics),
            "predicted_completion_time": predict_completion_time(combined_metrics),
        }
    )

    return enhanced_metrics


def analyze_performance_trends() -> List[TrendAnalysis]:
    """
    Analyze performance trends across key metrics.

    Returns trend analysis for metrics critical to scaling decisions.
    """
    if len(_performance_history) < 10:  # Need minimum history
        return []

    key_metrics = [
        "memory_usage_mb",
        "success_rate",
        "avg_processing_time_ms",
        "pages_processed",
        "browser_pool_size",
        "cpu_usage_percent",
    ]

    trends = []
    recent_history = list(_performance_history)[-50:]  # Last 50 data points

    for metric in key_metrics:
        try:
            values = [h.get(metric, 0) for h in recent_history if metric in h]
            if len(values) < 5:
                continue

            trend = _analyze_single_metric_trend(metric, values)
            if trend:
                trends.append(trend)
        except Exception:
            continue  # Skip problematic metrics

    return trends


def _analyze_single_metric_trend(
    metric_name: str, values: List[float]
) -> Optional[TrendAnalysis]:
    """Analyze trend for a single metric."""
    if len(values) < 5:
        return None

    try:
        # Calculate simple trend using linear regression approximation
        trend_data = _calculate_simple_trend(values)
        if not trend_data:
            return None

        slope, current_value, mean_value, std_dev = trend_data

        # Determine trend direction and strength
        trend_direction, trend_strength = _determine_trend_characteristics(
            metric_name, slope, mean_value
        )

        # Predict next value and confidence
        predicted_next = current_value + slope
        confidence = max(0.5, 1.0 - (std_dev / (mean_value + 1)))

        # Generate recommendation
        recommendation = _generate_trend_recommendation(
            metric_name, trend_direction, trend_strength
        )

        return TrendAnalysis(
            metric_name=metric_name,
            current_value=current_value,
            trend_direction=trend_direction,
            trend_strength=trend_strength,
            predicted_next_value=predicted_next,
            confidence_level=confidence,
            recommendation=recommendation,
        )

    except Exception:
        return None


def _calculate_simple_trend(values: List[float]) -> Optional[tuple]:
    """Calculate simple linear trend from values."""
    try:
        x = list(range(len(values)))
        n = len(values)
        sum_x = sum(x)
        sum_y = sum(values)
        sum_xy = sum(x[i] * values[i] for i in range(n))
        sum_x2 = sum(xi * xi for xi in x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        current_value = values[-1]
        mean_value = statistics.mean(values)
        std_dev = statistics.stdev(values) if len(values) > 1 else 0

        return slope, current_value, mean_value, std_dev
    except Exception:
        return None


def _determine_trend_characteristics(
    metric_name: str, slope: float, mean_value: float
) -> tuple:
    """Determine trend direction and strength."""
    if abs(slope) < 0.01 * mean_value:
        return "stable", 0.1

    improving_metrics = ["success_rate", "pages_processed"]
    degrading_metrics = ["memory_usage_mb", "avg_processing_time_ms"]

    if slope > 0:
        if metric_name in improving_metrics:
            direction = "improving"
        elif metric_name in degrading_metrics:
            direction = "degrading"
        else:
            direction = "improving"
    else:
        if metric_name in improving_metrics:
            direction = "degrading"
        elif metric_name in degrading_metrics:
            direction = "improving"
        else:
            direction = "degrading"

    strength = min(abs(slope) / (mean_value + 1), 1.0)
    return direction, strength


def _generate_trend_recommendation(
    metric_name: str, direction: str, strength: float
) -> str:
    """Generate recommendation based on trend analysis."""
    if strength < 0.2:
        return f"{metric_name} is stable - continue monitoring"

    recommendations = {
        "memory_usage_mb": {
            "degrading": "Memory usage increasing - consider scaling down or cleanup",
            "improving": "Memory usage improving - can potentially scale up",
        },
        "success_rate": {
            "degrading": "Success rate declining - investigate failures",
            "improving": "Success rate improving - system performing well",
        },
        "avg_processing_time_ms": {
            "degrading": "Processing time increasing - may need optimization",
            "improving": "Processing time improving - system optimizing well",
        },
    }

    if metric_name in recommendations and direction in recommendations[metric_name]:
        return recommendations[metric_name][direction]

    return f"{metric_name} trend: {direction} (strength: {strength:.2f})"


def identify_current_bottlenecks(metrics: Dict[str, Any]) -> List[BottleneckDetection]:
    """
    Identify current system bottlenecks based on metrics.

    Returns list of detected bottlenecks with severity and recommendations.
    """
    bottlenecks = []

    # Memory bottleneck detection
    memory_mb = metrics.get("memory_usage_mb", 0)
    if memory_mb > 800:
        bottlenecks.append(
            BottleneckDetection(
                bottleneck_type="memory",
                severity="critical" if memory_mb > 1200 else "high",
                impact_score=min(memory_mb / 1000, 1.0),
                description=f"High memory usage: {memory_mb:.1f} MB",
                scaling_recommendation="scale_down",
            )
        )

    # CPU bottleneck detection
    cpu_percent = metrics.get("cpu_usage_percent", 0)
    if cpu_percent > 85:
        bottlenecks.append(
            BottleneckDetection(
                bottleneck_type="cpu",
                severity="high" if cpu_percent > 95 else "medium",
                impact_score=cpu_percent / 100,
                description=f"High CPU usage: {cpu_percent:.1f}%",
                scaling_recommendation="scale_down",
            )
        )

    # Success rate bottleneck
    success_rate = metrics.get("success_rate", 1.0)
    if success_rate < 0.8:
        bottlenecks.append(
            BottleneckDetection(
                bottleneck_type="reliability",
                severity="high" if success_rate < 0.6 else "medium",
                impact_score=1.0 - success_rate,
                description=f"Low success rate: {success_rate:.2f}",
                scaling_recommendation="scale_down",
            )
        )

    # Browser pool stress
    circuit_breaker_failures = metrics.get("circuit_breaker_failures", 0)
    if circuit_breaker_failures > 5:
        bottlenecks.append(
            BottleneckDetection(
                bottleneck_type="browser_pool",
                severity="high",
                impact_score=min(circuit_breaker_failures / 10, 1.0),
                description=f"Browser pool stressed: {circuit_breaker_failures} failures",
                scaling_recommendation="scale_down",
            )
        )

    # Store bottleneck history
    _bottleneck_detection_history.append(
        {
            "timestamp": time.time(),
            "bottlenecks": len(bottlenecks),
            "severity_counts": {b.severity: 1 for b in bottlenecks},
        }
    )

    return bottlenecks


def calculate_scaling_recommendation(metrics: Dict[str, Any]) -> ScalingRecommendation:
    """
    Calculate scaling recommendation based on current metrics and trends.

    Returns recommendation for scaling action with confidence level.
    """
    # Get current performance indicators
    memory_mb = metrics.get("memory_usage_mb", 0)
    cpu_percent = metrics.get("cpu_usage_percent", 0)
    success_rate = metrics.get("success_rate", 1.0)
    avg_time_ms = metrics.get("avg_processing_time_ms", 0)

    # Default values
    action = "maintain"
    current_workers = 2  # Default from main_self_contained.py
    target_workers = current_workers

    # Calculate scaling scores
    scale_up_score = _calculate_scale_up_score(
        success_rate, memory_mb, cpu_percent, avg_time_ms
    )
    scale_down_score = _calculate_scale_down_score(
        success_rate, memory_mb, cpu_percent, avg_time_ms
    )

    # Make scaling decision
    if scale_up_score > 0.8 and scale_down_score < 0.2:
        action = "scale_up"
        target_workers = min(current_workers + 1, 6)  # Max 6 workers for safety
        confidence = scale_up_score
        reasoning = f"Excellent performance - can handle more load (success: {success_rate:.2f})"
        expected_improvement = "Increased throughput with maintained quality"
    elif scale_down_score > 0.5:
        action = "scale_down"
        target_workers = max(current_workers - 1, 1)  # Min 1 worker
        confidence = scale_down_score
        reasoning = (
            f"Performance degradation - reduce load (success: {success_rate:.2f})"
        )
        expected_improvement = "Improved stability and success rate"
    else:
        confidence = 0.7
        reasoning = (
            f"Balanced performance - maintain scaling (success: {success_rate:.2f})"
        )
        expected_improvement = "Maintain current performance"

    return ScalingRecommendation(
        action=action,
        confidence=confidence,
        target_workers=target_workers,
        reasoning=reasoning,
        expected_improvement=expected_improvement,
    )


def _calculate_scale_up_score(
    success_rate: float, memory_mb: float, cpu_percent: float, avg_time_ms: float
) -> float:
    """Calculate score for scaling up."""
    score = 0
    if success_rate > 0.95:
        score += 0.3
    if memory_mb < 300:
        score += 0.3
    if cpu_percent < 70:
        score += 0.2
    if avg_time_ms < 2000:
        score += 0.2
    return score


def _calculate_scale_down_score(
    success_rate: float, memory_mb: float, cpu_percent: float, avg_time_ms: float
) -> float:
    """Calculate score for scaling down."""
    score = 0
    if success_rate < 0.8:
        score += 0.4
    if memory_mb > 600:
        score += 0.3
    if cpu_percent > 85:
        score += 0.2
    if avg_time_ms > 5000:
        score += 0.1
    return score


def calculate_performance_efficiency(metrics: Dict[str, Any]) -> Dict[str, float]:
    """Calculate various performance efficiency metrics."""
    pages_processed = metrics.get("pages_processed", 0)
    total_time = metrics.get("avg_processing_time_ms", 0) / 1000  # Convert to seconds
    memory_mb = metrics.get("memory_usage_mb", 1)
    success_rate = metrics.get("success_rate", 1.0)

    return {
        "pages_per_second": pages_processed / max(total_time, 1),
        "memory_efficiency": pages_processed / max(memory_mb, 1),
        "success_efficiency": success_rate * (pages_processed / max(total_time, 1)),
        "resource_utilization": min(
            (memory_mb / 1000) + metrics.get("cpu_usage_percent", 0) / 100, 2.0
        )
        / 2.0,
    }


def calculate_system_health_score(metrics: Dict[str, Any]) -> float:
    """
    Calculate overall system health score (0.0 to 1.0).

    Higher score indicates better system health.
    """
    success_rate = metrics.get("success_rate", 1.0)
    memory_mb = metrics.get("memory_usage_mb", 0)
    cpu_percent = metrics.get("cpu_usage_percent", 0)
    circuit_breaker_failures = metrics.get("circuit_breaker_failures", 0)

    # Success rate component (0.4 weight)
    success_component = success_rate * 0.4

    # Memory health component (0.3 weight)
    memory_health = max(0, 1.0 - (memory_mb / 1000)) * 0.3

    # CPU health component (0.2 weight)
    cpu_health = max(0, 1.0 - (cpu_percent / 100)) * 0.2

    # Reliability component (0.1 weight)
    reliability = max(0, 1.0 - (circuit_breaker_failures / 10)) * 0.1

    health_score = success_component + memory_health + cpu_health + reliability
    return min(max(health_score, 0.0), 1.0)


def predict_completion_time(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Predict completion time based on current performance trends."""
    if len(_performance_history) < 5:
        return {"prediction": "Insufficient data", "confidence": 0.0}

    recent_metrics = list(_performance_history)[-10:]
    avg_time_ms = statistics.mean(
        [m.get("avg_processing_time_ms", 0) for m in recent_metrics]
    )
    pages_processed = metrics.get("pages_processed", 0)

    # Simple prediction based on current rate
    if avg_time_ms > 0 and pages_processed > 0:
        estimated_pages_per_hour = 3600000 / avg_time_ms  # Convert ms to hours
        return {
            "estimated_pages_per_hour": estimated_pages_per_hour,
            "current_processing_rate_ms": avg_time_ms,
            "confidence": 0.7,
        }

    return {"prediction": "Unable to predict", "confidence": 0.0}


def get_metrics_summary() -> Dict[str, Any]:
    """Get a summary of recent metrics performance."""
    if len(_performance_history) < 1:
        return {"status": "No metrics history available"}

    latest_enhanced_metrics = collect_predictive_metrics()

    return {
        "timestamp": latest_enhanced_metrics.get("datetime"),
        "system_health_score": latest_enhanced_metrics.get("system_health_score", 0),
        "performance_efficiency": latest_enhanced_metrics.get(
            "performance_efficiency", {}
        ),
        "active_bottlenecks": len(
            latest_enhanced_metrics.get("bottleneck_detection", [])
        ),
        "scaling_recommendation": latest_enhanced_metrics.get(
            "scaling_recommendation", {}
        ).get("action", "maintain"),
        "trend_analysis_count": len(latest_enhanced_metrics.get("trend_analysis", [])),
        "metrics_history_size": len(_performance_history),
    }
