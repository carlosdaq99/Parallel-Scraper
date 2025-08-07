#!/usr/bin/env python3
"""
Proactive Scaling Configuration Test
Validates that all components are configured for maximum output proactive scaling
"""


def test_proactive_scaling_configuration():
    """Test that all scaling components are configured for proactive scaling"""

    print("🚀 PROACTIVE SCALING CONFIGURATION TEST")
    print("=" * 80)
    print("Philosophy: Maximize output while staying within safe resource limits")
    print("Worker Range: 20-100 (starting at 50)")
    print()

    # Test Configuration
    try:
        from config import ScraperConfig

        print("📋 SCRAPER CONFIGURATION:")
        print(f"   • Max Workers: {ScraperConfig.MAX_WORKERS} (target: 100)")
        print(
            f"   • Min Workers: {getattr(ScraperConfig, 'MIN_WORKERS', 'Not configured')} (target: 20)"
        )
        print(
            f"   • Initial Workers: {getattr(ScraperConfig, 'INITIAL_WORKERS', 'Not configured')} (target: 50)"
        )
        print(
            f"   • Max Concurrent Pages: {ScraperConfig.MAX_CONCURRENT_PAGES} (increased for throughput)"
        )

        # Validate configuration
        config_ok = True
        if ScraperConfig.MAX_WORKERS != 100:
            print(f"   ❌ MAX_WORKERS should be 100, got {ScraperConfig.MAX_WORKERS}")
            config_ok = False
        if not hasattr(ScraperConfig, "MIN_WORKERS") or ScraperConfig.MIN_WORKERS != 20:
            print(f"   ❌ MIN_WORKERS should be 20")
            config_ok = False
        if (
            not hasattr(ScraperConfig, "INITIAL_WORKERS")
            or ScraperConfig.INITIAL_WORKERS != 50
        ):
            print(f"   ❌ INITIAL_WORKERS should be 50")
            config_ok = False

        if config_ok:
            print("   ✅ Scraper configuration: PROACTIVE")
        print()

    except Exception as e:
        print(f"   ❌ Error loading scraper config: {e}")
        print()

    # Test Adaptive Scaling Engine
    try:
        from adaptive_scaling_engine import get_scaling_config

        scaling_config = get_scaling_config()
        print("⚖️ ADAPTIVE SCALING ENGINE:")
        print(f"   • Min Workers: {scaling_config['min_workers']} (target: 20)")
        print(f"   • Max Workers: {scaling_config['max_workers']} (target: 100)")
        print(f"   • Initial Workers: {scaling_config['initial_workers']} (target: 50)")
        print(
            f"   • Scale Up Increment: {scaling_config['scale_up_increment']} (target: 5)"
        )
        print(
            f"   • Scale Down Increment: {scaling_config['scale_down_increment']} (target: 2)"
        )
        print(
            f"   • Scale Up Threshold: {scaling_config['scale_up_success_rate_threshold']} (target: 0.90)"
        )
        print(
            f"   • Monitoring Interval: {scaling_config['monitoring_interval']}s (target: 20s)"
        )

        # Validate adaptive scaling
        adaptive_ok = True
        if scaling_config["min_workers"] != 20:
            print(
                f"   ❌ min_workers should be 20, got {scaling_config['min_workers']}"
            )
            adaptive_ok = False
        if scaling_config["max_workers"] != 100:
            print(
                f"   ❌ max_workers should be 100, got {scaling_config['max_workers']}"
            )
            adaptive_ok = False
        if scaling_config["initial_workers"] != 50:
            print(
                f"   ❌ initial_workers should be 50, got {scaling_config['initial_workers']}"
            )
            adaptive_ok = False
        if scaling_config["scale_up_increment"] != 5:
            print(
                f"   ❌ scale_up_increment should be 5, got {scaling_config['scale_up_increment']}"
            )
            adaptive_ok = False
        if scaling_config["scale_up_success_rate_threshold"] != 0.90:
            print(
                f"   ❌ scale_up_threshold should be 0.90, got {scaling_config['scale_up_success_rate_threshold']}"
            )
            adaptive_ok = False

        if adaptive_ok:
            print("   ✅ Adaptive scaling: PROACTIVE")
        print()

    except Exception as e:
        print(f"   ❌ Error loading adaptive scaling config: {e}")
        print()

    # Test Auto-Tuning Engine
    try:
        from auto_tuning_engine import TuningParameters

        tuning_params = TuningParameters()
        print("🎯 AUTO-TUNING ENGINE:")
        print(f"   • Min Workers: {tuning_params.min_workers} (target: 20)")
        print(f"   • Max Workers: {tuning_params.max_workers} (target: 100)")
        print(
            f"   • Scale Up Increment: {tuning_params.scale_up_increment} (target: 5)"
        )
        print(
            f"   • Scale Down Increment: {tuning_params.scale_down_increment} (target: 2)"
        )
        print(
            f"   • Scale Up Threshold: {tuning_params.scale_up_threshold} (target: 0.90)"
        )
        print(
            f"   • Scale Down Threshold: {tuning_params.scale_down_threshold} (target: 0.80)"
        )

        # Validate auto-tuning
        tuning_ok = True
        if tuning_params.min_workers != 20:
            print(f"   ❌ min_workers should be 20, got {tuning_params.min_workers}")
            tuning_ok = False
        if tuning_params.max_workers != 100:
            print(f"   ❌ max_workers should be 100, got {tuning_params.max_workers}")
            tuning_ok = False
        if tuning_params.scale_up_increment != 5:
            print(
                f"   ❌ scale_up_increment should be 5, got {tuning_params.scale_up_increment}"
            )
            tuning_ok = False
        if tuning_params.scale_up_threshold != 0.90:
            print(
                f"   ❌ scale_up_threshold should be 0.90, got {tuning_params.scale_up_threshold}"
            )
            tuning_ok = False

        if tuning_ok:
            print("   ✅ Auto-tuning: PROACTIVE")
        print()

    except Exception as e:
        print(f"   ❌ Error loading auto-tuning config: {e}")
        print()

    # Test Browser Pool Configuration
    try:
        from optimization_utils import OptimizationConfig

        print("🌐 BROWSER POOL CONFIGURATION:")
        print(
            f"   • Browser Pool Size: {OptimizationConfig.BROWSER_POOL_SIZE} (target: 6)"
        )
        print(
            f"   • Browser Reuse: {OptimizationConfig.BROWSER_REUSE_ENABLED} (should be True)"
        )
        print(f"   • Formula: ~17 workers per browser")
        print(f"   • Capacity: {OptimizationConfig.BROWSER_POOL_SIZE * 17} workers max")

        # Calculate browser scaling recommendations
        for workers in [20, 50, 75, 100]:
            optimal_browsers = min(
                OptimizationConfig.BROWSER_POOL_SIZE, max(1, workers // 17)
            )
            print(f"   • {workers} workers → {optimal_browsers} browsers")

        browser_ok = OptimizationConfig.BROWSER_POOL_SIZE >= 6
        if browser_ok:
            print("   ✅ Browser pool: PROACTIVE")
        else:
            print(
                f"   ❌ Browser pool size should be ≥6, got {OptimizationConfig.BROWSER_POOL_SIZE}"
            )
        print()

    except Exception as e:
        print(f"   ❌ Error loading browser config: {e}")
        print()

    # Test Main Scraper Integration
    try:
        from main_self_contained import INITIAL_WORKERS

        print("🏗️ MAIN SCRAPER INTEGRATION:")
        print(f"   • Initial Workers: {INITIAL_WORKERS} (target: 50)")

        main_ok = INITIAL_WORKERS == 50
        if main_ok:
            print("   ✅ Main scraper: PROACTIVE")
        else:
            print(f"   ❌ INITIAL_WORKERS should be 50, got {INITIAL_WORKERS}")
        print()

    except Exception as e:
        print(f"   ❌ Error loading main scraper config: {e}")
        print()

    print("🎯 PROACTIVE SCALING PHILOSOPHY SUMMARY:")
    print("   • Starting Configuration: 50 workers, 3 browsers")
    print("   • Scaling Range: 20-100 workers, 1-6 browsers")
    print(
        "   • Scaling Strategy: Aggressive scale up (+5), conservative scale down (-2)"
    )
    print("   • Thresholds: Scale up at 90% success, scale down at 80%")
    print("   • Monitoring: Every 20 seconds for responsiveness")
    print("   • Safety Limits: CPU <90%, Memory <85%")
    print("   • Goal: Maximum output while staying within safe resource usage")


if __name__ == "__main__":
    test_proactive_scaling_configuration()
