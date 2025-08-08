"""
Quick script to replace debug prints with worker tracking calls in main_self_contained.py
"""

import re


def fix_debug_prints():
    """Replace debug prints with proper worker tracking function calls."""
    file_path = "main_self_contained.py"

    # Read the file
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace specific debug print patterns
    replacements = [
        # Scaling applied prints
        (
            r'print\(\s*f"🔧 SCALING APPLIED: Tasks list now has \{len\(tasks\)\} total tasks"\s*\)',
            'log_scaling_decision(len(tasks), target_workers, f"Scaling applied: Tasks list now has {len(tasks)} total tasks")',
        ),
        # Scaling error prints
        (
            r'print\(\s*f"🔧 SCALING ERROR: Failed to scale workers: \{e\}"\s*\)',
            'log_worker_error("System", f"Failed to scale workers: {e}")',
        ),
        # Scaling skipped prints
        (
            r'print\(\s*"🔧 SCALING SKIPPED: Missing parameters for dynamic worker scaling"\s*\)',
            'log_scaling_decision(current_workers, current_workers, "Scaling skipped: Missing parameters for dynamic worker scaling")',
        ),
        # No change prints
        (
            r'print\(\s*f"🔧 NO CHANGE: Current worker count is already optimal \(\{current_workers\}\)"\s*\)',
            'log_scaling_decision(current_workers, current_workers, f"No change: Current worker count is already optimal ({current_workers})")',
        ),
    ]

    # Apply replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content)

    # Write back the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("✅ Debug prints replaced with worker tracking calls")


if __name__ == "__main__":
    fix_debug_prints()
