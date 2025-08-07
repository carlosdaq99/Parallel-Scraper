#!/usr/bin/env python3
"""
Enhanced Error Handling - Level 2 upgrade for parallel_scraper.
Provides intelligent error handling and recovery for JavaScript-heavy sites.
"""

import asyncio
import time
import json
import traceback
from dataclasses import dataclass, asdict
from typing import Dict, Any, Callable
from enum import Enum
from pathlib import Path


class ErrorSeverity(Enum):
    """Error severity levels for intelligent handling."""

    IGNORE = 1  # Ignorable errors (404 on optional content)
    WARNING = 2  # Warning-level errors (slow responses)
    ERROR = 3  # Standard errors (network timeouts)
    CRITICAL = 4  # Critical errors (authentication failures)


class ErrorCategory(Enum):
    """Categories of errors for targeted handling."""

    NETWORK = "network"
    JAVASCRIPT = "javascript"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    PARSING = "parsing"
    BROWSER = "browser"
    UNKNOWN = "unknown"


@dataclass
class ErrorInfo:
    """Comprehensive error information."""

    category: ErrorCategory
    severity: ErrorSeverity
    message: str
    timestamp: float
    url: str = ""
    retry_count: int = 0
    stack_trace: str = ""
    context: Dict[str, Any] = None

    def __post_init__(self):
        if self.context is None:
            self.context = {}


class SmartErrorHandler:
    """
    Intelligent error handler for JavaScript-heavy sites.
    Provides non-intrusive error handling that can be added to existing code.
    """

    def __init__(self, max_error_history: int = 100):
        self.max_error_history = max_error_history
        self.error_history = []
        self.error_stats = {
            "total_errors": 0,
            "by_category": {cat.value: 0 for cat in ErrorCategory},
            "by_severity": {sev.name: 0 for sev in ErrorSeverity},
            "recovery_attempts": 0,
            "successful_recoveries": 0,
        }
        self.recovery_strategies = self._init_recovery_strategies()

    def _init_recovery_strategies(self) -> Dict[ErrorCategory, Callable]:
        """Initialize recovery strategies for different error types."""
        return {
            ErrorCategory.NETWORK: self._handle_network_error,
            ErrorCategory.JAVASCRIPT: self._handle_javascript_error,
            ErrorCategory.TIMEOUT: self._handle_timeout_error,
            ErrorCategory.BROWSER: self._handle_browser_error,
            ErrorCategory.PARSING: self._handle_parsing_error,
            ErrorCategory.AUTHENTICATION: self._handle_auth_error,
            ErrorCategory.UNKNOWN: self._handle_unknown_error,
        }

    def classify_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> ErrorInfo:
        """
        Classify an error and determine its severity and category.
        This is specifically tuned for JavaScript-heavy scraping.
        """
        error_msg = str(error).lower()

        # Network-related errors
        if any(
            keyword in error_msg
            for keyword in ["connection", "network", "dns", "ssl", "certificate"]
        ):
            category = ErrorCategory.NETWORK
            severity = ErrorSeverity.ERROR

        # JavaScript-specific errors
        elif any(
            keyword in error_msg
            for keyword in [
                "javascript",
                "js",
                "script",
                "evaluation failed",
                "page crashed",
            ]
        ):
            category = ErrorCategory.JAVASCRIPT
            severity = ErrorSeverity.ERROR

        # Timeout errors
        elif any(
            keyword in error_msg
            for keyword in ["timeout", "waiting", "deadline", "exceeded"]
        ):
            category = ErrorCategory.TIMEOUT
            severity = ErrorSeverity.WARNING

        # Browser/Playwright errors
        elif any(
            keyword in error_msg
            for keyword in ["browser", "page", "context", "playwright"]
        ):
            category = ErrorCategory.BROWSER
            severity = ErrorSeverity.ERROR

        # Authentication errors (even though user doesn't need these)
        elif any(
            keyword in error_msg
            for keyword in ["401", "403", "unauthorized", "forbidden", "authentication"]
        ):
            category = ErrorCategory.AUTHENTICATION
            severity = ErrorSeverity.CRITICAL

        # Parsing errors
        elif any(
            keyword in error_msg
            for keyword in ["parse", "json", "html", "xml", "syntax"]
        ):
            category = ErrorCategory.PARSING
            severity = ErrorSeverity.WARNING

        else:
            category = ErrorCategory.UNKNOWN
            severity = ErrorSeverity.ERROR

        return ErrorInfo(
            category=category,
            severity=severity,
            message=str(error),
            timestamp=time.time(),
            url=context.get("url", "") if context else "",
            stack_trace=traceback.format_exc(),
            context=context or {},
        )

    async def handle_error(
        self, error: Exception, context: Dict[str, Any] = None
    ) -> bool:
        """
        Handle an error intelligently and return whether recovery was successful.
        Returns True if the operation should be retried, False if it should fail.
        """
        error_info = self.classify_error(error, context)
        self._record_error(error_info)

        # Apply recovery strategy
        strategy = self.recovery_strategies.get(
            error_info.category, self._handle_unknown_error
        )

        try:
            self.error_stats["recovery_attempts"] += 1
            recovery_successful = await strategy(error_info, context)

            if recovery_successful:
                self.error_stats["successful_recoveries"] += 1
                return True

        except Exception as recovery_error:
            # Recovery failed
            print(f"Error recovery failed: {recovery_error}")

        return False

    def _record_error(self, error_info: ErrorInfo):
        """Record error for statistics and analysis."""
        self.error_history.append(error_info)

        # Keep history size manageable
        if len(self.error_history) > self.max_error_history:
            self.error_history.pop(0)

        # Update statistics
        self.error_stats["total_errors"] += 1
        self.error_stats["by_category"][error_info.category.value] += 1
        self.error_stats["by_severity"][error_info.severity.name] += 1

    async def _handle_network_error(
        self, error_info: ErrorInfo, context: Dict[str, Any]
    ) -> bool:
        """Handle network-related errors with smart retry."""
        if error_info.retry_count < 3:
            # Exponential backoff for network errors
            delay = 2**error_info.retry_count
            await asyncio.sleep(delay)
            return True  # Retry
        return False

    async def _handle_javascript_error(
        self, error_info: ErrorInfo, context: Dict[str, Any]
    ) -> bool:
        """Handle JavaScript errors - critical for JS-heavy sites."""
        if error_info.retry_count < 2:
            # For JS errors, wait longer and try to reload page
            await asyncio.sleep(5)
            return True  # Retry with page reload
        return False

    async def _handle_timeout_error(
        self, error_info: ErrorInfo, context: Dict[str, Any]
    ) -> bool:
        """Handle timeout errors with progressive delays."""
        if error_info.retry_count < 2:
            # Progressive timeout handling
            delay = 10 + (error_info.retry_count * 5)
            await asyncio.sleep(delay)
            return True  # Retry
        return False

    async def _handle_browser_error(
        self, error_info: ErrorInfo, context: Dict[str, Any]
    ) -> bool:
        """Handle browser-specific errors."""
        if error_info.retry_count < 1:
            # Browser errors usually need a fresh start
            await asyncio.sleep(3)
            return True  # Retry (will trigger browser restart in calling code)
        return False

    async def _handle_parsing_error(
        self, error_info: ErrorInfo, context: Dict[str, Any]
    ) -> bool:
        """Handle parsing errors - often recoverable."""
        if error_info.retry_count < 2:
            # Short delay for parsing errors
            await asyncio.sleep(1)
            return True  # Retry
        return False

    async def _handle_auth_error(
        self, error_info: ErrorInfo, context: Dict[str, Any]
    ) -> bool:
        """Handle authentication errors - don't retry."""
        # Since user doesn't need auth, these are probably false positives
        return False  # Don't retry auth errors

    async def _handle_unknown_error(
        self, error_info: ErrorInfo, context: Dict[str, Any]
    ) -> bool:
        """Handle unknown errors conservatively."""
        if error_info.retry_count < 1:
            await asyncio.sleep(2)
            return True  # Single retry
        return False

    def get_error_summary(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        recent_errors = [
            e for e in self.error_history if time.time() - e.timestamp < 3600
        ]  # Last hour

        recovery_rate = (
            self.error_stats["successful_recoveries"]
            / self.error_stats["recovery_attempts"]
            * 100
            if self.error_stats["recovery_attempts"] > 0
            else 0
        )

        return {
            "total_errors": self.error_stats["total_errors"],
            "recent_errors_count": len(recent_errors),
            "recovery_rate_percent": recovery_rate,
            "errors_by_category": self.error_stats["by_category"],
            "errors_by_severity": self.error_stats["by_severity"],
            "recent_error_trends": self._analyze_recent_trends(recent_errors),
        }

    def _analyze_recent_trends(self, recent_errors) -> Dict[str, Any]:
        """Analyze recent error trends."""
        if not recent_errors:
            return {"trend": "stable", "dominant_category": "none"}

        # Find most common recent category
        category_counts = {}
        for error in recent_errors:
            cat = error.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1

        dominant_category = max(category_counts.items(), key=lambda x: x[1])[0]

        return {
            "trend": "increasing" if len(recent_errors) > 5 else "stable",
            "dominant_category": dominant_category,
            "total_recent": len(recent_errors),
        }

    def save_error_report(self, filepath: Path):
        """Save comprehensive error report to file."""
        report = {
            "timestamp": time.time(),
            "summary": self.get_error_summary(),
            "recent_errors": [
                asdict(e) for e in self.error_history[-20:]
            ],  # Last 20 errors
        }

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2, default=str)


# Integration helpers for existing code


def create_error_handler() -> SmartErrorHandler:
    """Create a smart error handler for integration with existing code."""
    return SmartErrorHandler()


async def handle_with_smart_retry(
    func: Callable,
    error_handler: SmartErrorHandler,
    max_retries: int = 3,
    context: Dict[str, Any] = None,
):
    """
    Wrapper function to add smart error handling to any async function.

    Usage in existing code:
    # Instead of: result = await some_function(args)
    # Use: result = await handle_with_smart_retry(some_function, error_handler, context={'url': url})
    """
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as error:
            last_error = error

            if attempt < max_retries:
                should_retry = await error_handler.handle_error(error, context)
                if should_retry:
                    continue

            # If we get here, either we've exhausted retries or shouldn't retry
            break

    # Re-raise the last error if all retries failed
    raise last_error


# Example integration patterns:
"""
Integration with existing worker.py:

1. Add error handler to worker initialization:
   from error_handler import create_error_handler, handle_with_smart_retry
   
   error_handler = create_error_handler()

2. Wrap existing task processing:
   # Old: result = await process_page(page, url)
   # New: result = await handle_with_smart_retry(
   #          lambda: process_page(page, url), 
   #          error_handler, 
   #          context={'url': url}
   #      )

3. Get error statistics periodically:
   error_summary = error_handler.get_error_summary()
   print(f"Error recovery rate: {error_summary['recovery_rate_percent']:.1f}%")

4. Save error report at end:
   error_handler.save_error_report(Path("error_report.json"))

This provides intelligent error handling without changing your core logic!
"""
