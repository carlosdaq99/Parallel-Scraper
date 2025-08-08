#!/usr/bin/env python3
"""
Integration test for graceful shutdown functionality in main_self_contained.py

This test verifies that the main scraper handles Ctrl+C gracefully and saves progress.
"""

import asyncio
import os
import json
import subprocess
import signal
import time
from pathlib import Path


def test_main_scraper_graceful_shutdown():
    """Test the main scraper's graceful shutdown with a short run."""
    print("🧪 Testing graceful shutdown integration with main scraper")
    print("   This test will start the main scraper and stop it quickly")
    print("   to verify progress saving works in the real environment\n")

    # Clean up any existing output file
    output_file = "objectarx_structure_map_parallel.json"
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"🗑️  Cleaned up existing {output_file}")

    try:
        # Start the main scraper with limited workers for quick testing
        cmd = [
            "python",
            "main_self_contained.py",
            "--workers",
            "2",  # Minimal workers for quick test
            "--no-dashboard",  # Disable dashboard for simpler testing
            "--tracking-verbosity",
            "normal",
        ]

        print(f"🚀 Starting command: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )

        # Let it run for a few seconds to accumulate some progress
        print("⏱️  Allowing scraper to run for 10 seconds...")
        time.sleep(10)

        print("⚠️  Sending interrupt signal...")
        if os.name == "nt":  # Windows
            process.send_signal(signal.CTRL_BREAK_EVENT)
        else:  # Unix-like
            process.send_signal(signal.SIGINT)

        # Wait for graceful shutdown
        print("⏳ Waiting for graceful shutdown (max 30 seconds)...")
        try:
            stdout, stderr = process.communicate(timeout=30)
            print(f"✅ Process terminated with return code: {process.returncode}")
        except subprocess.TimeoutExpired:
            print("⚠️  Timeout - forcefully terminating process")
            process.kill()
            stdout, stderr = process.communicate()
            print(f"🔪 Process killed with return code: {process.returncode}")

        # Check output
        if stdout:
            print(f"\n📋 Stdout output (last 500 chars):")
            print(stdout[-500:])

        if stderr:
            print(f"\n🚨 Stderr output (last 500 chars):")
            print(stderr[-500:])

        # Check if progress file was created
        if os.path.exists(output_file):
            print(f"\n✅ Progress file created: {output_file}")

            # Analyze the saved progress
            try:
                with open(output_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if "metadata" in data:
                    metadata = data["metadata"]
                    print(f"   📊 Metadata:")
                    print(
                        f"      Generated at: {metadata.get('generated_at', 'unknown')}"
                    )
                    print(
                        f"      Total completed: {metadata.get('total_completed', 0)}"
                    )
                    print(f"      Total failed: {metadata.get('total_failed', 0)}")
                    print(f"      Interrupted: {metadata.get('interrupted', False)}")
                    print(
                        f"      Scraper version: {metadata.get('scraper_version', 'unknown')}"
                    )

                if "completed_tasks" in data:
                    completed_count = len(data["completed_tasks"])
                    print(f"   ✅ Completed tasks: {completed_count}")

                    # Show sample of completed tasks
                    if completed_count > 0:
                        sample_tasks = list(data["completed_tasks"].items())[:3]
                        print(f"   📋 Sample completed tasks:")
                        for task_id, task_data in sample_tasks:
                            label = task_data.get("label", "Unknown")
                            path = task_data.get("path", "Unknown")
                            print(f"      {task_id}: {label} at {path}")

                if "failed_tasks" in data:
                    failed_count = len(data["failed_tasks"])
                    print(f"   ❌ Failed tasks: {failed_count}")

                print(
                    f"   🎯 Graceful shutdown test: {'✅ PASSED' if metadata.get('interrupted') else '❌ FAILED'}"
                )

            except Exception as e:
                print(f"   ❌ Error reading progress file: {e}")
        else:
            print(f"\n❌ No progress file found: {output_file}")
            print("   This could mean:")
            print("   - The scraper didn't have time to complete any tasks")
            print("   - The graceful shutdown didn't work properly")
            print("   - The signal wasn't received correctly")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")

    finally:
        print(f"\n🏁 Integration test completed!")


def show_help():
    """Show help information about this test."""
    print("=== Graceful Shutdown Integration Test ===")
    print()
    print("This test verifies that the main scraper (main_self_contained.py)")
    print("properly handles Ctrl+C (SIGINT) and saves progress to JSON.")
    print()
    print("The test will:")
    print("1. Start the main scraper with minimal configuration")
    print("2. Let it run for ~10 seconds to accumulate some progress")
    print("3. Send an interrupt signal (simulating Ctrl+C)")
    print("4. Verify that progress is saved to JSON file")
    print("5. Analyze the saved progress for completeness")
    print()
    print("Expected outcome:")
    print("- Process should terminate gracefully (not crash)")
    print("- JSON file should be created with progress data")
    print("- Metadata should indicate 'interrupted: true'")
    print("- Some completed tasks should be present")
    print()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        show_help()
    else:
        test_main_scraper_graceful_shutdown()
