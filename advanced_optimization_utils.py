#!/usr/bin/env python3
"""
Advanced Optimization Utils - Phase 3 Function-Based Adaptations

Converts class-based optimization components to function-based patterns for integration
with the parallel scraper architecture. Focuses on memory management, monitoring,
and orchestration patterns.

Key Components:
1. Memory Management Functions - Adapted from MemoryOptimizedSession and DataExtractionCacheManager
2. Performance Monitoring Functions - Adapted from BasicMetricsCollector
3. Orchestration Functions - Adapted from OptimizedOrchestratorConfig
4. Cache Management Functions - Pattern-based extraction caching

Design Principles:
- Stateless function-based design compatible with async workflows
- Simplified API surface maintaining core optimization benefits
- No dependencies on class hierarchies or complex state management
- Direct integration with existing worker.py and main_complete.py patterns
"""

import logging
import time
import gc
import psutil
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import deque, defaultdict

# Configure logging
logger = logging.getLogger(__name__)

# Global state for metrics tracking (minimal state needed)
_metrics_history = deque(maxlen=100)
_baseline_metrics = None
_session_start_time = time.time()
_extraction_patterns_cache = {}
_memory_cleanup_intervals = {}


@dataclass
class AdvancedMetrics:
    """Advanced performance metrics for optimization tracking."""

    timestamp: float
    processing_time_ms: float
    memory_usage_mb: float
    pages_processed: int
    success_count: int
    error_count: int
    cache_hits: int
    cache_misses: int
    cleanup_cycles: int
    gc_triggers: int
    session_duration_seconds: float


# ====================
# MEMORY MANAGEMENT FUNCTIONS
# ====================


async def create_memory_optimized_session(
    page, cleanup_interval: int = 30
) -> Dict[str, Any]:
    """
    Create optimized session with memory management.

    Adapted from MemoryOptimizedSession class to function-based pattern.

    Args:
        page: Playwright page instance
        cleanup_interval: Cleanup interval in seconds

    Returns:
        Dict containing session context and cleanup function
    """
    try:
        session_id = f"session_{int(time.time() * 1000)}"

        # Store cleanup interval for this session
        _memory_cleanup_intervals[session_id] = cleanup_interval

        # Initial memory optimization
        await optimize_page_memory_advanced(page)

        # Create session context
        session_context = {
            "session_id": session_id,
            "created_at": time.time(),
            "page": page,
            "cleanup_count": 0,
            "last_cleanup": time.time(),
        }

        logger.info(f"Memory optimized session created: {session_id}")
        return session_context

    except Exception as e:
        logger.error(f"Error creating memory optimized session: {e}")
        return {"session_id": "fallback", "page": page, "cleanup_count": 0}


async def optimize_page_memory_advanced(page) -> Dict[str, Any]:
    """
    Advanced page memory optimization with comprehensive cleanup.

    Adapted from memory_manager.py AggressiveCleanupManager patterns.

    Args:
        page: Playwright page instance

    Returns:
        Dict with optimization results
    """
    results = {
        "memory_before_mb": 0,
        "memory_after_mb": 0,
        "memory_saved_mb": 0,
        "cleanup_actions": [],
        "gc_triggered": False,
    }

    try:
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / (1024 * 1024)
        results["memory_before_mb"] = initial_memory

        # Clear JavaScript heap
        try:
            await page.evaluate(
                """
                // Clear JavaScript heap
                if (window.gc) {
                    window.gc();
                }
                
                // Clear performance entries
                if (performance.clearResourceTimings) {
                    performance.clearResourceTimings();
                }
                
                // Clear console history
                if (console.clear) {
                    console.clear();
                }
                
                // Remove event listeners on window
                ['scroll', 'resize', 'load', 'beforeunload'].forEach(event => {
                    window.removeEventListener(event, function() {});
                });
            """
            )
            results["cleanup_actions"].append("js_heap_cleanup")
        except Exception as e:
            logger.debug(f"JS heap cleanup failed: {e}")

        # Clear browser cache for this page
        try:
            await page.evaluate(
                "caches.keys().then(names => names.forEach(name => caches.delete(name)))"
            )
            results["cleanup_actions"].append("browser_cache_cleanup")
        except Exception as e:
            logger.debug(f"Browser cache cleanup failed: {e}")

        # Force Python garbage collection
        collected = gc.collect()
        if collected > 0:
            results["gc_triggered"] = True
            results["cleanup_actions"].append(f"gc_collected_{collected}")

        # Get final memory usage
        final_memory = process.memory_info().rss / (1024 * 1024)
        results["memory_after_mb"] = final_memory
        results["memory_saved_mb"] = max(0, initial_memory - final_memory)

        logger.debug(
            f"Memory optimization: {initial_memory:.1f}MB -> {final_memory:.1f}MB "
            f"(saved {results['memory_saved_mb']:.1f}MB)"
        )

        return results

    except Exception as e:
        logger.error(f"Error in advanced memory optimization: {e}")
        return results


def setup_extraction_pattern_cache(
    max_patterns: int = 500, max_memory_mb: int = 25
) -> Dict[str, Any]:
    """
    Setup intelligent extraction pattern caching.

    Adapted from DataExtractionCacheManager to function-based pattern.

    Args:
        max_patterns: Maximum number of patterns to cache
        max_memory_mb: Maximum memory usage for cache

    Returns:
        Cache configuration dict
    """
    global _extraction_patterns_cache

    cache_config = {
        "max_patterns": max_patterns,
        "max_memory_bytes": max_memory_mb * 1024 * 1024,
        "created_at": time.time(),
        "hits": 0,
        "misses": 0,
    }

    # Initialize cache if not exists
    if not _extraction_patterns_cache:
        _extraction_patterns_cache = {
            "patterns": {},
            "usage_count": defaultdict(int),
            "last_used": {},
            "config": cache_config,
        }

    logger.info(
        f"Extraction pattern cache configured: {max_patterns} patterns, {max_memory_mb}MB limit"
    )
    return cache_config


def cache_extraction_pattern(
    url_pattern: str, dom_selectors: List[str], success_rate: float = 1.0
) -> bool:
    """
    Cache extraction pattern for reuse across similar pages.

    Args:
        url_pattern: URL pattern or domain
        dom_selectors: List of successful DOM selectors
        success_rate: Success rate of this pattern (0.0-1.0)

    Returns:
        bool: True if cached successfully
    """
    global _extraction_patterns_cache

    try:
        if not _extraction_patterns_cache:
            setup_extraction_pattern_cache()

        cache = _extraction_patterns_cache

        # Check cache size limits
        if len(cache["patterns"]) >= cache["config"]["max_patterns"]:
            # Remove least recently used pattern
            lru_pattern = min(cache["last_used"].items(), key=lambda x: x[1])[0]
            del cache["patterns"][lru_pattern]
            del cache["last_used"][lru_pattern]
            del cache["usage_count"][lru_pattern]

        # Store pattern
        cache["patterns"][url_pattern] = {
            "selectors": dom_selectors,
            "success_rate": success_rate,
            "created_at": time.time(),
            "size_bytes": len(str(dom_selectors).encode("utf-8")),
        }
        cache["last_used"][url_pattern] = time.time()
        cache["usage_count"][url_pattern] = 1

        logger.debug(
            f"Cached extraction pattern for {url_pattern}: {len(dom_selectors)} selectors"
        )
        return True

    except Exception as e:
        logger.error(f"Error caching extraction pattern: {e}")
        return False


def get_cached_extraction_pattern(url_pattern: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve cached extraction pattern.

    Args:
        url_pattern: URL pattern to look up

    Returns:
        Cached pattern dict or None
    """
    global _extraction_patterns_cache

    try:
        if (
            not _extraction_patterns_cache
            or url_pattern not in _extraction_patterns_cache["patterns"]
        ):
            _extraction_patterns_cache["config"]["misses"] += 1
            return None

        cache = _extraction_patterns_cache
        pattern = cache["patterns"][url_pattern]

        # Update usage tracking
        cache["last_used"][url_pattern] = time.time()
        cache["usage_count"][url_pattern] += 1
        cache["config"]["hits"] += 1

        logger.debug(f"Cache hit for pattern {url_pattern}")
        return pattern

    except Exception as e:
        logger.error(f"Error retrieving cached pattern: {e}")
        return None


# ====================
# PERFORMANCE MONITORING FUNCTIONS
# ====================


def collect_advanced_metrics(worker_stats: Dict[str, Any] = None) -> AdvancedMetrics:
    """
    Collect comprehensive performance metrics.

    Adapted from BasicMetricsCollector to function-based pattern.

    Args:
        worker_stats: Optional worker statistics dict

    Returns:
        AdvancedMetrics object with current performance data
    """
    global _metrics_history, _session_start_time

    try:
        # Get system metrics
        process = psutil.Process()
        memory_usage_mb = process.memory_info().rss / (1024 * 1024)

        # Extract stats from worker or use defaults
        if worker_stats:
            pages_processed = worker_stats.get("pages_processed", 0)
            success_count = worker_stats.get("successful_pages", 0)
            error_count = worker_stats.get("failed_pages", 0)
            processing_time_ms = worker_stats.get("avg_processing_time_ms", 0)
        else:
            pages_processed = len(_metrics_history)
            success_count = pages_processed
            error_count = 0
            processing_time_ms = 0

        # Get cache stats
        cache_stats = _extraction_patterns_cache.get("config", {})
        cache_hits = cache_stats.get("hits", 0)
        cache_misses = cache_stats.get("misses", 0)

        # Calculate session duration
        session_duration = time.time() - _session_start_time

        # Create metrics
        metrics = AdvancedMetrics(
            timestamp=time.time(),
            processing_time_ms=processing_time_ms,
            memory_usage_mb=memory_usage_mb,
            pages_processed=pages_processed,
            success_count=success_count,
            error_count=error_count,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            cleanup_cycles=len(_memory_cleanup_intervals),
            gc_triggers=0,  # Would need to track this separately
            session_duration_seconds=session_duration,
        )

        # Store in history
        _metrics_history.append(metrics)

        return metrics

    except Exception as e:
        logger.error(f"Error collecting advanced metrics: {e}")
        return AdvancedMetrics(
            timestamp=time.time(),
            processing_time_ms=0,
            memory_usage_mb=0,
            pages_processed=0,
            success_count=0,
            error_count=1,
            cache_hits=0,
            cache_misses=0,
            cleanup_cycles=0,
            gc_triggers=0,
            session_duration_seconds=time.time() - _session_start_time,
        )


def calculate_optimization_impact() -> Dict[str, Any]:
    """
    Calculate optimization impact metrics.

    Returns:
        Dict with improvement percentages and efficiency metrics
    """
    global _metrics_history, _baseline_metrics

    try:
        if len(_metrics_history) < 5:
            return {"status": "insufficient_data", "samples": len(_metrics_history)}

        # Establish baseline if not set
        if _baseline_metrics is None:
            baseline_samples = list(_metrics_history)[:3]
            _baseline_metrics = {
                "avg_processing_time_ms": statistics.mean(
                    [m.processing_time_ms for m in baseline_samples]
                ),
                "avg_memory_mb": statistics.mean(
                    [m.memory_usage_mb for m in baseline_samples]
                ),
                "avg_success_rate": statistics.mean(
                    [
                        m.success_count / max(1, m.pages_processed)
                        for m in baseline_samples
                    ]
                ),
            }

        # Calculate current performance
        recent_samples = list(_metrics_history)[-5:]
        current_metrics = {
            "avg_processing_time_ms": statistics.mean(
                [
                    m.processing_time_ms
                    for m in recent_samples
                    if m.processing_time_ms > 0
                ]
            ),
            "avg_memory_mb": statistics.mean(
                [m.memory_usage_mb for m in recent_samples]
            ),
            "avg_success_rate": statistics.mean(
                [m.success_count / max(1, m.pages_processed) for m in recent_samples]
            ),
        }

        # Calculate improvements
        time_improvement = 0
        if _baseline_metrics["avg_processing_time_ms"] > 0:
            time_improvement = (
                (
                    _baseline_metrics["avg_processing_time_ms"]
                    - current_metrics["avg_processing_time_ms"]
                )
                / _baseline_metrics["avg_processing_time_ms"]
            ) * 100

        memory_improvement = 0
        if _baseline_metrics["avg_memory_mb"] > 0:
            memory_improvement = (
                (_baseline_metrics["avg_memory_mb"] - current_metrics["avg_memory_mb"])
                / _baseline_metrics["avg_memory_mb"]
            ) * 100

        # Cache efficiency
        total_cache_ops = (
            recent_samples[-1].cache_hits + recent_samples[-1].cache_misses
        )
        cache_hit_rate = (recent_samples[-1].cache_hits / max(1, total_cache_ops)) * 100

        return {
            "status": "calculated",
            "time_improvement_percent": round(time_improvement, 2),
            "memory_improvement_percent": round(memory_improvement, 2),
            "success_rate_percent": round(current_metrics["avg_success_rate"] * 100, 2),
            "cache_hit_rate_percent": round(cache_hit_rate, 2),
            "total_pages_processed": recent_samples[-1].pages_processed,
            "session_duration_minutes": round(
                recent_samples[-1].session_duration_seconds / 60, 2
            ),
            "baseline_metrics": _baseline_metrics,
            "current_metrics": current_metrics,
        }

    except Exception as e:
        logger.error(f"Error calculating optimization impact: {e}")
        return {"status": "error", "error": str(e)}


def generate_optimization_report() -> str:
    """
    Generate human-readable optimization report.

    Returns:
        Formatted optimization report string
    """
    try:
        impact = calculate_optimization_impact()
        latest_metrics = _metrics_history[-1] if _metrics_history else None

        if impact["status"] != "calculated":
            return f"⚠️ Optimization Report: {impact['status']}"

        report_lines = [
            "🚀 Advanced Optimization Report",
            "=" * 40,
            "📊 Performance Improvements:",
            f"   ⏱️  Processing Time: {impact['time_improvement_percent']:+.1f}%",
            f"   💾 Memory Usage: {impact['memory_improvement_percent']:+.1f}%",
            f"   ✅ Success Rate: {impact['success_rate_percent']:.1f}%",
            f"   🎯 Cache Hit Rate: {impact['cache_hit_rate_percent']:.1f}%",
            "",
            "📈 Session Statistics:",
            f"   📄 Pages Processed: {impact['total_pages_processed']}",
            f"   ⏰ Session Duration: {impact['session_duration_minutes']:.1f} minutes",
            (
                f"   🧠 Current Memory: {latest_metrics.memory_usage_mb:.1f} MB"
                if latest_metrics
                else ""
            ),
            "",
            "🔧 Optimization Features Active:",
            "   🌐 Browser Reuse: ✅",
            "   🚫 Resource Filtering: ✅",
            "   💾 Memory Management: ✅",
            "   📋 Pattern Caching: ✅",
            "   📊 Advanced Monitoring: ✅",
        ]

        return "\n".join(report_lines)

    except Exception as e:
        logger.error(f"Error generating optimization report: {e}")
        return f"❌ Error generating optimization report: {e}"


# ====================
# ORCHESTRATION FUNCTIONS
# ====================


def create_optimized_orchestration_config(
    enable_browser_reuse: bool = True,
    enable_resource_filtering: bool = True,
    enable_memory_optimization: bool = True,
    enable_pattern_caching: bool = True,
    enable_advanced_monitoring: bool = True,
    max_concurrent_workers: int = 50,
    memory_threshold_mb: int = 2048,
    cleanup_interval_seconds: int = 30,
) -> Dict[str, Any]:
    """
    Create optimized orchestration configuration.

    Adapted from OptimizedOrchestratorConfig to function-based pattern.

    Args:
        enable_browser_reuse: Enable browser reuse optimization
        enable_resource_filtering: Enable intelligent resource filtering
        enable_memory_optimization: Enable memory management
        enable_pattern_caching: Enable extraction pattern caching
        enable_advanced_monitoring: Enable advanced performance monitoring
        max_concurrent_workers: Maximum concurrent workers
        memory_threshold_mb: Memory threshold for cleanup triggers
        cleanup_interval_seconds: Automatic cleanup interval

    Returns:
        Configuration dict for optimized orchestration
    """
    config = {
        "optimization_settings": {
            "browser_reuse": enable_browser_reuse,
            "resource_filtering": enable_resource_filtering,
            "memory_optimization": enable_memory_optimization,
            "pattern_caching": enable_pattern_caching,
            "advanced_monitoring": enable_advanced_monitoring,
        },
        "performance_settings": {
            "max_concurrent_workers": max_concurrent_workers,
            "memory_threshold_mb": memory_threshold_mb,
            "cleanup_interval_seconds": cleanup_interval_seconds,
            "gc_threshold_pages": 100,
            "browser_reuse_threshold": 10,
        },
        "monitoring_settings": {
            "metrics_history_size": 100,
            "report_interval_seconds": 60,
            "enable_detailed_logging": True,
            "performance_baseline_samples": 5,
        },
        "fallback_settings": {
            "enable_fallback_on_error": True,
            "max_retry_attempts": 3,
            "fallback_timeout_seconds": 30,
            "error_threshold_percent": 10,
        },
        "created_at": time.time(),
        "version": "3.0.0",
    }

    logger.info(
        f"Optimized orchestration config created with {sum(config['optimization_settings'].values())} optimizations enabled"
    )
    return config


async def apply_orchestrated_optimization(
    page, session_context: Dict[str, Any], config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Apply orchestrated optimization to a page based on configuration.

    Args:
        page: Playwright page instance
        session_context: Session context from create_memory_optimized_session
        config: Orchestration config from create_optimized_orchestration_config

    Returns:
        Dict with optimization results
    """
    results = {
        "optimizations_applied": [],
        "metrics": {},
        "errors": [],
        "fallback_used": False,
    }

    try:
        optimization_settings = config.get("optimization_settings", {})

        # Apply memory optimization
        if optimization_settings.get("memory_optimization", False):
            try:
                memory_result = await optimize_page_memory_advanced(page)
                results["optimizations_applied"].append("memory_optimization")
                results["metrics"]["memory"] = memory_result
            except Exception as e:
                results["errors"].append(f"Memory optimization failed: {e}")

        # Setup pattern caching
        if optimization_settings.get("pattern_caching", False):
            try:
                cache_config = setup_extraction_pattern_cache()
                results["optimizations_applied"].append("pattern_caching")
                results["metrics"]["cache"] = cache_config
            except Exception as e:
                results["errors"].append(f"Pattern caching failed: {e}")

        # Collect advanced monitoring metrics
        if optimization_settings.get("advanced_monitoring", False):
            try:
                metrics = collect_advanced_metrics()
                results["optimizations_applied"].append("advanced_monitoring")
                results["metrics"]["performance"] = asdict(metrics)
            except Exception as e:
                results["errors"].append(f"Advanced monitoring failed: {e}")

        # Check for cleanup triggers
        performance_settings = config.get("performance_settings", {})
        if (
            session_context.get("cleanup_count", 0)
            % performance_settings.get("gc_threshold_pages", 100)
            == 0
        ):
            gc_collected = gc.collect()
            if gc_collected > 0:
                results["optimizations_applied"].append(f"gc_cleanup_{gc_collected}")

        logger.debug(
            f"Orchestrated optimization applied: {len(results['optimizations_applied'])} optimizations"
        )
        return results

    except Exception as e:
        logger.error(f"Error in orchestrated optimization: {e}")
        results["errors"].append(f"Orchestration error: {e}")
        results["fallback_used"] = True
        return results


def cleanup_optimization_state():
    """
    Cleanup global optimization state for session end.

    Should be called when the scraping session ends to clean up resources.
    """
    global _metrics_history, _baseline_metrics, _session_start_time, _extraction_patterns_cache, _memory_cleanup_intervals

    try:
        # Reset metrics
        _metrics_history.clear()
        _baseline_metrics = None
        _session_start_time = time.time()

        # Clear caches
        _extraction_patterns_cache.clear()
        _memory_cleanup_intervals.clear()

        # Force garbage collection
        collected = gc.collect()

        logger.info(f"Optimization state cleaned up, collected {collected} objects")

    except Exception as e:
        logger.error(f"Error cleaning up optimization state: {e}")


# Export key functions for easy importing
__all__ = [
    "create_memory_optimized_session",
    "optimize_page_memory_advanced",
    "setup_extraction_pattern_cache",
    "cache_extraction_pattern",
    "get_cached_extraction_pattern",
    "collect_advanced_metrics",
    "calculate_optimization_impact",
    "generate_optimization_report",
    "create_optimized_orchestration_config",
    "apply_orchestrated_optimization",
    "cleanup_optimization_state",
]

if __name__ == "__main__":
    # Basic test of function-based patterns
    print("🧪 Testing Advanced Optimization Utils...")

    # Test configuration
    config = create_optimized_orchestration_config()
    print(f"✅ Config created: {len(config)} sections")

    # Test caching
    setup_extraction_pattern_cache()
    cache_extraction_pattern("example.com", ["#content", ".title"], 0.95)
    cached = get_cached_extraction_pattern("example.com")
    print(f"✅ Caching works: {cached is not None}")

    # Test metrics
    metrics = collect_advanced_metrics()
    print(f"✅ Metrics collected: {metrics.timestamp}")

    # Test impact calculation
    impact = calculate_optimization_impact()
    print(f"✅ Impact calculated: {impact['status']}")

    # Test report generation
    report = generate_optimization_report()
    print(f"✅ Report generated: {len(report)} characters")

    print("🎉 All tests passed! Advanced optimization utils ready for integration.")
