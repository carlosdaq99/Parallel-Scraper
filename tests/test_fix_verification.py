#!/usr/bin/env python3
"""
Verification script to check that display accuracy fixes were applied correctly.
Checks the actual code files to verify the changes are in place.
"""

import os
import re


def check_file_content(file_path, pattern, description, should_exist=True):
    """Check if a pattern exists in a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        if should_exist:
            if re.search(pattern, content):
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ {description} - Pattern not found")
                return False
        else:
            if not re.search(pattern, content):
                print(f"✓ {description}")
                return True
            else:
                print(f"✗ {description} - Pattern should not exist")
                return False
    except Exception as e:
        print(f"✗ Error checking {description}: {e}")
        return False


def main():
    """Verify all display accuracy fixes."""
    print("Display Accuracy Fixes Verification")
    print("=" * 50)

    base_path = "c:\\Users\\dea29431\\OneDrive - Rsk Group Limited\\Documents\\Scripts\\Scraper2\\parallel_scraper"

    checks = []

    # Check #1: Task/Worker confusion fixes in main_self_contained.py
    main_file = os.path.join(base_path, "main_self_contained.py")

    # Should now use current_workers instead of len(tasks) in scaling decisions
    checks.append(
        check_file_content(
            main_file,
            r'log_scaling_decision\(\s*current_workers,\s*target_workers,\s*f"Scaling applied: Workers changed from',
            "Task/Worker confusion fix #1: Scaling messages use current_workers",
        )
    )

    # Should use get_current_workers() in startup logging
    checks.append(
        check_file_content(
            main_file,
            r"get_current_workers\(\)",
            "Task/Worker confusion fix #2: Startup logging uses get_current_workers()",
        )
    )

    # Should NOT have the old len(tasks) pattern in scaling decisions
    checks.append(
        check_file_content(
            main_file,
            r"log_scaling_decision\(\s*len\(tasks\),\s*target_workers",
            "Task/Worker confusion fix #3: Old len(tasks) pattern removed",
            should_exist=False,
        )
    )

    # Check #2: Browser pool calculation fix in worker_tracking_display.py
    worker_file = os.path.join(base_path, "worker_tracking_display.py")

    # Should import get_current_workers from main_self_contained
    checks.append(
        check_file_content(
            worker_file,
            r"from main_self_contained import get_current_workers",
            "Browser pool fix #1: Import get_current_workers",
        )
    )

    # Should use current_workers in calculation
    checks.append(
        check_file_content(
            worker_file,
            r"current_workers = get_current_workers\(\)",
            "Browser pool fix #2: Use actual current workers",
        )
    )

    # Should have fallback to old method if import fails
    checks.append(
        check_file_content(
            worker_file,
            r"except ImportError:",
            "Browser pool fix #3: Import fallback implemented",
        )
    )

    # Check #3: CPU monitoring fixes
    resource_file = os.path.join(base_path, "resource_monitor.py")
    adaptive_file = os.path.join(base_path, "adaptive_scaling_engine.py")

    # Should use interval=1.0 instead of interval=0.1
    checks.append(
        check_file_content(
            resource_file,
            r"psutil\.cpu_percent\(interval=1\.0\)",
            "CPU fix #1: resource_monitor.py uses 1.0s interval",
        )
    )

    checks.append(
        check_file_content(
            main_file,
            r"psutil\.cpu_percent\(interval=1\.0\)",
            "CPU fix #2: main_self_contained.py uses 1.0s interval",
        )
    )

    checks.append(
        check_file_content(
            adaptive_file,
            r"psutil\.cpu_percent\(interval=1\.0\)",
            "CPU fix #3: adaptive_scaling_engine.py uses 1.0s interval",
        )
    )

    # Should NOT have the old interval=0.1 pattern
    checks.append(
        check_file_content(
            resource_file,
            r"psutil\.cpu_percent\(interval=0\.1\)",
            "CPU fix #4: Old 0.1s interval removed from resource_monitor.py",
            should_exist=False,
        )
    )

    # Summary
    passed = sum(checks)
    total = len(checks)

    print("\n" + "=" * 50)
    print(f"Verification Results: {passed}/{total} checks passed")

    if passed == total:
        print("🎉 All display accuracy fixes have been applied correctly!")
        print("\nSUMMARY OF FIXES:")
        print("1. ✅ Fixed Task/Worker confusion in scaling messages")
        print("2. ✅ Fixed Browser Pool worker count calculation")
        print("3. ✅ Fixed CPU sampling intervals across all modules")
        return True
    else:
        print("❌ Some fixes may not be applied correctly.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
