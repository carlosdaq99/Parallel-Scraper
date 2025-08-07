"""
DOM utilities module for parallel scraper system.

Contains all DOM manipulation, navigation, and browser interaction functions
with comprehensive timeout protection to prevent hanging operations.
"""

import asyncio
import logging

try:
    from playwright.async_api import Page, Locator
except ImportError:
    # For type hints when Playwright not available
    Page = type(None)
    Locator = type(None)

# Import config with fallback
try:
    from .config import ScraperConfig
    from .data_structures import NodeInfo
    from .logging_setup import (
        log_browser_operation,
        log_function_entry,
        log_function_exit,
    )

    # Use self-contained config
    START_URL = ScraperConfig.START_URL
    FOLDER_LABEL = ScraperConfig.FOLDER_LABEL
    EXPAND_BUTTON_SELECTOR = ScraperConfig.EXPAND_BUTTON_SELECTOR
    DOM_OPERATION_TIMEOUT = ScraperConfig.DOM_OPERATION_TIMEOUT
    PAGE_LOAD_TIMEOUT = ScraperConfig.PAGE_LOAD_TIMEOUT
    PAGE_WAIT_AFTER_EXPAND = ScraperConfig.PAGE_WAIT_AFTER_EXPAND
except ImportError:
    from config import ScraperConfig
    import data_structures
    import logging_setup

    START_URL = ScraperConfig.START_URL
    FOLDER_LABEL = ScraperConfig.FOLDER_LABEL
    EXPAND_BUTTON_SELECTOR = ScraperConfig.EXPAND_BUTTON_SELECTOR
    DOM_OPERATION_TIMEOUT = ScraperConfig.DOM_OPERATION_TIMEOUT
    PAGE_LOAD_TIMEOUT = ScraperConfig.PAGE_LOAD_TIMEOUT
    PAGE_WAIT_AFTER_EXPAND = ScraperConfig.PAGE_WAIT_AFTER_EXPAND

    NodeInfo = data_structures.NodeInfo
    log_browser_operation = logging_setup.log_browser_operation
    log_function_entry = logging_setup.log_function_entry
    log_function_exit = logging_setup.log_function_exit
    log_function_entry = logging_setup.log_function_entry
    log_function_exit = logging_setup.log_function_exit


async def safe_browser_operation(
    operation_func,
    timeout: float = DOM_OPERATION_TIMEOUT,
    operation_name: str = "browser_operation",
    **kwargs,
):
    """
    Wrapper for all browser operations with timeout protection and logging.

    Args:
        operation_func: Async function to execute
        timeout: Timeout in seconds
        operation_name: Name for logging
        **kwargs: Arguments to pass to operation_func

    Returns:
        Result of operation_func or None if timeout/error
    """
    logger = logging.getLogger(__name__)

    try:
        log_browser_operation(logger, operation_name, timeout=timeout, **kwargs)
        result = await asyncio.wait_for(operation_func, timeout=timeout)
        return result
    except asyncio.TimeoutError:
        logger.error(f"TIMEOUT: {operation_name} exceeded {timeout}s timeout")
        return None
    except Exception as e:
        logger.error(f"ERROR: {operation_name} failed: {e}")
        return None


async def create_browser_page(browser, url=START_URL):
    """
    Create a new browser page with timeout protection.

    Args:
        browser: Playwright browser instance
        url: URL to navigate to

    Returns:
        Page instance or None if failed
    """
    logger = logging.getLogger(__name__)
    log_function_entry(logger, "create_browser_page", url=url)

    try:
        # Check if browser is still connected
        if not browser or hasattr(browser, "_closed") and browser._closed:
            logger.error("Browser is closed, cannot create page")
            return None

        # Check browser connectivity with a quick contexts check
        try:
            _ = browser.contexts  # Check if browser is still accessible
            if hasattr(browser, "is_connected") and not browser.is_connected():
                logger.error("Browser connection lost, cannot create page")
                return None
        except Exception as e:
            logger.error(f"Browser connectivity check failed: {e}")
            return None

        # Create page with timeout
        page = await safe_browser_operation(
            browser.new_page(), timeout=PAGE_LOAD_TIMEOUT, operation_name="create_page"
        )

        if not page:
            return None

        # Navigate with timeout
        navigation_result = await safe_browser_operation(
            page.goto(url, wait_until="networkidle"),
            timeout=PAGE_LOAD_TIMEOUT,
            operation_name="navigate_to_page",
            url=url,
        )

        if navigation_result is None:
            await page.close()
            return None

        # Initial page load wait
        await page.wait_for_timeout(2000)

        log_function_exit(logger, "create_browser_page", result="success")
        return page

    except Exception as e:
        logger.error(f"Failed to create browser page: {e}")
        return None


async def find_objectarx_root_node(page):
    """
    Find the ObjectARX root node using multiple strategies with timeout protection.

    Strategies:
    1. Find by data-id="OARX-Header_id" (most reliable)
    2. Find <a role="button"> with exact text "ObjectARX and Managed .NET"
    3. Find by partial text match

    Args:
        page: Playwright page instance

    Returns:
        Root node locator or None if not found
    """
    logger = logging.getLogger(__name__)
    log_function_entry(logger, "find_objectarx_root_node", folder_label=FOLDER_LABEL)

    try:
        # Strategy 1: Find by data-id (most reliable based on actual DOM)
        # Wait longer for tree items to load (sometimes takes time)
        try:
            await page.wait_for_selector('li[role="treeitem"]', timeout=30000)
            logger.info("Tree items loaded, searching for ObjectARX root")
        except Exception as e:
            logger.warning(f"Timeout waiting for tree items, continuing anyway: {e}")
            # Continue anyway - maybe they're already there

        # Give a bit more time for dynamic loading
        await page.wait_for_timeout(2000)

        root_by_data_id = page.locator(
            'li[role="treeitem"][data-id="OARX-Header_id"]'
        ).first

        data_id_count = await root_by_data_id.count()
        logger.info(f"Data-id root node count: {data_id_count}")

        if data_id_count > 0:
            root_text = await root_by_data_id.inner_text()
            logger.info(f"Found ObjectARX root node by data-id with text: {root_text}")
            log_function_exit(
                logger, "find_objectarx_root_node", result="success_data_id"
            )
            return root_by_data_id

        # Strategy 2: Find by exact anchor text
        anchor_selector = f'a[role="button"]:has-text("{FOLDER_LABEL}")'
        anchor_element = page.locator(anchor_selector).first

        anchor_count = await safe_browser_operation(
            anchor_element.count(),
            operation_name="check_anchor_exists",
            selector=anchor_selector,
        )

        if anchor_count is not None and anchor_count > 0:
            logger.info(f"Found anchor element with text: {FOLDER_LABEL}")

            # Traverse up to parent li.node-tree-item[role=treeitem]
            root_node = anchor_element.locator(
                'xpath=ancestor::li[@role="treeitem"][1]'
            )

            root_count = await safe_browser_operation(
                root_node.count(), operation_name="check_root_node_exists"
            )

            if root_count is not None and root_count > 0:
                logger.info("Found parent li.node-tree-item element")
                log_function_exit(
                    logger, "find_objectarx_root_node", result="success_anchor"
                )
                return root_node

        # Strategy 3: Find by partial text match (fallback)
        partial_selector = (
            'li[role="treeitem"]:has(a[role="button"]:text-matches("ObjectARX.*", "i"))'
        )
        partial_element = page.locator(partial_selector).first

        partial_count = await safe_browser_operation(
            partial_element.count(),
            operation_name="check_partial_text_match",
            selector=partial_selector,
        )

        if partial_count is not None and partial_count > 0:
            logger.info("Found ObjectARX root node by partial text match")
            log_function_exit(
                logger, "find_objectarx_root_node", result="success_partial"
            )
            return partial_element

        logger.error("Could not find ObjectARX root node using any strategy")
        log_function_exit(logger, "find_objectarx_root_node", result="not_found")
        return None

    except Exception as e:
        logger.error(f"Error finding ObjectARX root node: {e}")
        log_function_exit(logger, "find_objectarx_root_node", result="error")
        return None


async def get_direct_child_treeitems(parent_node):
    """
    Get all direct child li.node-tree-item elements with timeout protection.

    Args:
        parent_node: Parent locator element

    Returns:
        List of dictionaries with element, label, and is_leaf information
    """
    logger = logging.getLogger(__name__)
    log_function_entry(logger, "get_direct_child_treeitems")
    children = []

    try:
        logger.debug("Finding direct child treeitems under parent...")

        # Find all li[role="treeitem"] elements that are direct children
        child_selector = 'xpath=./ul/li[@role="treeitem"]'
        child_elements = parent_node.locator(child_selector)

        # Get count with timeout
        count = await safe_browser_operation(
            child_elements.count(),
            operation_name="get_children_count",
            selector=child_selector,
        )

        if count is None:
            logger.error("Could not get children count")
            return children

        logger.info(f"Found {count} direct child treeitem elements")

        for i in range(count):
            try:
                child = child_elements.nth(i)

                # Get the label from the child's anchor or text content
                label_element = child.locator('a[role="button"]').first

                # Check if label element exists
                label_count = await safe_browser_operation(
                    label_element.count(),
                    operation_name="check_label_element_exists",
                    child_index=i,
                )

                if label_count is None:
                    logger.warning(f"Skipping child {i}: could not check label element")
                    continue

                # Get label text
                if label_count > 0:
                    label = await safe_browser_operation(
                        label_element.inner_text(),
                        operation_name="get_label_text",
                        child_index=i,
                    )
                else:
                    # Fallback to getting text from the child directly
                    child_text = await safe_browser_operation(
                        child.inner_text(),
                        operation_name="get_child_text",
                        child_index=i,
                    )
                    label = child_text.strip().split("\\n")[0] if child_text else None

                if not label:
                    logger.warning(f"Skipping child {i}: empty label")
                    continue

                label = label.strip()

                # Check if this is a leaf node (no expand-collapse button)
                expand_button = child.locator(EXPAND_BUTTON_SELECTOR)
                expand_count = await safe_browser_operation(
                    expand_button.count(),
                    operation_name="check_expand_button",
                    child_index=i,
                    label=label,
                )

                is_leaf = expand_count is None or expand_count == 0

                # Extract GUID from data-id attribute if available
                data_id = await safe_browser_operation(
                    child.get_attribute("data-id"),
                    operation_name="get_data_id_attribute",
                    child_index=i,
                    label=label,
                )

                # Only keep data-id if it's in GUID format (starts with "GUID-")
                guid = ""
                if data_id and data_id.strip() and data_id.startswith("GUID-"):
                    guid = data_id.strip()
                    logger.debug(f"Found GUID for {label}: {guid}")
                elif data_id:
                    logger.debug(f"Found non-GUID data-id for {label}: {data_id}")

                children.append(
                    {"element": child, "label": label, "is_leaf": is_leaf, "guid": guid}
                )

                logger.debug(f"Found {'leaf' if is_leaf else 'folder'}: {label}")

            except Exception as e:
                logger.warning(f"Error processing child {i}: {e}")
                continue

        log_function_exit(
            logger, "get_direct_child_treeitems", result=f"{len(children)} children"
        )
        return children

    except Exception as e:
        logger.error(f"Error getting direct child treeitems: {e}")
        log_function_exit(logger, "get_direct_child_treeitems", result="error")
        return children


async def expand_node_safely(node, worker_id):
    """
    Expand a node by clicking its expand button with timeout protection.

    Args:
        node: Node locator to expand
        worker_id: Worker ID for logging

    Returns:
        True if successfully expanded, False otherwise
    """
    logger = logging.getLogger(__name__)
    log_function_entry(logger, "expand_node_safely", worker_id=worker_id)

    try:
        # Check if expand button exists
        expand_btn = node.locator(EXPAND_BUTTON_SELECTOR)

        expand_count = await safe_browser_operation(
            expand_btn.count(),
            operation_name="check_expand_button_exists",
            worker_id=worker_id,
        )

        if expand_count is None or expand_count == 0:
            logger.info(f"[{worker_id}] No expand button found")
            return False

        # Scroll into view (don't fail if this times out - enhanced script continues anyway)
        try:
            await safe_browser_operation(
                node.scroll_into_view_if_needed(),
                operation_name="scroll_into_view",
                worker_id=worker_id,
            )
        except Exception as e:
            logger.warning(f"[{worker_id}] Scroll operation failed but continuing: {e}")
            # Continue anyway - enhanced script doesn't fail on scroll issues

        # Click expand button (simplified like enhanced script)
        try:
            await expand_btn.first.click()
            logger.info(f"[{worker_id}] Successfully clicked expand button")
        except Exception as e:
            logger.error(f"[{worker_id}] Could not click expand button: {e}")
            return False

        # Wait for expansion to complete
        await asyncio.sleep(PAGE_WAIT_AFTER_EXPAND / 1000.0)

        logger.info(f"[{worker_id}] Successfully expanded node")
        log_function_exit(logger, "expand_node_safely", result="success")
        return True

    except Exception as e:
        logger.error(f"[{worker_id}] Error expanding node: {e}")
        log_function_exit(logger, "expand_node_safely", result="error")
        return False


async def find_target_folder_dom_async(page, folder_info, worker_id):
    """
    Find the target folder element in DOM with comprehensive timeout protection.

    Uses breadth-first search to navigate through the DOM hierarchy to find
    the specific folder by following the path components.

    Args:
        page: Playwright page instance
        folder_info: Information about the folder to find
        worker_id: Worker ID for logging

    Returns:
        Locator for the target folder or None if not found
    """
    logger = logging.getLogger(__name__)
    log_function_entry(
        logger,
        "find_target_folder_dom_async",
        worker_id=worker_id,
        label=folder_info.label,
        depth=folder_info.depth,
    )

    try:
        # Start from the ObjectARX root
        current_node = await find_objectarx_root_node(page)
        if not current_node:
            logger.error(f"[{worker_id}] Could not find ObjectARX root node")
            return None

        # For depth 1 folders, find direct child under root (like monolithic version)
        if folder_info.depth == 1:
            # Ensure root is expanded first
            expanded = await safe_browser_operation(
                current_node.get_attribute("aria-expanded"),
                operation_name="check_root_expanded",
                worker_id=worker_id,
            )

            if expanded != "true":
                expand_btn = current_node.locator(EXPAND_BUTTON_SELECTOR)
                expand_count = await safe_browser_operation(
                    expand_btn.count(),
                    operation_name="check_expand_button_exists",
                    worker_id=worker_id,
                )

                if expand_count and expand_count > 0:
                    await safe_browser_operation(
                        expand_btn.first.click(),
                        operation_name="click_expand_button",
                        worker_id=worker_id,
                    )
                    await asyncio.sleep(ScraperConfig.DOM_RETRY_DELAY)

            # Find the child with matching label using DOM
            children = await get_direct_child_treeitems(current_node)
            for child_info in children:
                if child_info["label"] == folder_info.label:
                    logger.info(
                        f"[{worker_id}] Successfully found target folder: {folder_info.label}"
                    )
                    log_function_exit(
                        logger, "find_target_folder_dom_async", result="success"
                    )
                    return child_info["element"]

            logger.warning(
                f"[{worker_id}] Could not find direct child with label: {folder_info.label}"
            )
            log_function_exit(
                logger, "find_target_folder_dom_async", result="not_found"
            )
            return None

        # For deeper folders, navigate through the path hierarchy
        else:
            path_components = folder_info.path.split(" > ")
            logger.debug(f"[{worker_id}] Navigating path: {path_components}")

            # Navigate through each level of the path (skip root component)
            for level, component in enumerate(path_components[1:], 1):
                if not component:
                    continue

                logger.debug(
                    f"[{worker_id}] Looking for component: '{component}' at level {level}"
                )

                # Expand current node
                expand_success = await expand_node_safely(current_node, worker_id)
                if not expand_success:
                    logger.warning(
                        f"[{worker_id}] Could not expand node at level {level}"
                    )
                    return None

                # Find the child with matching label
                children = await get_direct_child_treeitems(current_node)

                found_child = None
                for child in children:
                    if child["label"] == component:
                        found_child = child["element"]
                        logger.debug(f"[{worker_id}] Found matching child: {component}")
                        break

                if not found_child:
                    logger.warning(
                        f"[{worker_id}] Could not find child '{component}' at level {level}"
                    )
                    return None

                current_node = found_child

            logger.info(
                f"[{worker_id}] Successfully found target folder: {folder_info.label}"
            )
            log_function_exit(logger, "find_target_folder_dom_async", result="success")
            return current_node

    except Exception as e:
        logger.error(f"[{worker_id}] Error finding target folder: {e}")
        log_function_exit(logger, "find_target_folder_dom_async", result="error")
        return None


async def get_children_at_level_async(page, parent_node, depth, worker_id, parent_info):
    """
    Get children at a specific level with timeout protection.

    Args:
        page: Playwright page instance
        parent_node: Parent node locator
        depth: Current depth level
        worker_id: Worker ID for logging
        parent_info: Parent node information

    Returns:
        List of child information dictionaries with label and guid
    """
    logger = logging.getLogger(__name__)
    log_function_entry(
        logger,
        "get_children_at_level_async",
        worker_id=worker_id,
        depth=depth,
        parent_label=parent_info.label,
    )

    try:
        # Get direct child elements
        children = await get_direct_child_treeitems(parent_node)
        child_info_list = []

        for child in children:
            child_info = {"label": child["label"], "guid": child.get("guid", "")}
            child_info_list.append(child_info)

            # Mark leaves appropriately
            if child["is_leaf"]:
                logger.debug(f"[{worker_id}] Found leaf node: {child['label']}")

        logger.info(
            f"[{worker_id}] Found {len(child_info_list)} children at depth {depth}"
        )
        log_function_exit(
            logger,
            "get_children_at_level_async",
            result=f"{len(child_info_list)} children",
        )

        return child_info_list

    except Exception as e:
        logger.error(f"[{worker_id}] Error getting children at level {depth}: {e}")
        log_function_exit(logger, "get_children_at_level_async", result="error")
        return []


async def get_level1_folders(page, root_treeitem):
    """
    Get all level 1 folders using DOM-only logic - no label filtering.

    This is a critical function from the monolithic script that discovers
    the initial folder structure to seed the parallel processing queue.
    """
    logger = logging.getLogger(__name__)
    log_function_entry(logger, "get_level1_folders")

    try:
        # Ensure root is expanded first
        await safe_browser_operation(
            root_treeitem.scroll_into_view_if_needed(),
            timeout=DOM_OPERATION_TIMEOUT,
            operation_name="scroll_root_into_view",
        )

        expanded = await safe_browser_operation(
            root_treeitem.get_attribute("aria-expanded"),
            timeout=DOM_OPERATION_TIMEOUT,
            operation_name="check_root_expanded",
        )

        if expanded != "true":
            logger.info(f"Expanding root: {FOLDER_LABEL}")
            expand_btn = root_treeitem.locator(EXPAND_BUTTON_SELECTOR)

            expand_count = await safe_browser_operation(
                expand_btn.count(),
                timeout=DOM_OPERATION_TIMEOUT,
                operation_name="count_expand_buttons",
            )

            if expand_count and expand_count > 0:
                await safe_browser_operation(
                    expand_btn.first.click(),
                    timeout=DOM_OPERATION_TIMEOUT,
                    operation_name="click_root_expand",
                )
                await page.wait_for_timeout(1000)

        # Wait for child nodes to load
        await page.wait_for_timeout(1500)

        # Use DOM-based approach to get direct children
        children = await get_direct_child_treeitems(root_treeitem)

        level1_folders = []
        for child_info in children:
            node_info = NodeInfo(
                label=child_info["label"],
                path=f"{FOLDER_LABEL} > {child_info['label']}",
                depth=1,
                is_leaf=child_info["is_leaf"],
                guid=child_info.get("guid", ""),
            )
            level1_folders.append(node_info)

        log_function_exit(
            logger, "get_level1_folders", result=f"{len(level1_folders)} folders"
        )
        logger.info(f"Total level 1 folders found: {len(level1_folders)}")
        return level1_folders

    except Exception as e:
        logger.error(f"Error getting level 1 folders: {e}")
        log_function_exit(logger, "get_level1_folders", result="error")
        return []
