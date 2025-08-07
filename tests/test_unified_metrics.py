#!/usr/bin/env python3
"""
Test Unified Metrics System

This script tests the new unified metrics system to ensure it provides
consistent data to both dashboard and scaling engine.
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from unified_metrics import get_metrics_for_scaling_engine, get_metrics_for_dashboard
from main_self_contained import initialize_adaptive_scaling, get_current_workers
from adaptive_scaling_engine import make_scaling_decision_simple


def test_unified_metrics():
    """Test the unified metrics system for data consistency"""

    print("🔧 Testing Unified Metrics System")
    print("=" * 50)

    # Initialize scaling system
    initialize_adaptive_scaling()

    print("📊 TESTING UNIFIED METRICS:")
    print()

    # Test scaling engine format
    print("🚀 SCALING ENGINE FORMAT:")
    scaling_metrics = get_metrics_for_scaling_engine()
    for key, value in scaling_metrics.items():
        print(f"   {key}: {value}")

    print()

    # Test dashboard format
    print("📺 DASHBOARD FORMAT:")
    dashboard_metrics = get_metrics_for_dashboard()
    key_metrics = [
        "active_workers",
        "worker_utilization",
        "queue_length",
        "pages_per_second",
        "queue_to_worker_ratio",
        "resource_capacity",
        "performance_score",
        "browser_pool_size",
        "browser_pool_recommendation",
    ]

    for key in key_metrics:
        value = dashboard_metrics.get(key, "N/A")
        print(f"   {key}: {value}")

    print()

    # Test scaling decision
    print("🧠 SCALING DECISION TEST:")
    scaling_decision = make_scaling_decision_simple(scaling_metrics)
    print(f"   Decision: {scaling_decision}")

    print()

    # Verify data consistency
    print("✅ DATA CONSISTENCY CHECK:")
    current_workers_engine = scaling_metrics.get("current_workers")
    current_workers_dashboard = dashboard_metrics.get("current_workers")
    current_workers_global = get_current_workers()

    print(f"   Scaling Engine Workers: {current_workers_engine}")
    print(f"   Dashboard Workers: {current_workers_dashboard}")
    print(f"   Global Workers: {current_workers_global}")

    if current_workers_engine == current_workers_dashboard == current_workers_global:
        print("   ✅ Worker counts are synchronized!")
    else:
        print("   ❌ Worker count mismatch detected")

    # Check utilization formats
    scaling_util = scaling_metrics.get("worker_utilization", 0)  # Should be 0-1.0
    dashboard_util = dashboard_metrics.get("worker_utilization", 0)  # Should be 0-100%

    print(f"   Scaling Engine Utilization: {scaling_util} (decimal)")
    print(f"   Dashboard Utilization: {dashboard_util}% (percentage)")

    if 0 <= scaling_util <= 1.0 and 0 <= dashboard_util <= 100:
        print("   ✅ Utilization formats are correct!")
    else:
        print("   ❌ Utilization format issues detected")

    # Check queue data consistency
    scaling_queue = scaling_metrics.get("queue_size", 0)
    dashboard_queue = dashboard_metrics.get("queue_length", 0)

    print(f"   Scaling Engine Queue: {scaling_queue}")
    print(f"   Dashboard Queue: {dashboard_queue}")

    if scaling_queue == dashboard_queue:
        print("   ✅ Queue data is synchronized!")
    else:
        print("   ❌ Queue data mismatch detected")


if __name__ == "__main__":
    test_unified_metrics()
