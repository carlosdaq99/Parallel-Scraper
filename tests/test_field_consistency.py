#!/usr/bin/env python3
"""
Diagnostic script to identify field name inconsistencies between unified_metrics and real_time_monitor.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test imports
from unified_metrics import get_unified_metrics, get_metrics_for_dashboard
from real_time_monitor import DashboardMetrics, RealTimeMonitor


def analyze_field_consistency():
    """Analyze field consistency between data providers and consumers."""
    print("🔍 Analyzing Field Name Consistency...")
    print("=" * 60)

    # Step 1: Get sample data from unified_metrics
    print("📊 Step 1: Collecting sample unified metrics data...")
    try:
        unified_data = get_unified_metrics().to_dict()
        print(f"   Unified metrics keys: {sorted(unified_data.keys())}")

        # Look for CPU/memory related fields
        cpu_fields = [k for k in unified_data.keys() if "cpu" in k.lower()]
        memory_fields = [k for k in unified_data.keys() if "memory" in k.lower()]

        print(f"   CPU-related fields: {cpu_fields}")
        print(f"   Memory-related fields: {memory_fields}")
        print()

    except Exception as e:
        print(f"   ❌ Failed to collect unified metrics: {e}")
        return False

    # Step 2: Get dashboard format
    print("📈 Step 2: Getting dashboard format from unified metrics...")
    try:
        dashboard_data = get_metrics_for_dashboard()
        print(f"   Dashboard format keys: {sorted(dashboard_data.keys())}")

        # Look for CPU/memory in dashboard format
        dash_cpu_fields = [k for k in dashboard_data.keys() if "cpu" in k.lower()]
        dash_memory_fields = [k for k in dashboard_data.keys() if "memory" in k.lower()]

        print(f"   Dashboard CPU-related fields: {dash_cpu_fields}")
        print(f"   Dashboard Memory-related fields: {dash_memory_fields}")
        print()

    except Exception as e:
        print(f"   ❌ Failed to get dashboard format: {e}")
        return False

    # Step 3: Check DashboardMetrics dataclass fields
    print("📋 Step 3: Checking DashboardMetrics dataclass fields...")
    from dataclasses import fields

    metric_fields = [f.name for f in fields(DashboardMetrics)]
    cpu_metric_fields = [k for k in metric_fields if "cpu" in k.lower()]
    memory_metric_fields = [k for k in metric_fields if "memory" in k.lower()]

    print(f"   DashboardMetrics CPU fields: {cpu_metric_fields}")
    print(f"   DashboardMetrics Memory fields: {memory_metric_fields}")
    print()

    # Step 4: Test mapping consistency
    print("🔧 Step 4: Testing field mapping consistency...")

    # Check if dashboard_data fields map to DashboardMetrics fields
    field_mapping_issues = []

    for field_name in dashboard_data.keys():
        if hasattr(DashboardMetrics, field_name):
            print(f"   ✅ {field_name}: Mapped correctly")
        else:
            field_mapping_issues.append(field_name)
            print(f"   ❌ {field_name}: No corresponding DashboardMetrics field")

    if field_mapping_issues:
        print(f"\n⚠️  Field mapping issues found: {field_mapping_issues}")
    else:
        print(f"\n✅ All dashboard fields have corresponding DashboardMetrics fields")

    print()

    # Step 5: Create test monitor and check history storage
    print("📚 Step 5: Testing performance history field storage...")

    # Create a test DashboardMetrics instance
    test_metrics = DashboardMetrics(
        timestamp="2025-01-15T10:00:00",
        cpu_usage=45.0,  # Test CPU field
        memory_usage_percent=60.0,  # Test memory field
        success_rate=0.95,
    )

    # Create test monitor
    monitor = RealTimeMonitor()

    # Test the history update method
    try:
        monitor._update_performance_history(test_metrics)

        if monitor.performance_history:
            history_entry = monitor.performance_history[-1]
            print(f"   History entry keys: {sorted(history_entry.keys())}")

            # Check specific fields
            cpu_in_history = "cpu_usage" in history_entry
            memory_in_history = "memory_usage_percent" in history_entry

            print(f"   cpu_usage in history: {cpu_in_history}")
            print(f"   memory_usage_percent in history: {memory_in_history}")

            if cpu_in_history and memory_in_history:
                print("   ✅ Performance history stores expected fields")
            else:
                print("   ❌ Performance history missing expected fields")
        else:
            print("   ❌ No history entries created")

    except Exception as e:
        print(f"   ❌ Failed to test history storage: {e}")

    print("\n" + "=" * 60)
    print("🎯 CONSISTENCY ANALYSIS COMPLETE")

    return True


if __name__ == "__main__":
    success = analyze_field_consistency()
    sys.exit(0 if success else 1)
