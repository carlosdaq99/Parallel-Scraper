#!/usr/bin/env python3
"""
Enhanced Configuration Manager - Dynamic parameter adjustment for adaptive scaling

This module extends the existing OptimizationConfig with dynamic parameter adjustment
capabilities. Provides function-based configuration management that adapts based on
performance metrics and scaling decisions.

Features:
- Dynamic parameter adjustment based on performance metrics
- Configuration validation and bounds checking
- Integration with existing OptimizationConfig
- Function-based architecture for consistency
- Real-time configuration updates

Author: AI Assistant
Date: August 2025
"""

import time
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

# Import existing configuration
from config import OptimizationConfig, ScraperConfig


# Global configuration state
_dynamic_config: Dict[str, Any] = {}
_config_history: list = []
_last_adjustment_time: float = 0.0
_adjustment_cooldown: float = 30.0  # seconds


@dataclass
class DynamicConfigSnapshot:
    """Snapshot of dynamic configuration at a point in time."""

    timestamp: float
    datetime_str: str
    config_values: Dict[str, Any]
    adjustment_reason: str
    performance_trigger: Dict[str, Any]
    validation_status: str


def initialize_dynamic_config() -> Dict[str, Any]:
    """
    Initialize dynamic configuration from existing OptimizationConfig.

    Returns:
        Dictionary with initial dynamic configuration values
    """
    global _dynamic_config

    # Base configuration from existing OptimizationConfig
    base_config = {
        # Browser pool settings
        "browser_pool_size": getattr(OptimizationConfig, "BROWSER_POOL_SIZE", 3),
        "browser_reuse_threshold": getattr(
            OptimizationConfig, "BROWSER_REUSE_THRESHOLD", 100
        ),
        "circuit_breaker_threshold": getattr(
            OptimizationConfig, "CIRCUIT_BREAKER_THRESHOLD", 5
        ),
        "browser_launch_delay": getattr(
            OptimizationConfig, "BROWSER_LAUNCH_DELAY", 1.0
        ),
        # Resource filtering settings
        "resource_filtering_enabled": getattr(
            OptimizationConfig, "RESOURCE_FILTERING_ENABLED", True
        ),
        "blocked_resource_types": getattr(
            OptimizationConfig, "BLOCKED_RESOURCE_TYPES", ["image", "media", "font"]
        ),
        "whitelist_domains": getattr(
            OptimizationConfig, "WHITELIST_DOMAINS", ["help.autodesk.com"]
        ),
        # Memory optimization settings
        "memory_cleanup_interval": getattr(
            OptimizationConfig, "MEMORY_CLEANUP_INTERVAL", 10
        ),
        "memory_optimization_enabled": getattr(
            OptimizationConfig, "MEMORY_OPTIMIZATION_ENABLED", True
        ),
        "gc_threshold": getattr(OptimizationConfig, "GC_THRESHOLD", 100),
        # Performance settings
        "page_timeout": getattr(OptimizationConfig, "PAGE_TIMEOUT", 30000),
        "navigation_timeout": getattr(OptimizationConfig, "NAVIGATION_TIMEOUT", 60000),
        "request_timeout": getattr(OptimizationConfig, "REQUEST_TIMEOUT", 30000),
        # Scaling settings (new dynamic parameters) - Use values from ScraperConfig
        "max_workers": getattr(
            ScraperConfig, "MAX_WORKERS", 100
        ),  # Proactive scaling: up to 100 workers
        "min_workers": getattr(
            ScraperConfig, "MIN_WORKERS", 20
        ),  # Minimum workers for baseline
        "initial_workers": getattr(
            ScraperConfig, "INITIAL_WORKERS", 50
        ),  # Starting worker count
        "worker_scale_increment": 5,  # Aggressive scale-up (+5)
        "worker_scale_decrement": 2,  # Conservative scale-down (-2)
        "performance_threshold_high": 0.95,
        "performance_threshold_low": 0.80,
        "memory_threshold_mb": 500,
        "cpu_threshold_percent": 85,
        # Adaptive tuning settings
        "auto_tuning_enabled": True,
        "tuning_aggressiveness": 0.5,  # 0.0 conservative, 1.0 aggressive
        "tuning_frequency_minutes": 5,
        "safety_mode_enabled": True,
    }

    # Initialize global state
    _dynamic_config = base_config.copy()

    print("🔧 Dynamic Configuration Manager initialized")
    print(f"   Base parameters: {len(_dynamic_config)} settings")
    print(
        f"   Auto-tuning: {'enabled' if _dynamic_config['auto_tuning_enabled'] else 'disabled'}"
    )

    return _dynamic_config.copy()


def get_dynamic_config() -> Dict[str, Any]:
    """
    Get current dynamic configuration.

    Returns:
        Dictionary with current configuration values
    """
    global _dynamic_config
    if not _dynamic_config:
        initialize_dynamic_config()
    return _dynamic_config.copy()


def update_dynamic_config(
    updates: Dict[str, Any], reason: str = "Manual update"
) -> bool:
    """
    Update dynamic configuration with validation.

    Args:
        updates: Dictionary of configuration updates
        reason: Reason for the update

    Returns:
        bool: True if update was successful, False otherwise
    """
    global _dynamic_config, _config_history, _last_adjustment_time

    current_time = time.time()

    # Validate updates
    validation_result = validate_config_updates(updates)
    if not validation_result["valid"]:
        print(f"❌ Configuration update failed: {validation_result['error']}")
        return False

    # Apply updates
    _dynamic_config.update(updates)

    # Record the change in history
    snapshot = DynamicConfigSnapshot(
        timestamp=current_time,
        datetime_str=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time)),
        config_values=updates.copy(),
        adjustment_reason=reason,
        performance_trigger={},
        validation_status="valid",
    )
    _config_history.append(snapshot)
    _last_adjustment_time = current_time

    # Log the change
    print(f"🔧 Configuration updated: {list(updates.keys())}")
    print(f"   Reason: {reason}")

    return True


def _validate_single_config_item(
    key: str, value, validation_rules: Dict[str, Any]
) -> Optional[str]:
    """Validate a single configuration item against rules."""
    if key not in validation_rules:
        return None

    rule = validation_rules[key]

    # Type check
    if not isinstance(value, rule["type"]):
        return f"{key}: Expected {rule['type'].__name__}, got {type(value).__name__}"

    # Range check
    if "min" in rule and value < rule["min"]:
        return f"{key}: Value {value} below minimum {rule['min']}"
    if "max" in rule and value > rule["max"]:
        return f"{key}: Value {value} above maximum {rule['max']}"

    return None


def validate_config_updates(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate configuration updates against safety bounds.

    Args:
        updates: Dictionary of proposed configuration changes

    Returns:
        Dictionary with validation result
    """
    errors = []

    # Define validation rules
    validation_rules = {
        "browser_pool_size": {"min": 1, "max": 10, "type": int},
        "browser_reuse_threshold": {"min": 10, "max": 1000, "type": int},
        "circuit_breaker_threshold": {"min": 1, "max": 20, "type": int},
        "browser_launch_delay": {"min": 0.1, "max": 10.0, "type": float},
        "memory_cleanup_interval": {"min": 1, "max": 60, "type": int},
        "page_timeout": {"min": 5000, "max": 120000, "type": int},
        "navigation_timeout": {"min": 10000, "max": 180000, "type": int},
        "request_timeout": {"min": 5000, "max": 60000, "type": int},
        "max_workers": {"min": 1, "max": 100, "type": int},
        "worker_scale_increment": {"min": 1, "max": 10, "type": int},
        "worker_scale_decrement": {"min": 1, "max": 5, "type": int},
        "performance_threshold_high": {"min": 0.70, "max": 0.99, "type": float},
        "performance_threshold_low": {"min": 0.50, "max": 0.95, "type": float},
        "memory_threshold_mb": {"min": 100, "max": 2000, "type": int},
        "cpu_threshold_percent": {"min": 50, "max": 95, "type": int},
        "tuning_aggressiveness": {"min": 0.0, "max": 1.0, "type": float},
        "tuning_frequency_minutes": {"min": 1, "max": 60, "type": int},
    }

    # Validate each update
    for key, value in updates.items():
        error = _validate_single_config_item(key, value, validation_rules)
        if error:
            errors.append(error)

    # Logical consistency checks
    current_config = get_dynamic_config()
    test_config = current_config.copy()
    test_config.update(updates)

    if (
        "performance_threshold_high" in test_config
        and "performance_threshold_low" in test_config
        and test_config["performance_threshold_high"]
        <= test_config["performance_threshold_low"]
    ):
        errors.append(
            "performance_threshold_high must be greater than performance_threshold_low"
        )

    return {
        "valid": len(errors) == 0,
        "error": "; ".join(errors) if errors else None,
        "error_count": len(errors),
    }


def adjust_config_for_performance(performance_metrics: Dict[str, Any]) -> bool:
    """
    Automatically adjust configuration based on performance metrics.

    Args:
        performance_metrics: Current performance metrics

    Returns:
        bool: True if adjustments were made, False otherwise
    """
    global _last_adjustment_time

    current_time = time.time()
    config = get_dynamic_config()

    # Check cooldown period
    if current_time - _last_adjustment_time < _adjustment_cooldown:
        return False

    # Skip if auto-tuning is disabled
    if not config.get("auto_tuning_enabled", True):
        return False

    adjustments = {}
    reasons = []

    # Performance-based adjustments
    success_rate = performance_metrics.get("success_rate", 1.0)
    response_time_ms = performance_metrics.get("avg_processing_time_ms", 0)
    memory_usage_mb = performance_metrics.get("memory_usage_mb", 0)

    # Browser pool adjustments
    if success_rate < 0.85 and config["browser_pool_size"] < 5:
        adjustments["browser_pool_size"] = min(5, config["browser_pool_size"] + 1)
        reasons.append("Low success rate - increasing browser pool")
    elif success_rate > 0.95 and config["browser_pool_size"] > 2:
        adjustments["browser_pool_size"] = max(2, config["browser_pool_size"] - 1)
        reasons.append("High success rate - optimizing browser pool")

    # Timeout adjustments based on response time
    if response_time_ms > 10000:  # Slow responses
        adjustments["page_timeout"] = min(90000, config["page_timeout"] + 10000)
        adjustments["navigation_timeout"] = min(
            180000, config["navigation_timeout"] + 15000
        )
        reasons.append("Slow response times - increasing timeouts")
    elif response_time_ms < 3000 and config["page_timeout"] > 20000:  # Fast responses
        adjustments["page_timeout"] = max(20000, config["page_timeout"] - 5000)
        adjustments["navigation_timeout"] = max(
            30000, config["navigation_timeout"] - 10000
        )
        reasons.append("Fast response times - optimizing timeouts")

    # Memory optimization adjustments
    if memory_usage_mb > 400:
        adjustments["memory_cleanup_interval"] = max(
            5, config["memory_cleanup_interval"] - 2
        )
        adjustments["gc_threshold"] = max(50, config["gc_threshold"] - 20)
        reasons.append("High memory usage - increasing cleanup frequency")
    elif memory_usage_mb < 150:
        adjustments["memory_cleanup_interval"] = min(
            30, config["memory_cleanup_interval"] + 3
        )
        adjustments["gc_threshold"] = min(200, config["gc_threshold"] + 30)
        reasons.append("Low memory usage - reducing cleanup overhead")

    # Circuit breaker adjustments
    circuit_failures = performance_metrics.get("circuit_breaker_failures", 0)
    if circuit_failures > 0 and config["circuit_breaker_threshold"] > 2:
        adjustments["circuit_breaker_threshold"] = max(
            2, config["circuit_breaker_threshold"] - 1
        )
        reasons.append("Circuit breaker activations - tightening threshold")

    # Apply adjustments if any were made
    if adjustments:
        reason = "; ".join(reasons)
        return update_dynamic_config(adjustments, f"Auto-tuning: {reason}")

    return False


def adjust_config_for_scaling(scaling_decision: Dict[str, Any]) -> bool:
    """
    Adjust configuration based on scaling decisions.

    Args:
        scaling_decision: Scaling decision from adaptive engine

    Returns:
        bool: True if adjustments were made, False otherwise
    """
    config = get_dynamic_config()
    adjustments = {}
    reasons = []

    action = scaling_decision.get("action", "no_change")
    confidence = scaling_decision.get("confidence", 0.0)
    current_workers = scaling_decision.get("current_workers", 1)

    # Scaling-based configuration adjustments
    if action == "scale_up" and confidence > 0.7:
        # When scaling up with high confidence, optimize for performance
        if config["browser_pool_size"] < 4:
            adjustments["browser_pool_size"] = min(4, config["browser_pool_size"] + 1)
            reasons.append("Scale-up: Increasing browser pool for performance")

        # Adjust worker increment for future scaling
        if current_workers > 10:
            adjustments["worker_scale_increment"] = min(
                5, config["worker_scale_increment"] + 1
            )
            reasons.append("Scale-up: Increasing scale increment for efficiency")

    elif action == "scale_down" and confidence > 0.7:
        # When scaling down, optimize for resource conservation
        if config["browser_pool_size"] > 2:
            adjustments["browser_pool_size"] = max(2, config["browser_pool_size"] - 1)
            reasons.append("Scale-down: Reducing browser pool for efficiency")

        # Increase memory cleanup frequency
        adjustments["memory_cleanup_interval"] = max(
            5, config["memory_cleanup_interval"] - 1
        )
        reasons.append("Scale-down: Increasing cleanup for resource conservation")

    # Apply adjustments if any were made
    if adjustments:
        reason = "; ".join(reasons)
        return update_dynamic_config(adjustments, f"Scaling adjustment: {reason}")

    return False


def get_config_for_optimization() -> Dict[str, Any]:
    """
    Get configuration values formatted for the existing optimization functions.

    Returns:
        Dictionary compatible with existing optimization code
    """
    config = get_dynamic_config()

    # Map to existing OptimizationConfig format
    optimization_config = {
        "BROWSER_POOL_SIZE": config["browser_pool_size"],
        "BROWSER_REUSE_THRESHOLD": config["browser_reuse_threshold"],
        "CIRCUIT_BREAKER_THRESHOLD": config["circuit_breaker_threshold"],
        "BROWSER_LAUNCH_DELAY": config["browser_launch_delay"],
        "RESOURCE_FILTERING_ENABLED": config["resource_filtering_enabled"],
        "BLOCKED_RESOURCE_TYPES": config["blocked_resource_types"],
        "WHITELIST_DOMAINS": config["whitelist_domains"],
        "MEMORY_CLEANUP_INTERVAL": config["memory_cleanup_interval"],
        "MEMORY_OPTIMIZATION_ENABLED": config["memory_optimization_enabled"],
        "GC_THRESHOLD": config["gc_threshold"],
        "PAGE_TIMEOUT": config["page_timeout"],
        "NAVIGATION_TIMEOUT": config["navigation_timeout"],
        "REQUEST_TIMEOUT": config["request_timeout"],
    }

    return optimization_config


def apply_dynamic_config_to_optimization() -> None:
    """
    Apply current dynamic configuration to the existing OptimizationConfig.
    This allows existing optimization functions to use dynamic values.
    """
    config = get_config_for_optimization()

    # Update OptimizationConfig class attributes
    for key, value in config.items():
        if hasattr(OptimizationConfig, key):
            setattr(OptimizationConfig, key, value)

    print("🔧 Applied dynamic configuration to OptimizationConfig")


def get_config_status() -> Dict[str, Any]:
    """
    Get comprehensive status of the configuration manager.

    Returns:
        Dictionary with current configuration status
    """
    current_time = time.time()
    config = get_dynamic_config()

    status = {
        "timestamp": current_time,
        "datetime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(current_time)),
        "config_loaded": bool(_dynamic_config),
        "auto_tuning_enabled": config.get("auto_tuning_enabled", False),
        "total_parameters": len(config),
        "adjustments_made": len(_config_history),
        "last_adjustment_time": _last_adjustment_time,
        "time_since_last_adjustment": current_time - _last_adjustment_time,
        "cooldown_remaining": max(
            0, _adjustment_cooldown - (current_time - _last_adjustment_time)
        ),
        "current_config": config.copy(),
    }

    # Add recent adjustment history
    if _config_history:
        status["recent_adjustments"] = [
            {
                "timestamp": adj.timestamp,
                "datetime": adj.datetime_str,
                "reason": adj.adjustment_reason,
                "parameters": list(adj.config_values.keys()),
            }
            for adj in _config_history[-5:]
        ]

    return status


def print_config_status() -> None:
    """Print current configuration status to console."""
    status = get_config_status()

    print("\n" + "=" * 80)
    print("DYNAMIC CONFIGURATION MANAGER STATUS")
    print("=" * 80)

    print(f"Configuration Loaded: {'✅' if status['config_loaded'] else '❌'}")
    print(
        f"Auto-tuning: {'✅ Enabled' if status['auto_tuning_enabled'] else '❌ Disabled'}"
    )
    print(f"Total Parameters: {status['total_parameters']}")
    print(f"Adjustments Made: {status['adjustments_made']}")
    print(f"Time Since Last Adjustment: {status['time_since_last_adjustment']:.1f}s")

    if status.get("cooldown_remaining", 0) > 0:
        print(f"Cooldown Remaining: {status['cooldown_remaining']:.1f}s")

    # Show key configuration values
    config = status["current_config"]
    print("\nKey Configuration Values:")
    print(f"  Browser Pool Size: {config.get('browser_pool_size', 'N/A')}")
    print(f"  Max Workers: {config.get('max_workers', 'N/A')}")
    print(f"  Page Timeout: {config.get('page_timeout', 'N/A')}ms")
    print(f"  Memory Cleanup Interval: {config.get('memory_cleanup_interval', 'N/A')}s")
    print(f"  Auto-tuning Aggressiveness: {config.get('tuning_aggressiveness', 'N/A')}")

    # Show recent adjustments
    if status.get("recent_adjustments"):
        print("\nRecent Adjustments:")
        for adj in status["recent_adjustments"][-3:]:
            print(
                f"  📝 {adj['datetime']}: {adj['reason']} ({len(adj['parameters'])} params)"
            )


def save_config_to_file(filepath: str = "config/dynamic_config.json") -> bool:
    """
    Save current dynamic configuration to file.

    Args:
        filepath: Path to save configuration file

    Returns:
        bool: True if save was successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        # Prepare data for saving
        save_data = {
            "timestamp": time.time(),
            "datetime": time.strftime("%Y-%m-%d %H:%M:%S"),
            "config": get_dynamic_config(),
            "adjustment_history": [
                {
                    "timestamp": adj.timestamp,
                    "datetime": adj.datetime_str,
                    "config_values": adj.config_values,
                    "reason": adj.adjustment_reason,
                }
                for adj in _config_history
            ],
        }

        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2, default=str)

        print(f"💾 Configuration saved to: {filepath}")
        return True

    except Exception as e:
        print(f"❌ Failed to save configuration: {e}")
        return False


def load_config_from_file(filepath: str = "config/dynamic_config.json") -> bool:
    """
    Load dynamic configuration from file.

    Args:
        filepath: Path to load configuration file from

    Returns:
        bool: True if load was successful, False otherwise
    """
    global _dynamic_config, _config_history

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Load configuration
        loaded_config = data.get("config", {})
        validation_result = validate_config_updates(loaded_config)

        if validation_result["valid"]:
            _dynamic_config = loaded_config
            print(f"📂 Configuration loaded from: {filepath}")
            print(f"   Parameters loaded: {len(_dynamic_config)}")
            return True
        else:
            print(f"❌ Invalid configuration in file: {validation_result['error']}")
            return False

    except FileNotFoundError:
        print(f"⚠️  Configuration file not found: {filepath}")
        print("   Using default configuration")
        initialize_dynamic_config()
        return False
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False


# Initialize the configuration manager
def initialize_configuration_manager() -> Dict[str, Any]:
    """Initialize the dynamic configuration manager."""

    result = initialize_dynamic_config()

    print("🎯 Dynamic Configuration Manager ready")
    print(f"   Parameters: {len(result)} settings managed")
    print(
        f"   Auto-tuning: {'enabled' if result.get('auto_tuning_enabled') else 'disabled'}"
    )

    return {
        "status": "initialized",
        "parameter_count": len(result),
        "auto_tuning_enabled": result.get("auto_tuning_enabled", False),
    }
