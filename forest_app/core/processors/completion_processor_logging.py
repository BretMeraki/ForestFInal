"""
Extended completion processor with additional logging for concurrency testing.
This implements a custom processor wrapper to log request ID and task data.
"""

import logging
import uuid
from typing import Dict, Any, Optional
from functools import wraps

from forest_app.core.processors.completion_processor import CompletionProcessor
from forest_app.snapshot.snapshot import MemorySnapshot

logger = logging.getLogger(__name__)

def log_method_with_request_id(func):
    """Decorator to log function calls with request IDs and task data."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        # Generate a request ID if not provided
        request_id = kwargs.get("request_id", str(uuid.uuid4())[:8])
        
        # Extract task ID
        task_id = kwargs.get("task_id", "unknown")
        
        # Try to get user_id from snapshot if available
        user_id = "unknown"
        if 'snapshot' in kwargs and hasattr(kwargs['snapshot'], 'user_id'):
            user_id = kwargs['snapshot'].user_id
        
        # Log entry with request ID, engine ID, and task data
        engine_id = id(self)
        logger.info(f"[REQ-{request_id}] Engine {self.__class__.__name__}[{engine_id}] processing task: '{task_id}' for user: {user_id}")
        
        # Execute the original method
        result = await func(self, *args, **kwargs)
        
        # Log completion
        logger.info(f"[REQ-{request_id}] Engine {self.__class__.__name__}[{engine_id}] completed processing task: '{task_id}'")
        
        return result
    return wrapper

class LoggingCompletionProcessor(CompletionProcessor):
    """Completion processor with enhanced logging for concurrency testing."""
    
    @log_method_with_request_id
    async def process(self, task_id: str, success: bool, snapshot: MemorySnapshot, 
                    db=None, task_logger=None, request_id: str = None) -> Dict[str, Any]:
        """Process task completion with request ID tracking."""
        return await super().process(task_id, success, snapshot, db, task_logger)
    
    def __str__(self):
        return f"LoggingCompletionProcessor[{id(self)}]"
