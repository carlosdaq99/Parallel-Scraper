#!/usr/bin/env python3
"""
Diagnostic script to inspect the actual page structure
"""

import asyncio
from playwright.async_api import async_playwright


async def diagnose_page_structure():
    """Diagnose what's actually on the page"""

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(
            headless=False
        )  # Show browser for debugging
        page = await browser.new_page()

        try:
            # Go to the actual page
            await page.goto(
                "https://help.autodesk.com/view/OARX/2025/ENU/",
                wait_until="domcontentloaded",
            )

            # Wait for page to fully load
            await page.wait_for_timeout(5000)

            print("🔍 Page Structure Diagnosis")
            print("=" * 50)

            # Check for any li elements with role="treeitem"
            tree_items = page.locator('li[role="treeitem"]')
            count = await tree_items.count()
            print(f"\\n1. Found {count} li[role='treeitem'] elements")

            if count > 0:
                print("\\n2. First 5 tree items:")
                for i in range(min(5, count)):
                    item = tree_items.nth(i)

                    # Get data-id
                    data_id = await item.get_attribute("data-id")

                    # Get text content
                    text = await item.inner_text()
                    text_preview = (
                        text.replace("\\n", " ")[:100] + "..."
                        if text and len(text) > 100
                        else text
                    )

                    # Get anchor text
                    anchor = item.locator('a[role="button"]')
                    anchor_count = await anchor.count()
                    anchor_text = (
                        await anchor.inner_text() if anchor_count > 0 else "No anchor"
                    )

                    print(f"  Item {i}:")
                    print(f"    Data-ID: {data_id}")
                    print(f"    Anchor text: {anchor_text}")
                    print(f"    Full text: {text_preview}")
                    print()

            # Check for specific data-id values we're looking for
            print("\\n3. Checking for specific data-id values:")

            oarx_header = page.locator('li[data-id="OARX-Header_id"]')
            header_count = await oarx_header.count()
            print(f"   OARX-Header_id: {header_count} found")

            if header_count > 0:
                header_text = await oarx_header.inner_text()
                print(f"   Text: {header_text}")

            # Check for ObjectARX text
            print("\\n4. Checking for ObjectARX text:")
            objectarx_elements = page.locator(':text("ObjectARX")')
            objectarx_count = await objectarx_elements.count()
            print(f"   Elements containing 'ObjectARX': {objectarx_count}")

            if objectarx_count > 0:
                for i in range(min(3, objectarx_count)):
                    element = objectarx_elements.nth(i)
                    text = await element.inner_text()
                    tag_name = await element.tag_name()
                    print(f"   Element {i}: <{tag_name}> {text}")

            # Check page title and URL
            title = await page.title()
            url = page.url
            print(f"\\n5. Page Info:")
            print(f"   Title: {title}")
            print(f"   URL: {url}")

            # Wait a bit for manual inspection
            print("\\n⏳ Waiting 10 seconds for manual inspection...")
            await page.wait_for_timeout(10000)

        except Exception as e:
            print(f"Error during diagnosis: {e}")

        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(diagnose_page_structure())
