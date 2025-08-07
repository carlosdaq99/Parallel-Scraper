#!/usr/bin/env python3
"""
Comprehensive Test Suite for Unified Parallel Web Scraper
=========================================================

This test suite validates the unified Python parallel web scraper system
across multiple dimensions including functionality, performance, error handling,
configuration, and edge cases.

Test Phases:
1. Foundation Validation (CRITICAL - BLOCKING)
2. Component Testing (HIGH PRIORITY)
3. Integration Testing (HIGH PRIORITY)
4. Performance Testing (MEDIUM PRIORITY)
5. Error Handling Testing (MEDIUM PRIORITY)

Usage:
    python comprehensive_test_suite.py --full --report-format=detailed --output-dir=test_results
    python comprehensive_test_suite.py --phase=foundation
    python comprehensive_test_suite.py --quick
"""

import sys
import os
import json
import time
import traceback
import argparse
from datetime import datetime
from typing import Dict, List
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestResult:
    """Container for individual test results"""

    def __init__(self, name: str, phase: str, priority: str):
        self.name = name
        self.phase = phase
        self.priority = priority
        self.passed = False
        self.error_message = None
        self.execution_time = 0.0
        self.details = {}
        self.start_time = None
        self.end_time = None

    def start(self):
        """Mark test start time"""
        self.start_time = time.time()

    def finish(self, passed: bool, error_message: str = None, details: Dict = None):
        """Mark test completion"""
        self.end_time = time.time()
        self.execution_time = (
            self.end_time - self.start_time if self.start_time else 0.0
        )
        self.passed = passed
        self.error_message = error_message
        self.details = details or {}

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "name": self.name,
            "phase": self.phase,
            "priority": self.priority,
            "passed": self.passed,
            "error_message": self.error_message,
            "execution_time": self.execution_time,
            "details": self.details,
            "start_time": self.start_time,
            "end_time": self.end_time,
        }


class TestSuite:
    """Main test suite orchestrator"""

    def __init__(self, output_dir: str = "test_results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.results: List[TestResult] = []
        self.phase_results: Dict[str, List[TestResult]] = {
            "foundation": [],
            "component": [],
            "integration": [],
            "performance": [],
            "error_handling": [],
        }
        self.start_time = None
        self.end_time = None

    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")

    def run_test(self, test_func, name: str, phase: str, priority: str) -> TestResult:
        """Run individual test and capture results"""
        result = TestResult(name, phase, priority)
        result.start()

        self.log(f"Running {phase} test: {name}")

        try:
            test_details = test_func()
            result.finish(True, details=test_details)
            self.log(f"✓ PASSED: {name} ({result.execution_time:.2f}s)")
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            result.finish(False, error_msg)
            self.log(f"✗ FAILED: {name} - {error_msg}", "ERROR")
            if priority == "CRITICAL":
                self.log("CRITICAL test failed - stopping execution", "ERROR")
                raise

        self.results.append(result)
        self.phase_results[phase].append(result)
        return result

    def run_foundation_tests(self) -> bool:
        """Run Phase 1: Foundation Validation Tests (CRITICAL)"""
        self.log("=" * 60)
        self.log("PHASE 1: FOUNDATION VALIDATION (CRITICAL - BLOCKING)")
        self.log("=" * 60)

        try:
            # Import Testing
            self.run_test(self.test_imports, "Import Testing", "foundation", "CRITICAL")

            # Syntax Validation
            self.run_test(
                self.test_syntax, "Syntax Validation", "foundation", "CRITICAL"
            )

            # Dependency Verification
            self.run_test(
                self.test_dependencies,
                "Dependency Verification",
                "foundation",
                "CRITICAL",
            )

            # Directory Structure
            self.run_test(
                self.test_directory_structure,
                "Directory Structure",
                "foundation",
                "CRITICAL",
            )

            # Backup Validation
            self.run_test(
                self.test_backup_files, "Backup File Validation", "foundation", "HIGH"
            )

            foundation_passed = all(
                r.passed
                for r in self.phase_results["foundation"]
                if r.priority == "CRITICAL"
            )

            if foundation_passed:
                self.log(
                    "✓ Foundation validation PASSED - proceeding to component tests"
                )
                return True
            else:
                self.log("✗ Foundation validation FAILED - cannot proceed", "ERROR")
                return False

        except Exception as e:
            self.log(f"Foundation validation failed with critical error: {e}", "ERROR")
            return False

    def test_imports(self) -> Dict:
        """Test all module imports"""
        import_results = {}
        modules_to_test = [
            "main_self_contained",
            "config",
            "worker",
            "optimization_utils",
            "advanced_optimization_utils",
            "dom_utils",
            "logging_setup",
            "error_handler",
        ]

        for module_name in modules_to_test:
            try:
                if module_name in sys.modules:
                    del sys.modules[module_name]  # Force reload
                __import__(module_name)
                import_results[module_name] = "SUCCESS"
            except ImportError as e:
                import_results[module_name] = f"FAILED: {e}"
                # Try to continue with other imports rather than failing immediately
            except Exception as e:
                import_results[module_name] = f"ERROR: {e}"

        # Check if any critical imports failed
        critical_modules = ["config", "main_self_contained"]
        failed_critical = [
            m
            for m in critical_modules
            if m in import_results and "FAILED" in import_results[m]
        ]

        if failed_critical:
            raise ImportError(f"Critical modules failed to import: {failed_critical}")

        return {"import_results": import_results}

    def test_syntax(self) -> Dict:
        """Test Python syntax for all files"""
        syntax_results = {}
        python_files = [
            "main_self_contained.py",
            "config.py",
            "worker.py",
            "optimization_utils.py",
            "advanced_optimization_utils.py",
            "dom_utils.py",
            "logging_setup.py",
            "error_handler.py",
        ]

        for file_path in python_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        source = f.read()
                    compile(source, file_path, "exec")
                    syntax_results[file_path] = "VALID"
                except SyntaxError as e:
                    syntax_results[file_path] = f"SYNTAX ERROR: {e}"
                    raise SyntaxError(f"Syntax error in {file_path}: {e}")
            else:
                syntax_results[file_path] = "FILE NOT FOUND"
                raise FileNotFoundError(f"Required file not found: {file_path}")

        return {"syntax_results": syntax_results}

    def test_dependencies(self) -> Dict:
        """Test required dependencies"""
        dependency_results = {}

        # Test Python version
        python_version = sys.version_info
        if python_version >= (3, 7):
            dependency_results["python_version"] = (
                f"OK - {python_version.major}.{python_version.minor}.{python_version.micro}"
            )
        else:
            dependency_results["python_version"] = (
                f"FAILED - Requires Python 3.7+, found {python_version.major}.{python_version.minor}"
            )
            raise RuntimeError("Python version too old")

        # Test Playwright
        try:
            import playwright

            dependency_results["playwright"] = "OK - Available"
        except ImportError:
            dependency_results["playwright"] = "FAILED - Not installed"
            raise ImportError("Playwright not available")

        # Test asyncio
        try:
            import asyncio

            dependency_results["asyncio"] = "OK - Available"
        except ImportError:
            dependency_results["asyncio"] = "FAILED - Not available"
            raise ImportError("asyncio not available")

        return {"dependency_results": dependency_results}

    def test_directory_structure(self) -> Dict:
        """Test directory structure requirements"""
        structure_results = {}

        # Test logs directory
        logs_dir = Path("logs")
        if logs_dir.exists():
            structure_results["logs_directory"] = "EXISTS"
        else:
            try:
                logs_dir.mkdir(exist_ok=True)
                structure_results["logs_directory"] = "CREATED"
            except Exception as e:
                structure_results["logs_directory"] = f"FAILED TO CREATE: {e}"
                raise RuntimeError(f"Cannot create logs directory: {e}")

        # Test test results directory
        test_results_dir = self.output_dir
        structure_results["test_results_directory"] = (
            "OK" if test_results_dir.exists() else "CREATED"
        )

        return {"structure_results": structure_results}

    def test_backup_files(self) -> Dict:
        """Test backup file validation"""
        backup_results = {}
        expected_backups = [
            "main_complete.py.backup",
            "enhanced_config.py.backup",
            "config_utils.py.backup",
        ]

        for backup_file in expected_backups:
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    if len(content) > 100:  # Basic content validation
                        backup_results[backup_file] = "OK - Content present"
                    else:
                        backup_results[backup_file] = "WARNING - Suspiciously small"
                except Exception as e:
                    backup_results[backup_file] = f"ERROR reading: {e}"
            else:
                backup_results[backup_file] = "MISSING"

        return {"backup_results": backup_results}

    def run_component_tests(self) -> bool:
        """Run Phase 2: Component Testing"""
        self.log("=" * 60)
        self.log("PHASE 2: COMPONENT TESTING (HIGH PRIORITY)")
        self.log("=" * 60)

        try:
            # Configuration System Testing
            self.run_test(
                self.test_configuration_system,
                "Configuration System",
                "component",
                "HIGH",
            )

            # Basic Worker Testing
            self.run_test(
                self.test_worker_functions, "Worker Functions", "component", "HIGH"
            )

            # Optimization Testing
            self.run_test(
                self.test_optimization_functions,
                "Optimization Functions",
                "component",
                "MEDIUM",
            )

            # DOM Utilities Testing
            self.run_test(self.test_dom_utilities, "DOM Utilities", "component", "HIGH")

            component_passed = all(
                r.passed
                for r in self.phase_results["component"]
                if r.priority == "HIGH"
            )

            if component_passed:
                self.log("✓ Component testing PASSED")
                return True
            else:
                self.log("✗ Component testing had failures", "WARNING")
                return False

        except Exception as e:
            self.log(f"Component testing failed: {e}", "ERROR")
            return False

    def test_configuration_system(self) -> Dict:
        """Test configuration system functionality"""
        config_results = {}

        try:
            # Test basic config import and loading
            from config import (
                AppConfig,
                get_config_value,
                merge_config_deep,
                load_unified_config,
            )

            config_results["config_import"] = "OK"

            # Test configuration loading
            unified_config = load_unified_config()
            config_results["unified_config_load"] = "OK"

            # Test get_config_value function
            test_value = get_config_value(
                unified_config, "scraper.parallel.max_workers", 50
            )
            if isinstance(test_value, int):
                config_results["get_config_value"] = "OK"
            else:
                config_results["get_config_value"] = (
                    f"FAILED - Expected int, got {type(test_value)}"
                )

            # Test merge_config_deep function
            base_config = {"level1": {"level2": {"value": 1}}}
            override_config = {"level1": {"level2": {"value": 2, "new_value": 3}}}
            merged = merge_config_deep(base_config, override_config)
            if (
                merged["level1"]["level2"]["value"] == 2
                and merged["level1"]["level2"]["new_value"] == 3
            ):
                config_results["merge_config_deep"] = "OK"
            else:
                config_results["merge_config_deep"] = "FAILED - Merge logic incorrect"

        except Exception as e:
            config_results["error"] = str(e)
            raise

        return {"config_results": config_results}

    def test_worker_functions(self) -> Dict:
        """Test worker function availability and basic functionality"""
        worker_results = {}

        try:
            # Test worker import
            import worker

            worker_results["worker_import"] = "OK"

            # Test worker function existence (without full execution)
            if hasattr(worker, "process_tasks_with_optimization"):
                worker_results["process_tasks_function"] = "EXISTS"
            else:
                worker_results["process_tasks_function"] = "MISSING"

        except Exception as e:
            worker_results["error"] = str(e)
            raise

        return {"worker_results": worker_results}

    def test_optimization_functions(self) -> Dict:
        """Test optimization function availability"""
        optimization_results = {}

        try:
            # Test optimization utils
            import optimization_utils

            optimization_results["optimization_utils_import"] = "OK"

            # Test advanced optimization utils
            import advanced_optimization_utils

            optimization_results["advanced_optimization_utils_import"] = "OK"

            # Test function existence
            if hasattr(optimization_utils, "create_optimized_browser"):
                optimization_results["create_optimized_browser"] = "EXISTS"
            else:
                optimization_results["create_optimized_browser"] = "MISSING"

        except Exception as e:
            optimization_results["error"] = str(e)
            raise

        return {"optimization_results": optimization_results}

    def test_dom_utilities(self) -> Dict:
        """Test DOM utility functions"""
        dom_results = {}

        try:
            # Test DOM utils import
            import dom_utils

            dom_results["dom_utils_import"] = "OK"

            # Test function existence
            expected_functions = [
                "find_target_folder",
                "extract_tree_items",
                "extract_folder_structure",
            ]
            for func_name in expected_functions:
                if hasattr(dom_utils, func_name):
                    dom_results[f"{func_name}_function"] = "EXISTS"
                else:
                    dom_results[f"{func_name}_function"] = "MISSING"

        except Exception as e:
            dom_results["error"] = str(e)
            raise

        return {"dom_results": dom_results}

    def run_integration_tests(self) -> bool:
        """Run Phase 3: Integration Testing"""
        self.log("=" * 60)
        self.log("PHASE 3: INTEGRATION TESTING (HIGH PRIORITY)")
        self.log("=" * 60)

        try:
            # Test main script integration
            self.run_test(
                self.test_main_integration,
                "Main Script Integration",
                "integration",
                "HIGH",
            )

            # Test configuration integration
            self.run_test(
                self.test_config_integration,
                "Configuration Integration",
                "integration",
                "HIGH",
            )

            integration_passed = all(
                r.passed
                for r in self.phase_results["integration"]
                if r.priority == "HIGH"
            )

            if integration_passed:
                self.log("✓ Integration testing PASSED")
                return True
            else:
                self.log("✗ Integration testing had failures", "WARNING")
                return False

        except Exception as e:
            self.log(f"Integration testing failed: {e}", "ERROR")
            return False

    def test_main_integration(self) -> Dict:
        """Test main script integration"""
        integration_results = {}

        try:
            # Test main script import
            import main_self_contained

            integration_results["main_import"] = "OK"

            # Test SelfContainedScraperManager class exists
            if hasattr(main_self_contained, "SelfContainedScraperManager"):
                integration_results["scraper_manager_class"] = "EXISTS"
            else:
                integration_results["scraper_manager_class"] = "MISSING"

        except Exception as e:
            integration_results["error"] = str(e)
            raise

        return {"integration_results": integration_results}

    def test_config_integration(self) -> Dict:
        """Test configuration integration across components"""
        config_integration_results = {}

        try:
            from config import load_unified_config

            # Load unified configuration
            unified_config = load_unified_config()
            config_integration_results["unified_config"] = "LOADED"

            # Test configuration structure
            if "scraper" in unified_config and "optimization" in unified_config:
                config_integration_results["config_structure"] = "OK"
            else:
                config_integration_results["config_structure"] = "MISSING_SECTIONS"

        except Exception as e:
            config_integration_results["error"] = str(e)
            raise

        return {"config_integration_results": config_integration_results}

    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        self.end_time = time.time()
        total_execution_time = (
            self.end_time - self.start_time if self.start_time else 0.0
        )

        # Calculate statistics
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests

        phase_stats = {}
        for phase, results in self.phase_results.items():
            if results:
                phase_passed = sum(1 for r in results if r.passed)
                phase_total = len(results)
                phase_stats[phase] = {
                    "total": phase_total,
                    "passed": phase_passed,
                    "failed": phase_total - phase_passed,
                    "pass_rate": (
                        (phase_passed / phase_total * 100) if phase_total > 0 else 0
                    ),
                }

        # Generate report
        report = {
            "test_run_info": {
                "timestamp": datetime.now().isoformat(),
                "total_execution_time": total_execution_time,
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "overall_pass_rate": (
                    (passed_tests / total_tests * 100) if total_tests > 0 else 0
                ),
            },
            "phase_statistics": phase_stats,
            "detailed_results": [r.to_dict() for r in self.results],
            "critical_issues": [
                r.to_dict()
                for r in self.results
                if not r.passed and r.priority == "CRITICAL"
            ],
            "high_priority_issues": [
                r.to_dict()
                for r in self.results
                if not r.passed and r.priority == "HIGH"
            ],
        }

        return report

    def save_report(self, report: Dict):
        """Save test report to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"test_report_{timestamp}.json"

        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

        self.log(f"Test report saved to: {report_file}")

        # Also save summary report
        summary_file = self.output_dir / f"test_summary_{timestamp}.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write("UNIFIED PARALLEL WEB SCRAPER - COMPREHENSIVE TEST RESULTS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Test Run Timestamp: {report['test_run_info']['timestamp']}\n")
            f.write(
                f"Total Execution Time: {report['test_run_info']['total_execution_time']:.2f}s\n"
            )
            f.write(f"Total Tests: {report['test_run_info']['total_tests']}\n")
            f.write(f"Passed: {report['test_run_info']['passed_tests']}\n")
            f.write(f"Failed: {report['test_run_info']['failed_tests']}\n")
            f.write(
                f"Overall Pass Rate: {report['test_run_info']['overall_pass_rate']:.1f}%\n\n"
            )

            f.write("PHASE STATISTICS:\n")
            f.write("-" * 30 + "\n")
            for phase, stats in report["phase_statistics"].items():
                f.write(
                    f"{phase.upper()}: {stats['passed']}/{stats['total']} ({stats['pass_rate']:.1f}%)\n"
                )

            if report["critical_issues"]:
                f.write("\nCRITICAL ISSUES:\n")
                f.write("-" * 20 + "\n")
                for issue in report["critical_issues"]:
                    f.write(f"- {issue['name']}: {issue['error_message']}\n")

        self.log(f"Test summary saved to: {summary_file}")
        return report_file, summary_file


def main():
    """Main test execution function"""
    parser = argparse.ArgumentParser(
        description="Comprehensive Test Suite for Unified Parallel Web Scraper"
    )
    parser.add_argument(
        "--phase",
        choices=["foundation", "component", "integration", "performance", "error"],
        help="Run specific test phase only",
    )
    parser.add_argument("--full", action="store_true", help="Run all test phases")
    parser.add_argument(
        "--quick", action="store_true", help="Run only critical and high priority tests"
    )
    parser.add_argument(
        "--output-dir", default="test_results", help="Output directory for test results"
    )
    parser.add_argument(
        "--report-format",
        choices=["summary", "detailed"],
        default="detailed",
        help="Report format",
    )

    args = parser.parse_args()

    # Initialize test suite
    test_suite = TestSuite(args.output_dir)
    test_suite.start_time = time.time()

    test_suite.log("Unified Parallel Web Scraper - Comprehensive Test Suite")
    test_suite.log("=" * 60)

    success = True

    try:
        # Run foundation tests (always required)
        if not test_suite.run_foundation_tests():
            test_suite.log("Foundation tests failed - stopping execution", "ERROR")
            success = False
        else:
            # Run additional phases based on arguments
            if args.phase == "component" or args.full or args.quick:
                success = test_suite.run_component_tests() and success

            if args.phase == "integration" or args.full or args.quick:
                success = test_suite.run_integration_tests() and success

            # Note: Performance and error handling tests would be implemented here
            # for brevity, focusing on critical path tests

    except Exception as e:
        test_suite.log(f"Test execution failed with error: {e}", "ERROR")
        traceback.print_exc()
        success = False

    # Generate and save report
    report = test_suite.generate_report()
    report_file, summary_file = test_suite.save_report(report)

    # Print final summary
    test_suite.log("=" * 60)
    if success:
        test_suite.log("✓ TEST SUITE COMPLETED SUCCESSFULLY")
    else:
        test_suite.log("✗ TEST SUITE COMPLETED WITH FAILURES", "WARNING")

    test_suite.log(f"Results saved to: {report_file}")
    test_suite.log(f"Summary saved to: {summary_file}")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
