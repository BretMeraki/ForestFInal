"""
Forest App Types Module

This module contains shared type definitions to avoid circular imports.
"""

<<<<<<< HEAD
from typing import List, Dict, Any, Optional, TypeVar, Protocol

class HTANodeProtocol(Protocol):
    """Protocol defining the interface for HTANode."""
=======
from typing import Any, Dict, List, Optional, Protocol


class HTANodeProtocol(Protocol):
    """Protocol defining the interface for HTANode."""

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    id: str
    title: str
    description: str
    status: str
    priority: float
    magnitude: float
    is_milestone: bool
    depends_on: List[str]
    estimated_energy: str
    estimated_time: str
<<<<<<< HEAD
    children: List['HTANodeProtocol']
    linked_tasks: List[str]

class HTATreeProtocol(Protocol):
    """Protocol defining the interface for HTATree."""
    root: Optional[HTANodeProtocol]
=======
    children: List["HTANodeProtocol"]
    linked_tasks: List[str]


class HTATreeProtocol(Protocol):
    """Protocol defining the interface for HTATree."""

    root: Optional[HTANodeProtocol]

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    def get_node_map(self) -> Dict[str, HTANodeProtocol]: ...
    def get_node_depth(self, node_id: str) -> int: ...
    def flatten_tree(self) -> List[HTANodeProtocol]: ...

<<<<<<< HEAD
class SemanticMemoryProtocol(Protocol):
    """Protocol defining the interface for SemanticMemoryManager."""
    async def store_memory(self, event_type: str, content: str, metadata: Dict[str, Any], importance: float = 0.5) -> Dict[str, Any]: ...
    async def query_memories(self, query: str, k: int = 5, event_types: Optional[List[str]] = None, time_window_days: Optional[int] = None) -> List[Dict[str, Any]]: ...
    async def update_memory_stats(self, memory_id: str, access_count: int = 1) -> bool: ...
=======

class SemanticMemoryProtocol(Protocol):
    """Protocol defining the interface for SemanticMemoryManager."""

    async def store_memory(
        self,
        event_type: str,
        content: str,
        metadata: Dict[str, Any],
        importance: float = 0.5,
    ) -> Dict[str, Any]: ...
    async def query_memories(
        self,
        query: str,
        k: int = 5,
        event_types: Optional[List[str]] = None,
        time_window_days: Optional[int] = None,
    ) -> List[Dict[str, Any]]: ...
    async def update_memory_stats(
        self, memory_id: str, access_count: int = 1
    ) -> bool: ...
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    async def get_recent_memories(self, limit: int = 5) -> List[Dict[str, Any]]: ...
    async def extract_themes(self, memories: List[Dict[str, Any]]) -> List[str]: ...
    async def get_memory_stats(self) -> Dict[str, Any]: ...

<<<<<<< HEAD
# Type aliases for common types
MemoryDict = Dict[str, Any]
TaskDict = Dict[str, Any]
SnapshotDict = Dict[str, Any] 
=======

# Type aliases for common types
MemoryDict = Dict[str, Any]
TaskDict = Dict[str, Any]
SnapshotDict = Dict[str, Any]
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
