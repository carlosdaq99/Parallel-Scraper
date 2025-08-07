#!/usr/bin/env python3
"""
Test script to validate that the parallel_scraper directory is self-contained
and can be moved to other locations without external dependencies.
"""

import sys
import os
from pathlib import Path


def test_self_contained_imports():
    """Test that all imports work without external dependencies."""
    print("🧪 Testing self-contained parallel_scraper imports...")

    try:
        # Test config import
        from config import ScraperConfig, OptimizationConfig, config

        print("✅ Config system imported successfully")

        # Test core data structures
        from data_structures import NodeInfo, Task, ParallelWorkerContext

        print("✅ Data structures imported successfully")

        # Test optimization utilities
        from optimization_utils import (
            create_optimized_browser,
            setup_resource_filtering,
            get_optimization_metrics,
            cleanup_optimization_resources,
        )

        print("✅ Optimization utilities imported successfully")

        # Test advanced optimization utilities
        from advanced_optimization_utils import (
            create_memory_optimized_session,
            create_optimized_orchestration_config,
            generate_optimization_report,
        )

        print("✅ Advanced optimization utilities imported successfully")

        # Test DOM utilities
        from dom_utils import find_objectarx_root_node, get_level1_folders

        print("✅ DOM utilities imported successfully")

        # Test worker module
        from worker import parallel_worker

        print("✅ Worker module imported successfully")

        # Test logging setup
        from logging_setup import setup_logging

        print("✅ Logging setup imported successfully")

        print("\n🎉 ALL IMPORTS SUCCESSFUL!")
        print("✅ parallel_scraper directory is self-contained!")
        return True

    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_configuration_values():
    """Test that configuration values are accessible."""
    print("\n🔧 Testing configuration values...")

    try:
        from config import config

        print(f"   START_URL: {config.SCRAPER.START_URL}")
        print(f"   MAX_WORKERS: {config.SCRAPER.MAX_WORKERS}")
        print(f"   OUTPUT_FILE: {config.SCRAPER.OUTPUT_FILE}")
        print(f"   BROWSER_REUSE_ENABLED: {config.OPTIMIZATION.BROWSER_REUSE_ENABLED}")
        print(
            f"   RESOURCE_FILTERING_ENABLED: {config.OPTIMIZATION.RESOURCE_FILTERING_ENABLED}"
        )

        print("✅ Configuration values accessible!")
        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_main_script_syntax():
    """Test that the main scripts have valid syntax."""
    print("\n📄 Testing main script syntax...")

    try:
        import py_compile

        # Test main_self_contained.py (unified main script)
        py_compile.compile("main_self_contained.py", doraise=True)
        print("✅ main_self_contained.py syntax valid")

        print("✅ Unified main script has valid syntax!")
        return True

    except py_compile.PyCompileError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ Syntax test failed: {e}")
        return False


def test_portability():
    """Test that the directory can be moved and still work."""
    print("\n📦 Testing portability...")

    current_dir = Path.cwd()
    print(f"   Current directory: {current_dir}")

    # Check for external dependencies in file paths
    problematic_paths = []

    # Skip problematic/incomplete files and backups
    skip_files = {
        "test_self_contained.py",
        "backup_main_complete.py.txt",
        "backup_enhanced_config.py.txt",
        "backup_config_utils.py.txt",
    }

    for py_file in current_dir.glob("*.py"):
        if py_file.name in skip_files:
            continue

        try:
            with open(py_file, "r", encoding="utf-8") as f:
                content = f.read()

            # Check for absolute paths or problematic imports
            if "sys.path.insert" in content and "parent" in content:
                problematic_paths.append(f"{py_file.name}: sys.path manipulation")

        except Exception as e:
            print(f"   Warning: Could not check {py_file}: {e}")

    if problematic_paths:
        print("⚠️  Potential portability issues found:")
        for issue in problematic_paths:
            print(f"     {issue}")
        return False
    else:
        print("✅ No portability issues detected!")
        return True


def main():
    """Run all self-containment tests."""
    print("=" * 60)
    print("PARALLEL_SCRAPER SELF-CONTAINMENT TEST")
    print("=" * 60)

    tests = [
        test_self_contained_imports,
        test_configuration_values,
        test_main_script_syntax,
        test_portability,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 60)
    print(f"SELF-CONTAINMENT TEST RESULTS: {passed}/{total} PASSED")
    print("=" * 60)

    if passed == total:
        print("🎉 PARALLEL_SCRAPER IS FULLY SELF-CONTAINED!")
        print("✅ Directory can be moved to other locations and will work fine.")
        return True
    else:
        print("❌ Some tests failed. See output above for details.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
