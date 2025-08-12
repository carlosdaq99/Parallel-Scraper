"""
Worker module for parallel scraper system.

Contains the worker functions that process tasks from the queue,
handle retries, and coordinate with the browser automation system.
"""

import asyncio

# Import with fallback for standalone execution
try:
    from .config import ScraperConfig
    from .data_structures import Task, NodeInfo, ParallelWorkerContext
    from .dom_utils import (
        create_browser_page,
        find_target_folder_dom_async,
        expand_node_safely,
        get_children_at_level_async,
    )
    from .logging_setup import log_worker_state, log_function_entry, log_function_exit
    from .optimization_utils import create_optimized_browser
    from .worker_tracking_display import (
        log_worker_completion,
        log_worker_error,
        track_task_start,
        track_task_completion,
        track_task_child_creation,
    )

    # Advanced optimization utilities are reserved for future performance improvements
    ADVANCED_OPTIMIZATION_AVAILABLE = False

    # Use self-contained config
    MAX_RETRIES = ScraperConfig.MAX_RETRIES
    RETRY_DELAY_BASE = ScraperConfig.RETRY_DELAY_BASE
    EXPONENTIAL_BACKOFF_MULTIPLIER = ScraperConfig.EXPONENTIAL_BACKOFF_MULTIPLIER
except ImportError:
    from config import ScraperConfig
    import data_structures
    import dom_utils
    import logging_setup
    import optimization_utils
    import worker_tracking_display

    MAX_RETRIES = ScraperConfig.MAX_RETRIES
    RETRY_DELAY_BASE = ScraperConfig.RETRY_DELAY_BASE
    EXPONENTIAL_BACKOFF_MULTIPLIER = ScraperConfig.EXPONENTIAL_BACKOFF_MULTIPLIER

    Task = data_structures.Task
    NodeInfo = data_structures.NodeInfo
    ParallelWorkerContext = data_structures.ParallelWorkerContext
    create_browser_page = dom_utils.create_browser_page
    find_target_folder_dom_async = dom_utils.find_target_folder_dom_async
    expand_node_safely = dom_utils.expand_node_safely
    get_children_at_level_async = dom_utils.get_children_at_level_async
    log_worker_state = logging_setup.log_worker_state
    log_function_entry = logging_setup.log_function_entry
    log_function_exit = logging_setup.log_function_exit
    create_optimized_browser = optimization_utils.create_optimized_browser
    log_worker_completion = worker_tracking_display.log_worker_completion
    log_worker_error = worker_tracking_display.log_worker_error
    track_task_start = worker_tracking_display.track_task_start
    track_task_completion = worker_tracking_display.track_task_completion
    track_task_child_creation = worker_tracking_display.track_task_child_creation
    ADVANCED_OPTIMIZATION_AVAILABLE = False

    Task = data_structures.Task
    NodeInfo = data_structures.NodeInfo
    ParallelWorkerContext = data_structures.ParallelWorkerContext

    create_browser_page = dom_utils.create_browser_page
    find_target_folder_dom_async = dom_utils.find_target_folder_dom_async
    expand_node_safely = dom_utils.expand_node_safely
    get_children_at_level_async = dom_utils.get_children_at_level_async

    log_worker_state = logging_setup.log_worker_state
    log_function_entry = logging_setup.log_function_entry
    log_function_exit = logging_setup.log_function_exit


async def process_task_async(task, context, browser):
    """
    Process a single task using async Playwright operations with comprehensive timeout protection.

    This function is the core of the scraping operation. It:
    1. Creates a new browser page with timeout protection
    2. Navigates to the target folder using DOM-based approach
    3. Expands the folder and discovers children
    4. Returns the updated NodeInfo with discovered children

    Args:
        task: Task to process containing the folder information
        context: Worker context for coordination and statistics
        browser: Playwright browser instance

    Returns:
        NodeInfo with updated children and leaf status
    """
    worker_id = task.worker_id
    folder_info = task.node_info
    logger = context.logger

    # Track task start in hierarchical tracker
    track_task_start(
        context.tracker_state,
        task.task_id,
        worker_id,
        parent_id=task.parent_task_id,
        metadata={"label": folder_info.label, "depth": folder_info.depth},
    )

    log_function_entry(
        logger,
        "process_task_async",
        worker_id=worker_id,
        label=folder_info.label,
        depth=folder_info.depth,
    )

    start_time = asyncio.get_event_loop().time()

    try:
        log_worker_state(logger, worker_id, "creating_page", label=folder_info.label)

        # Create browser page with timeout protection
        page = await create_browser_page(browser)
        if not page:
            logger.error(f"[{worker_id}] Failed to create browser page")
            folder_info.is_leaf = True
            return folder_info

        log_worker_state(logger, worker_id, "finding_target", label=folder_info.label)

        # Navigate to the target folder using DOM-based approach
        target_folder = await find_target_folder_dom_async(page, folder_info, worker_id)
        if not target_folder:
            logger.warning(
                f"[{worker_id}] Could not find target folder: {folder_info.label}"
            )
            folder_info.is_leaf = True
            await page.close()
            return folder_info

        log_worker_state(logger, worker_id, "expanding_node", label=folder_info.label)

        # Try to expand the target folder
        expand_success = await expand_node_safely(target_folder, worker_id)
        if not expand_success:
            logger.info(
                f"[{worker_id}] Could not expand or no expand button - marking as leaf"
            )
            folder_info.is_leaf = True
            await page.close()
            return folder_info

        log_worker_state(
            logger, worker_id, "discovering_children", label=folder_info.label
        )

        # Discover children using DOM-only approach
        children = await get_children_at_level_async(
            page, target_folder, folder_info.depth + 1, worker_id, folder_info
        )

        # Update folder info with discovered children
        folder_info.subfolders = [child["label"] for child in children]
        folder_info.is_leaf = len(children) == 0

        logger.info(
            f"[{worker_id}] Discovered {len(children)} children for: {folder_info.label}"
        )

        # Submit child tasks to the queue for hierarchical processing
        for i, child_info in enumerate(children):
            # Generate hierarchical worker ID: parent.childIndex
            child_worker_id = f"{worker_id}.{i + 1}"
            child_path = f"{folder_info.path} > {child_info['label']}"
            child_node = NodeInfo(
                label=child_info["label"],
                path=child_path,
                depth=folder_info.depth + 1,
                parent_worker_id=worker_id,
                worker_id=child_worker_id,
                guid=child_info.get("guid", ""),
            )

            child_task = Task(
                worker_id=child_worker_id,
                node_info=child_node,
                priority=folder_info.depth
                + 1,  # Breadth-first: deeper = lower priority
                parent_task_id=task.task_id,  # Use task_id for hierarchical tracking
            )

            # Track parent-child relationship
            track_task_child_creation(
                context.tracker_state, task.task_id, child_task.task_id
            )

            # Submit child task for processing
            await context.submit_task(child_task)

        await page.close()

        execution_time = (asyncio.get_event_loop().time() - start_time) * 1000

        # Track task completion
        track_task_completion(context.tracker_state, task.task_id, "completed")

        log_function_exit(
            logger,
            "process_task_async",
            result=f"{len(children)} children",
            duration_ms=execution_time,
        )

        log_worker_state(
            logger,
            worker_id,
            "completed",
            label=folder_info.label,
            children_count=len(children),
            execution_time_ms=execution_time,
        )

        return folder_info

    except Exception as e:
        execution_time = (asyncio.get_event_loop().time() - start_time) * 1000
        logger.error(f"[{worker_id}] Error processing task: {e}")

        # Track task failure
        track_task_completion(context.tracker_state, task.task_id, "failed")

        log_function_exit(
            logger, "process_task_async", result="error", duration_ms=execution_time
        )
        log_worker_state(
            logger, worker_id, "error", label=folder_info.label, error=str(e)
        )

        # Ensure page is closed on error
        try:
            if "page" in locals():
                await page.close()
        except Exception:
            pass

        # Mark as leaf on error to prevent infinite retries
        folder_info.is_leaf = True
        return folder_info


async def process_task_with_semaphore(task, context, browser):
    """
    Process a single task with semaphore-controlled concurrency.

    This wrapper ensures that only a limited number of browser pages
    are active simultaneously, preventing resource exhaustion.

    Args:
        task: Task to process
        context: Worker context with semaphore control
        browser: Playwright browser instance

    Returns:
        Processed NodeInfo
    """
    async with context.semaphore:
        return await process_task_async(task, context, browser)


async def parallel_worker(context, playwright, worker_id):
    """
    Concurrent worker that processes tasks from the queue with robust error handling.

    This is the main worker function that:
    1. Continuously pulls tasks from the queue
    2. Processes them with timeout and retry logic
    3. Handles graceful shutdown when no more tasks are available
    4. Provides detailed logging for debugging hanging issues

    Args:
        context: Shared worker context for coordination
        playwright: Playwright instance for getting browsers from pool
        worker_id: Unique identifier for this worker
    """
    logger = context.logger
    log_function_entry(logger, "parallel_worker", worker_id=worker_id)

    consecutive_timeouts = 0
    max_consecutive_timeouts = 3  # Exit after 3 consecutive timeouts (15 seconds)
    tasks_processed = 0

    log_worker_state(
        logger, f"Worker-{worker_id}", "starting", max_timeouts=max_consecutive_timeouts
    )

    try:
        # Register this worker with the WorkerManager for tracking
        await context.worker_manager.register_worker(f"Worker-{worker_id}")

        while True:
            try:
                log_worker_state(
                    logger,
                    f"Worker-{worker_id}",
                    "waiting_for_task",
                    tasks_processed=tasks_processed,
                    timeouts=consecutive_timeouts,
                )

                # Wait for a task with timeout to avoid infinite blocking
                task = await asyncio.wait_for(context.task_queue.get(), timeout=5.0)
                consecutive_timeouts = (
                    0  # Reset timeout counter on successful task retrieval
                )

                log_worker_state(
                    logger,
                    f"Worker-{worker_id}",
                    "received_task",
                    task_id=task.worker_id,
                    priority=task.priority,
                    retry_count=task.retry_count,
                )

            except asyncio.TimeoutError:
                consecutive_timeouts += 1
                log_worker_state(
                    logger,
                    f"Worker-{worker_id}",
                    "timeout",
                    consecutive_timeouts=consecutive_timeouts,
                    max_timeouts=max_consecutive_timeouts,
                )

                # Check if we should continue waiting or exit
                if context.should_shutdown():
                    log_worker_state(
                        logger, f"Worker-{worker_id}", "shutdown_signal_received"
                    )
                    break
                elif consecutive_timeouts >= max_consecutive_timeouts:
                    log_worker_state(
                        logger, f"Worker-{worker_id}", "max_timeouts_reached"
                    )
                    break

                continue

            try:
                log_worker_state(
                    logger,
                    f"Worker-{worker_id}",
                    "processing_task",
                    task_id=task.worker_id,
                )

                # Track task start time for completion logging
                import time

                task_start_time = time.time()

                # Get browser from pool for this task
                browser = await create_optimized_browser(
                    playwright, reuse_existing=True
                )
                if not browser:
                    logger.error(
                        f"[Worker-{worker_id}] Failed to get browser from pool"
                    )
                    await context.mark_task_failed(
                        task.worker_id, Exception("Failed to get browser")
                    )
                    continue

                # Process the task with semaphore control
                result = await process_task_with_semaphore(task, context, browser)

                # Calculate task duration
                task_duration = time.time() - task_start_time

                # Mark task as completed
                await context.mark_task_completed(task.worker_id, result)
                tasks_processed += 1

                # Log worker completion to tracking display
                # Extract hierarchical path (part after last underscore) for display
                task_path = task.worker_id.split('_')[-1] if '_' in task.worker_id else task.worker_id
                log_worker_completion(
                    f"Worker-{worker_id}",
                    f"Task-[{task_path}]",
                    task_duration,
                    len(result) if isinstance(result, list) else 0,
                )

                log_worker_state(
                    logger,
                    f"Worker-{worker_id}",
                    "task_completed",
                    task_id=task.worker_id,
                    tasks_processed=tasks_processed,
                )

            except Exception as e:
                log_worker_state(
                    logger,
                    f"Worker-{worker_id}",
                    "task_error",
                    task_id=task.worker_id,
                    error=str(e),
                    retry_count=task.retry_count,
                )

                # Log worker error to tracking display
                log_worker_error(f"Worker-{worker_id}", str(e), task.retry_count)

                # Retry logic with exponential backoff
                if task.retry_count < MAX_RETRIES:
                    task.retry_count += 1
                    context.total_retries += 1

                    delay = RETRY_DELAY_BASE * (
                        EXPONENTIAL_BACKOFF_MULTIPLIER ** (task.retry_count - 1)
                    )

                    log_worker_state(
                        logger,
                        f"Worker-{worker_id}",
                        "retrying_task",
                        task_id=task.worker_id,
                        attempt=task.retry_count,
                        delay_seconds=delay,
                        max_retries=MAX_RETRIES,
                    )

                    await asyncio.sleep(delay)
                    await context.task_queue.put(task)  # Re-queue for retry
                    # NOTE: Do NOT call task_done() here - task is being retried, not completed

                else:
                    log_worker_state(
                        logger,
                        f"Worker-{worker_id}",
                        "task_failed_permanently",
                        task_id=task.worker_id,
                        max_retries=MAX_RETRIES,
                    )
                    await context.mark_task_failed(task.worker_id, e)

    finally:
        # Unregister this worker when exiting
        try:
            await context.worker_manager.unregister_worker(f"Worker-{worker_id}")
        except Exception as e:
            logger.warning(f"Worker-{worker_id} unregister error: {e}")

        log_worker_state(
            logger,
            f"Worker-{worker_id}",
            "finished",
            tasks_processed=tasks_processed,
            total_timeouts=consecutive_timeouts,
        )

        # Log worker completion to tracking display (shutdown)
        log_worker_completion(
            f"Worker-{worker_id}",
            "shutdown",
            0.0,  # No specific task duration for shutdown
            tasks_processed,
        )

        log_function_exit(
            logger, "parallel_worker", result=f"processed {tasks_processed} tasks"
        )


async def create_workers(context, playwright, num_workers):
    """
    Create and start the specified number of workers.

    Args:
        context: Shared worker context
        playwright: Playwright instance for browser pool access
        num_workers: Number of workers to create

    Returns:
        List of worker tasks
    """
    logger = context.logger
    workers = []

    logger.info(f"Creating {num_workers} parallel workers")

    for i in range(num_workers):
        worker_task = asyncio.create_task(
            parallel_worker(context, playwright, i + 1), name=f"worker-{i + 1}"
        )
        workers.append(worker_task)

        # Small delay between worker startups to prevent thundering herd
        if i < num_workers - 1:
            await asyncio.sleep(ScraperConfig.WORKER_COORDINATION_DELAY)

    logger.info(f"All {num_workers} workers started successfully")
    return workers
