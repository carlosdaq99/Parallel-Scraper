"""
Optimization utilities for parallel scraper system.

This module contains key optimization functions extracted from the optimization framework
and adapted for the parallel scraper's function-based async architecture.

Key Features:
- Browser reuse with circuit breaker pattern
- Intelligent resource filtering for faster page loads
- Memory optimization with cleanup strategies
- Performance monitoring and metrics collection
"""

import asyncio
import logging
import time
import gc
import weakref
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib

try:
    from playwright.async_api import Browser, BrowserContext, Page
except ImportError:
    Browser = type(None)
    BrowserContext = type(None)
    Page = type(None)

try:
    from .config import ScraperConfig, OptimizationConfig
except ImportError:
    # Fallback configuration if unified config not available
    class ScraperConfig:
        BROWSER_HEADLESS = True
        BROWSER_TIMEOUT = 30000

    class OptimizationConfig:
        BROWSER_REUSE_ENABLED = True
        # BROWSER_POOL_SIZE is now set in config.py via OPT_BROWSER_POOL_SIZE environment variable
        # Default fallback only (main config takes precedence)
        BROWSER_POOL_SIZE = (
            6  # Fallback default - actual value from config.py OptimizationConfig
        )
        RESOURCE_FILTERING_ENABLED = True
        MEMORY_MANAGEMENT_ENABLED = True
        BLOCKED_RESOURCE_TYPES = ["image", "media", "font", "stylesheet", "other"]
        ALLOWED_DOMAINS = ["help.autodesk.com"]
        MAX_MEMORY_MB = 512
        GARBAGE_COLLECTION_INTERVAL = 100


logger = logging.getLogger(__name__)

# Global browser pool for reuse
_browser_pool: List[Browser] = []
_browser_pool_lock = asyncio.Lock()
_browser_contexts: Dict[str, BrowserContext] = {}
_performance_metrics = {
    "browsers_created": 0,
    "browsers_reused": 0,
    "requests_blocked": 0,
    "requests_allowed": 0,
    "memory_cleanups": 0,
    "gc_triggers": 0,
    "total_pages_processed": 0,
}

# Circuit breaker for browser failures
_circuit_breaker = {
    "failure_count": 0,
    "last_failure_time": None,
    "is_open": False,
    "failure_threshold": 5,
    "recovery_timeout": 60,  # seconds
}


async def create_optimized_browser(
    playwright_instance, reuse_existing=True
) -> Optional[Browser]:
    """
    Create or reuse a browser instance with optimization.

    Implements browser reuse pattern with circuit breaker for reliability.
    Falls back to creating new browser if reuse fails.

    Args:
        playwright_instance: Playwright instance for browser creation
        reuse_existing: Whether to attempt browser reuse

    Returns:
        Browser instance or None if creation fails
    """
    global _browser_pool, _performance_metrics, _circuit_breaker

    if not OptimizationConfig.BROWSER_REUSE_ENABLED or not reuse_existing:
        return await _create_new_browser(playwright_instance)

    async with _browser_pool_lock:
        # Check circuit breaker
        if _circuit_breaker["is_open"]:
            if (
                time.time() - _circuit_breaker["last_failure_time"]
                > _circuit_breaker["recovery_timeout"]
            ):
                _circuit_breaker["is_open"] = False
                _circuit_breaker["failure_count"] = 0
                logger.info("Browser circuit breaker recovered")
            else:
                logger.warning("Browser circuit breaker is open, creating new browser")
                return await _create_new_browser(playwright_instance)

        # Try to reuse existing browser
        for i, browser in enumerate(_browser_pool):
            try:
                # Test if browser is still alive
                contexts = browser.contexts
                if len(contexts) < 5:  # Limit contexts per browser
                    _performance_metrics["browsers_reused"] += 1
                    logger.debug(f"Reusing browser {i} with {len(contexts)} contexts")
                    return browser
            except Exception as e:
                logger.warning(f"Browser {i} failed health check: {e}")
                try:
                    await browser.close()
                except:
                    pass
                _browser_pool.pop(i)
                break

        # Create new browser if pool is empty or under capacity
        if len(_browser_pool) < OptimizationConfig.BROWSER_POOL_SIZE:
            browser = await _create_new_browser(playwright_instance)
            if browser:
                _browser_pool.append(browser)
                logger.debug(f"Added browser to pool, pool size: {len(_browser_pool)}")
                return browser

        # Pool is full, return first available browser
        if _browser_pool:
            _performance_metrics["browsers_reused"] += 1
            return _browser_pool[0]

        # Fallback: create new browser
        return await _create_new_browser(playwright_instance)


async def _create_new_browser(playwright_instance) -> Optional[Browser]:
    """Create a new browser instance with optimized settings."""
    global _performance_metrics, _circuit_breaker

    try:
        browser_options = {
            "headless": ScraperConfig.BROWSER_HEADLESS,
            "args": [
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-features=VizDisplayCompositor",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
            ],
        }

        browser = await playwright_instance.chromium.launch(**browser_options)
        _performance_metrics["browsers_created"] += 1

        # Reset circuit breaker on success
        _circuit_breaker["failure_count"] = 0
        _circuit_breaker["is_open"] = False

        logger.debug(
            f"Created new browser, total created: {_performance_metrics['browsers_created']}"
        )
        return browser

    except Exception as e:
        logger.error(f"Failed to create browser: {e}")

        # Update circuit breaker
        _circuit_breaker["failure_count"] += 1
        _circuit_breaker["last_failure_time"] = time.time()

        if _circuit_breaker["failure_count"] >= _circuit_breaker["failure_threshold"]:
            _circuit_breaker["is_open"] = True
            logger.error("Browser circuit breaker opened due to repeated failures")

        return None


async def setup_resource_filtering(
    page: Page, domain: str = "help.autodesk.com"
) -> bool:
    """
    Setup intelligent resource filtering for faster page loads.

    Blocks unnecessary resources while preserving JavaScript functionality.
    Essential for GUID-based sites like Autodesk documentation.

    Args:
        page: Playwright page instance
        domain: Domain to allow resources from

    Returns:
        True if filtering was set up successfully
    """
    if not OptimizationConfig.RESOURCE_FILTERING_ENABLED:
        return True

    global _performance_metrics

    # Essential resource patterns for GUID/JavaScript sites
    essential_patterns = [
        r".*/(jquery|react|angular|vue|ember).*\.js",
        r".*/guid.*\.js",
        r".*/auth.*\.js",
        r".*/api.*\.js",
        r".*/help\..*\.js",
        r".*\.autodesk\.com.*\.js",
        r".*/search.*\.js",
        r".*/analytics.*\.js",
    ]

    async def route_handler(route, request):
        """Handle resource requests with intelligent filtering."""
        global _performance_metrics

        try:
            url = request.url
            resource_type = request.resource_type

            # Always allow documents and scripts from allowed domains
            if resource_type in ["document", "script"]:
                if any(
                    allowed_domain in url
                    for allowed_domain in OptimizationConfig.ALLOWED_DOMAINS
                ):
                    _performance_metrics["requests_allowed"] += 1
                    await route.continue_()
                    return

            # Check essential patterns for scripts
            if resource_type == "script":
                import re

                for pattern in essential_patterns:
                    if re.match(pattern, url, re.IGNORECASE):
                        _performance_metrics["requests_allowed"] += 1
                        await route.continue_()
                        return

            # Block unnecessary resource types
            if resource_type in OptimizationConfig.BLOCKED_RESOURCE_TYPES:
                _performance_metrics["requests_blocked"] += 1
                await route.abort()
                return

            # Allow everything else
            _performance_metrics["requests_allowed"] += 1
            await route.continue_()

        except Exception as e:
            logger.warning(f"Error in resource filtering: {e}")
            # On error, allow the request to continue
            try:
                await route.continue_()
            except:
                pass

    try:
        await page.route("**/*", route_handler)
        logger.debug(f"Resource filtering enabled for domain: {domain}")
        return True
    except Exception as e:
        logger.error(f"Failed to setup resource filtering: {e}")
        return False


async def optimize_page_memory(page: Page) -> bool:
    """
    Optimize page memory usage with cleanup strategies.

    Implements aggressive cleanup for JavaScript-heavy pages to prevent memory leaks.

    Args:
        page: Playwright page instance

    Returns:
        True if optimization was successful
    """
    if not OptimizationConfig.MEMORY_MANAGEMENT_ENABLED:
        return True

    global _performance_metrics

    try:
        # Clear browser cache and storage
        context = page.context
        await context.clear_cookies()

        # Execute JavaScript cleanup
        await page.evaluate(
            """
            () => {
                // Clear JavaScript variables and objects
                if (window.gc) {
                    window.gc();
                }
                
                // Clear any global variables that might be holding references
                if (window.objectarxData) {
                    window.objectarxData = null;
                }
                
                // Force garbage collection in supported browsers
                if (window.performance && window.performance.memory) {
                    console.log('Memory usage:', window.performance.memory);
                }
                
                // Clear event listeners on document
                const newDoc = document.cloneNode(true);
                document.parentNode.replaceChild(newDoc, document);
            }
        """
        )

        _performance_metrics["memory_cleanups"] += 1

        # Trigger Python garbage collection periodically
        if (
            _performance_metrics["total_pages_processed"]
            % OptimizationConfig.GARBAGE_COLLECTION_INTERVAL
            == 0
        ):
            gc.collect()
            _performance_metrics["gc_triggers"] += 1
            logger.debug("Triggered garbage collection")

        return True

    except Exception as e:
        logger.warning(f"Memory optimization failed: {e}")
        return False


async def create_optimized_page(browser: Browser, url: str = None) -> Optional[Page]:
    """
    Create an optimized page with all performance enhancements.

    Combines browser optimization, resource filtering, and memory management.

    Args:
        browser: Browser instance
        url: URL to navigate to (optional)

    Returns:
        Optimized page instance or None if creation fails
    """
    global _performance_metrics

    try:
        # Create context with optimizations
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        )

        page = await context.new_page()

        # Setup resource filtering
        if url:
            domain = (
                url.split("//")[1].split("/")[0] if "//" in url else "help.autodesk.com"
            )
            await setup_resource_filtering(page, domain)

        # Navigate to URL if provided
        if url:
            await page.goto(
                url, timeout=ScraperConfig.BROWSER_TIMEOUT, wait_until="networkidle"
            )

        _performance_metrics["total_pages_processed"] += 1

        return page

    except Exception as e:
        logger.error(f"Failed to create optimized page: {e}")
        return None


async def cleanup_optimization_resources():
    """
    Clean up all optimization resources.

    Should be called at the end of scraping session.
    """
    global _browser_pool, _browser_contexts

    logger.info("Cleaning up optimization resources...")

    async with _browser_pool_lock:
        # Close all browsers in pool
        for browser in _browser_pool:
            try:
                await browser.close()
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")

        _browser_pool.clear()

    # Close all contexts
    for context in _browser_contexts.values():
        try:
            await context.close()
        except Exception as e:
            logger.warning(f"Error closing context: {e}")

    _browser_contexts.clear()

    # Final garbage collection
    gc.collect()

    logger.info("Optimization cleanup completed")


def get_optimization_metrics() -> Dict[str, Any]:
    """
    Get current optimization performance metrics.

    Returns:
        Dictionary with performance statistics
    """
    global _performance_metrics

    metrics = _performance_metrics.copy()

    # Calculate derived metrics
    total_browsers = metrics["browsers_created"] + metrics["browsers_reused"]
    if total_browsers > 0:
        metrics["browser_reuse_rate"] = metrics["browsers_reused"] / total_browsers
    else:
        metrics["browser_reuse_rate"] = 0.0

    total_requests = metrics["requests_blocked"] + metrics["requests_allowed"]
    if total_requests > 0:
        metrics["resource_block_rate"] = metrics["requests_blocked"] / total_requests
    else:
        metrics["resource_block_rate"] = 0.0

    metrics["browser_pool_size"] = len(_browser_pool)
    metrics["circuit_breaker_status"] = (
        "open" if _circuit_breaker["is_open"] else "closed"
    )
    metrics["circuit_breaker_failures"] = _circuit_breaker["failure_count"]

    return metrics


def reset_optimization_metrics():
    """Reset all optimization metrics to zero."""
    global _performance_metrics

    _performance_metrics = {
        "browsers_created": 0,
        "browsers_reused": 0,
        "requests_blocked": 0,
        "requests_allowed": 0,
        "memory_cleanups": 0,
        "gc_triggers": 0,
        "total_pages_processed": 0,
    }

    logger.info("Optimization metrics reset")


# Compatibility functions for existing code
async def create_browser_with_optimization(playwright_instance):
    """Compatibility function for existing code."""
    return await create_optimized_browser(playwright_instance)


async def setup_page_optimization(page: Page, url: str = None):
    """Compatibility function for existing code."""
    if url:
        domain = (
            url.split("//")[1].split("/")[0] if "//" in url else "help.autodesk.com"
        )
        await setup_resource_filtering(page, domain)
    return await optimize_page_memory(page)


async def scale_browser_pool_to_target(playwright_instance, target_size: int):
    """
    Proactively scale browser pool to target size based on scaling recommendations
    This allows the browser pool to scale based on worker scaling decisions
    """
    global _browser_pool

    try:
        current_size = len(_browser_pool)
        max_size = OptimizationConfig.BROWSER_POOL_SIZE
        target_size = min(target_size, max_size)  # Respect maximum limit

        if target_size > current_size:
            browsers_to_add = target_size - current_size
            logger.info(
                f"Proactively scaling browser pool from {current_size} to {target_size} (+{browsers_to_add})"
            )

            for i in range(browsers_to_add):
                browser = await _create_new_browser(playwright_instance)
                if browser:
                    _browser_pool.append(browser)
                    logger.debug(
                        f"Added proactive browser {i+1}/{browsers_to_add}, pool size: {len(_browser_pool)}"
                    )
                else:
                    logger.warning(
                        f"Failed to create proactive browser {i+1}/{browsers_to_add}"
                    )
                    break

            return len(_browser_pool)
        else:
            logger.debug(
                f"Browser pool size {current_size} already meets or exceeds target {target_size}"
            )
            return current_size

    except Exception as e:
        logger.error(f"Failed to scale browser pool to target {target_size}: {e}")
        return len(_browser_pool)


# Export main functions
__all__ = [
    "create_optimized_browser",
    "setup_resource_filtering",
    "optimize_page_memory",
    "create_optimized_page",
    "cleanup_optimization_resources",
    "get_optimization_metrics",
    "reset_optimization_metrics",
    "create_browser_with_optimization",
    "setup_page_optimization",
    "scale_browser_pool_to_target",
]
