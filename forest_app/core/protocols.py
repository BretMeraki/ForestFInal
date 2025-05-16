<<<<<<< HEAD
from typing import Protocol, List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

=======
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol
from uuid import UUID


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
class HTANodeProtocol(Protocol):
    node_id: UUID
    parent_id: Optional[UUID]
    title: str
    description: str
<<<<<<< HEAD
    children: List['HTANodeProtocol']
=======
    children: List["HTANodeProtocol"]
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    completion_status: float  # 0.0 to 1.0
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any]
<<<<<<< HEAD
    
    def add_child(self, node: 'HTANodeProtocol') -> None: ...
    def remove_child(self, node_id: UUID) -> None: ...
    def update_completion(self) -> None: ...
    def get_frontier_tasks(self) -> List['HTANodeProtocol']: ...

class HTATreeProtocol(Protocol):
    root: HTANodeProtocol
    
=======

    def add_child(self, node: "HTANodeProtocol") -> None: ...
    def remove_child(self, node_id: UUID) -> None: ...
    def update_completion(self) -> None: ...
    def get_frontier_tasks(self) -> List["HTANodeProtocol"]: ...


class HTATreeProtocol(Protocol):
    root: HTANodeProtocol

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    def get_node(self, node_id: UUID) -> Optional[HTANodeProtocol]: ...
    def update_node(self, node_id: UUID, updates: Dict[str, Any]) -> None: ...
    def propagate_completion(self, node_id: UUID) -> None: ...
    def get_all_frontier_tasks(self) -> List[HTANodeProtocol]: ...

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
class TaskEngineProtocol(Protocol):
    def generate_task_batch(self, context: Dict[str, Any]) -> List[HTANodeProtocol]: ...
    def recommend_next_tasks(self, count: int = 3) -> List[HTANodeProtocol]: ...
    def update_task_status(self, task_id: UUID, completion: float) -> None: ...

<<<<<<< HEAD
class SemanticMemoryProtocol(Protocol):
    def store_milestone(self, node_id: UUID, description: str, impact: float) -> None: ...
    def store_reflection(self, reflection_type: str, content: str, emotion: Optional[str] = None) -> None: ...
    def get_relevant_memories(self, context: str, limit: int = 5) -> List[Dict[str, Any]]: ...
    def update_context(self, new_context: Dict[str, Any]) -> None: ... 
=======

class SemanticMemoryProtocol(Protocol):
    def store_milestone(
        self, node_id: UUID, description: str, impact: float
    ) -> None: ...
    def store_reflection(
        self, reflection_type: str, content: str, emotion: Optional[str] = None
    ) -> None: ...
    def get_relevant_memories(
        self, context: str, limit: int = 5
    ) -> List[Dict[str, Any]]: ...
    def update_context(self, new_context: Dict[str, Any]) -> None: ...
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
