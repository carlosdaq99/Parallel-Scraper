#!/usr/bin/env python3
"""
Diagnostic test for worker timeout issue.

This test checks if the initial task creation is working correctly.
"""

import asyncio
import logging
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging to capture details
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def test_initial_setup():
    """Test the initial setup and task creation process."""
    print("🔍 Testing initial setup and task creation...")

    try:
        from playwright.async_api import async_playwright
        from dom_utils import find_objectarx_root_node, get_level1_folders
        from config import ScraperConfig
        from data_structures import NodeInfo, Task, ParallelWorkerContext

        print("✅ All imports successful")

        # Test basic playwright setup
        async with async_playwright() as playwright:
            print("✅ Playwright context created")

            browser = await playwright.chromium.launch(headless=True)
            print("✅ Browser launched")

            page = await browser.new_page()
            print("✅ Page created")

            # Test navigation
            START_URL = "https://help.autodesk.com/view/OARX/2025/ENU/"
            try:
                await page.goto(START_URL, timeout=30000)
                print("✅ Navigation successful")

                # Test root node finding
                root_node = await find_objectarx_root_node(page)
                if root_node:
                    print("✅ Root node found")

                    # Test level 1 folders
                    level1_folders = await get_level1_folders(page, root_node)
                    print(f"✅ Found {len(level1_folders)} level 1 folders")

                    if level1_folders:
                        # Test task creation
                        initial_tasks = []
                        for i, folder in enumerate(level1_folders[:2]):  # Test first 2
                            folder_name = (
                                getattr(folder, "text_content", f"Level1_Folder_{i}")
                                or f"Level1_Folder_{i}"
                            )
                            node_info = NodeInfo(
                                label=folder_name,
                                path=START_URL,
                                depth=0,
                                worker_id=f"initial_worker_{i}",
                                guid=getattr(folder, "data_id", None) or "",
                            )
                            task = Task(
                                worker_id=f"initial_worker_{i}",
                                node_info=node_info,
                                priority=0,
                            )
                            initial_tasks.append(task)

                        print(f"✅ Created {len(initial_tasks)} test tasks")

                        # Test worker context creation
                        worker_context = ParallelWorkerContext(2, logger)
                        print("✅ Worker context created")

                        # Test adding tasks to queue
                        for task in initial_tasks:
                            await worker_context.task_queue.put(task)

                        print(f"✅ Added {len(initial_tasks)} tasks to queue")
                        print(f"   Queue size: {worker_context.task_queue.qsize()}")

                    else:
                        print(
                            "❌ No level 1 folders found - this explains worker timeouts!"
                        )
                else:
                    print("❌ Root node not found - this explains worker timeouts!")

            except Exception as e:
                print(f"❌ Navigation failed: {e}")

            await page.close()
            await browser.close()

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_initial_setup())
