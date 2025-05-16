"""
Pydantic models for the Roadmap Manifest, which serves as the single source of truth
for the HTA (Hierarchical Task Analysis) tree and its evolution.

The Roadmap Manifest consists of:
- A collection of RoadmapSteps with dependencies
- Metadata about the overall tree structure
- Status tracking for steps that are synchronized with HTANodes

<<<<<<< HEAD
This module implements the [Manifest-HTA - Core] PRD requirement where the 
RoadmapManifest is the single source of truth for the HTA tree.
"""

from pydantic import BaseModel, Field, validator, ConfigDict, PrivateAttr
from datetime import datetime
from typing import List, Optional, Dict, Any, Literal, FrozenSet
from uuid import UUID, uuid4

=======
This module implements the [Manifest-HTA - Core] PRD requirement where the
RoadmapManifest is the single source of truth for the HTA tree.
"""

from datetime import datetime
from typing import Any, Dict, FrozenSet, List, Literal, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, validator

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

class RoadmapStep(BaseModel):
    """
    A single step in the roadmap manifest.
<<<<<<< HEAD
    
    Each step represents a task or action to be taken, and can have dependencies
    on other steps in the manifest. The status field is synchronized with the 
    corresponding HTANode's status.
    
    [LeanMVP - Simplify]: Focusing on essential fields for MVP, deferring estimated_duration and semantic_context.
    """
    # Core Identification & Content
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the step")
    title: str = Field(description="Title of the roadmap step")
    description: str = Field(description="Detailed description of the step")
    
    # Status Management
    status: Literal["pending", "in_progress", "completed", "deferred", "cancelled"] = "pending"
    
    # Dependency Management
    dependencies: FrozenSet[UUID] = Field(
        default_factory=frozenset, 
        description="Set of step IDs this step depends on"
    )

    @validator('dependencies', pre=True, always=True)
=======

    Each step represents a task or action to be taken, and can have dependencies
    on other steps in the manifest. The status field is synchronized with the
    corresponding HTANode's status.

    [LeanMVP - Simplify]: Focusing on essential fields for MVP, deferring estimated_duration and semantic_context.
    """

    # Core Identification & Content
    id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the step"
    )
    title: str = Field(description="Title of the roadmap step")
    description: str = Field(description="Detailed description of the step")

    # Status Management
    status: Literal["pending", "in_progress", "completed", "deferred", "cancelled"] = (
        "pending"
    )

    # Dependency Management
    dependencies: FrozenSet[UUID] = Field(
        default_factory=frozenset, description="Set of step IDs this step depends on"
    )

    @validator("dependencies", pre=True, always=True)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    def convert_dependencies(cls, v):
        if v is None:
            return frozenset()
        if isinstance(v, (list, set, tuple)):
            return frozenset(v)
        return v
<<<<<<< HEAD
    
    # Priority & Metadata
    priority: Literal["high", "medium", "low"] = "medium"
    hta_metadata: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Metadata about this step in the HTA structure (e.g., {\"is_major_phase\": true/false})"
    )
    
    # Audit Trail
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of step creation")
    # updated_at is set only on logical mutation (e.g., status change or adding steps), not on every validation.
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last step update")

    model_config = ConfigDict(
        frozen=True,
        extra='forbid',
        validate_assignment=False,
        populate_by_name=True,
        validate_default=False,
        arbitrary_types_allowed=True
=======

    # Priority & Metadata
    priority: Literal["high", "medium", "low"] = "medium"
    hta_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description='Metadata about this step in the HTA structure (e.g., {"is_major_phase": true/false})',
    )

    # Audit Trail
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of step creation"
    )
    # updated_at is set only on logical mutation (e.g., status change or adding steps), not on every validation.
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of last step update"
    )

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        validate_assignment=False,
        populate_by_name=True,
        validate_default=False,
        arbitrary_types_allowed=True,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    )


class RoadmapManifest(BaseModel):
    """
    The manifest that serves as the single source of truth for the HTA tree.
    Implements internal indexes and helper methods per PRD v4.0.
    """
<<<<<<< HEAD
    model_config = ConfigDict(
        extra='forbid',
        validate_assignment=False,
        populate_by_name=True,
        arbitrary_types_allowed=True
=======

    model_config = ConfigDict(
        extra="forbid",
        validate_assignment=False,
        populate_by_name=True,
        arbitrary_types_allowed=True,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    )
    # Internal indexes and caches as PrivateAttr (not serialized)
    _step_index: Dict[UUID, RoadmapStep] = PrivateAttr(default_factory=dict)
    _dependency_graph: Dict[UUID, FrozenSet[UUID]] = PrivateAttr(default_factory=dict)
    _reverse_dependency_graph: Dict[UUID, list] = PrivateAttr(default_factory=dict)
    _topological_sort_cache: list = PrivateAttr(default=None)

    """
    The manifest that serves as the single source of truth for the HTA tree.
    
    This model contains all the steps in the roadmap, with their dependencies and status.
    When the HTA tree is updated, the manifest is updated to reflect those changes,
    ensuring consistency between the two.
    
    [LeanMVP - Simplify]: Focusing on essential fields for MVP, deferring some context capture fields.
    """
    # Core Identification
<<<<<<< HEAD
    id: UUID = Field(default_factory=uuid4, description="Unique identifier for the manifest")
    tree_id: UUID = Field(description="Corresponds to HTATreeModel.id")
    
    # Versioning - Simplified for MVP
    manifest_version: str = Field(default="1.0", description="Version of the manifest schema")
    
    # Goal Capture - Essential for context
    user_goal: str = Field(description="Primary user goal or objective")
    
    # Q&A Traceability - Keeping basic structure for future expansion
    q_and_a_responses: List[Dict[str, Any]] = Field(
        default_factory=list, 
        description="Recorded clarifying questions and user responses during onboarding"
    )
    
    # Steps Content
    steps: List[RoadmapStep] = Field(default_factory=list)
    
    # Audit Trail
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of manifest creation")
    # updated_at is set only on logical mutation (e.g., status change or adding steps), not on every validation.
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of last manifest update")
=======
    id: UUID = Field(
        default_factory=uuid4, description="Unique identifier for the manifest"
    )
    tree_id: UUID = Field(description="Corresponds to HTATreeModel.id")

    # Versioning - Simplified for MVP
    manifest_version: str = Field(
        default="1.0", description="Version of the manifest schema"
    )

    # Goal Capture - Essential for context
    user_goal: str = Field(description="Primary user goal or objective")

    # Q&A Traceability - Keeping basic structure for future expansion
    q_and_a_responses: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Recorded clarifying questions and user responses during onboarding",
    )

    # Steps Content
    steps: List[RoadmapStep] = Field(default_factory=list)

    # Audit Trail
    created_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of manifest creation"
    )
    # updated_at is set only on logical mutation (e.g., status change or adding steps), not on every validation.
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, description="Timestamp of last manifest update"
    )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    def __init__(self, **data):
        super().__init__(**data)
        self._build_indexes()

    def _build_indexes(self):
        self._step_index = {step.id: step for step in self.steps}
        self._dependency_graph = {step.id: step.dependencies for step in self.steps}
        self._reverse_dependency_graph = {}
        for step in self.steps:
            for dep in step.dependencies:
                self._reverse_dependency_graph.setdefault(dep, []).append(step.id)
        self._topological_sort_cache = None

    def get_step_by_id(self, step_id: UUID) -> Optional[RoadmapStep]:
        """
        Find and return a step by its ID.
<<<<<<< HEAD
        
        Args:
            step_id: The UUID of the step to find
            
=======

        Args:
            step_id: The UUID of the step to find

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            The step with the given ID, or None if not found
        """
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
<<<<<<< HEAD
    
    def update_step_status(self, step_id: UUID, new_status: Literal["pending", "in_progress", "completed", "deferred", "cancelled"]) -> 'RoadmapManifest':
=======

    def update_step_status(
        self,
        step_id: UUID,
        new_status: Literal[
            "pending", "in_progress", "completed", "deferred", "cancelled"
        ],
    ) -> "RoadmapManifest":
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        """
        Return a new manifest with the step status updated (immutability pattern).
        """
        steps = [
<<<<<<< HEAD
            step.copy(update={"status": new_status, "updated_at": datetime.utcnow()}) if step.id == step_id else step
=======
            (
                step.copy(
                    update={"status": new_status, "updated_at": datetime.utcnow()}
                )
                if step.id == step_id
                else step
            )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            for step in self.steps
        ]
        return self.copy(update=self._ensure_updated_timestamp({"steps": steps}))

<<<<<<< HEAD
    
    def _ensure_updated_timestamp(self, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper to ensure that updated_at is always set on mutation operations.
        
        Args:
            update_dict: Dictionary of updates to apply
            
=======
    def _ensure_updated_timestamp(self, update_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper to ensure that updated_at is always set on mutation operations.

        Args:
            update_dict: Dictionary of updates to apply

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            Dictionary with updated_at added if not present
        """
        if "updated_at" not in update_dict:
            update_dict["updated_at"] = datetime.utcnow()
        return update_dict
<<<<<<< HEAD
        
    def add_step(self, step: RoadmapStep) -> 'RoadmapManifest':
        """
        Return a new manifest with the additional step (immutability pattern).
        """
        return self.copy(update=self._ensure_updated_timestamp({"steps": self.steps + [step]}))
=======

    def add_step(self, step: RoadmapStep) -> "RoadmapManifest":
        """
        Return a new manifest with the additional step (immutability pattern).
        """
        return self.copy(
            update=self._ensure_updated_timestamp({"steps": self.steps + [step]})
        )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    def get_pending_actionable_steps(self) -> List[RoadmapStep]:
        """
        Returns all steps that are pending and have all dependencies completed.
        """
        actionable = []
        for step in self.steps:
            if step.status == "pending" and all(
                self.get_step_by_id(dep_id).status == "completed"
                for dep_id in step.dependencies
            ):
                actionable.append(step)
        return actionable

    def get_major_phases(self) -> List[RoadmapStep]:
        """
        Returns all steps marked as major phases in hta_metadata.
        """
<<<<<<< HEAD
        return [step for step in self.steps if step.hta_metadata.get("is_major_phase", False)]
=======
        return [
            step
            for step in self.steps
            if step.hta_metadata.get("is_major_phase", False)
        ]
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    def check_circular_dependencies(self) -> List[str]:
        """
        Check for circular dependencies in the manifest steps.
<<<<<<< HEAD
        
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        Returns:
            A list of error messages describing any circular dependencies found
        """
        errors = []
<<<<<<< HEAD
        visited = {}  # Maps step_id to visit status: 0=unvisited, 1=in progress, 2=visited
        
        def dfs(step_id):
            # Mark as in-progress
            visited[step_id] = 1
            
            step = self.get_step_by_id(step_id)
            if not step:
                return
            
=======
        visited = (
            {}
        )  # Maps step_id to visit status: 0=unvisited, 1=in progress, 2=visited

        def dfs(step_id):
            # Mark as in-progress
            visited[step_id] = 1

            step = self.get_step_by_id(step_id)
            if not step:
                return

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            for dep_id in step.dependencies:
                if dep_id not in visited:
                    # Not visited yet
                    visited[dep_id] = 0
<<<<<<< HEAD
                    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                if visited.get(dep_id) == 0:
                    # Visit unvisited node
                    if dfs(dep_id):
                        # Propagate cycle detection
                        return True
                elif visited.get(dep_id) == 1:
                    # Found a cycle
                    cycle_step = self.get_step_by_id(dep_id)
                    current_step = self.get_step_by_id(step_id)
                    if cycle_step and current_step:
                        errors.append(
                            f"Circular dependency detected: '{current_step.title}' ({step_id}) "
                            f"depends on '{cycle_step.title}' ({dep_id}) which creates a cycle."
                        )
                    return True
<<<<<<< HEAD
            
            # Mark as visited
            visited[step_id] = 2
            return False
        
=======

            # Mark as visited
            visited[step_id] = 2
            return False

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        # Check each step that hasn't been visited
        for step in self.steps:
            if step.id not in visited:
                visited[step.id] = 0
                dfs(step.id)
<<<<<<< HEAD
        
        return errors
=======

        return errors


class RoadmapManifest:
    """Placeholder for RoadmapManifest. Implement as needed."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("RoadmapManifest is not yet implemented.")


class RoadmapStep:
    """Placeholder for RoadmapStep. Implement as needed."""

    def __init__(self, *args, **kwargs):
        raise NotImplementedError("RoadmapStep is not yet implemented.")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
