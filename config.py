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
    # ============================================================================
    START_URL = "https://help.autodesk.com/view/OARX/2025/ENU/"
    FOLDER_LABEL = "ObjectARX and Managed .NET"

    # ============================================================================
    # DOM SELECTOR CONFIGURATION
    # ============================================================================
    EXPAND_BUTTON_SELECTOR = 'span.expand-collapse[role="button"]'
    TREEITEM_SELECTOR = '[role="treeitem"]'

    # ============================================================================
    # OUTPUT CONFIGURATION
    # ============================================================================
    OUTPUT_FILE = "objectarx_structure_map_parallel.json"

    # ============================================================================
    # PARALLEL PROCESSING CONFIGURATION
    # ============================================================================
    # PROACTIVE SCALING CONFIGURATION
    # Maximize output while staying within safe resource limits
    # ============================================================================
    MAX_CONCURRENT_PAGES = int(
        os.getenv("SCRAPER_MAX_CONCURRENT_PAGES", "100")
    )  # Increased for higher throughput
    MAX_WORKERS = int(
        os.getenv("SCRAPER_MAX_WORKERS", "100")
    )  # Maximum limit for scaling
    MIN_WORKERS = int(
        os.getenv("SCRAPER_MIN_WORKERS", "20")
    )  # Minimum workers for scaling down
    INITIAL_WORKERS = int(
        os.getenv("SCRAPER_INITIAL_WORKERS", "50")
    )  # Starting worker count
    MAX_DEPTH = int(os.getenv("SCRAPER_MAX_DEPTH", "999"))
    MAX_SUBFOLDERS_TO_SPAWN = int(os.getenv("SCRAPER_MAX_SUBFOLDERS", "100"))

    # ============================================================================
    # TIMING CONFIGURATION
    # ============================================================================
    WORKER_STARTUP_DELAY = float(os.getenv("SCRAPER_STARTUP_DELAY", "0.05"))
    PAGE_LOAD_TIMEOUT = float(os.getenv("SCRAPER_PAGE_TIMEOUT", "30.0"))
    DOM_OPERATION_TIMEOUT = float(os.getenv("SCRAPER_DOM_TIMEOUT", "15.0"))
    WORKER_SHUTDOWN_TIMEOUT = float(os.getenv("SCRAPER_SHUTDOWN_TIMEOUT", "5.0"))
    PAGE_WAIT_AFTER_EXPAND = int(
        os.getenv("SCRAPER_EXPAND_WAIT", "500")
    )  # milliseconds

    # ============================================================================
    # MONITORING AND SCALING INTERVALS
    # ============================================================================
    # Dashboard and monitoring timing intervals
    DASHBOARD_UPDATE_INTERVAL = float(
        os.getenv("SCRAPER_DASHBOARD_INTERVAL", "30.0")
    )  # seconds
    DASHBOARD_DEMO_INTERVAL = float(
        os.getenv("SCRAPER_DASHBOARD_DEMO", "5.0")
    )  # seconds for demo mode

    # Trend analysis configuration
    TREND_ANALYSIS_MIN_SAMPLES = int(
        os.getenv("SCRAPER_TREND_MIN_SAMPLES", "2")
    )  # minimum samples for trends
    TREND_ANALYSIS_HISTORY_SIZE = int(
        os.getenv("SCRAPER_TREND_HISTORY_SIZE", "10")
    )  # maximum history samples
    TREND_COLLECTION_INTERVAL = float(
        os.getenv("SCRAPER_TREND_COLLECTION", "5.0")
    )  # seconds between trend samples

    # Scaling decision timing
    SCALING_CHECK_INTERVAL = float(os.getenv("SCRAPER_SCALING_CHECK", "5.0"))  # seconds
    SCALING_MONITOR_INTERVAL = float(
        os.getenv("SCRAPER_SCALING_MONITOR", "20.0")
    )  # seconds
    ADAPTIVE_SCALING_INTERVAL = float(
        os.getenv("SCRAPER_ADAPTIVE_SCALING", "30.0")
    )  # seconds

    # Worker coordination timing
    WORKER_STARTUP_BATCH_DELAY = float(
        os.getenv("SCRAPER_WORKER_BATCH_DELAY", "1.0")
    )  # seconds
    WORKER_STATUS_CHECK_DELAY = float(
        os.getenv("SCRAPER_WORKER_STATUS_DELAY", "2.0")
    )  # seconds
    WORKER_COORDINATION_DELAY = float(
        os.getenv("SCRAPER_WORKER_COORD_DELAY", "0.05")
    )  # seconds
    WORKER_TASK_YIELD_DELAY = float(
        os.getenv("SCRAPER_TASK_YIELD_DELAY", "0.0")
    )  # seconds - allow other tasks to run

    # DOM operation timing
    DOM_RETRY_DELAY = float(os.getenv("SCRAPER_DOM_RETRY_DELAY", "0.5"))  # seconds

    # Terminal output control
    TERMINAL_OUTPUT_SUPPRESSION = float(
        os.getenv("SCRAPER_TERMINAL_SUPPRESS", "0.5")
    )  # seconds

    # ============================================================================
    # RETRY CONFIGURATION
    # ============================================================================
    MAX_RETRIES = int(os.getenv("SCRAPER_MAX_RETRIES", "3"))
    RETRY_DELAY_BASE = float(os.getenv("SCRAPER_RETRY_DELAY", "1.0"))
    EXPONENTIAL_BACKOFF_MULTIPLIER = float(
        os.getenv("SCRAPER_BACKOFF_MULTIPLIER", "2.0")
    )

    # ============================================================================
    # BROWSER CONFIGURATION
    # ============================================================================
    BROWSER_HEADLESS = os.getenv("SCRAPER_HEADLESS", "true").lower() == "true"
    BROWSER_SLOW_MO = int(os.getenv("SCRAPER_SLOW_MO", "0"))
    BROWSER_TIMEOUT = int(os.getenv("SCRAPER_BROWSER_TIMEOUT", "30000"))  # 30 seconds

    # ============================================================================
    # LOGGING CONFIGURATION
    # ============================================================================
    LOG_LEVEL = os.getenv("SCRAPER_LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv(
        "SCRAPER_LOG_FORMAT",
        "%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
    )
    LOG_DATE_FORMAT = os.getenv("SCRAPER_LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")

    # ============================================================================
    # PERFORMANCE MONITORING
    # ============================================================================
    PROGRESS_REPORT_INTERVAL = int(os.getenv("SCRAPER_PROGRESS_INTERVAL", "10"))

    # ============================================================================
    # REAL-TIME MONITORING DASHBOARD
    # ============================================================================
    REAL_TIME_MONITOR_ENABLED = (
        os.getenv("SCRAPER_MONITOR_ENABLED", "true").lower() == "true"
    )
    REAL_TIME_MONITOR_INTERVAL = int(
        os.getenv("SCRAPER_MONITOR_INTERVAL", "30")
    )  # seconds


class OptimizationConfig:
    """Configuration settings for the optimization framework."""

    # ============================================================================
    # BROWSER OPTIMIZATION SETTINGS
    # ============================================================================
    BROWSER_REUSE_ENABLED = os.getenv("OPT_BROWSER_REUSE", "true").lower() == "true"
    BROWSER_POOL_SIZE = int(os.getenv("OPT_BROWSER_POOL_SIZE", "3"))
    BROWSER_LAUNCH_OPTIONS = {
        "headless": os.getenv("OPT_BROWSER_HEADLESS", "true").lower() == "true",
        "args": [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-features=VizDisplayCompositor",
        ],
    }

    # ============================================================================
    # RESOURCE FILTERING SETTINGS
    # ============================================================================
    RESOURCE_FILTERING_ENABLED = (
        os.getenv("OPT_RESOURCE_FILTERING", "true").lower() == "true"
    )
    BLOCKED_RESOURCE_TYPES = ["image", "media", "font", "stylesheet", "other"]
    ALLOWED_DOMAINS = ["help.autodesk.com"]

    # ============================================================================
    # MEMORY MANAGEMENT SETTINGS
    # ============================================================================
    MEMORY_MANAGEMENT_ENABLED = (
        os.getenv("OPT_MEMORY_MANAGEMENT", "true").lower() == "true"
    )
    MAX_MEMORY_MB = int(os.getenv("OPT_MAX_MEMORY_MB", "512"))
    GARBAGE_COLLECTION_INTERVAL = int(os.getenv("OPT_GC_INTERVAL", "100"))

    # ============================================================================
    # ORCHESTRATOR SETTINGS
    # ============================================================================
    ORCHESTRATOR_ENABLED = os.getenv("OPT_ORCHESTRATOR", "false").lower() == "true"
    MAX_WORKERS = int(os.getenv("OPT_MAX_WORKERS", "10"))
    WORKER_QUEUE_SIZE = int(os.getenv("OPT_QUEUE_SIZE", "100"))

    # ============================================================================
    # MONITORING SETTINGS
    # ============================================================================
    MONITORING_ENABLED = os.getenv("OPT_MONITORING", "true").lower() == "true"
    METRICS_COLLECTION_INTERVAL = int(os.getenv("OPT_METRICS_INTERVAL", "30"))
    PERFORMANCE_LOGGING = os.getenv("OPT_PERFORMANCE_LOG", "true").lower() == "true"

    # ============================================================================
    # FALLBACK SETTINGS
    # ============================================================================
    FALLBACK_ON_ERROR = os.getenv("OPT_FALLBACK", "true").lower() == "true"
    OPTIMIZATION_TIMEOUT = int(os.getenv("OPT_TIMEOUT", "10"))  # seconds

    # ============================================================================
    # PRESET CONFIGURATIONS
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
    # ============================================================================
    TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30"))  # seconds
    INTEGRATION_TEST_ENABLED = os.getenv("INTEGRATION_TEST", "true").lower() == "true"
    PERFORMANCE_TEST_ENABLED = os.getenv("PERFORMANCE_TEST", "true").lower() == "true"

    # ============================================================================
    # TEST DATA SETTINGS
    # ============================================================================
    TEST_URL = os.getenv("TEST_URL", "https://help.autodesk.com/view/OARX/2025/ENU/")
    TEST_OUTPUT_DIR = os.getenv("TEST_OUTPUT_DIR", "test_outputs")

    # ============================================================================
    # VALIDATION SETTINGS
    # ============================================================================
    VALIDATION_ENABLED = os.getenv("VALIDATION_ENABLED", "true").lower() == "true"
    STRICT_VALIDATION = os.getenv("STRICT_VALIDATION", "false").lower() == "true"


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
