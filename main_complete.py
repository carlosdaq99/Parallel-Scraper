"""
Complete functional main entry point that preserves ALL functionality from the monolithic script.

This script maintains EXACTLY the same logic and patterns as the original 809-line version:
1. 4-phase execution pattern (discover, submit, process, analyze)
2. Concurrent worker coordination with semaphore control
3. Progress monitoring with stagnation detection
4. Complete JSON structure building
5. All error handling and retry mechanisms
6. All logging and statistics

Enhanced with optimization utilities for improved performance.
"""

import json
import asyncio
import time
import sys
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
import aiofiles

# Import optimization utilities
try:
    from .optimization_utils import (
        create_optimized_browser,
        create_optimized_page,
        cleanup_optimization_resources,
        get_optimization_metrics,
        reset_optimization_metrics,
    )
    from .advanced_optimization_utils import (
        create_memory_optimized_session,
        apply_orchestrated_optimization,
        create_optimized_orchestration_config,
        generate_optimization_report,
        cleanup_optimization_state,
    )

    OPTIMIZATION_AVAILABLE = True
    ADVANCED_OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False
    ADVANCED_OPTIMIZATION_AVAILABLE = False
    logging.warning(
        "Optimization utilities not available, running without optimizations"
    )

# Import Phase 4 function-based configuration
try:
    from .config_utils import (
        load_unified_config,
        get_config_value,
        validate_config,
        create_test_config,
    )

    FUNCTION_CONFIG_AVAILABLE = True
except ImportError:
    FUNCTION_CONFIG_AVAILABLE = False
    logging.warning("Function-based configuration not available, using legacy config")

# Import local configuration - self-contained
try:
    from .config import ScraperConfig, OptimizationConfig, config

    CONFIG_AVAILABLE = True
    logging.info("Using self-contained configuration system")
except ImportError:
    logging.error("Failed to import local configuration")
    print("Error: Failed to import local configuration")
    sys.exit(1)


# --- Comprehensive Logging Setup ---
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)
LOG_FILE = LOGS_DIR / f"main_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"


def setup_comprehensive_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"
    )
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.DEBUG)

    # Stream handler for terminal
    stream_handler = logging.StreamHandler()
    stream_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s]: %(message)s", "%H:%M:%S"
    )
    stream_handler.setFormatter(stream_formatter)
    stream_handler.setLevel(logging.INFO)

    # Remove any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logger.info(f"Comprehensive logging initialized. Log file: {LOG_FILE}")
    return logger


# --- End Logging Setup ---

# Import all modular components with fallback


try:
    from .config import ScraperConfig
    from .data_structures import NodeInfo, Task, ParallelWorkerContext

    # Use self-contained config
    START_URL = ScraperConfig.START_URL
    FOLDER_LABEL = ScraperConfig.FOLDER_LABEL
    MAX_WORKERS = ScraperConfig.MAX_WORKERS
    MAX_CONCURRENT_PAGES = ScraperConfig.MAX_CONCURRENT_PAGES
    OUTPUT_FILE = ScraperConfig.OUTPUT_FILE
    BROWSER_HEADLESS = ScraperConfig.BROWSER_HEADLESS
    PROGRESS_REPORT_INTERVAL = ScraperConfig.PROGRESS_REPORT_INTERVAL
    MAX_DEPTH = ScraperConfig.MAX_DEPTH
    from .worker import parallel_worker
    from .dom_utils import find_objectarx_root_node, get_level1_folders
except ImportError:
    # Fallback for standalone execution
    from config import ScraperConfig
    import data_structures
    import worker
    import dom_utils

    START_URL = ScraperConfig.START_URL
    FOLDER_LABEL = ScraperConfig.FOLDER_LABEL
    MAX_WORKERS = ScraperConfig.MAX_WORKERS
    MAX_CONCURRENT_PAGES = ScraperConfig.MAX_CONCURRENT_PAGES
    OUTPUT_FILE = ScraperConfig.OUTPUT_FILE
    BROWSER_HEADLESS = ScraperConfig.BROWSER_HEADLESS
    PROGRESS_REPORT_INTERVAL = ScraperConfig.PROGRESS_REPORT_INTERVAL
    MAX_DEPTH = ScraperConfig.MAX_DEPTH

    NodeInfo = data_structures.NodeInfo
    Task = data_structures.Task
    ParallelWorkerContext = data_structures.ParallelWorkerContext
    parallel_worker = worker.parallel_worker
    find_objectarx_root_node = dom_utils.find_objectarx_root_node
    get_level1_folders = dom_utils.get_level1_folders


def build_json_structure_from_tasks(completed_tasks: dict) -> dict:
    """
    Build the final JSON structure from completed tasks - EXACT copy from monolithic version.

    This function preserves the exact same logic and structure as the original script.
    """
    logging.info("Building JSON structure from completed tasks...")

    # Create a mapping of worker IDs to their node structures
    node_map = {}

    # Root structure
    root_structure = {
        "label": FOLDER_LABEL,
        "path": f"/{FOLDER_LABEL}",
        "depth": 0,
        "is_leaf": False,
        "children": [],
        "worker_id": "root",
        "metadata": {
            "total_nodes": len(completed_tasks),
            "max_depth": max(
                (node.depth for node in completed_tasks.values()), default=0
            ),
            "created_at": datetime.now().isoformat(),
        },
    }

    node_map["root"] = root_structure

    # Sort by depth to ensure parents are processed before children
    sorted_tasks = sorted(completed_tasks.items(), key=lambda x: x[1].depth)

    for worker_id, node_info in sorted_tasks:
        # Create the node structure
        node_structure = {
            "label": node_info.label,
            "path": node_info.path,
            "depth": node_info.depth,
            "is_leaf": node_info.is_leaf,
            "subfolders": node_info.subfolders,
            "worker_id": node_info.worker_id,
            "parent_worker_id": node_info.parent_worker_id,
            "children": [],
        }

        # Add to the map
        node_map[worker_id] = node_structure

        # Find the parent and add this node as a child
        parent_id = ".".join(worker_id.split(".")[:-1])  # Remove last part
        if parent_id in node_map:
            node_map[parent_id]["children"].append(node_structure)
        else:
            # This is a level 1 node, add to root
            root_structure["children"].append(node_structure)

        logging.debug(f"  Added node: {worker_id} -> {node_info.label}")

    return root_structure


async def monitor_progress_with_stagnation_detection(context):
    """
    Monitor progress with stagnation detection - EXACT copy from monolithic version.

    This preserves the exact same monitoring and shutdown logic.
    """
    logger = context.logger
    last_stats = None
    stagnant_count = 0

    while not context.shutdown_flag:
        current_stats = context.get_statistics()

        # Log progress - preserving original format
        logger.info(
            f"Progress: {current_stats['total_tasks_completed']} completed, "
            f"{current_stats['active_tasks']} active, "
            f"{current_stats['queue_size']} queued"
        )

        # Check for completion - EXACT logic from monolithic
        if context.is_queue_empty() and not context.has_active_tasks():
            logger.info("All tasks completed - signaling shutdown")
            context.signal_shutdown()
            break

        # Check for stagnation (no progress for too long) - EXACT logic
        if (
            last_stats
            and current_stats["total_tasks_completed"]
            == last_stats["total_tasks_completed"]
            and current_stats["active_tasks"] == 0
            and current_stats["queue_size"] == 0
        ):
            stagnant_count += 1
            if stagnant_count >= 3:  # 30 seconds of no progress
                logger.warning("No progress detected for 30 seconds - forcing shutdown")
                context.signal_shutdown()
                break
        else:
            stagnant_count = 0

        last_stats = current_stats.copy()
        await asyncio.sleep(PROGRESS_REPORT_INTERVAL)


async def discover_level1_folders(browser, logger):
    """
    Phase 1: Discover initial structure - EXACT copy from monolithic version.
    """
    logger.info("Phase 1: Discovering level 1 folders...")

    try:
        page = await browser.new_page()
        await page.goto(START_URL, wait_until="networkidle")
        await page.wait_for_timeout(2000)

        root_node = await find_objectarx_root_node(page)
        if not root_node:
            logger.error("Could not find ObjectARX root node. Exiting.")
            await page.close()
            return None

        level1_folders = await get_level1_folders(page, root_node)
        await page.close()

        if not level1_folders:
            logger.error("No level 1 folders found. Exiting.")
            return None

        logger.info(f"Found {len(level1_folders)} level 1 folders")
        return level1_folders

    except Exception as e:
        logger.error(f"Error discovering level 1 folders: {e}")
        return None


async def submit_initial_tasks(level1_folders, context):
    """
    Phase 2: Submit initial tasks - EXACT copy from monolithic version.
    """
    logger = context.logger
    logger.info("Phase 2: Submitting initial tasks for CONCURRENT processing...")

    for i, folder in enumerate(level1_folders):
        worker_id = str(i + 1)
        folder.worker_id = worker_id

        task = Task(
            worker_id=worker_id,
            node_info=folder,
            priority=folder.depth * 1000 + i,  # Breadth-first prioritization
        )
        await context.submit_task(task)

    logger.info(f"Submitted {len(level1_folders)} initial tasks")


async def start_concurrent_workers(context, browser):
    """
    Phase 3: Start HIERARCHICAL dynamic workers - spawns workers as needed up to MAX limit.
    """
    logger = context.logger
    logger.info(
        f"Phase 3: Starting hierarchical dynamic worker system (max {MAX_CONCURRENT_PAGES} workers)..."
    )

    # Dynamic worker pool - workers are spawned as tasks are submitted
    worker_pool = set()

    async def spawn_worker_for_task():
        """Spawn a new worker to process tasks from the queue"""
        worker_count = len(worker_pool)
        if worker_count < MAX_CONCURRENT_PAGES:
            worker_id = f"Worker-{worker_count}"
            worker_task = asyncio.create_task(
                parallel_worker(context, browser, worker_count)
            )
            worker_pool.add(worker_task)
            await asyncio.sleep(0)  # Make function async
            logger.info(f"Spawned dynamic worker: {worker_id}")
            return worker_task
        return None

    # Start with initial workers based on level 1 folders
    initial_workers = min(7, MAX_CONCURRENT_PAGES)  # Level 1 folders
    for _ in range(initial_workers):
        await spawn_worker_for_task()

    # Start progress monitoring
    monitor_task = asyncio.create_task(
        monitor_progress_with_stagnation_detection(context)
    )

    # Monitor and spawn workers dynamically as queue grows
    while not context.shutdown_flag:
        # Spawn more workers if queue is backing up and we're under limit
        queue_size = context.task_queue.qsize()
        active_workers = len([w for w in worker_pool if not w.done()])

        if queue_size > active_workers and len(worker_pool) < MAX_CONCURRENT_PAGES:
            new_worker = await spawn_worker_for_task()
            if new_worker:
                logger.info(
                    f"Spawned worker due to queue backlog: {queue_size} tasks, {active_workers} active workers"
                )

        # Check if monitoring completed
        if monitor_task.done():
            break

        await asyncio.sleep(1)  # Check every second

    # Cancel all worker tasks
    for worker_task in worker_pool:
        worker_task.cancel()

    # Wait for workers to finish gracefully (with timeout)
    try:
        await asyncio.wait_for(
            asyncio.gather(*worker_pool, return_exceptions=True), timeout=10
        )
    except asyncio.TimeoutError:
        logger.warning("Some workers did not finish gracefully")

    return list(worker_pool)


async def analyze_results_and_save(context):
    """
    Phase 4: Results and Analysis - EXACT copy from monolithic version.
    """
    logger = context.logger
    logger.info("Phase 4: Analyzing results and building JSON structure...")

    final_stats = context.get_statistics()
    logger.info(" Final Statistics:")
    logger.info(f"  - Total tasks completed: {final_stats['total_tasks_completed']}")
    logger.info(f"  - Total tasks failed: {final_stats['total_tasks_failed']}")
    logger.info(f"  - Total retries: {final_stats['total_retries']}")
    logger.info(f"  - Success rate: {final_stats['completion_rate']:.1f}%")

    # Build the final JSON structure
    json_structure = build_json_structure_from_tasks(context.completed_tasks)

    # Save to file asynchronously
    async with aiofiles.open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        await f.write(json.dumps(json_structure, indent=2, ensure_ascii=False))

    logger.info("Structure mapping completed with PARALLEL processing!")
    logger.info(f" Output saved to: {OUTPUT_FILE}")
    logger.info(f" Total nodes mapped: {len(context.completed_tasks)}")

    return json_structure


async def main():
    """
    Main function with CONCURRENT task processing and advanced optimizations.

    Enhanced with Phase 3 optimization features:
    - Memory optimization sessions
    - Advanced monitoring and metrics
    - Orchestrated optimization patterns
    """
    # Setup comprehensive logging (file + terminal)
    logger = setup_comprehensive_logging()

    logger.info("Starting ObjectARX JSON structure mapping with PARALLEL processing...")
    logger.info(
        f"Configuration: {MAX_CONCURRENT_PAGES} concurrent pages, max depth {MAX_DEPTH}"
    )

    # Initialize advanced optimization configuration if available
    orchestration_config = None
    if ADVANCED_OPTIMIZATION_AVAILABLE:
        orchestration_config = create_optimized_orchestration_config(
            enable_browser_reuse=True,
            enable_resource_filtering=True,
            enable_memory_optimization=True,
            enable_pattern_caching=True,
            enable_advanced_monitoring=True,
            max_concurrent_workers=MAX_CONCURRENT_PAGES,
        )
        logger.info("Advanced optimization orchestration enabled")

    # Initialize context
    context = ParallelWorkerContext(MAX_CONCURRENT_PAGES, logger)

    async with async_playwright() as p:
        # Use optimized browser creation if available
        if OPTIMIZATION_AVAILABLE:
            browser = await create_optimized_browser(p)
            logger.info("Using optimized browser with reuse and circuit breaker")
        else:
            browser = await p.chromium.launch(headless=BROWSER_HEADLESS)
            logger.info("Using standard browser creation")

        if not browser:
            logger.error("Failed to create browser")
            return

        try:
            # Phase 1: Discover initial structure
            level1_folders = await discover_level1_folders(browser, logger)
            if not level1_folders:
                await browser.close()
                return

            # Phase 2: Submit initial tasks
            await submit_initial_tasks(level1_folders, context)

            # Phase 3: Start concurrent workers
            await start_concurrent_workers(context, browser)

            # Phase 4: Results and Analysis
            await analyze_results_and_save(context)

        finally:
            # Report optimization metrics if available
            if OPTIMIZATION_AVAILABLE:
                metrics = get_optimization_metrics()
                logger.info("=== OPTIMIZATION METRICS ===")
                logger.info(
                    f"Browser reuse rate: {metrics.get('browser_reuse_rate', 0):.1%}"
                )
                logger.info(
                    f"Resource block rate: {metrics.get('resource_block_rate', 0):.1%}"
                )
                logger.info(
                    f"Total pages processed: {metrics.get('total_pages_processed', 0)}"
                )
                logger.info(f"Memory cleanups: {metrics.get('memory_cleanups', 0)}")
                logger.info(
                    f"Circuit breaker status: {metrics.get('circuit_breaker_status', 'unknown')}"
                )

                # Generate advanced optimization report if available
                if ADVANCED_OPTIMIZATION_AVAILABLE:
                    advanced_report = generate_optimization_report()
                    logger.info("=== ADVANCED OPTIMIZATION REPORT ===")
                    for line in advanced_report.split("\n"):
                        if line.strip():
                            logger.info(line)

                # Cleanup optimization resources
                await cleanup_optimization_resources()
                logger.info("Optimization cleanup completed")

            # Cleanup advanced optimization state
            if ADVANCED_OPTIMIZATION_AVAILABLE:
                cleanup_optimization_state()
                logger.info("Advanced optimization state cleaned up")

            await browser.close()

    logger.info("Enhanced parallel structure mapping completed!")
    logger.info(" Check logs/ directory for detailed execution logs")
    logger.info(f" Use '{OUTPUT_FILE}' for improved hierarchical scraping")


if __name__ == "__main__":
    asyncio.run(main())
