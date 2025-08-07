#!/usr/bin/env python3
"""Test adaptive scaling functionality"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from auto_tuning_engine import get_auto_tuning_engine, initialize_auto_tuning

print("Testing adaptive scaling engine...")

# Check if engine exists
engine = get_auto_tuning_engine()
if engine is None:
    print("No engine found, initializing...")
    engine = initialize_auto_tuning()

if engine:
    print("✅ Auto-tuning engine available!")
    print(f"Engine type: {type(engine)}")

    # Test getting parameters
    params = engine.get_current_parameters()
    print(f"Current parameters: {len(params)} items")
    for key, value in list(params.items())[:5]:  # Show first 5
        print(f"  - {key}: {value}")
else:
    print("❌ Failed to get auto-tuning engine")
