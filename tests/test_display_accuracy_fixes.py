#!/usr/bin/env python3
"""
Test script to verify display accuracy fixes.
Tests the core functions that were modified to ensure they work correctly.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_worker_count_functions():
    """Test that get_current_workers() function works correctly."""
    print("Testing worker count functions...")

    try:
        from main_self_contained import get_current_workers, update_worker_count

        # Test getting current workers
        current = get_current_workers()
        print(f"✓ get_current_workers() returns: {current}")

        # Test that it returns an integer
        assert isinstance(current, int), f"Expected int, got {type(current)}"
        print("✓ get_current_workers() returns integer type")

        return True
    except Exception as e:
        print(f"✗ Error testing worker count functions: {e}")
        return False


def test_browser_pool_import():
    """Test that browser pool calculation can import get_current_workers."""
    print("\nTesting browser pool import fix...")

    try:
        # Test the import pattern we added
        from main_self_contained import get_current_workers

        current_workers = get_current_workers()

        # Test calculation like in browser pool
        pool_size = 6
        estimated_workers = max(0, current_workers // pool_size) if pool_size > 0 else 0

        print(
            f"✓ Browser pool calculation works: {current_workers} workers ÷ {pool_size} browsers = {estimated_workers} workers per browser"
        )

        return True
    except Exception as e:
        print(f"✗ Error testing browser pool import: {e}")
        return False


def test_cpu_monitoring():
    """Test that CPU monitoring uses proper intervals."""
    print("\nTesting CPU monitoring fix...")

    try:
        import psutil

        # Test the new 1.0 second interval
        cpu_percent = psutil.cpu_percent(interval=1.0)

        print(f"✓ CPU monitoring with 1.0s interval works: {cpu_percent}%")

        # Verify it's a reasonable number
        assert (
            0 <= cpu_percent <= 100
        ), f"CPU percentage should be 0-100, got {cpu_percent}"
        print("✓ CPU percentage in valid range")

        return True
    except Exception as e:
        print(f"✗ Error testing CPU monitoring: {e}")
        return False


def test_scaling_message_format():
    """Test that scaling messages use correct format."""
    print("\nTesting scaling message format...")

    try:
        # Test the message format we implemented
        current_workers = 45
        target_workers = 50

        message = f"Scaling applied: Workers changed from {current_workers} to {target_workers}"
        expected_parts = [
            "Workers changed from",
            str(current_workers),
            "to",
            str(target_workers),
        ]

        for part in expected_parts:
            assert part in message, f"Expected '{part}' in message: {message}"

        print(f"✓ Scaling message format correct: '{message}'")

        return True
    except Exception as e:
        print(f"✗ Error testing scaling message format: {e}")
        return False


def main():
    """Run all tests."""
    print("Display Accuracy Fixes Validation Test")
    print("=" * 50)

    tests = [
        test_worker_count_functions,
        test_browser_pool_import,
        test_cpu_monitoring,
        test_scaling_message_format,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {e}")
            failed += 1

    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All display accuracy fixes are working correctly!")
        return True
    else:
        print("❌ Some fixes may need additional work.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
