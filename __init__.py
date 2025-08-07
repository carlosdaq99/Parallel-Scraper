"""
Parallel scraper package for ObjectARX documentation extraction.

This package provides a modular, async-based web scraping system with:
- Comprehensive timeout protection to prevent hanging
- Semaphore-controlled concurrency for resource management
- Detailed logging for debugging and monitoring
- Robust error handling and retry mechanisms
"""

from .data_structures import NodeInfo, Task, ParallelWorkerContext
from .logging_setup import setup_logging

__version__ = "1.0.0"
__author__ = "Parallel Scraper Team"

# Export main components
__all__ = ["NodeInfo", "Task", "ParallelWorkerContext", "setup_logging"]
