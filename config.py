"""
Self-Contained Configuration for Parallel Scraper

This module provides all configuration settings for the parallel web scraper
in a completely self-contained way, with no external dependencies.
Consolidates scraper and optimization settings into a single, well-organized structure.
"""

import os
from typing import Dict, Any, Optional


class ScraperConfig:
    """Configuration settings for the parallel web scraper."""

    # ============================================================================
    # TARGET DOCUMENTATION CONFIGURATION
    # Defines the starting point and scope of the scraping operation.
    # ============================================================================
    START_URL = "https://help.autodesk.com/view/OARX/2025/ENU/"
    """The initial URL where the scraper begins its operation."""

    FOLDER_LABEL = "ObjectARX and Managed .NET"
    """The label of the root folder to identify and start scraping from."""

    # ============================================================================
    # DOM SELECTOR CONFIGURATION
    # Defines the CSS selectors used to find and interact with elements on the page.
    # ============================================================================
    EXPAND_BUTTON_SELECTOR = 'span.expand-collapse[role="button"]'
    """CSS selector for the button that expands a folder to reveal its children."""

    TREEITEM_SELECTOR = '[role="treeitem"]'
    """CSS selector for a single item in the documentation tree structure."""

    # ============================================================================
    # OUTPUT CONFIGURATION
    # Specifies where the scraped data will be saved.
    # ============================================================================
    OUTPUT_FILE = "objectarx_structure_map_parallel.json"
    """File name for the final JSON output containing the scraped data."""

    # ============================================================================
    # PARALLEL PROCESSING CONFIGURATION
    # Controls the concurrency and scaling behavior of the scraper.
    # ============================================================================
    MAX_CONCURRENT_PAGES = int(os.getenv("SCRAPER_MAX_CONCURRENT_PAGES", "500"))
    """The absolute maximum number of concurrent browser pages allowed."""

    MAX_WORKERS = int(os.getenv("SCRAPER_MAX_WORKERS", "500"))
    """The upper limit for the adaptive scaling engine."""

    MIN_WORKERS = int(os.getenv("SCRAPER_MIN_WORKERS", "20"))
    """The lower limit for the adaptive scaling engine."""

    INITIAL_WORKERS = int(os.getenv("SCRAPER_INITIAL_WORKERS", "50"))
    """The number of workers to start with, for proactive scaling."""

    MAX_DEPTH = int(os.getenv("SCRAPER_MAX_DEPTH", "999"))
    """The maximum depth to traverse in the documentation tree."""

    MAX_SUBFOLDERS_TO_SPAWN = int(os.getenv("SCRAPER_MAX_SUBFOLDERS", "999"))
    """The maximum number of subfolders a single worker can spawn tasks for."""

    # ============================================================================
    # TIMING CONFIGURATION
    # Fine-tunes the delays and timeouts for various operations.
    # ============================================================================
    WORKER_STARTUP_DELAY = float(os.getenv("SCRAPER_STARTUP_DELAY", "0.05"))
    """Delay between starting each worker to prevent overwhelming the system."""

    PAGE_LOAD_TIMEOUT = float(os.getenv("SCRAPER_PAGE_TIMEOUT", "30.0"))
    """Maximum time to wait for a page to load, in seconds."""

    DOM_OPERATION_TIMEOUT = float(os.getenv("SCRAPER_DOM_TIMEOUT", "15.0"))
    """Maximum time to wait for a single DOM operation to complete, in seconds."""

    WORKER_SHUTDOWN_TIMEOUT = float(os.getenv("SCRAPER_SHUTDOWN_TIMEOUT", "5.0"))
    """Maximum time to wait for a worker to shut down gracefully, in seconds."""

    PAGE_WAIT_AFTER_EXPAND = int(os.getenv("SCRAPER_EXPAND_WAIT", "500"))
    """Time to wait after expanding a node to allow content to load, in milliseconds."""

    # ============================================================================
    # MONITORING AND SCALING INTERVALS
    # Configures how frequently the system monitors performance and makes scaling decisions.
    # ============================================================================
    REAL_TIME_MONITOR_ENABLED = (
        os.getenv("SCRAPER_MONITOR_ENABLED", "false").lower() == "true"
    )
    """Whether to enable the real-time monitoring dashboard."""

    REAL_TIME_MONITOR_INTERVAL = int(os.getenv("SCRAPER_MONITOR_INTERVAL", "20"))
    """Update interval for the real-time monitor, in seconds."""

    # Legacy dashboard settings (deprecated - use REAL_TIME_MONITOR_* instead)
    DASHBOARD_UPDATE_INTERVAL = (
        REAL_TIME_MONITOR_INTERVAL  # Use real-time monitor interval
    )
    ENABLE_DASHBOARD = (
        REAL_TIME_MONITOR_ENABLED  # Use real-time monitor enabled setting
    )

    DASHBOARD_DEMO_INTERVAL = float(os.getenv("SCRAPER_DASHBOARD_DEMO", "5.0"))
    """Update interval for the dashboard's demo mode, in seconds."""

    TREND_ANALYSIS_MIN_SAMPLES = int(os.getenv("SCRAPER_TREND_MIN_SAMPLES", "5"))
    """Minimum number of data points required to perform trend analysis."""

    TREND_ANALYSIS_HISTORY_SIZE = int(os.getenv("SCRAPER_TREND_HISTORY_SIZE", "10"))
    """Maximum number of historical data points to store for trend analysis."""

    TREND_COLLECTION_INTERVAL = float(os.getenv("SCRAPER_TREND_COLLECTION", "2.0"))
    """Frequency of collecting data for trend analysis, in seconds."""

    SCALING_CHECK_INTERVAL = float(os.getenv("SCRAPER_SCALING_CHECK", "2.0"))
    """Frequency of checking if a scaling decision should be made, in seconds."""

    SCALING_MONITOR_INTERVAL = float(os.getenv("SCRAPER_SCALING_MONITOR", "6.0"))
    """Frequency of monitoring system performance for scaling purposes, in seconds."""

    ADAPTIVE_SCALING_INTERVAL = float(os.getenv("SCRAPER_ADAPTIVE_SCALING", "10.0"))
    """The main interval for the adaptive scaling engine to make decisions, in seconds."""

    WORKER_STARTUP_BATCH_DELAY = float(os.getenv("SCRAPER_WORKER_BATCH_DELAY", "1.0"))
    """Delay between starting batches of workers, in seconds."""

    WORKER_STATUS_CHECK_DELAY = float(os.getenv("SCRAPER_WORKER_STATUS_DELAY", "1.0"))
    """Delay between checking the status of workers, in seconds."""

    WORKER_COORDINATION_DELAY = float(os.getenv("SCRAPER_WORKER_COORD_DELAY", "0.05"))
    """Small delay for coordinating actions between workers, in seconds."""

    WORKER_TASK_YIELD_DELAY = float(os.getenv("SCRAPER_TASK_YIELD_DELAY", "0.0"))
    """Delay to allow other asyncio tasks to run, in seconds."""

    DOM_RETRY_DELAY = float(os.getenv("SCRAPER_DOM_RETRY_DELAY", "0.5"))
    """Delay between retrying a failed DOM operation, in seconds."""

    TERMINAL_OUTPUT_SUPPRESSION = float(os.getenv("SCRAPER_TERMINAL_SUPPRESS", "2.0"))
    """Delay to suppress terminal output to avoid flickering, in seconds."""

    # ============================================================================
    # WORKER TRACKING CONFIGURATION
    # Controls granular worker tracking and output features.
    # ============================================================================

    # Worker tracking display options
    SHOW_SCALING = os.getenv("SCRAPER_SHOW_SCALING", "true").lower() == "true"
    """Whether to show scaling decisions in terminal output."""

    SHOW_WORKER_CREATED = os.getenv("SCRAPER_SHOW_CREATED", "false").lower() == "true"
    """Whether to show worker creation events."""

    SHOW_WORKER_STATE = os.getenv("SCRAPER_SHOW_STATE", "true").lower() == "true"
    """Whether to show worker state transitions."""

    SHOW_WORKER_COMPLETED = (
        os.getenv("SCRAPER_SHOW_COMPLETED", "false").lower() == "true"
    )
    """Whether to show worker completion events."""

    SHOW_WORKER_ERRORS = os.getenv("SCRAPER_SHOW_ERRORS", "true").lower() == "true"
    """Whether to show worker error events."""

    SHOW_WORKER_STATUS = os.getenv("SCRAPER_SHOW_STATUS", "true").lower() == "true"
    """Whether to show periodic worker status summaries."""

    SHOW_WORKER_HIERARCHY = (
        os.getenv("SCRAPER_SHOW_HIERARCHY", "true").lower() == "true"
    )
    """Whether to show hierarchical worker relationships."""

    SHOW_BROWSER_POOL = os.getenv("SCRAPER_SHOW_BROWSER_POOL", "true").lower() == "true"
    """Whether to show browser pool utilization status."""

    SHOW_QUEUE_ANALYSIS = (
        os.getenv("SCRAPER_SHOW_QUEUE_ANALYSIS", "true").lower() == "true"
    )
    """Whether to show detailed queue analysis with depth and processing rates."""

    MAX_RECENT_COMPLETIONS = int(os.getenv("SCRAPER_MAX_RECENT", "10"))
    """Maximum number of recent completions to track and display."""

    # ============================================================================
    # RETRY CONFIGURATION
    # Defines the behavior for retrying failed operations.
    # ============================================================================
    MAX_RETRIES = int(os.getenv("SCRAPER_MAX_RETRIES", "3"))
    """Maximum number of times to retry a failed task."""

    RETRY_DELAY_BASE = float(os.getenv("SCRAPER_RETRY_DELAY", "1.0"))
    """The base delay for retries, in seconds. Used with exponential backoff."""

    EXPONENTIAL_BACKOFF_MULTIPLIER = float(
        os.getenv("SCRAPER_BACKOFF_MULTIPLIER", "2.0")
    )
    """Multiplier for exponential backoff between retries."""

    # ============================================================================
    # BROWSER CONFIGURATION
    # Configures the behavior of the Playwright browser instances.
    # ============================================================================
    BROWSER_HEADLESS = os.getenv("SCRAPER_HEADLESS", "true").lower() == "true"
    """Whether to run the browser in headless mode (no GUI)."""

    BROWSER_SLOW_MO = int(os.getenv("SCRAPER_SLOW_MO", "0"))
    """Slows down Playwright operations by the specified amount in milliseconds. Useful for debugging."""

    BROWSER_TIMEOUT = int(os.getenv("SCRAPER_BROWSER_TIMEOUT", "30000"))
    """Default timeout for browser operations, in milliseconds."""

    # ============================================================================
    # LOGGING CONFIGURATION
    # Defines the settings for logging application events.
    # ============================================================================
    LOG_LEVEL = os.getenv("SCRAPER_LOG_LEVEL", "INFO")
    """The minimum level of log messages to record."""

    LOG_FORMAT = os.getenv(
        "SCRAPER_LOG_FORMAT",
        "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
    )
    """The format string for log messages."""

    LOG_DATE_FORMAT = os.getenv("SCRAPER_LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")
    """The format string for dates in log messages."""

    # ============================================================================
    # PERFORMANCE MONITORING
    # Configures how frequently progress is reported.
    # ============================================================================
    PROGRESS_REPORT_INTERVAL = int(os.getenv("SCRAPER_PROGRESS_INTERVAL", "10"))
    """Interval for reporting progress to the console, in seconds."""

    # ============================================================================
    # REAL-TIME MONITORING DASHBOARD
    # Configures the real-time terminal dashboard.
    # ============================================================================
    REAL_TIME_MONITOR_ENABLED = (
        os.getenv("SCRAPER_MONITOR_ENABLED", "false").lower() == "true"
    )
    """Whether to enable the real-time monitoring dashboard."""

    REAL_TIME_MONITOR_INTERVAL = int(os.getenv("SCRAPER_MONITOR_INTERVAL", "20"))
    """Update interval for the real-time monitor, in seconds."""

    # ============================================================================
    # DASHBOARD CONTROL (Phase 1 Implementation)
    # Controls the dashboard display behavior for terminal output separation.
    # ============================================================================
    # DEPRECATED: Use REAL_TIME_MONITOR_ENABLED instead
    # ENABLE_DASHBOARD is now set above to use REAL_TIME_MONITOR_ENABLED


class OptimizationConfig:
    """Configuration settings for the optimization framework."""

    # ============================================================================
    # BROWSER OPTIMIZATION SETTINGS
    # Controls browser reuse, pooling, and launch options.
    # ============================================================================
    BROWSER_REUSE_ENABLED = os.getenv("OPT_BROWSER_REUSE", "true").lower() == "true"
    """Whether to reuse browser instances to reduce startup overhead."""

    BROWSER_POOL_SIZE = int(os.getenv("OPT_BROWSER_POOL_SIZE", "1"))
    """The number of browser instances to maintain in the pool. Set to 1 for minimal resource usage."""

    BROWSER_LAUNCH_OPTIONS = {
        "headless": os.getenv("OPT_BROWSER_HEADLESS", "true").lower() == "true",
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-features=VizDisplayCompositor",
        ],
    }
    """Command-line arguments for launching browser instances."""

    # ============================================================================
    # RESOURCE FILTERING SETTINGS
    # Configures which network resources to block for faster page loads.
    # ============================================================================
    RESOURCE_FILTERING_ENABLED = (
        os.getenv("OPT_RESOURCE_FILTERING", "true").lower() == "true"
    )
    """Whether to enable resource filtering."""

    BLOCKED_RESOURCE_TYPES = ["image", "media", "font", "stylesheet", "other"]
    """A list of resource types to block."""

    ALLOWED_DOMAINS = ["help.autodesk.com"]
    """A list of domains from which resources are allowed."""

    # ============================================================================
    # MEMORY MANAGEMENT SETTINGS
    # Controls how the application manages memory to prevent leaks.
    # ============================================================================
    MEMORY_MANAGEMENT_ENABLED = (
        os.getenv("OPT_MEMORY_MANAGEMENT", "true").lower() == "true"
    )
    """Whether to enable memory management features."""

    MAX_MEMORY_MB = int(os.getenv("OPT_MAX_MEMORY_MB", "512"))
    """The maximum memory usage allowed before triggering cleanup, in megabytes."""

    GARBAGE_COLLECTION_INTERVAL = int(os.getenv("OPT_GC_INTERVAL", "100"))
    """The interval (in number of operations) for running garbage collection."""

    # ============================================================================
    # ORCHESTRATOR SETTINGS
    # Configures the high-level orchestration of workers and tasks.
    # ============================================================================
    ORCHESTRATOR_ENABLED = os.getenv("OPT_ORCHESTRATOR", "false").lower() == "true"
    """Whether to enable the advanced orchestrator."""

    MAX_WORKERS = int(os.getenv("OPT_MAX_WORKERS", "10"))
    """The maximum number of workers for the orchestrator."""

    WORKER_QUEUE_SIZE = int(os.getenv("OPT_QUEUE_SIZE", "100"))
    """The size of the queue for the orchestrator's workers."""

    # ============================================================================
    # MONITORING SETTINGS
    # Configures the collection and logging of performance metrics.
    # ============================================================================
    MONITORING_ENABLED = os.getenv("OPT_MONITORING", "true").lower() == "true"
    """Whether to enable performance monitoring."""

    METRICS_COLLECTION_INTERVAL = int(os.getenv("OPT_METRICS_INTERVAL", "30"))
    """The interval for collecting performance metrics, in seconds."""

    PERFORMANCE_LOGGING = os.getenv("OPT_PERFORMANCE_LOG", "true").lower() == "true"
    """Whether to log performance metrics."""

    # ============================================================================
    # FALLBACK SETTINGS
    # Defines behavior for handling errors in the optimization framework.
    # ============================================================================
    FALLBACK_ON_ERROR = os.getenv("OPT_FALLBACK", "true").lower() == "true"
    """Whether to fall back to a basic mode on optimization errors."""

    OPTIMIZATION_TIMEOUT = int(os.getenv("OPT_TIMEOUT", "10"))
    """Timeout for optimization operations, in seconds."""

    # ============================================================================
    # PRESET CONFIGURATIONS
    # Provides predefined configurations for different environments.
    # ============================================================================
    @classmethod
    def create_minimal_config(cls):
        """Create minimal optimization configuration for testing."""
        config = cls()
        config.BROWSER_REUSE_ENABLED = True
        config.RESOURCE_FILTERING_ENABLED = False
        config.MEMORY_MANAGEMENT_ENABLED = False
        config.ORCHESTRATOR_ENABLED = False
        config.MONITORING_ENABLED = False
        return config

    @classmethod
    def create_development_config(cls):
        """Create development optimization configuration."""
        config = cls()
        config.BROWSER_REUSE_ENABLED = True
        config.RESOURCE_FILTERING_ENABLED = True
        config.MEMORY_MANAGEMENT_ENABLED = True
        config.ORCHESTRATOR_ENABLED = False
        config.MONITORING_ENABLED = True
        config.BROWSER_LAUNCH_OPTIONS["headless"] = False  # Visible for debugging
        return config

    @classmethod
    def create_production_config(cls):
        """Create production optimization configuration."""
        config = cls()
        config.BROWSER_REUSE_ENABLED = True
        config.RESOURCE_FILTERING_ENABLED = True
        config.MEMORY_MANAGEMENT_ENABLED = True
        config.ORCHESTRATOR_ENABLED = True
        config.MONITORING_ENABLED = True
        config.BROWSER_LAUNCH_OPTIONS["headless"] = True
        return config


class TestingConfig:
    """Configuration settings for testing and validation."""

    # ============================================================================
    # TEST EXECUTION SETTINGS
    # Controls how tests are executed.
    # ============================================================================
    TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30"))
    """Timeout for test execution, in seconds."""

    INTEGRATION_TEST_ENABLED = os.getenv("INTEGRATION_TEST", "true").lower() == "true"
    """Whether to run integration tests."""

    PERFORMANCE_TEST_ENABLED = os.getenv("PERFORMANCE_TEST", "true").lower() == "true"
    """Whether to run performance tests."""

    # ============================================================================
    # TEST DATA SETTINGS
    # Defines the data and resources used for testing.
    # ============================================================================
    TEST_URL = os.getenv("TEST_URL", "https://help.autodesk.com/view/OARX/2025/ENU/")
    """The URL to use for testing."""

    TEST_OUTPUT_DIR = os.getenv("TEST_OUTPUT_DIR", "test_outputs")
    """The directory for saving test outputs."""

    # ============================================================================
    # VALIDATION SETTINGS
    # Configures how test results are validated.
    # ============================================================================
    VALIDATION_ENABLED = os.getenv("VALIDATION_ENABLED", "true").lower() == "true"
    """Whether to enable validation of test results."""

    STRICT_VALIDATION = os.getenv("STRICT_VALIDATION", "false").lower() == "true"
    """Whether to use strict validation rules."""


class AppConfig:
    """Root configuration object that consolidates all settings."""

    def __init__(self):
        self.SCRAPER = ScraperConfig()
        self.OPTIMIZATION = OptimizationConfig()
        self.TESTING = TestingConfig()

        # Global application settings
        self.APP_NAME = "Parallel Scraper with Optimization"
        self.APP_VERSION = "1.0.0"
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"

        # Environment detection
        self.ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

        # Real-time monitoring configuration
        self.REAL_TIME_MONITOR_ENABLED = self.SCRAPER.REAL_TIME_MONITOR_ENABLED
        self.REAL_TIME_MONITOR_INTERVAL = self.SCRAPER.REAL_TIME_MONITOR_INTERVAL

        # Auto-configure based on environment
        if self.ENVIRONMENT == "production":
            self.OPTIMIZATION = OptimizationConfig.create_production_config()
        elif self.ENVIRONMENT == "development":
            self.OPTIMIZATION = OptimizationConfig.create_development_config()
        elif self.ENVIRONMENT == "testing":
            self.OPTIMIZATION = OptimizationConfig.create_minimal_config()

    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration settings."""
        return {
            "app_name": self.APP_NAME,
            "app_version": self.APP_VERSION,
            "environment": self.ENVIRONMENT,
            "debug": self.DEBUG,
            "scraper": {
                "max_workers": self.SCRAPER.MAX_WORKERS,
                "max_concurrent_pages": self.SCRAPER.MAX_CONCURRENT_PAGES,
                "headless": self.SCRAPER.BROWSER_HEADLESS,
                "output_file": self.SCRAPER.OUTPUT_FILE,
            },
            "optimization": {
                "browser_reuse": self.OPTIMIZATION.BROWSER_REUSE_ENABLED,
                "resource_filtering": self.OPTIMIZATION.RESOURCE_FILTERING_ENABLED,
                "memory_management": self.OPTIMIZATION.MEMORY_MANAGEMENT_ENABLED,
                "orchestrator": self.OPTIMIZATION.ORCHESTRATOR_ENABLED,
                "monitoring": self.OPTIMIZATION.MONITORING_ENABLED,
            },
        }

    def validate_config(self) -> bool:
        """Validate configuration settings for consistency."""
        errors = []

        # Validate scraper settings
        if self.SCRAPER.MAX_WORKERS <= 0:
            errors.append("MAX_WORKERS must be positive")

        if self.SCRAPER.PAGE_LOAD_TIMEOUT <= 0:
            errors.append("PAGE_LOAD_TIMEOUT must be positive")

        # Validate optimization settings
        if self.OPTIMIZATION.BROWSER_POOL_SIZE <= 0:
            errors.append("BROWSER_POOL_SIZE must be positive")

        if self.OPTIMIZATION.MAX_MEMORY_MB <= 0:
            errors.append("MAX_MEMORY_MB must be positive")

        if errors:
            print(f"Configuration validation errors: {errors}")
            return False

        return True


# ============================================================================
# CONFIGURATION UTILITY FUNCTIONS (Merged from config_utils.py)
# ============================================================================


def get_config_value(
    config_dict: Dict[str, Any], path: str, default: Any = None
) -> Any:
    """
    Get configuration value using dot notation path.

    Args:
        config_dict: Configuration dictionary
        path: Dot-notation path (e.g., "parallel.max_workers")
        default: Default value if path not found

    Returns:
        Configuration value or default
    """
    try:
        keys = path.split(".")
        value = config_dict
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default


def merge_config_deep(
    base_config: Dict[str, Any], override_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Deep merge configuration dictionaries.

    Args:
        base_config: Base configuration dictionary
        override_config: Override configuration dictionary

    Returns:
        Merged configuration dictionary
    """
    result = base_config.copy()

    for key, value in override_config.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_config_deep(result[key], value)
        else:
            result[key] = value

    return result


def load_unified_config(
    scraper_overrides: Optional[Dict[str, Any]] = None,
    optimization_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Load unified configuration combining scraper and optimization settings.

    Args:
        scraper_overrides: Optional scraper configuration overrides
        optimization_overrides: Optional optimization configuration overrides

    Returns:
        Dictionary containing unified configuration
    """
    base_config = {
        "scraper": {
            "target": {
                "start_url": config.SCRAPER.START_URL,
                "folder_label": config.SCRAPER.FOLDER_LABEL,
                "output_file": config.SCRAPER.OUTPUT_FILE,
            },
            "parallel": {
                "max_workers": config.SCRAPER.MAX_WORKERS,
                "max_concurrent_pages": config.SCRAPER.MAX_CONCURRENT_PAGES,
                "max_depth": config.SCRAPER.MAX_DEPTH,
            },
            "timing": {
                "page_load_timeout": config.SCRAPER.PAGE_LOAD_TIMEOUT,
                "dom_operation_timeout": config.SCRAPER.DOM_OPERATION_TIMEOUT,
            },
        },
        "optimization": {
            "browser_reuse": config.OPTIMIZATION.BROWSER_REUSE_ENABLED,
            "resource_filtering": config.OPTIMIZATION.RESOURCE_FILTERING_ENABLED,
            "memory_management": config.OPTIMIZATION.MEMORY_MANAGEMENT_ENABLED,
        },
        "version": "1.0.0",
    }

    # Apply overrides if provided
    if scraper_overrides:
        base_config["scraper"] = merge_config_deep(
            base_config["scraper"], scraper_overrides
        )
    if optimization_overrides:
        base_config["optimization"] = merge_config_deep(
            base_config["optimization"], optimization_overrides
        )

    return base_config


# ============================================================================
# ENHANCED CONFIGURATION - Migrated from enhanced_config_manager.py
# ============================================================================


class EnhancedScraperConfig:
    """Enhanced scraper configuration with dynamic scaling support."""

    # Worker Scaling Configuration (NO CAPS - User Settings Respected)
    MAX_WORKERS = int(os.getenv("SCRAPER_MAX_WORKERS", "500"))  # User wants 500
    MIN_WORKERS = int(os.getenv("SCRAPER_MIN_WORKERS", "20"))
    INITIAL_WORKERS = int(os.getenv("SCRAPER_INITIAL_WORKERS", "50"))

    # Scaling Increments (NO CAPS - User Settings Respected)
    WORKER_SCALE_INCREMENT = int(
        os.getenv("SCRAPER_SCALE_INCREMENT", "20")
    )  # User wants +20
    WORKER_SCALE_DECREMENT = int(
        os.getenv("SCRAPER_SCALE_DECREMENT", "10")
    )  # User wants -10

    # Performance Thresholds
    PERFORMANCE_THRESHOLD_HIGH = float(os.getenv("SCRAPER_PERF_HIGH", "0.95"))
    PERFORMANCE_THRESHOLD_LOW = float(os.getenv("SCRAPER_PERF_LOW", "0.80"))
    MEMORY_THRESHOLD_MB = int(os.getenv("SCRAPER_MEMORY_THRESHOLD", "500"))
    CPU_THRESHOLD_PERCENT = int(os.getenv("SCRAPER_CPU_THRESHOLD", "85"))

    # Browser Pool Configuration
    # Use simple configurable browser pool size (set via OPT_BROWSER_POOL_SIZE environment variable)
    BROWSER_POOL_SIZE = (
        OptimizationConfig.BROWSER_POOL_SIZE
    )  # Use simple configurable value
    BROWSER_REUSE_THRESHOLD = int(os.getenv("SCRAPER_BROWSER_REUSE", "100"))
    CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("SCRAPER_CIRCUIT_BREAKER", "5"))
    BROWSER_LAUNCH_DELAY = float(os.getenv("SCRAPER_BROWSER_DELAY", "1.0"))

    # Auto-tuning Configuration
    AUTO_TUNING_ENABLED = os.getenv("SCRAPER_AUTO_TUNING", "true").lower() == "true"
    TUNING_AGGRESSIVENESS = float(os.getenv("SCRAPER_TUNING_AGGRESSION", "0.5"))
    TUNING_FREQUENCY_MINUTES = int(os.getenv("SCRAPER_TUNING_FREQ", "5"))
    SAFETY_MODE_ENABLED = os.getenv("SCRAPER_SAFETY_MODE", "true").lower() == "true"


def get_enhanced_config() -> dict:
    """
    Get enhanced configuration as dictionary.
    Replacement for enhanced_config_manager.get_dynamic_config()
    """
    return {
        "max_workers": EnhancedScraperConfig.MAX_WORKERS,
        "min_workers": EnhancedScraperConfig.MIN_WORKERS,
        "initial_workers": EnhancedScraperConfig.INITIAL_WORKERS,
        "worker_scale_increment": EnhancedScraperConfig.WORKER_SCALE_INCREMENT,
        "worker_scale_decrement": EnhancedScraperConfig.WORKER_SCALE_DECREMENT,
        "performance_threshold_high": EnhancedScraperConfig.PERFORMANCE_THRESHOLD_HIGH,
        "performance_threshold_low": EnhancedScraperConfig.PERFORMANCE_THRESHOLD_LOW,
        "memory_threshold_mb": EnhancedScraperConfig.MEMORY_THRESHOLD_MB,
        "cpu_threshold_percent": EnhancedScraperConfig.CPU_THRESHOLD_PERCENT,
        "browser_pool_size": EnhancedScraperConfig.BROWSER_POOL_SIZE,
        "browser_reuse_threshold": EnhancedScraperConfig.BROWSER_REUSE_THRESHOLD,
        "circuit_breaker_threshold": EnhancedScraperConfig.CIRCUIT_BREAKER_THRESHOLD,
        "browser_launch_delay": EnhancedScraperConfig.BROWSER_LAUNCH_DELAY,
        "auto_tuning_enabled": EnhancedScraperConfig.AUTO_TUNING_ENABLED,
        "tuning_aggressiveness": EnhancedScraperConfig.TUNING_AGGRESSIVENESS,
        "tuning_frequency_minutes": EnhancedScraperConfig.TUNING_FREQUENCY_MINUTES,
        "safety_mode_enabled": EnhancedScraperConfig.SAFETY_MODE_ENABLED,
    }


# ============================================================================
# CONFIGURATION INSTANCES - IMPORT THESE
# ============================================================================

# Create configuration instances for easy importing
config = AppConfig()

# Validate configuration on import
if not config.validate_config():
    raise ValueError("Invalid configuration detected. Please check settings.")

# Also export individual config classes for backward compatibility
scraper_config = config.SCRAPER
optimization_config = config.OPTIMIZATION
testing_config = config.TESTING
