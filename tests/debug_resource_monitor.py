#!/usr/bin/env python3
"""
Debug Resource Monitor - Isolate the format error
"""

from resource_monitor import SystemResourceMonitor


def test_resource_monitor():
    """Test resource monitor to find the format error."""
    print("Creating resource monitor...")
    monitor = SystemResourceMonitor()

    print("Taking snapshot...")
    try:
        snapshot = monitor.take_comprehensive_snapshot(active_workers=2, queue_size=10)
        print(f"Snapshot type: {type(snapshot)}")
        print(f"Snapshot: {snapshot}")
        return True
    except Exception as e:
        print(f"Error in take_comprehensive_snapshot: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_resource_monitor()
