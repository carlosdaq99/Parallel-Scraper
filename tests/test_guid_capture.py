#!/usr/bin/env python3
"""
Test script to verify GUID capture functionality
"""

import asyncio
import json
from playwright.async_api import async_playwright


async def test_guid_capture():
    """Test GUID capture on a simple HTML page"""

    # Create a test HTML page with data-id attributes
    test_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Test GUID Capture</title></head>
    <body>
        <ul>
            <li class="node-tree-item" role="treeitem" data-id="GUID-123-456-789">
                <a role="button">Test Node 1</a>
            </li>
            <li class="node-tree-item" role="treeitem" data-id="GUID-ABC-DEF-GHI">
                <a role="button">Test Node 2</a>
            </li>
            <li class="node-tree-item" role="treeitem">
                <a role="button">Test Node 3 (No GUID)</a>
            </li>
        </ul>
    </body>
    </html>
    """

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page()

        # Set content
        await page.set_content(test_html)

        # Test GUID extraction
        tree_items = page.locator('li[role="treeitem"]')
        count = await tree_items.count()

        print(f"Found {count} tree items")

        results = []
        for i in range(count):
            item = tree_items.nth(i)

            # Get label
            label_element = item.locator('a[role="button"]')
            label = (
                await label_element.inner_text()
                if await label_element.count() > 0
                else "No label"
            )

            # Get data-id attribute
            data_id = await item.get_attribute("data-id")

            result = {
                "index": i,
                "label": label,
                "data_id": data_id,
                "has_guid": bool(data_id and data_id.strip()),
            }
            results.append(result)

            print(f"Item {i}: {label} -> GUID: {data_id}")

        await browser.close()

        # Save test results
        with open("test_guid_results.json", "w") as f:
            json.dump(results, f, indent=2)

        print(f"\\nTest completed! Results saved to test_guid_results.json")
        print(f"Total items: {len(results)}")
        print(f"Items with GUIDs: {sum(1 for r in results if r['has_guid'])}")

        return results


if __name__ == "__main__":
    asyncio.run(test_guid_capture())
