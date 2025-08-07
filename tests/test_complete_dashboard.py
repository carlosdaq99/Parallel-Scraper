#!/usr/bin/env python3
"""Test complete dashboard functionality"""

import sys
import os
import asyncio

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from real_time_monitor import RealTimeMonitor
from data_structures import ParallelWorkerContext


async def test_complete_dashboard():
    """Test complete dashboard with all sections"""
    print("Testing complete dashboard functionality...")

    # Create monitor
    monitor = RealTimeMonitor(update_interval=3)

    # Get one set of metrics and display
    metrics = monitor._collect_current_metrics()

    print("=== DASHBOARD OUTPUT ===")
    monitor.display_dashboard(metrics)

    print("\n=== METRICS ANALYSIS ===")
    print(f"Performance metrics available: {metrics.has_performance_data}")
    print(f"Worker data available: {metrics.has_worker_data}")
    print(f"System resources available: {metrics.has_system_data}")
    print(f"Adaptive scaling available: {metrics.has_adaptive_data}")
    print(f"Auto-tuning active: {metrics.auto_tuning_active}")

    print("\nTest completed!")


if __name__ == "__main__":
    asyncio.run(test_complete_dashboard())
