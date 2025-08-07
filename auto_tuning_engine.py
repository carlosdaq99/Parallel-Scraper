#!/usr/bin/env python3
"""
Auto-Tuning Engine for Adaptive Scaling System

This module provides intelligent parameter optimization based on performance patterns,
system conditions, and historical data. It continuously learns from scraping patterns
to optimize configuration parameters automatically.
"""

import time
import statistics
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class TuningParameters:
    """Configuration parameters that can be auto-tuned"""

    # Proactive worker scaling parameters (20-200, starting at 50)
    min_workers: int = 20
    max_workers: int = 200  # Updated from 100 to 200
    scale_up_threshold: float = 0.90  # More aggressive scaling up
    scale_down_threshold: float = 0.80  # Conservative scaling down
    scale_up_increment: int = 10  # Scale up faster (+10)
    scale_down_increment: int = 5  # Scale down more conservatively (-5)

    # Performance thresholds
    max_response_time_ms: float = 10000.0
    optimal_response_time_ms: float = 3000.0
    cpu_threshold_percent: float = 80.0
    memory_threshold_mb: float = 1000.0

    # Timing parameters
    scaling_cooldown_seconds: int = 30
    metrics_collection_interval: int = 30
    performance_window_size: int = 10

    # Browser optimization
    page_timeout_ms: int = 30000
    navigation_timeout_ms: int = 20000
    browser_pool_size: int = 3

    # Resource management
    memory_cleanup_interval: int = 100
    gc_threshold: int = 50
    pattern_cache_max_size: int = 1000


@dataclass
class PerformancePattern:
    """Represents a detected performance pattern"""

    pattern_type: str  # 'peak_load', 'low_activity', 'steady_state', 'degrading'
    confidence: float  # 0.0 to 1.0
    duration_minutes: float
    characteristics: Dict[str, Any]
    recommended_action: str


@dataclass
class TuningRecommendation:
    """A recommendation for parameter tuning"""

    parameter_name: str
    current_value: Any
    recommended_value: Any
    confidence: float
    reason: str
    expected_improvement: str


class AutoTuningEngine:
    """
    Intelligent auto-tuning engine that learns from performance patterns
    and optimizes configuration parameters automatically.
    """

    def __init__(self, learning_rate: float = 0.1):
        self.learning_rate = learning_rate
        self.tuning_params = TuningParameters()

        # Performance history tracking
        self.performance_history = deque(maxlen=1000)
        self.parameter_effectiveness = defaultdict(list)
        self.pattern_history = deque(maxlen=100)

        # Learning state
        self.patterns_detected = {}
        self.optimization_cycles = 0
        self.last_tuning_time = 0
        self.baseline_performance = None

        # Tuning statistics
        self.successful_tunings = 0
        self.failed_tunings = 0
        self.total_improvements = 0.0

        logger.info("🤖 Auto-Tuning Engine initialized")
        logger.info(f"   Learning rate: {learning_rate}")
        logger.info(f"   Parameter count: {len(asdict(self.tuning_params))}")

    def collect_performance_sample(self, metrics: Dict[str, Any]) -> None:
        """
        Collect a performance sample for pattern analysis.

        Args:
            metrics: Performance metrics from the scraping system
        """
        timestamp = time.time()

        # Helper function to safely get numeric values
        def safe_get(key: str, default: float) -> float:
            value = metrics.get(key, default)
            if value is None or (isinstance(value, str) and value == "invalid"):
                return default
            try:
                return float(value)
            except (ValueError, TypeError):
                return default

        def safe_get_int(key: str, default: int) -> int:
            value = metrics.get(key, default)
            if value is None or (isinstance(value, str) and value == "invalid"):
                return default
            try:
                return int(value)
            except (ValueError, TypeError):
                return default

        # Create performance sample with safe value extraction
        sample = {
            "timestamp": timestamp,
            "success_rate": safe_get("success_rate", 0.0),
            "avg_response_time": safe_get("avg_processing_time", 0.0),
            "cpu_usage": safe_get("cpu_usage_percent", 0.0),
            "memory_usage": safe_get("memory_usage_mb", 0.0),
            "active_workers": safe_get_int("active_workers", 0),
            "queue_length": safe_get_int("queue_length", 0),
            "error_rate": safe_get("error_rate", 0.0),
        }

        self.performance_history.append(sample)

        # Set baseline if this is the first sample
        if self.baseline_performance is None:
            self.baseline_performance = sample.copy()
            logger.info("📊 Baseline performance established")

    def detect_performance_patterns(self) -> List[PerformancePattern]:
        """
        Analyze performance history to detect patterns.

        Returns:
            List of detected performance patterns
        """
        if len(self.performance_history) < 3:
            return []

        patterns = []
        recent_data = list(self.performance_history)[-20:]  # Last 20 samples

        # Pattern 1: Peak Load Detection
        peak_pattern = self._detect_peak_load_pattern(recent_data)
        if peak_pattern:
            patterns.append(peak_pattern)

        # Pattern 2: Performance Degradation
        degradation_pattern = self._detect_degradation_pattern(recent_data)
        if degradation_pattern:
            patterns.append(degradation_pattern)

        # Pattern 3: Low Activity Period
        low_activity_pattern = self._detect_low_activity_pattern(recent_data)
        if low_activity_pattern:
            patterns.append(low_activity_pattern)

        # Pattern 4: Steady State
        steady_state_pattern = self._detect_steady_state_pattern(recent_data)
        if steady_state_pattern:
            patterns.append(steady_state_pattern)

        # Store patterns for historical analysis
        for pattern in patterns:
            self.pattern_history.append({"timestamp": time.time(), "pattern": pattern})

        return patterns

    def _detect_peak_load_pattern(
        self, data: List[Dict]
    ) -> Optional[PerformancePattern]:
        """Detect if system is under peak load"""
        if len(data) < 3:
            return None

        # Calculate recent averages
        recent_response_times = [d["avg_response_time"] for d in data[-5:]]
        recent_cpu = [d["cpu_usage"] for d in data[-5:]]
        recent_errors = [d["error_rate"] for d in data[-5:]]

        avg_response_time = statistics.mean(recent_response_times)
        avg_cpu = statistics.mean(recent_cpu)
        avg_error_rate = statistics.mean(recent_errors)

        # Peak load indicators - more lenient thresholds for testing
        high_response_time = avg_response_time > 10.0  # 10 seconds threshold
        high_cpu = avg_cpu > 70.0  # 70% CPU threshold
        increasing_errors = avg_error_rate > 0.1  # 10% error rate

        if high_response_time or high_cpu or increasing_errors:
            confidence = min(
                1.0,
                (avg_response_time / 20.0 + avg_cpu / 100.0 + avg_error_rate * 5.0)
                / 3.0,
            )

            return PerformancePattern(
                pattern_type="peak_load",
                confidence=confidence,
                duration_minutes=len(data) * 0.5,  # Assuming 30-second intervals
                characteristics={
                    "avg_response_time": avg_response_time,
                    "avg_cpu_usage": avg_cpu,
                    "avg_error_rate": avg_error_rate,
                },
                recommended_action="scale_down_workers",  # FIXED: Reduce load when system is overloaded
            )

        return None

    def _detect_degradation_pattern(
        self, data: List[Dict]
    ) -> Optional[PerformancePattern]:
        """Detect if performance is degrading over time"""
        if len(data) < 5:
            return None

        # Check for declining performance trends
        response_times = [d["avg_response_time"] for d in data]
        success_rates = [d["success_rate"] for d in data]

        # Simple trend detection (slope analysis)
        n = len(response_times)
        x_vals = list(range(n))

        # Calculate response time trend
        response_trend = self._calculate_trend_slope(x_vals, response_times)
        success_trend = self._calculate_trend_slope(x_vals, success_rates)

        # Degradation indicators
        increasing_response_time = response_trend > 0.1
        decreasing_success_rate = success_trend < -0.01

        if increasing_response_time or decreasing_success_rate:
            confidence = min(1.0, abs(response_trend) + abs(success_trend))

            return PerformancePattern(
                pattern_type="degrading",
                confidence=confidence,
                duration_minutes=len(data) * 0.5,
                characteristics={
                    "response_time_trend": response_trend,
                    "success_rate_trend": success_trend,
                },
                recommended_action="optimize_configuration",
            )

        return None

    def _detect_low_activity_pattern(
        self, data: List[Dict]
    ) -> Optional[PerformancePattern]:
        """Detect periods of low activity"""
        if len(data) < 3:
            return None

        recent_workers = [d["active_workers"] for d in data[-5:]]
        recent_queue = [d["queue_length"] for d in data[-5:]]
        recent_cpu = [d["cpu_usage"] for d in data[-5:]]

        avg_workers = statistics.mean(recent_workers)
        avg_queue = statistics.mean(recent_queue)
        avg_cpu = statistics.mean(recent_cpu)

        # Low activity indicators
        low_utilization = avg_cpu < 30.0
        small_queue = avg_queue < 2.0
        moderate_workers = avg_workers > self.tuning_params.min_workers + 2

        if low_utilization and small_queue and moderate_workers:
            confidence = (30.0 - avg_cpu) / 30.0  # Higher confidence with lower CPU

            return PerformancePattern(
                pattern_type="low_activity",
                confidence=confidence,
                duration_minutes=len(data) * 0.5,
                characteristics={
                    "avg_cpu_usage": avg_cpu,
                    "avg_queue_length": avg_queue,
                    "avg_workers": avg_workers,
                },
                recommended_action="scale_up_workers",  # FIXED: Increase capacity when resources are available
            )

        return None

    def _detect_steady_state_pattern(
        self, data: List[Dict]
    ) -> Optional[PerformancePattern]:
        """Detect steady state operation"""
        if len(data) < 10:
            return None

        # Check for stability in key metrics
        response_times = [d["avg_response_time"] for d in data]
        success_rates = [d["success_rate"] for d in data]
        cpu_usage = [d["cpu_usage"] for d in data]

        # Calculate coefficient of variation (std dev / mean)
        response_cv = (
            statistics.stdev(response_times) / statistics.mean(response_times)
            if statistics.mean(response_times) > 0
            else 1.0
        )
        success_cv = (
            statistics.stdev(success_rates) / statistics.mean(success_rates)
            if statistics.mean(success_rates) > 0
            else 1.0
        )
        cpu_cv = (
            statistics.stdev(cpu_usage) / statistics.mean(cpu_usage)
            if statistics.mean(cpu_usage) > 0
            else 1.0
        )

        # Steady state indicators (low variation)
        stable_response = response_cv < 0.2
        stable_success = success_cv < 0.1
        stable_cpu = cpu_cv < 0.3

        if stable_response and stable_success and stable_cpu:
            confidence = 1.0 - (response_cv + success_cv + cpu_cv) / 3.0

            return PerformancePattern(
                pattern_type="steady_state",
                confidence=confidence,
                duration_minutes=len(data) * 0.5,
                characteristics={
                    "response_time_stability": response_cv,
                    "success_rate_stability": success_cv,
                    "cpu_stability": cpu_cv,
                },
                recommended_action="maintain_current",
            )

        return None

    def _calculate_trend_slope(self, x_vals: List[float], y_vals: List[float]) -> float:
        """Calculate the slope of a trend line"""
        if len(x_vals) != len(y_vals) or len(x_vals) < 2:
            return 0.0

        n = len(x_vals)
        sum_x = sum(x_vals)
        sum_y = sum(y_vals)
        sum_xy = sum(x * y for x, y in zip(x_vals, y_vals))
        sum_x2 = sum(x * x for x in x_vals)

        # Calculate slope using least squares method
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope

    def generate_tuning_recommendations(
        self, patterns: List[PerformancePattern]
    ) -> List[TuningRecommendation]:
        """
        Generate tuning recommendations based on detected patterns.

        Args:
            patterns: List of detected performance patterns

        Returns:
            List of tuning recommendations
        """
        recommendations = []

        for pattern in patterns:
            if pattern.confidence < 0.5:  # Skip low-confidence patterns
                continue

            pattern_recommendations = self._get_pattern_recommendations(pattern)
            recommendations.extend(pattern_recommendations)

        # Deduplicate and prioritize recommendations
        return self._prioritize_recommendations(recommendations)

    def _get_pattern_recommendations(
        self, pattern: PerformancePattern
    ) -> List[TuningRecommendation]:
        """Get recommendations for a specific pattern"""
        recommendations = []

        if pattern.pattern_type == "peak_load":
            # FIXED: Recommend scaling DOWN and reducing load when system is overloaded
            if self.tuning_params.max_workers > 5:
                recommendations.append(
                    TuningRecommendation(
                        parameter_name="max_workers",
                        current_value=self.tuning_params.max_workers,
                        recommended_value=max(5, self.tuning_params.max_workers - 3),
                        confidence=pattern.confidence,
                        reason=f"Peak load detected - reducing workers (confidence: {pattern.confidence:.2f})",
                        expected_improvement="Reduced system stress and improved stability",
                    )
                )

            # Increase timeouts to handle slower responses under load
            if self.tuning_params.page_timeout_ms < 45000:
                recommendations.append(
                    TuningRecommendation(
                        parameter_name="page_timeout_ms",
                        current_value=self.tuning_params.page_timeout_ms,
                        recommended_value=min(
                            45000, self.tuning_params.page_timeout_ms + 10000
                        ),
                        confidence=pattern.confidence * 0.8,
                        reason="Peak load - increase timeout tolerance",
                        expected_improvement="Reduced timeout errors",
                    )
                )

        elif pattern.pattern_type == "low_activity":
            # FIXED: Recommend scaling UP to utilize available resources and increase output
            if self.tuning_params.max_workers < 25:
                recommendations.append(
                    TuningRecommendation(
                        parameter_name="max_workers",
                        current_value=self.tuning_params.max_workers,
                        recommended_value=min(25, self.tuning_params.max_workers + 3),
                        confidence=pattern.confidence,
                        reason=f"Low activity - scaling up to utilize resources (confidence: {pattern.confidence:.2f})",
                        expected_improvement="Increased throughput with available resources",
                    )
                )

            # Optimize timeouts for faster operation
            if self.tuning_params.page_timeout_ms > 20000:
                recommendations.append(
                    TuningRecommendation(
                        parameter_name="page_timeout_ms",
                        current_value=self.tuning_params.page_timeout_ms,
                        recommended_value=max(
                            20000, self.tuning_params.page_timeout_ms - 5000
                        ),
                        confidence=pattern.confidence * 0.7,
                        reason="Low activity - optimize for speed",
                        expected_improvement="Faster response times",
                    )
                )

        elif pattern.pattern_type == "degrading":
            # Recommend conservative adjustments and cleanup
            recommendations.append(
                TuningRecommendation(
                    parameter_name="memory_cleanup_interval",
                    current_value=self.tuning_params.memory_cleanup_interval,
                    recommended_value=max(
                        50, self.tuning_params.memory_cleanup_interval - 20
                    ),
                    confidence=pattern.confidence,
                    reason="Performance degradation - increase cleanup frequency",
                    expected_improvement="Better memory management",
                )
            )

            recommendations.append(
                TuningRecommendation(
                    parameter_name="gc_threshold",
                    current_value=self.tuning_params.gc_threshold,
                    recommended_value=max(20, self.tuning_params.gc_threshold - 10),
                    confidence=pattern.confidence * 0.8,
                    reason="Performance degradation - more aggressive garbage collection",
                    expected_improvement="Reduced memory pressure",
                )
            )

        elif pattern.pattern_type == "steady_state":
            # Fine-tune for optimal performance
            characteristics = pattern.characteristics

            # If response times are good, we can be more aggressive
            if characteristics.get("response_time_stability", 1.0) < 0.1:
                recommendations.append(
                    TuningRecommendation(
                        parameter_name="scale_up_threshold",
                        current_value=self.tuning_params.scale_up_threshold,
                        recommended_value=min(
                            0.98, self.tuning_params.scale_up_threshold + 0.01
                        ),
                        confidence=pattern.confidence * 0.6,
                        reason="Steady high performance - optimize scaling threshold",
                        expected_improvement="More precise scaling decisions",
                    )
                )

        return recommendations

    def _prioritize_recommendations(
        self, recommendations: List[TuningRecommendation]
    ) -> List[TuningRecommendation]:
        """Sort and deduplicate recommendations by priority"""
        # Remove duplicates by parameter name (keep highest confidence)
        param_recommendations = {}
        for rec in recommendations:
            if (
                rec.parameter_name not in param_recommendations
                or rec.confidence > param_recommendations[rec.parameter_name].confidence
            ):
                param_recommendations[rec.parameter_name] = rec

        # Sort by confidence (highest first)
        sorted_recommendations = sorted(
            param_recommendations.values(), key=lambda x: x.confidence, reverse=True
        )

        return sorted_recommendations

    def apply_tuning_recommendations(
        self, recommendations: List[TuningRecommendation]
    ) -> Dict[str, Any]:
        """
        Apply tuning recommendations to the configuration.

        Args:
            recommendations: List of tuning recommendations to apply

        Returns:
            Dictionary with applied changes and results
        """
        applied_changes = {}
        successful_changes = 0

        for rec in recommendations:
            if rec.confidence < 0.6:  # Only apply high-confidence recommendations
                continue

            try:
                # Apply the recommendation
                old_value = getattr(self.tuning_params, rec.parameter_name)
                setattr(self.tuning_params, rec.parameter_name, rec.recommended_value)

                applied_changes[rec.parameter_name] = {
                    "old_value": old_value,
                    "new_value": rec.recommended_value,
                    "confidence": rec.confidence,
                    "reason": rec.reason,
                    "expected_improvement": rec.expected_improvement,
                }

                successful_changes += 1

                logger.info(
                    f"🔧 Applied tuning: {rec.parameter_name} = {rec.recommended_value} (was {old_value})"
                )
                logger.info(f"   Reason: {rec.reason}")

            except Exception as e:
                logger.error(f"❌ Failed to apply tuning for {rec.parameter_name}: {e}")

        self.successful_tunings += successful_changes
        self.optimization_cycles += 1
        self.last_tuning_time = time.time()

        result = {
            "applied_changes": applied_changes,
            "successful_changes": successful_changes,
            "total_recommendations": len(recommendations),
            "optimization_cycle": self.optimization_cycles,
        }

        if successful_changes > 0:
            logger.info(
                f"🎯 Auto-tuning cycle {self.optimization_cycles} completed: {successful_changes} changes applied"
            )

        return result

    def run_auto_tuning_cycle(self, current_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a complete auto-tuning cycle.

        Args:
            current_metrics: Current performance metrics

        Returns:
            Results of the tuning cycle
        """
        # Collect performance sample
        self.collect_performance_sample(current_metrics)

        # Detect patterns
        patterns = self.detect_performance_patterns()

        # Generate recommendations
        recommendations = self.generate_tuning_recommendations(patterns)

        # Apply recommendations
        results = self.apply_tuning_recommendations(recommendations)

        # Update results with pattern information
        results.update(
            {
                "patterns_detected": [p.pattern_type for p in patterns],
                "pattern_count": len(patterns),
                "performance_samples": len(self.performance_history),
                "tuning_statistics": self.get_tuning_statistics(),
            }
        )

        return results

    def get_tuning_statistics(self) -> Dict[str, Any]:
        """Get auto-tuning performance statistics"""
        return {
            "optimization_cycles": self.optimization_cycles,
            "successful_tunings": self.successful_tunings,
            "failed_tunings": self.failed_tunings,
            "total_improvements": self.total_improvements,
            "success_rate": self.successful_tunings / max(1, self.optimization_cycles),
            "last_tuning_time": self.last_tuning_time,
            "patterns_detected_count": len(self.pattern_history),
            "performance_history_size": len(self.performance_history),
        }

    def get_current_parameters(self) -> Dict[str, Any]:
        """Get current tuning parameters as dictionary"""
        return asdict(self.tuning_params)


# Global auto-tuning engine instance
_auto_tuning_engine = None


def initialize_auto_tuning(learning_rate: float = 0.1) -> AutoTuningEngine:
    """Initialize the global auto-tuning engine"""
    global _auto_tuning_engine
    _auto_tuning_engine = AutoTuningEngine(learning_rate=learning_rate)
    return _auto_tuning_engine


def get_auto_tuning_engine() -> Optional[AutoTuningEngine]:
    """Get the global auto-tuning engine instance"""
    return _auto_tuning_engine


def run_auto_tuning_cycle(metrics: Dict[str, Any]) -> Dict[str, Any]:
    """Run an auto-tuning cycle with the global engine"""
    if _auto_tuning_engine is None:
        raise RuntimeError(
            "Auto-tuning engine not initialized. Call initialize_auto_tuning() first."
        )

    return _auto_tuning_engine.run_auto_tuning_cycle(metrics)


def get_tuned_parameters() -> Dict[str, Any]:
    """Get current auto-tuned parameters"""
    if _auto_tuning_engine is None:
        return {}

    return _auto_tuning_engine.get_current_parameters()
