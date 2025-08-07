"""
Logging setup module for parallel scraper system.

Provides centralized logging configuration with file and console output,
structured formatting, and detailed debugging capabilities for async operations.
"""

import logging
import os
from datetime import datetime

# Import config directly instead of relative import
try:
    from .config import ScraperConfig

    LOG_LEVEL = ScraperConfig.LOG_LEVEL
    LOG_FORMAT = ScraperConfig.LOG_FORMAT
    LOG_DATE_FORMAT = ScraperConfig.LOG_DATE_FORMAT
except ImportError:
    # Fallback for when running as standalone module
    from config import ScraperConfig

    LOG_LEVEL = ScraperConfig.LOG_LEVEL
    LOG_FORMAT = ScraperConfig.LOG_FORMAT
    LOG_DATE_FORMAT = ScraperConfig.LOG_DATE_FORMAT


def setup_logging(logger_name: str = None) -> logging.Logger:
    """
    Setup structured logging for the parallel scraper system.

    Args:
        logger_name: Optional logger name. If None, uses the root logger.

    Returns:
        Configured logger instance
    """
    # Ensure logs directory exists
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(logs_dir, f"parallel_scraper_{timestamp}.log")

    # Configure logging
    logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()

    # Clear any existing handlers to avoid duplicates
    logger.handlers.clear()

    # Set level
    logger.setLevel(getattr(logging, LOG_LEVEL.upper()))

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # File handler with UTF-8 encoding
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # File gets all debug info
    file_handler.setFormatter(formatter)

    # Console handler with configurable level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL.upper()))
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # Log initialization
    logger.info(f"Logging initialized - File: {log_file}")
    logger.info(f"Log level: {LOG_LEVEL}")

    return logger


def log_function_entry(logger: logging.Logger, function_name: str, **kwargs):
    """
    Log function entry with parameters for debugging async operations.

    Args:
        logger: Logger instance
        function_name: Name of the function being entered
        **kwargs: Function parameters to log
    """
    params = ", ".join([f"{k}={v}" for k, v in kwargs.items()])
    logger.debug(f"ENTRY: {function_name}({params})")


def log_function_exit(
    logger: logging.Logger, function_name: str, result=None, duration_ms: float = None
):
    """
    Log function exit with result and timing for debugging async operations.

    Args:
        logger: Logger instance
        function_name: Name of the function being exited
        result: Function result to log (optional)
        duration_ms: Function execution time in milliseconds (optional)
    """
    timing = f" [{duration_ms:.2f}ms]" if duration_ms is not None else ""
    result_info = f" -> {result}" if result is not None else ""
    logger.debug(f"EXIT: {function_name}{timing}{result_info}")


def log_worker_state(logger: logging.Logger, worker_id: str, state: str, **context):
    """
    Log worker state changes for debugging hanging issues.

    Args:
        logger: Logger instance
        worker_id: Unique worker identifier
        state: Current worker state (starting, working, waiting, stopping, etc.)
        **context: Additional context information
    """
    context_info = ", ".join([f"{k}={v}" for k, v in context.items()])
    logger.info(f"WORKER {worker_id}: {state} | {context_info}")


def log_browser_operation(
    logger: logging.Logger,
    operation: str,
    url: str = None,
    selector: str = None,
    timeout: float = None,
    **context,
):
    """
    Log browser operations for debugging DOM hanging issues.

    Args:
        logger: Logger instance
        operation: Browser operation being performed
        url: Target URL (optional)
        selector: DOM selector (optional)
        timeout: Operation timeout (optional)
        **context: Additional context information
    """
    operation_info = []
    if url:
        operation_info.append(f"url={url}")
    if selector:
        operation_info.append(f"selector='{selector}'")
    if timeout:
        operation_info.append(f"timeout={timeout}s")

    for k, v in context.items():
        operation_info.append(f"{k}={v}")

    context_str = " | " + ", ".join(operation_info) if operation_info else ""
    logger.debug(f"BROWSER: {operation}{context_str}")
