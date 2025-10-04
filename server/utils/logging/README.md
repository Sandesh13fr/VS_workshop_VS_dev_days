# Logging System Documentation

## Overview
This document provides comprehensive guidance on using the standardized logging system implemented for the Python Flask Dog Shelter application.

## Table of Contents
1. [Logging Levels](#logging-levels)
2. [Log Format](#log-format)
3. [Configuration](#configuration)
4. [Usage Examples](#usage-examples)
5. [Performance Considerations](#performance-considerations)

## Logging Levels

The system implements five distinct logging levels, each with specific usage guidelines:

| Level | When to Use |
|-------|-------------|
| **DEBUG** | Detailed information, typically useful only for diagnosing problems. Include variable values, execution paths, and detailed flow information. |
| **INFO** | Confirmation that things are working as expected. Log application startup, important state changes, successful operations, and user actions. |
| **WARNING** | Indication that something unexpected happened, or may happen in the near future (e.g., disk space low). The application is still working as expected but requires attention. |
| **ERROR** | Due to a more serious problem, the application has not been able to perform a specific function. Failed API calls, database errors, or invalid inputs that prevent normal operation. |
| **CRITICAL** | A serious error indicating that the application itself may be unable to continue running. Database connection failures, critical system resource unavailability. |

## Log Format

Each log entry follows a consistent format with these components:

```
YYYY-MM-DD HH:MM:SS.mmm [LEVEL] [THREAD_ID] [MODULE_NAME] Message content
```

Example:
```
2025-10-04 10:15:23.456 [INFO] [123456] [dogshelter.api] Successfully retrieved 15 dogs
```

Components:
- **Timestamp**: ISO 8601 format (YYYY-MM-DD HH:MM:SS.mmm)
- **Log level**: DEBUG, INFO, WARNING, ERROR, or CRITICAL
- **Thread ID**: Numeric identifier of the executing thread
- **Module/component name**: Name of the logging component or module
- **Message content**: The actual log message

## Configuration

The logging system is highly configurable through the following mechanisms:

### 1. Configuration File

The system uses a JSON configuration file (`config/logging.json`) which can be modified to control:
- Global and per-module log levels
- Log formatters
- Output destinations
- Rotation settings

### 2. Runtime Configuration

Logging can be configured at runtime using:

```python
from utils.logging.config import configure_logging

configure_logging(
    config_file='path/to/config.json',  # Optional custom config file
    log_level='DEBUG',                  # Override default level
    log_file='path/to/log/file.log'     # Override default log file
)
```

### 3. Multiple Output Destinations

The system supports multiple output destinations:
- **Console**: Terminal output for development
- **File**: Regular log files with rotation
- **Error File**: Separate file for errors and above
- **Daily File**: Time-based rotation (new file each day)

### 4. Log Rotation Settings

File-based logs use rotation to prevent excessive disk usage:
- **Size-based rotation**: Files rotate when they reach a specified size (default: 10MB)
- **Count-based retention**: Keep a specified number of backup files (default: 10)
- **Time-based rotation**: Create a new file daily, weekly, etc.

## Usage Examples

### Basic Logger Initialization

```python
from utils.logging.config import get_logger

# Create a logger for the current module
logger = get_logger(__name__)

# Log at different levels
logger.debug("Detailed debugging information")
logger.info("Normal application flow information")
logger.warning("Something unexpected happened")
logger.error("Failed to perform an operation")
logger.critical("Application cannot continue")
```

### Logging Exceptions with Stack Traces

```python
try:
    # Attempt an operation
    result = perform_risky_operation()
except Exception as e:
    # Log the exception with full stack trace
    logger.exception(f"Operation failed: {e}")
    
    # Alternative method
    logger.error(f"Operation failed: {str(e)}", exc_info=True)
```

### Context-Enriched Logging

```python
from utils.logging.examples import ContextualLogger
from flask import request

# Create a logger with request context
ctx_logger = ContextualLogger.with_request(request, logger)
ctx_logger.info("Processing request")

# Result includes request details:
# 2025-10-04 10:15:23.456 [INFO] [123456] [dogshelter.api] Processing request [request_id=abc123 user_agent=Mozilla/5.0... remote_addr=127.0.0.1 path=/api/dogs]
```

### Performance-Optimized Logging

```python
# BAD: Always evaluates expensive operation
logger.debug(f"Complex data: {calculate_expensive_data()}")

# GOOD: Only evaluates if debug is enabled
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(f"Complex data: {calculate_expensive_data()}")

# ALSO GOOD: Using lazy % formatting
logger.debug("Complex data: %s", calculate_expensive_data())
```

## Performance Considerations

The logging system is designed for minimal impact in production environments:

1. **Level Filtering**: In production, set the log level to INFO or WARNING to reduce logging overhead.

2. **Lazy Evaluation**: Use `%s` formatting or conditional checks before calling expensive operations in log messages.

3. **Sampling**: For high-frequency events, use the `SampledLogger` to log only a percentage of events.

4. **Batching**: For high-volume logging, use the `BatchLogger` to combine multiple log messages.

5. **Asynchronous Logging**: For applications with strict performance requirements, consider configuring an asynchronous handler.

6. **Log Rotation**: Ensure logs are properly rotated to prevent disk space issues in long-running applications.

7. **Production Configuration**: Use a separate logging configuration for production that focuses on important events and minimizes overhead.