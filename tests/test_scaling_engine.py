#!/usr/bin/env python3
"""
Test script to validate that the scaling engine is working correctly
after all the fixes applied.
"""

from adaptive_scaling_engine import (
    make_scaling_decision,
    PerformanceMetrics,
    ResourceAvailability,
)
import time


def main():
    print("Testing scaling engine...")

    # Create sample performance metrics (should trigger scale up)
    perf_metrics = PerformanceMetrics(
        timestamp=time.time(),
        avg_page_load_time=1.2,  # Fast response
        memory_usage_mb=450.0,  # Low memory (450MB out of ~8GB)
        cpu_usage_percent=35.0,  # Low CPU
        success_rate=1.0,  # Perfect success (0-1 scale)
        queue_depth=50,  # High queue (renamed from queue_size)
        pages_per_second=5.0,  # Good throughput
        worker_utilization=0.8,  # High utilization
    )

    # Create sample resource availability (should allow scaling)
    resource_availability = ResourceAvailability(
        timestamp=time.time(),
        total_memory_gb=16.0,  # 16GB total
        available_memory_gb=8.0,  # 8GB available
        memory_usage_percent=50.0,  # 50% memory usage
        cpu_count=8,  # 8 CPU cores
        cpu_usage_percent=35.0,  # Low CPU usage
        disk_usage_percent=60.0,  # Moderate disk usage
        network_bandwidth_mbps=100.0,  # 100 Mbps
        system_load_level="normal",  # Normal system load
    )

    print("Performance metrics:", perf_metrics)
    print("Resource availability:", resource_availability)

    # Test scaling decision with 50 current workers
    decision = make_scaling_decision(perf_metrics, resource_availability, 50)
    print("Scaling decision:", decision)

    if decision and hasattr(decision, "new_worker_count"):
        if decision.new_worker_count > 50:
            print("✓ SUCCESS: Scaling engine is working correctly!")
            print(f"  Scaled from 50 to {decision.new_worker_count} workers")
        else:
            print("✗ WARNING: Scaling engine not scaling up as expected")
            print(f"  Worker count: {decision.new_worker_count}")
    else:
        print("✗ ERROR: Scaling decision returned invalid result")
        print(f"  Decision: {decision}")


if __name__ == "__main__":
    main()
