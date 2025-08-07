#!/usr/bin/env python3
"""
Test script to verify browser management fixes.

Tests the enhanced browser state validation and cleanup handling
that should prevent the "Target page, context or browser has been closed" error.
"""

import asyncio
import logging
import sys
from datetime import datetime
from playwright.async_api import async_playwright

# Add current directory to path
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from dom_utils import create_browser_page, safe_browser_operation
from optimization_utils import create_optimized_browser
from config import ScraperConfig

# Test configuration
BROWSER_HEADLESS = True
START_URL = ScraperConfig.START_URL


class BrowserTester:
    """Browser management test harness"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )

    async def test_browser_state_validation(self):
        """Test browser state validation before page creation"""
        self.logger.info("Testing browser state validation...")

        async with async_playwright() as playwright:
            # Create browser
            browser = await playwright.chromium.launch(headless=BROWSER_HEADLESS)
            self.logger.info("✅ Browser created successfully")

            # Test normal page creation
            page = await create_browser_page(browser, START_URL)
            if page:
                self.logger.info("✅ Page created successfully with valid browser")
                await page.close()
            else:
                self.logger.error("❌ Failed to create page with valid browser")
                return False

            # Close browser
            await browser.close()
            self.logger.info("Browser closed")

            # Test page creation after browser close (should fail gracefully)
            page = await create_browser_page(browser, START_URL)
            if page is None:
                self.logger.info("✅ Gracefully handled closed browser (returned None)")
            else:
                self.logger.error("❌ Should have failed with closed browser")
                await page.close()
                return False

        return True

    async def test_optimized_browser_creation(self):
        """Test optimized browser creation and management"""
        self.logger.info("Testing optimized browser creation...")

        async with async_playwright() as playwright:
            # Test optimized browser creation
            browser = await create_optimized_browser(playwright)
            if browser:
                self.logger.info("✅ Optimized browser created successfully")

                # Test page creation with optimized browser
                page = await create_browser_page(browser, START_URL)
                if page:
                    self.logger.info("✅ Page created with optimized browser")
                    await page.close()
                else:
                    self.logger.error("❌ Failed to create page with optimized browser")
                    await browser.close()
                    return False

                await browser.close()
            else:
                self.logger.error("❌ Failed to create optimized browser")
                return False

        return True

    async def test_concurrent_page_creation(self):
        """Test concurrent page creation to check for race conditions"""
        self.logger.info("Testing concurrent page creation...")

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=BROWSER_HEADLESS)

            async def create_test_page(page_id: int):
                """Create a page and test basic functionality"""
                try:
                    page = await create_browser_page(browser, START_URL)
                    if page:
                        self.logger.info(f"✅ Page {page_id} created successfully")
                        await asyncio.sleep(0.1)  # Brief operation
                        await page.close()
                        return True
                    else:
                        self.logger.error(f"❌ Page {page_id} creation failed")
                        return False
                except Exception as e:
                    self.logger.error(f"❌ Page {page_id} exception: {e}")
                    return False

            # Create multiple pages concurrently
            tasks = [create_test_page(i) for i in range(5)]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            success_count = sum(1 for result in results if result is True)
            total_count = len(results)

            self.logger.info(
                f"Concurrent page creation: {success_count}/{total_count} successful"
            )

            await browser.close()
            return success_count == total_count

    async def test_safe_browser_operation(self):
        """Test the safe_browser_operation wrapper"""
        self.logger.info("Testing safe browser operation wrapper...")

        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=BROWSER_HEADLESS)

            # Test normal operation
            result = await safe_browser_operation(
                browser.new_page(), timeout=10.0, operation_name="test_page_creation"
            )

            if result:
                self.logger.info("✅ Safe browser operation succeeded")
                await result.close()
            else:
                self.logger.error("❌ Safe browser operation failed")
                await browser.close()
                return False

            await browser.close()

            # Test operation with closed browser (should return None)
            result = await safe_browser_operation(
                browser.new_page(), timeout=10.0, operation_name="test_closed_browser"
            )

            if result is None:
                self.logger.info(
                    "✅ Safe browser operation handled closed browser gracefully"
                )
            else:
                self.logger.error("❌ Should have returned None for closed browser")
                await result.close()
                return False

        return True

    async def run_all_tests(self):
        """Run all browser management tests"""
        self.logger.info("=" * 60)
        self.logger.info("BROWSER MANAGEMENT FIX TESTS")
        self.logger.info("=" * 60)
        self.logger.info(f"Test started at: {datetime.now().strftime('%H:%M:%S')}")

        tests = [
            ("Browser State Validation", self.test_browser_state_validation),
            ("Optimized Browser Creation", self.test_optimized_browser_creation),
            ("Concurrent Page Creation", self.test_concurrent_page_creation),
            ("Safe Browser Operation", self.test_safe_browser_operation),
        ]

        results = {}
        for test_name, test_func in tests:
            self.logger.info(f"\n--- {test_name} ---")
            try:
                result = await test_func()
                results[test_name] = result
                status = "✅ PASS" if result else "❌ FAIL"
                self.logger.info(f"{test_name}: {status}")
            except Exception as e:
                self.logger.error(f"{test_name}: ❌ EXCEPTION - {e}")
                results[test_name] = False

        # Final summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info("TEST RESULTS SUMMARY")
        self.logger.info("=" * 60)

        total_tests = len(results)
        passed_tests = sum(1 for result in results.values() if result)

        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            self.logger.info(f"{test_name}: {status}")

        self.logger.info(f"\nOverall: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            self.logger.info("🎉 All browser management tests PASSED!")
            return True
        else:
            self.logger.error("💥 Some browser management tests FAILED!")
            return False


async def main():
    """Main test execution"""
    tester = BrowserTester()
    success = await tester.run_all_tests()
    return success


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        if result:
            print("\n✅ Browser management fix tests completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Browser management fix tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)
