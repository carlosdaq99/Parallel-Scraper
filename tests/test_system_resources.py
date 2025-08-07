#!/usr/bin/env python3
"""Test system resources functionality"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from resource_monitor import get_system_resources

print("Testing system resources collection...")

try:
    resources = get_system_resources()
    if resources:
        print(f"✅ System resources collected successfully:")
        for key, value in resources.items():
            print(f"  - {key}: {value}")
    else:
        print("❌ Failed to collect system resources")
except Exception as e:
    print(f"❌ Error: {e}")
