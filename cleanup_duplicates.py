#!/usr/bin/env python3
"""
Clean up duplicate functions in main_self_contained.py

This script removes all duplicate function definitions to resolve linting issues.
"""

import sys
import os

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)


def cleanup_main_file():
    """Clean up duplicate functions in main_self_contained.py"""

    file_path = "main_self_contained.py"

    print("🔧 Cleaning up duplicate functions in main_self_contained.py")

    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Track which lines to keep
    lines_to_keep = []
    skip_until_line = -1

    for i, line in enumerate(lines):
        line_num = i + 1

        # Skip lines if we're in a section to delete
        if skip_until_line != -1 and line_num <= skip_until_line:
            continue
        else:
            skip_until_line = -1

        # Identify duplicate function blocks to remove
        if line_num >= 560 and line_num <= 710:
            # This is the duplicate section - check for specific functions
            if line.strip().startswith("def get_current_workers()"):
                # Skip this duplicate function (find the end)
                bracket_count = 0
                for j in range(i, len(lines)):
                    if "def " in lines[j] and j > i:
                        skip_until_line = j - 1
                        break
                continue

            elif line.strip().startswith("def update_worker_count("):
                # Skip this duplicate function
                for j in range(i, len(lines)):
                    if "def " in lines[j] and j > i:
                        skip_until_line = j - 1
                        break
                continue

            elif line.strip().startswith("def initialize_adaptive_scaling()"):
                # Skip this duplicate function
                for j in range(i, len(lines)):
                    if (
                        "def " in lines[j]
                        or "class " in lines[j]
                        or "# ---" in lines[j]
                    ) and j > i:
                        skip_until_line = j - 1
                        break
                continue

            elif line.strip().startswith(
                "async def perform_adaptive_scaling_check(performance_data"
            ):
                # Skip this duplicate function
                for j in range(i, len(lines)):
                    if (
                        "def " in lines[j]
                        or "class " in lines[j]
                        or "# ---" in lines[j]
                    ) and j > i:
                        skip_until_line = j - 1
                        break
                continue

            elif (
                line.strip().startswith("class SelfContainedScrapingManager:")
                and line_num > 500
            ):
                # Skip the duplicate class
                for j in range(i, len(lines)):
                    if (
                        (
                            "def " in lines[j]
                            or "class " in lines[j]
                            or "# ---" in lines[j]
                        )
                        and j > i
                        and not lines[j].strip().startswith("def ")
                        or lines[j].strip().startswith("# ---")
                    ):
                        skip_until_line = j - 1
                        break
                continue

            elif line.strip().startswith(
                "async def monitor_progress_and_scaling(manager, worker_context, stop_event)"
            ):
                # Skip this duplicate function (the one with unused parameter)
                for j in range(i, len(lines)):
                    if ("def " in lines[j] or "if __name__" in lines[j]) and j > i:
                        skip_until_line = j - 1
                        break
                continue

        # Keep this line
        lines_to_keep.append(line)

    # Write the cleaned file
    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(lines_to_keep)

    original_lines = len(lines)
    cleaned_lines = len(lines_to_keep)
    removed_lines = original_lines - cleaned_lines

    print(f"✅ Cleanup complete:")
    print(f"   Original lines: {original_lines}")
    print(f"   Cleaned lines: {cleaned_lines}")
    print(f"   Removed lines: {removed_lines}")


if __name__ == "__main__":
    cleanup_main_file()
