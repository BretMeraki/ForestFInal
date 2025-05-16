"""
Base interface for SemanticMemoryManager to avoid circular imports.
"""
<<<<<<< HEAD
from typing import Any, Dict, List, Optional
from datetime import datetime

class SemanticMemoryManagerBase:
    """Interface for semantic memory management."""
    async def store_memory(self, event_type: str, content: str, metadata: Optional[Dict[str, Any]] = None, importance: float = 0.5) -> Dict[str, Any]:
        raise NotImplementedError

    async def query_memories(self, query: str, k: int = 5, filter_event_type: Optional[str] = None) -> List[Dict[str, Any]]:
=======

from typing import Any, Dict, List, Optional


class SemanticMemoryManagerBase:
    """Interface for semantic memory management."""

    async def store_memory(
        self,
        event_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
    ) -> Dict[str, Any]:
        raise NotImplementedError

    async def query_memories(
        self, query: str, k: int = 5, filter_event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        raise NotImplementedError

    def get_recent_memories(self, n: int = 10) -> List[Dict[str, Any]]:
        raise NotImplementedError
