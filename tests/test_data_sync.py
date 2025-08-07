#!/usr/bin/env python3
"""
Live Dashboard Data vs Scaling Engine Data Test

This test runs the actual monitor with live data to compare what the dashboard shows
vs what gets passed to the scaling engine. This will help identify data sync issues.
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from main_self_contained import (
    initialize_adaptive_scaling,
    get_current_workers,
    _adaptive_workers,
)
from adaptive_scaling_engine import make_scaling_decision_simple
from real_time_monitor import RealTimeMonitor
import time


def test_data_sync_issues():
    """Test data synchronization between dashboard and scaling engine"""

    print("🔧 Testing Live Data Synchronization Issues")
    print("=" * 60)

    # Initialize scaling system
    initialize_adaptive_scaling()

    # Create monitor without worker context (standalone mode)
    monitor = RealTimeMonitor()

    # Collect current dashboard metrics
    dashboard_metrics = monitor._collect_current_metrics()

    print("📊 DASHBOARD METRICS:")
    print(f"   Active Workers: {dashboard_metrics.active_workers}")
    print(f"   Worker Utilization: {dashboard_metrics.worker_utilization}%")
    print(f"   Queue Length: {dashboard_metrics.queue_length}")
    print(f"   Pages/Second: {dashboard_metrics.pages_per_second}")
    print(f"   Queue/Worker Ratio: {dashboard_metrics.queue_to_worker_ratio}")
    print(f"   Resource Capacity: {dashboard_metrics.resource_capacity}")
    print(f"   Performance Score: {dashboard_metrics.performance_score}")
    print(f"   Browser Pool Size: {dashboard_metrics.browser_pool_size}")
    print(f"   Browser Pool Rec: {dashboard_metrics.browser_pool_recommendation}")
    print()

    # Now create metrics_dict like scaling engine expects
    print("🔧 SCALING ENGINE METRICS:")
    current_workers = get_current_workers()
    print(f"   Current Workers from Engine: {current_workers}")
    print(f"   Global _adaptive_workers: {_adaptive_workers}")

    # Create metrics dict like the scaling system does
    metrics_dict = {
        "success_rate": 1.0,
        "avg_processing_time": 2.0,
        "queue_size": 0,
        "cpu_usage_percent": 30.0,
        "memory_usage_mb": 512.0,
        "current_workers": current_workers,
    }

    print(f"   Metrics Dict: {metrics_dict}")

    # Test scaling decision
    scaling_decision = make_scaling_decision_simple(metrics_dict)
    print(f"   Scaling Decision: {scaling_decision}")
    print()

    print("❌ IDENTIFIED ISSUES:")

    # Issue 1: Dashboard worker count vs scaling engine worker count
    if dashboard_metrics.active_workers != current_workers:
        print(f"   1. Worker Count Mismatch:")
        print(
            f"      Dashboard shows: {dashboard_metrics.active_workers} active workers"
        )
        print(f"      Scaling engine has: {current_workers} workers")
        print(f"      This explains why dashboard may show wrong utilization")

    # Issue 2: Dashboard vs scaling engine metrics format
    if (
        dashboard_metrics.worker_utilization
        and dashboard_metrics.worker_utilization > 100
    ):
        print(f"   2. Worker Utilization Format Issue:")
        print(
            f"      Dashboard shows: {dashboard_metrics.worker_utilization}% (percentage)"
        )
        print(f"      Scaling engine may expect: decimal (0-1.0)")

    # Issue 3: No live data vs hardcoded data
    if (
        metrics_dict["queue_size"] == 0
        and dashboard_metrics.queue_length
        and dashboard_metrics.queue_length > 0
    ):
        print(f"   3. Data Source Mismatch:")
        print(f"      Dashboard queue: {dashboard_metrics.queue_length}")
        print(f"      Scaling engine queue: {metrics_dict['queue_size']} (hardcoded!)")

    # Issue 4: Success rate calculation differences
    if dashboard_metrics.success_rate and dashboard_metrics.success_rate < 1.0:
        print(f"   4. Success Rate Mismatch:")
        print(f"      Dashboard success rate: {dashboard_metrics.success_rate:.1%}")
        print(
            f"      Scaling engine success rate: {metrics_dict['success_rate']:.1%} (hardcoded!)"
        )

    print()
    print("✅ RECOMMENDATIONS:")
    print("   1. Synchronize worker count tracking between dashboard and engine")
    print("   2. Use consistent data format (percentage vs decimal)")
    print(
        "   3. Pass real dashboard metrics to scaling engine instead of hardcoded values"
    )
    print("   4. Ensure both systems use the same data sources")


if __name__ == "__main__":
    test_data_sync_issues()
