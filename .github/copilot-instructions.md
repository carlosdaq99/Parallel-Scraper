# Parallel Scraper - AI Agent Instructions

## Architecture Overview

This is a **high-performance parallel web scraper** designed to extract ObjectARX documentation structure from Autodesk Help pages. The system uses **adaptive scaling** (20-100 workers) with **proactive optimization** for maximum throughput within safe resource limits.

### Key Components & Data Flow

1. **Entry Point**: `main_self_contained.py` - Single unified script containing the complete scraping system
2. **Adaptive Scaling Engine**: `adaptive_scaling_engine.py` - Performance-based worker scaling with trend analysis
3. **Worker System**: `worker.py` + `data_structures.py` - Parallel task processing with queue management
4. **DOM Navigation**: `dom_utils.py` - Playwright-based tree traversal for Autodesk documentation
5. **Optimization Layer**: `optimization_utils.py` + `advanced_optimization_utils.py` - Browser reuse, resource filtering, memory management
6. **Real-time Monitoring**: `real_time_monitor.py` - Live dashboard showing performance metrics and scaling decisions

### Critical Architectural Patterns

**Function-Based Design**: This project deliberately uses function-based architecture over class hierarchies for simplicity and async compatibility. When adding features, prefer functions over classes.

**Self-Contained Philosophy**: All dependencies are internal - no external packages beyond Playwright. Maintain this isolation when adding features.

**Proactive Scaling**: The system starts with 50 workers and scales 20-100 based on performance metrics. Worker scaling decisions use the `make_scaling_decision_simple()` function with comprehensive metrics.

## Developer Workflows

### Running the System
```powershell
# Primary execution - everything is self-contained
python main_self_contained.py

# Run comprehensive validation tests
python tests/test_complete_validation.py

# Test individual components
python tests/test_adaptive_scaling_engine.py
```

### Testing Patterns
- Tests are in `tests/` directory with descriptive names like `test_complete_validation.py`
- Each test validates specific scaling issues or component functionality
- Use `python tests/test_*.py` for individual component testing
- The system includes extensive mock testing for scaling decisions

### Configuration System
- **Single Source**: All config is in `config.py` with `ScraperConfig` and `OptimizationConfig` classes
- **Environment Variables**: All settings support env var overrides (e.g., `SCRAPER_MAX_WORKERS`)
- **Proactive Defaults**: Optimized for high throughput (100 max workers, 6 browser pool, aggressive scaling)

## Critical Integration Points

### Adaptive Scaling Synchronization
The scaling engine requires **synchronized worker count tracking**:
```python
# CRITICAL: Always update both global state and scaling engine
set_current_worker_count(new_count)  # Updates scaling engine
_adaptive_workers = new_count         # Updates global state
```

### Browser Pool Management
- **6-browser pool** supports up to 102 workers (17 workers per browser optimal ratio)
- Browser reuse pattern in `optimization_utils.py` with circuit breaker protection
- Resource filtering blocks images/media/fonts for 50-70% faster page loads

### Performance Metrics Flow
```
worker.py → performance_history → adaptive_scaling_engine.py → scaling_decision → main_self_contained.py → worker_count_update
```

## Project-Specific Conventions

### Error Handling Pattern
```python
try:
    # Operation with comprehensive fallback
    result = await operation()
except Exception as e:
    logger.warning(f"Operation failed: {e}")
    # Always provide fallback behavior, never hard fail
    return default_result
```

### Async Function Signatures
- Use `async def` for all I/O operations
- Worker functions take `(context, browser, worker_id)` parameters
- Scaling functions are synchronous but called from async context

### Metrics Collection
- Performance metrics use `PerformanceMetrics` dataclass from `adaptive_scaling_engine.py`
- Real-time dashboard updates every 30 seconds via `DashboardMetrics`
- All metrics include timestamp and optional availability flags

### Resource Management
- Always use `async with async_playwright()` context managers
- Browser pages created via `create_browser_page()` utility with timeout protection
- Memory cleanup happens automatically via `optimization_utils.py` with GC intervals

## Development Guidelines

### Adding New Features
1. Check if `config.py` needs new settings with env var support
2. Add to appropriate module following function-based pattern  
3. Update metrics collection if performance-related
4. Add validation test in `tests/` directory
5. Update real-time dashboard if user-visible

### Scaling Engine Modifications
- Scaling decisions use `make_scaling_decision_simple(metrics_dict)` 
- Worker count changes must call `set_current_worker_count()`
- Test scaling behavior with mock metrics in `tests/test_adaptive_scaling_engine.py`

### DOM Operations
- Use `dom_utils.py` functions for all Playwright operations
- Target folder navigation via `find_target_folder_dom_async()`
- Always include timeout protection and retry logic

### Performance Optimization
- Browser operations use pooling from `optimization_utils.py`
- Resource filtering blocks non-essential content automatically
- Memory management includes aggressive cleanup every 100 operations
