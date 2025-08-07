#!/usr/bin/env python3
"""
Debug script for low activity pattern detection
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from auto_tuning_engine import AutoTuningEngine
import statistics


def debug_low_activity():
    """Debug the low activity pattern detection"""
    print("🔍 Debugging low activity pattern detection...")

    # Initialize engine
    engine = AutoTuningEngine()

    # Clear history and simulate low activity
    engine.performance_history.clear()
    low_activity_metrics = [
        {
            "success_rate": 0.99,
            "avg_processing_time": 0.8,
            "cpu_usage_percent": 10.0,
            "memory_usage_mb": 150.0,
            "active_workers": 12,
            "queue_length": 0,
            "error_rate": 0.01,
        },
        {
            "success_rate": 0.98,
            "avg_processing_time": 0.9,
            "cpu_usage_percent": 8.0,
            "memory_usage_mb": 140.0,
            "active_workers": 10,
            "queue_length": 0,
            "error_rate": 0.01,
        },
        {
            "success_rate": 0.99,
            "avg_processing_time": 0.7,
            "cpu_usage_percent": 12.0,
            "memory_usage_mb": 160.0,
            "active_workers": 9,
            "queue_length": 1,
            "error_rate": 0.01,
        },
        {
            "success_rate": 0.98,
            "avg_processing_time": 0.6,
            "cpu_usage_percent": 15.0,
            "memory_usage_mb": 130.0,
            "active_workers": 8,
            "queue_length": 0,
            "error_rate": 0.01,
        },
    ]

    print(f"📊 Test data has {len(low_activity_metrics)} metrics samples")

    # Collect samples
    for i, metrics in enumerate(low_activity_metrics):
        print(
            f"   Sample {i+1}: CPU={metrics['cpu_usage_percent']}%, Workers={metrics['active_workers']}, Queue={metrics['queue_length']}"
        )
        engine.collect_performance_sample(metrics)

    # Check what's in the performance history
    print(f"\n📝 Performance history has {len(engine.performance_history)} samples")
    if engine.performance_history:
        sample = engine.performance_history[-1]
        print(f"   Last sample keys: {list(sample.keys())}")
        print(f"   Last sample: {sample}")

    # Manual calculation for verification
    recent_data = (
        engine.performance_history[-5:]
        if len(engine.performance_history) >= 5
        else engine.performance_history
    )
    print(f"\n🔢 Manual calculation using {len(recent_data)} samples:")

    if recent_data:
        recent_workers = [d["active_workers"] for d in recent_data]
        recent_queue = [d["queue_length"] for d in recent_data]
        recent_cpu = [d["cpu_usage"] for d in recent_data]

        avg_workers = statistics.mean(recent_workers)
        avg_queue = statistics.mean(recent_queue)
        avg_cpu = statistics.mean(recent_cpu)

        print(f"   Recent workers: {recent_workers} → avg = {avg_workers}")
        print(f"   Recent queue: {recent_queue} → avg = {avg_queue}")
        print(f"   Recent CPU: {recent_cpu} → avg = {avg_cpu}")

        # Check conditions
        low_utilization = avg_cpu < 30.0
        small_queue = avg_queue < 2.0
        moderate_workers = avg_workers > engine.tuning_params.min_workers + 2

        print(f"\n🎯 Condition checks:")
        print(f"   Low utilization (CPU < 30.0): {avg_cpu} < 30.0 = {low_utilization}")
        print(f"   Small queue (queue < 2.0): {avg_queue} < 2.0 = {small_queue}")
        print(
            f"   Moderate workers (workers > {engine.tuning_params.min_workers + 2}): {avg_workers} > {engine.tuning_params.min_workers + 2} = {moderate_workers}"
        )
        print(
            f"   All conditions met: {low_utilization and small_queue and moderate_workers}"
        )

    # Test pattern detection
    print(f"\n🔍 Pattern detection test...")
    patterns = engine.detect_performance_patterns()
    print(f"   Detected {len(patterns)} patterns")

    for pattern in patterns:
        print(
            f"   Pattern: {pattern.pattern_type} (confidence: {pattern.confidence:.2f})"
        )

    low_activity_detected = any(p.pattern_type == "low_activity" for p in patterns)
    print(f"\n📊 Result: Low activity pattern detected = {low_activity_detected}")

    if not low_activity_detected:
        print("❌ LOW ACTIVITY PATTERN NOT DETECTED - DEBUGGING ISSUE FOUND")
        return False
    else:
        print("✅ LOW ACTIVITY PATTERN DETECTED - WORKING CORRECTLY")
        return True


if __name__ == "__main__":
    debug_low_activity()
