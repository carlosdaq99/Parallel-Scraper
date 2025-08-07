#!/usr/bin/env python3
"""
Debug Scaling Issues Test
Tests the specific scaling problems reported by user
"""

import asyncio
import time
from real_time_monitor import start_real_time_monitor, DashboardMetrics
from adaptive_scaling_engine import get_scaling_config, make_scaling_decision_simple
from data_structures import ParallelWorkerContext


def test_scaling_issues():
    """Test the scaling issues reported"""

    print("🔍 SCALING ISSUES DEBUG TEST")
    print("=" * 80)
    print("Testing reported issues:")
    print("1. Performance score constantly 1/1 but scaling status stays stable")
    print("2. Worker utilization shows 0%")
    print("3. Performance trends avg for success shows wrong value")
    print("4. Browser recommendation not being activated")
    print("5. No scaling happening")
    print()

    # Test 1: Check scaling config
    print("📋 SCALING CONFIGURATION:")
    try:
        config = get_scaling_config()
        print(
            f"   Scale up threshold: {config.get('scale_up_success_rate_threshold', 'NOT SET')}"
        )
        print(
            f"   Scale down threshold: {config.get('scale_down_success_rate_threshold', 'NOT SET')}"
        )
        print(f"   Scale up increment: {config.get('scale_up_increment', 'NOT SET')}")
        print(
            f"   Scale down increment: {config.get('scale_down_increment', 'NOT SET')}"
        )
        print(
            f"   Monitoring interval: {config.get('monitoring_interval_seconds', 'NOT SET')}"
        )
        print()
    except Exception as e:
        print(f"   ❌ Error loading scaling config: {e}")
        print()

    # Test 2: Create mock metrics to test scaling decision
    print("🧪 SCALING DECISION TEST:")
    mock_metrics = {
        "success_rate": 1.0,  # Perfect success rate
        "total_processed": 100,
        "errors_count": 0,
        "avg_processing_time": 2.0,  # Fast processing
        "active_workers": 50,
        "queue_length": 20,
        "cpu_usage": 45.0,
        "memory_usage_mb": 2048,
        "memory_usage_percent": 45.0,
    }

    try:
        decision = make_scaling_decision_simple(mock_metrics)
        print(
            f"   Input: success_rate={mock_metrics['success_rate']}, workers={mock_metrics['active_workers']}"
        )
        print(f"   Decision: {decision.get('action', 'NONE')}")
        print(f"   Reasoning: {decision.get('reasoning', 'NO REASONING')}")
        print(f"   Target workers: {decision.get('target_workers', 'NOT SET')}")
        print()
    except Exception as e:
        print(f"   ❌ Error making scaling decision: {e}")
        print()

    # Test 3: Test worker utilization calculation
    print("👥 WORKER UTILIZATION TEST:")
    try:
        # Simulate worker context
        total_workers = 50
        busy_workers = 25  # 50% utilization
        utilization = (busy_workers / total_workers) * 100
        print(f"   Total workers: {total_workers}")
        print(f"   Busy workers: {busy_workers}")
        print(f"   Calculated utilization: {utilization:.1f}%")
        print()
    except Exception as e:
        print(f"   ❌ Error calculating utilization: {e}")
        print()

    # Test 4: Check browser recommendations
    print("🌐 BROWSER POOL TEST:")
    try:
        from optimization_utils import OptimizationConfig

        workers = 50
        optimal_browsers = min(
            OptimizationConfig.BROWSER_POOL_SIZE, max(1, workers // 17)
        )
        print(f"   Workers: {workers}")
        print(f"   Optimal browsers: {optimal_browsers}")
        print(f"   Browser pool size limit: {OptimizationConfig.BROWSER_POOL_SIZE}")
        print()
    except Exception as e:
        print(f"   ❌ Error calculating browser recommendation: {e}")
        print()


if __name__ == "__main__":
    test_scaling_issues()
