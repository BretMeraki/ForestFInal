"""Helper functions and utilities for Enhanced HTA Service.

This module provides functionality for:
- Common operations shared across HTA components
- Format conversion and data transformation
- Error handling and validation utilities
- Performance optimization helpers

These utilities help maintain a consistent approach to common operations
and reduce code duplication across the service.
"""

<<<<<<< HEAD
import logging
import json
import time
import asyncio
from functools import wraps
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, Callable, Protocol, runtime_checkable
from uuid import UUID
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

T = TypeVar('T')
=======
import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from functools import wraps
from typing import (Any, Callable, Dict, Generic, Optional, Protocol, TypeVar,
                    Union, runtime_checkable)
from uuid import UUID

logger = logging.getLogger(__name__)

T = TypeVar("T")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)


def format_uuid(uuid_value: Union[UUID, str]) -> str:
    """Format a UUID object or string as a consistent string representation.
<<<<<<< HEAD
    
    Args:
        uuid_value: UUID object or string to format
        
=======

    Args:
        uuid_value: UUID object or string to format

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    Returns:
        Formatted UUID string
    """
    if uuid_value is None:
        return None
    if isinstance(uuid_value, UUID):
        return str(uuid_value)
    return str(uuid_value)


def safe_serialize(obj: Any) -> Dict[str, Any]:
    """Safely serialize an object to a dictionary for storage or transmission.
<<<<<<< HEAD
    
    Args:
        obj: Object to serialize
        
    Returns:
        Dictionary representation of the object
    """
    if hasattr(obj, 'model_dump'):
        # Pydantic v2
        return obj.model_dump()
    elif hasattr(obj, 'dict'):
        # Pydantic v1
        return obj.dict()
    elif hasattr(obj, '__dict__'):
        # Regular object
        result = {}
        for key, value in obj.__dict__.items():
            if not key.startswith('_'):
=======

    Args:
        obj: Object to serialize

    Returns:
        Dictionary representation of the object
    """
    if hasattr(obj, "model_dump"):
        # Pydantic v2
        return obj.model_dump()
    elif hasattr(obj, "dict"):
        # Pydantic v1
        return obj.dict()
    elif hasattr(obj, "__dict__"):
        # Regular object
        result = {}
        for key, value in obj.__dict__.items():
            if not key.startswith("_"):
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                if isinstance(value, (str, int, float, bool, type(None))):
                    result[key] = value
                else:
                    try:
                        # Try simple JSON serialization
                        json.dumps({key: value})
                        result[key] = value
                    except TypeError:
                        # Fall back to string representation
                        result[key] = str(value)
        return result
    return {}


def get_now() -> datetime:
    """Get current datetime with UTC timezone.
<<<<<<< HEAD
    
    This utility ensures consistent timestamp formatting across the application,
    helping maintain data integrity in logs, events, and database records.
    
=======

    This utility ensures consistent timestamp formatting across the application,
    helping maintain data integrity in logs, events, and database records.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    Returns:
        Current datetime with UTC timezone
    """
    return datetime.now(timezone.utc)


def measure_execution_time(func: Callable) -> Callable:
    """Decorator to measure and log execution time of functions.
<<<<<<< HEAD
    
    This helps identify performance bottlenecks and track execution metrics
    for optimization efforts.
    
    Args:
        func: The function to measure
        
    Returns:
        Wrapped function with timing measurement
    """
=======

    This helps identify performance bottlenecks and track execution metrics
    for optimization efforts.

    Args:
        func: The function to measure

    Returns:
        Wrapped function with timing measurement
    """

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result
<<<<<<< HEAD
        
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")
        return result
<<<<<<< HEAD
        
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def validate_uuid(uuid_str: str) -> Optional[UUID]:
    """Validate and convert a string to UUID.
<<<<<<< HEAD
    
    Safely handles UUID validation, returning None for invalid UUIDs
    instead of raising exceptions.
    
    Args:
        uuid_str: String to validate as UUID
        
=======

    Safely handles UUID validation, returning None for invalid UUIDs
    instead of raising exceptions.

    Args:
        uuid_str: String to validate as UUID

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    Returns:
        UUID object or None if invalid
    """
    if not uuid_str:
        return None
<<<<<<< HEAD
        
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    try:
        return UUID(uuid_str)
    except (ValueError, AttributeError, TypeError):
        logger.warning(f"Invalid UUID format: {uuid_str}")
        return None


@runtime_checkable
class JsonSerializable(Protocol):
    """Protocol for objects that can be serialized to JSON.
<<<<<<< HEAD
    
    This protocol allows for duck typing with JSON serializable objects.
    Classes don't need to explicitly inherit from this protocol.
    """
    def __dict__(self) -> Dict[str, Any]: ...


def truncate_string(s: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate a string to a maximum length with a suffix.
    
    Useful for logs and error messages to prevent excessive output.
    
=======

    This protocol allows for duck typing with JSON serializable objects.
    Classes don't need to explicitly inherit from this protocol.
    """

    def __dict__(self) -> Dict[str, Any]: ...


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate a string to a maximum length with a suffix.

    Useful for logs and error messages to prevent excessive output.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    Args:
        s: String to truncate
        max_length: Maximum length including suffix
        suffix: String to append when truncated
<<<<<<< HEAD
        
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    Returns:
        Truncated string with suffix if needed
    """
    if not s or len(s) <= max_length:
        return s
<<<<<<< HEAD
    return s[:max_length - len(suffix)] + suffix


def retry_operation(max_attempts: int = 3, delay_seconds: float = 1.0, backoff_factor: float = 2.0):
    """Decorator for retrying operations with exponential backoff.
    
    This helps handle transient failures in external services or network operations,
    creating more resilient code.
    
=======
    return s[: max_length - len(suffix)] + suffix


def retry_operation(
    max_attempts: int = 3, delay_seconds: float = 1.0, backoff_factor: float = 2.0
):
    """Decorator for retrying operations with exponential backoff.

    This helps handle transient failures in external services or network operations,
    creating more resilient code.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    Args:
        max_attempts: Maximum number of retry attempts
        delay_seconds: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each subsequent retry
<<<<<<< HEAD
        
    Returns:
        Decorator function that adds retry logic
    """
=======

    Returns:
        Decorator function that adds retry logic
    """

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay_seconds
<<<<<<< HEAD
            
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            for attempt in range(max_attempts):
                try:
                    if attempt > 0:
                        logger.debug(f"Retry attempt {attempt} for {func.__name__}")
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
<<<<<<< HEAD
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}")
                    
                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor
                        
            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_exception
            
=======
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}"
                    )

                    if attempt < max_attempts - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff_factor

            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_exception

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay_seconds
<<<<<<< HEAD
            
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            for attempt in range(max_attempts):
                try:
                    if attempt > 0:
                        logger.debug(f"Retry attempt {attempt} for {func.__name__}")
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
<<<<<<< HEAD
                    logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}")
                    
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                        
            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_exception
            
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
        
=======
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed for {func.__name__}: {e}"
                    )

                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff_factor

            logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            raise last_exception

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    return decorator


class Result(Generic[T]):
    """A result object that can represent success or failure.
<<<<<<< HEAD
    
    This utility helps with consistent error handling and allows for
    clean propagation of errors and successful results.
    """
    
    def __init__(self, value: Optional[T] = None, error: Optional[str] = None):
        """Initialize a result object.
        
=======

    This utility helps with consistent error handling and allows for
    clean propagation of errors and successful results.
    """

    def __init__(self, value: Optional[T] = None, error: Optional[str] = None):
        """Initialize a result object.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Args:
            value: The success value (if successful)
            error: The error message (if failed)
        """
        self.value = value
        self.error = error
        self.success = error is None
<<<<<<< HEAD
    
    @classmethod
    def ok(cls, value: T) -> 'Result[T]':
        """Create a successful result.
        
        Args:
            value: The success value
            
=======

    @classmethod
    def ok(cls, value: T) -> "Result[T]":
        """Create a successful result.

        Args:
            value: The success value

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            A successful Result object
        """
        return cls(value=value)
<<<<<<< HEAD
    
    @classmethod
    def fail(cls, error: str) -> 'Result[T]':
        """Create a failed result.
        
        Args:
            error: The error message
            
=======

    @classmethod
    def fail(cls, error: str) -> "Result[T]":
        """Create a failed result.

        Args:
            error: The error message

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            A failed Result object
        """
        return cls(error=error)
<<<<<<< HEAD
    
    def __bool__(self) -> bool:
        """Allow using the result in boolean context.
        
=======

    def __bool__(self) -> bool:
        """Allow using the result in boolean context.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            True if successful, False otherwise
        """
        return self.success
