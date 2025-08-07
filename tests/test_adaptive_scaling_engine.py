#!/usr/bin/env python3
"""
Test Adaptive Scaling Engine - Demonstration of Step 2 Implementation
Tests the core adaptive scaling engine functionality.

This script demonstrates:
1. Performance metrics collection and trend analysis
2. Resource availability monitoring and safety checks
3. Intelligent scaling decisions with confidence scoring
4. Integration with enhanced intelligence layer from Step 1
"""

import asyncio
import time
import json
from datetime import datetime
from pathlib import Path
from dataclasses import asdict

# Import the adaptive scaling engine
try:
    from adaptive_scaling_engine import (
        initialize_adaptive_scaling_engine,
        collect_performance_metrics,
        collect_resource_availability,
        analyze_performance_trends_for_scaling,
        make_scaling_decision,
        execute_scaling_decision,
        run_adaptive_scaling_cycle,
        get_scaling_status,
        print_scaling_status,
        get_current_worker_count,
        set_current_worker_count,
        update_scaling_config,
    )

    print("✅ Adaptive scaling engine module imported successfully")
except ImportError as e:
    print(f"❌ Failed to import adaptive scaling engine: {e}")
    exit(1)


class AdaptiveScalingDemo:
    """Demonstration of adaptive scaling engine capabilities."""

    def __init__(self):
        """Initialize the demo."""
        self.results = {}
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)

        # Initialize the scaling engine
        self.initialization_result = initialize_adaptive_scaling_engine()

    async def run_comprehensive_demo(self):
        """Run the complete adaptive scaling engine demonstration."""
        print("🚀 Starting Adaptive Scaling Engine Demo...")
        print("=" * 80)
        print("ADAPTIVE SCALING ENGINE DEMONSTRATION")
        print("=" * 80)

        # Test all components
        await self.test_initialization()
        await self.test_performance_metrics_collection()
        await self.test_resource_availability_monitoring()
        await self.test_trend_analysis()
        await self.test_scaling_decisions()
        await self.test_scaling_cycles()
        await self.test_scaling_scenarios()

        # Generate comprehensive report
        await self.generate_comprehensive_report()

        # Print summary
        self.print_test_summary()

    async def test_initialization(self):
        """Test adaptive scaling engine initialization."""
        print("\n🎯 Testing Adaptive Scaling Engine Initialization...")

        try:
            # Check initialization result
            if (
                self.initialization_result
                and self.initialization_result.get("status") == "initialized"
            ):
                print(f"  ✅ Engine initialized successfully")
                print(
                    f"  📊 Initial workers: {self.initialization_result['initial_workers']}"
                )
                print(
                    f"  ⚙️ Configuration loaded: {len(self.initialization_result['config'])} settings"
                )

                self.results["initialization"] = {
                    "status": "success",
                    "initial_workers": self.initialization_result["initial_workers"],
                    "config_loaded": True,
                }
            else:
                raise Exception("Initialization failed or returned invalid result")

        except Exception as e:
            print(f"  ❌ Initialization test failed: {e}")
            self.results["initialization"] = {"status": "failed", "error": str(e)}

    async def test_performance_metrics_collection(self):
        """Test performance metrics collection."""
        print("\n📊 Testing Performance Metrics Collection...")

        try:
            # Collect multiple performance snapshots
            metrics_samples = []
            for i in range(3):
                metrics = collect_performance_metrics()
                metrics_samples.append(metrics)
                print(f"  📈 Performance snapshot {i+1}/3 collected")
                await asyncio.sleep(0.5)

            # Analyze the metrics
            latest_metrics = metrics_samples[-1]
            performance_score = latest_metrics.calculate_performance_score()

            print(f"  ✅ Metrics collection successful")
            print(f"  🔍 Key Insights:")
            print(f"    - Performance Score: {performance_score:.3f}")
            print(f"    - Success Rate: {latest_metrics.success_rate:.1%}")
            print(f"    - Avg Response Time: {latest_metrics.avg_page_load_time:.2f}s")
            print(f"    - CPU Usage: {latest_metrics.cpu_usage_percent:.1f}%")
            print(f"    - Memory Usage: {latest_metrics.memory_usage_mb:.1f} MB")

            self.results["performance_metrics"] = {
                "status": "success",
                "samples_collected": len(metrics_samples),
                "latest_metrics": asdict(latest_metrics),
                "performance_score": performance_score,
            }

        except Exception as e:
            print(f"  ❌ Performance metrics test failed: {e}")
            self.results["performance_metrics"] = {"status": "failed", "error": str(e)}

    async def test_resource_availability_monitoring(self):
        """Test resource availability monitoring."""
        print("\n🖥️  Testing Resource Availability Monitoring...")

        try:
            # Collect resource availability
            resources = collect_resource_availability()
            scaling_capacity = resources.calculate_scaling_capacity()

            print(f"  📸 Resource snapshot taken")
            print(f"  ✅ Resource monitoring successful")
            print(f"  🔍 Key Insights:")
            print(f"    - Memory Usage: {resources.memory_usage_percent:.1f}%")
            print(f"    - CPU Usage: {resources.cpu_usage_percent:.1f}%")
            print(f"    - System Load: {resources.system_load_level}")
            print(f"    - Scaling Capacity: {scaling_capacity:.1%}")
            print(
                f"    - Safe to Scale Up: {'✅' if resources.is_safe_to_scale_up() else '❌'}"
            )
            print(
                f"    - Requires Scale Down: {'⚠️' if resources.requires_scale_down() else '✅'}"
            )

            self.results["resource_monitoring"] = {
                "status": "success",
                "resource_snapshot": asdict(resources),
                "scaling_capacity": scaling_capacity,
                "safe_to_scale_up": resources.is_safe_to_scale_up(),
                "requires_scale_down": resources.requires_scale_down(),
            }

        except Exception as e:
            print(f"  ❌ Resource monitoring test failed: {e}")
            self.results["resource_monitoring"] = {"status": "failed", "error": str(e)}

    async def test_trend_analysis(self):
        """Test performance trend analysis."""
        print("\n📈 Testing Performance Trend Analysis...")

        try:
            # Generate some performance history by collecting metrics
            print(f"  📊 Building performance history...")
            for i in range(5):
                metrics = collect_performance_metrics()
                # Simulate some variation
                await asyncio.sleep(0.2)

            # Analyze trends
            trend_analysis = analyze_performance_trends_for_scaling(lookback_minutes=1)

            print(f"  ✅ Trend analysis completed")
            print(f"  🔍 Key Insights:")
            print(f"    - Status: {trend_analysis.get('status', 'unknown')}")
            print(
                f"    - Trend Direction: {trend_analysis.get('trend_direction', 'unknown')}"
            )
            print(f"    - Confidence: {trend_analysis.get('confidence', 0):.2f}")
            print(
                f"    - Recommendation: {trend_analysis.get('recommendation', 'unknown')}"
            )
            print(f"    - Data Points: {trend_analysis.get('data_points', 0)}")

            self.results["trend_analysis"] = {
                "status": "success",
                "trend_results": trend_analysis,
            }

        except Exception as e:
            print(f"  ❌ Trend analysis test failed: {e}")
            self.results["trend_analysis"] = {"status": "failed", "error": str(e)}

    async def test_scaling_decisions(self):
        """Test intelligent scaling decision making."""
        print("\n🧠 Testing Intelligent Scaling Decisions...")

        try:
            # Collect current data
            performance_metrics = collect_performance_metrics()
            resource_availability = collect_resource_availability()
            trend_analysis = analyze_performance_trends_for_scaling()

            # Make scaling decision
            decision = make_scaling_decision(
                performance_metrics, resource_availability, trend_analysis
            )

            print(f"  ✅ Scaling decision made")
            print(f"  🔍 Decision Details:")
            print(f"    - Action: {decision.action}")
            print(f"    - Current Workers: {decision.current_workers}")
            print(f"    - Target Workers: {decision.target_workers}")
            print(f"    - Confidence: {decision.confidence:.2f}")
            print(f"    - Reasoning: {decision.reasoning}")
            print(f"    - Performance Score: {decision.performance_score:.3f}")
            print(f"    - Resource Capacity: {decision.resource_capacity:.1%}")

            # Test decision execution
            execution_result = execute_scaling_decision(decision)
            print(
                f"    - Execution: {'✅ Success' if execution_result else '❌ Failed'}"
            )

            self.results["scaling_decisions"] = {
                "status": "success",
                "decision": asdict(decision),
                "execution_successful": execution_result,
            }

        except Exception as e:
            print(f"  ❌ Scaling decision test failed: {e}")
            self.results["scaling_decisions"] = {"status": "failed", "error": str(e)}

    async def test_scaling_cycles(self):
        """Test complete scaling cycles."""
        print("\n🔄 Testing Complete Scaling Cycles...")

        try:
            cycle_results = []

            # Run multiple scaling cycles
            for i in range(3):
                print(f"  🔁 Running scaling cycle {i+1}/3...")
                decision = run_adaptive_scaling_cycle()
                cycle_results.append(decision)
                await asyncio.sleep(1.0)

            print(f"  ✅ Scaling cycles completed")
            print(f"  🔍 Cycle Summary:")
            for i, decision in enumerate(cycle_results):
                action_emoji = {"scale_up": "⬆️", "scale_down": "⬇️", "no_change": "➡️"}
                print(
                    f"    Cycle {i+1}: {action_emoji.get(decision.action, '❓')} {decision.action} (confidence: {decision.confidence:.2f})"
                )

            self.results["scaling_cycles"] = {
                "status": "success",
                "cycles_completed": len(cycle_results),
                "cycle_results": [asdict(decision) for decision in cycle_results],
            }

        except Exception as e:
            print(f"  ❌ Scaling cycles test failed: {e}")
            self.results["scaling_cycles"] = {"status": "failed", "error": str(e)}

    async def test_scaling_scenarios(self):
        """Test different scaling scenarios."""
        print("\n🎭 Testing Different Scaling Scenarios...")

        try:
            scenarios = []
            original_worker_count = get_current_worker_count()

            # Scenario 1: High performance - should scale up
            print(f"  📈 Scenario 1: High Performance")
            update_scaling_config(
                {
                    "scale_up_success_rate_threshold": 0.8,  # Lower threshold
                    "scale_up_response_time_threshold": 5.0,  # Higher threshold
                }
            )
            set_current_worker_count(5)
            decision1 = run_adaptive_scaling_cycle()
            scenarios.append(("high_performance", decision1))
            await asyncio.sleep(0.5)

            # Scenario 2: Resource pressure - should scale down or maintain
            print(f"  📉 Scenario 2: Resource Pressure")
            update_scaling_config(
                {
                    "max_memory_usage_percent": 60.0,  # Lower threshold
                    "max_cpu_usage_percent": 70.0,  # Lower threshold
                }
            )
            decision2 = run_adaptive_scaling_cycle()
            scenarios.append(("resource_pressure", decision2))
            await asyncio.sleep(0.5)

            # Scenario 3: Balanced conditions - should maintain
            print(f"  ⚖️ Scenario 3: Balanced Conditions")
            update_scaling_config(
                {
                    "scale_up_success_rate_threshold": 0.95,
                    "scale_down_success_rate_threshold": 0.85,
                    "max_memory_usage_percent": 85.0,
                    "max_cpu_usage_percent": 90.0,
                }
            )
            decision3 = run_adaptive_scaling_cycle()
            scenarios.append(("balanced", decision3))

            # Restore original worker count
            set_current_worker_count(original_worker_count)

            print(f"  ✅ Scaling scenarios completed")
            print(f"  🔍 Scenario Results:")
            for scenario_name, decision in scenarios:
                action_emoji = {"scale_up": "⬆️", "scale_down": "⬇️", "no_change": "➡️"}
                print(
                    f"    {scenario_name}: {action_emoji.get(decision.action, '❓')} {decision.action}"
                )

            self.results["scaling_scenarios"] = {
                "status": "success",
                "scenarios_tested": len(scenarios),
                "scenario_results": [
                    {"scenario": name, "decision": asdict(decision)}
                    for name, decision in scenarios
                ],
            }

        except Exception as e:
            print(f"  ❌ Scaling scenarios test failed: {e}")
            self.results["scaling_scenarios"] = {"status": "failed", "error": str(e)}

    async def generate_comprehensive_report(self):
        """Generate a comprehensive test report."""
        print("\n📋 Generating Comprehensive Scaling Engine Report...")

        try:
            # Get current status
            scaling_status = get_scaling_status()

            report = {
                "test_timestamp": time.time(),
                "test_datetime": datetime.now().isoformat(),
                "adaptive_scaling_engine_test_results": self.results,
                "final_scaling_status": scaling_status,
                "test_summary": {
                    "total_tests": len(self.results),
                    "successful_tests": len(
                        [
                            r
                            for r in self.results.values()
                            if r.get("status") == "success"
                        ]
                    ),
                    "failed_tests": len(
                        [
                            r
                            for r in self.results.values()
                            if r.get("status") == "failed"
                        ]
                    ),
                    "success_rate": (
                        len(
                            [
                                r
                                for r in self.results.values()
                                if r.get("status") == "success"
                            ]
                        )
                        / len(self.results)
                        * 100
                        if self.results
                        else 0
                    ),
                },
            }

            # Save report
            report_file = self.reports_dir / "adaptive_scaling_engine_test_report.json"
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, default=str)

            print(f"  ✅ Report saved to: {report_file}")

        except Exception as e:
            print(f"  ❌ Failed to generate report: {e}")

    def print_test_summary(self):
        """Print a comprehensive test summary."""
        print("\n" + "=" * 80)
        print("ADAPTIVE SCALING ENGINE TEST SUMMARY")
        print("=" * 80)

        total_tests = len(self.results)
        successful_tests = len(
            [r for r in self.results.values() if r.get("status") == "success"]
        )
        failed_tests = len(
            [r for r in self.results.values() if r.get("status") == "failed"]
        )
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"📊 Total Components Tested: {total_tests}")
        print(f"✅ Successful Tests: {successful_tests}")
        print(f"❌ Failed Tests: {failed_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")

        if success_rate == 100:
            print(f"🎯 Overall Status: SUCCESS")
            print(f"🎉 Adaptive Scaling Engine implementation successful!")
            print(f"   Ready for integration and production use!")
        elif success_rate >= 80:
            print(f"🎯 Overall Status: MOSTLY_SUCCESS")
            print(f"⚠️  Most components working - review failed tests")
        elif success_rate >= 50:
            print(f"🎯 Overall Status: PARTIAL_SUCCESS")
            print(f"⚠️  Some components failed - review errors before proceeding")
        else:
            print(f"🎯 Overall Status: NEEDS_WORK")
            print(f"❌ Major issues found - implementation needs significant fixes")

        print(f"\n📋 Component Status:")
        for component, result in self.results.items():
            status_emoji = "✅" if result.get("status") == "success" else "❌"
            component_name = component.replace("_", " ").title()
            print(
                f"  {status_emoji} {component_name}: {result.get('status', 'unknown')}"
            )

        # Print current scaling status
        print_scaling_status()

        print(
            f"\n✨ Demo completed! Check the reports/ directory for detailed results."
        )


async def main():
    """Main demo function."""
    demo = AdaptiveScalingDemo()
    await demo.run_comprehensive_demo()


if __name__ == "__main__":
    asyncio.run(main())
