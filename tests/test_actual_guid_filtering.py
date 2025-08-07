#!/usr/bin/env python3
"""
Test GUID filtering with actual DOM structure
"""

import asyncio
from playwright.async_api import async_playwright


async def test_actual_guid_filtering():
    """Test GUID filtering with actual website DOM structure"""

    # Create test HTML based on actual DOM structure
    test_html = """
    <!DOCTYPE html>
    <html>
    <head><title>Test Actual GUID Structure</title></head>
    <body>
        <ul>
            <li class="node-tree-item" data-id="GUID-C3F3C736-40CF-44A0-9210-55F6A939B6F2" role="treeitem" aria-selected="true">
                <a role="button">API Reference with GUID</a>
            </li>
            <li class="node-tree-item" aria-expanded="false" data-id="OARX-DevGuide" role="treeitem">
                <a role="button">Developer Guide (No GUID)</a>
            </li>
            <li class="node-tree-item" aria-expanded="true" data-id="OARX-Header_id" role="treeitem">
                <span class="expand-collapse" role="button"></span>
                <a role="button" tabindex="0">ObjectARX and Managed .NET</a>
            </li>
            <li class="node-tree-item" data-id="GUID-12345-ABCD-EFGH-6789" role="treeitem">
                <a role="button">Another GUID Node</a>
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

        # Test GUID extraction with filtering
        tree_items = page.locator('li[role="treeitem"]')
        count = await tree_items.count()

        print(f"🔍 Testing GUID filtering with {count} tree items")
        print("=" * 50)

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

            # Apply GUID filtering (only keep if starts with "GUID-")
            guid = ""
            if data_id and data_id.strip() and data_id.startswith("GUID-"):
                guid = data_id.strip()
                guid_status = "✅ GUID"
            elif data_id:
                guid_status = "📋 ID"
            else:
                guid_status = "❌ None"

            result = {
                "index": i,
                "label": label,
                "data_id": data_id,
                "guid": guid,
                "has_guid": bool(guid),
            }
            results.append(result)

            print(f"Item {i}: {label}")
            print(f"  Data-ID: {data_id}")
            print(f"  GUID: {guid if guid else 'None'}")
            print(f"  Status: {guid_status}")
            print()

        await browser.close()

        # Analysis
        total_items = len(results)
        items_with_data_id = sum(1 for r in results if r["data_id"])
        items_with_guid = sum(1 for r in results if r["has_guid"])

        print("📊 Analysis:")
        print(f"  Total items: {total_items}")
        print(f"  Items with data-id: {items_with_data_id}")
        print(f"  Items with GUID: {items_with_guid}")
        print(f"  GUID capture rate: {(items_with_guid/total_items)*100:.1f}%")

        # Show JSON output preview
        print("\\n💾 JSON Output Preview:")
        for result in results:
            if result["has_guid"]:
                print(f"  {result['label']}: {{ 'guid': '{result['guid']}' }}")
            else:
                print(f"  {result['label']}: {{ /* no guid field */ }}")


if __name__ == "__main__":
    asyncio.run(test_actual_guid_filtering())
