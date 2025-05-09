"""
Extended reflection processor with additional logging for concurrency testing.
This implements a custom processor wrapper to log request ID and user data.
"""

import logging
import uuid
import inspect
from typing import Dict, Any, Optional
from functools import wraps

from forest_app.core.processors.reflection_processor import ReflectionProcessor
from forest_app.snapshot.snapshot import MemorySnapshot

logger = logging.getLogger(__name__)

def log_method_with_request_id(func):
    """Decorator to log function calls with request IDs and user data."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        # Generate a request ID if not provided
        request_id = kwargs.get("request_id", str(uuid.uuid4())[:8])
        
        # Extract user ID from args or kwargs
        user_id = None
        if 'user_input' in kwargs and isinstance(kwargs['user_input'], str):
            user_data = kwargs['user_input'][:20]  # First 20 chars of input
        else:
            user_data = "unknown"
            
        # Try to get user_id from snapshot if available
        if 'snapshot' in kwargs and hasattr(kwargs['snapshot'], 'user_id'):
            user_id = kwargs['snapshot'].user_id
        
        # Log entry with request ID, engine ID, and user data
        engine_id = id(self)
        logger.info(f"[REQ-{request_id}] Engine {self.__class__.__name__}[{engine_id}] processing for user data: '{user_data}'")
        
        # Execute the original method
        result = await func(self, *args, **kwargs)
        
        # Log completion
        logger.info(f"[REQ-{request_id}] Engine {self.__class__.__name__}[{engine_id}] completed processing")
        
        return result
    return wrapper

class LoggingReflectionProcessor(ReflectionProcessor):
    """Reflection processor with enhanced logging for concurrency testing."""
    
    @log_method_with_request_id
    async def process(self, user_input: str, snapshot: MemorySnapshot, request_id: str = None) -> Dict[str, Any]:
        """Process user reflection with request ID tracking."""
        return await super().process(user_input, snapshot)
    
    def __str__(self):
        return f"LoggingReflectionProcessor[{id(self)}]"
