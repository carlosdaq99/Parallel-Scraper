#!/usr/bin/env python3
"""
Demonstration of enhanced NodeInfo with GUID capture
"""

import json
from data_structures import NodeInfo


def demonstrate_guid_capture():
    """Demonstrate the enhanced NodeInfo with GUID capture functionality"""

    print("🔍 GUID Capture Enhancement Demonstration")
    print("=" * 50)

    # Create sample NodeInfo objects with and without GUIDs
    nodes = [
        NodeInfo(
            label="AutoCAD API",
            path="ObjectARX > AutoCAD API",
            depth=2,
            worker_id="1.1",
            parent_worker_id="1",
            is_leaf=False,
            subfolders=["Database", "Graphics", "Commands"],
            guid="GUID-12345-ABCDE-67890",
        ),
        NodeInfo(
            label="Database Module",
            path="ObjectARX > AutoCAD API > Database",
            depth=3,
            worker_id="1.1.1",
            parent_worker_id="1.1",
            is_leaf=True,
            subfolders=[],
            guid="GUID-54321-EDCBA-09876",
        ),
        NodeInfo(
            label="Legacy Component",
            path="ObjectARX > Legacy Component",
            depth=2,
            worker_id="1.2",
            parent_worker_id="1",
            is_leaf=True,
            subfolders=[],
            guid="",  # No GUID available
        ),
    ]

    # Show the enhanced structure
    print("\\n📊 Enhanced NodeInfo Structure:")
    for i, node in enumerate(nodes, 1):
        print(f"\\nNode {i}: {node.label}")
        print(f"  Path: {node.path}")
        print(f"  Depth: {node.depth}")
        print(f"  Worker ID: {node.worker_id}")
        print(f"  Is Leaf: {node.is_leaf}")
        print(f"  GUID: {node.guid if node.guid else 'None'}")
        if node.subfolders:
            print(f"  Subfolders: {', '.join(node.subfolders)}")

    # Convert to JSON format (as would be saved in the output file)
    json_structure = {}
    for node in nodes:
        json_structure[node.worker_id] = node.to_dict()

    # Save demonstration output
    output_file = "guid_demonstration_output.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(json_structure, f, indent=2, ensure_ascii=False)

    print(f"\\n💾 JSON Output saved to: {output_file}")
    print("\\n📋 Sample JSON structure:")
    print(json.dumps(json_structure, indent=2, ensure_ascii=False))

    # Analyze GUID capture
    total_nodes = len(nodes)
    nodes_with_guid = sum(1 for node in nodes if node.guid)

    print(f"\\n📈 GUID Capture Analysis:")
    print(f"  Total nodes: {total_nodes}")
    print(f"  Nodes with GUID: {nodes_with_guid}")
    print(f"  GUID capture rate: {(nodes_with_guid/total_nodes)*100:.1f}%")

    # Show the difference in JSON output
    print(f"\\n🔄 JSON Field Changes:")
    print(f"  ✅ Added 'guid' field to NodeInfo class")
    print(f"  ✅ GUID only included in JSON when present (not empty)")
    print(f"  ✅ Preserves all existing fields and functionality")
    print(f"  ✅ Backward compatible with existing code")


if __name__ == "__main__":
    demonstrate_guid_capture()
