# forest_app/persistence/models.py

import uuid
from datetime import datetime
<<<<<<< HEAD
from typing import List, Dict, Any, Optional # Ensure basic types are imported
from enum import Enum as PyEnum

# --- SQLAlchemy Imports ---
from sqlalchemy import (
    Column, String, DateTime, Boolean, ForeignKey, Text, Index, Enum as SqlAlchemyEnum
)
# --- ADDED/MODIFIED IMPORT for PostgreSQL types ---
from sqlalchemy.dialects.postgresql import JSONB, UUID # Import specifically for PostgreSQL
# --- END ADDED/MODIFIED IMPORT ---
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.sql import func # For server-side timestamp defaults
from sqlalchemy.types import TypeDecorator, TEXT
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON

class JSONType(TypeDecorator):
    """Platform-independent JSON type: uses JSONB for Postgres, JSON for SQLite, TEXT fallback."""
=======
from enum import Enum as PyEnum
from typing import Any, Dict, List, Optional  # Ensure basic types are imported

# --- SQLAlchemy Imports ---
from sqlalchemy import Boolean, DateTime
from sqlalchemy import Enum as SqlAlchemyEnum
from sqlalchemy import ForeignKey, Index, String, Text
# --- ADDED/MODIFIED IMPORT for PostgreSQL types ---
from sqlalchemy.dialects.postgresql import (  # Import specifically for PostgreSQL
    JSONB, UUID)
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
# --- END ADDED/MODIFIED IMPORT ---
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func  # For server-side timestamp defaults
from sqlalchemy.types import TEXT, TypeDecorator


class JSONType(TypeDecorator):
    """Platform-independent JSON type: uses JSONB for Postgres, JSON for SQLite, TEXT fallback."""

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    impl = TEXT
    cache_ok = True

    def load_dialect_impl(self, dialect):
<<<<<<< HEAD
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(JSONB())
        elif dialect.name == 'sqlite':
=======
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        elif dialect.name == "sqlite":
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            try:
                return dialect.type_descriptor(SQLITE_JSON())
            except ImportError:
                return dialect.type_descriptor(TEXT())
        else:
            return dialect.type_descriptor(TEXT())

    def process_bind_param(self, value, dialect):
        import json
<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        if value is not None:
            return json.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        import json
<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        if value is not None:
            return json.loads(value)
        return None

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# --- Base Class ---
class Base(DeclarativeBase):
    pass

<<<<<<< HEAD
# --- Status Enum for HTA Nodes ---
class HTAStatus(str, PyEnum):
    """Status enum for HTA nodes, standardized across the application."""
=======

# --- Status Enum for HTA Nodes ---
class HTAStatus(str, PyEnum):
    """Status enum for HTA nodes, standardized across the application."""

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DEFERRED = "deferred"
    CANCELLED = "cancelled"

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# --- User Model with UUID ---
class UserModel(Base):
    __tablename__ = "users"

<<<<<<< HEAD
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    snapshots: Mapped[List["MemorySnapshotModel"]] = relationship("MemorySnapshotModel", back_populates="user", cascade="all, delete-orphan")
    task_footprints: Mapped[List["TaskFootprintModel"]] = relationship("TaskFootprintModel", back_populates="user", cascade="all, delete-orphan")
    reflection_logs: Mapped[List["ReflectionLogModel"]] = relationship("ReflectionLogModel", back_populates="user", cascade="all, delete-orphan")
    hta_trees: Mapped[List["HTATreeModel"]] = relationship("HTATreeModel", back_populates="user", cascade="all, delete-orphan")
    hta_nodes: Mapped[List["HTANodeModel"]] = relationship("HTANodeModel", back_populates="user", cascade="all, delete-orphan")
=======
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )
    email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # --- Relationships ---
    snapshots: Mapped[List["MemorySnapshotModel"]] = relationship(
        "MemorySnapshotModel", back_populates="user", cascade="all, delete-orphan"
    )
    task_footprints: Mapped[List["TaskFootprintModel"]] = relationship(
        "TaskFootprintModel", back_populates="user", cascade="all, delete-orphan"
    )
    reflection_logs: Mapped[List["ReflectionLogModel"]] = relationship(
        "ReflectionLogModel", back_populates="user", cascade="all, delete-orphan"
    )
    hta_trees: Mapped[List["HTATreeModel"]] = relationship(
        "HTATreeModel", back_populates="user", cascade="all, delete-orphan"
    )
    hta_nodes: Mapped[List["HTANodeModel"]] = relationship(
        "HTANodeModel", back_populates="user", cascade="all, delete-orphan"
    )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)


# --- HTA Tree Model ---
class HTATreeModel(Base):
    __tablename__ = "hta_trees"

<<<<<<< HEAD
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    goal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    initial_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    top_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("hta_nodes.id"), nullable=True)
    initial_roadmap_depth: Mapped[Optional[int]] = mapped_column(nullable=True)
    initial_task_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    manifest: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="hta_trees")
    top_node: Mapped[Optional["HTANodeModel"]] = relationship("HTANodeModel", foreign_keys=[top_node_id])
=======
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    goal_name: Mapped[str] = mapped_column(String(255), nullable=False)
    initial_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    top_node_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hta_nodes.id"), nullable=True
    )
    initial_roadmap_depth: Mapped[Optional[int]] = mapped_column(nullable=True)
    initial_task_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    manifest: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # --- Relationships ---
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="hta_trees")
    top_node: Mapped[Optional["HTANodeModel"]] = relationship(
        "HTANodeModel", foreign_keys=[top_node_id]
    )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    nodes: Mapped[List["HTANodeModel"]] = relationship(
        "HTANodeModel",
        primaryjoin="HTATreeModel.id == HTANodeModel.tree_id",
        back_populates="tree",
<<<<<<< HEAD
        cascade="all, delete-orphan"
=======
        cascade="all, delete-orphan",
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    )

    # --- Create indexes for common query patterns ---
    __table_args__ = (
<<<<<<< HEAD
        Index('idx_hta_trees_user_id_created_at', user_id, created_at),
        # Add GIN index for manifest JSONB to support efficient queries
        Index('idx_hta_trees_manifest_gin', manifest, postgresql_using='gin'),
=======
        Index("idx_hta_trees_user_id_created_at", user_id, created_at),
        # Add GIN index for manifest JSONB to support efficient queries
        Index("idx_hta_trees_manifest_gin", manifest, postgresql_using="gin"),
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    )


# --- HTA Node Model ---
class HTANodeModel(Base):
    __tablename__ = "hta_nodes"

<<<<<<< HEAD
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("hta_nodes.id"), nullable=True, index=True)
    tree_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("hta_trees.id"), index=True)
=======
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hta_nodes.id"), nullable=True, index=True
    )
    tree_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("hta_trees.id"), index=True
    )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_leaf: Mapped[bool] = mapped_column(default=True)
    status: Mapped[str] = mapped_column(
        SqlAlchemyEnum("pending", "in_progress", "completed", name="hta_status_enum"),
        default="pending",
<<<<<<< HEAD
        index=True
    )
    roadmap_step_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True, index=True)
    internal_task_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True, default=lambda: {})
    journey_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True, default=lambda: {})
    branch_triggers: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType, 
        nullable=True, 
        default=lambda: {"expand_now": False, "completion_count_for_expansion_trigger": 3, "current_completion_count": 0}
    )
    is_major_phase: Mapped[bool] = mapped_column(default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # --- Relationships ---
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="hta_nodes")
    tree: Mapped["HTATreeModel"] = relationship("HTATreeModel", back_populates="nodes", foreign_keys=[tree_id])
    parent: Mapped[Optional["HTANodeModel"]] = relationship(
        "HTANodeModel",
        remote_side=[id],
        back_populates="children"
    )
    children: Mapped[List["HTANodeModel"]] = relationship(
        "HTANodeModel",
        back_populates="parent",
        cascade="all, delete-orphan"
=======
        index=True,
    )
    roadmap_step_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), nullable=True, index=True
    )
    internal_task_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType, nullable=True, default=lambda: {}
    )
    journey_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType, nullable=True, default=lambda: {}
    )
    branch_triggers: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType,
        nullable=True,
        default=lambda: {
            "expand_now": False,
            "completion_count_for_expansion_trigger": 3,
            "current_completion_count": 0,
        },
    )
    is_major_phase: Mapped[bool] = mapped_column(default=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # --- Relationships ---
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="hta_nodes")
    tree: Mapped["HTATreeModel"] = relationship(
        "HTATreeModel", back_populates="nodes", foreign_keys=[tree_id]
    )
    parent: Mapped[Optional["HTANodeModel"]] = relationship(
        "HTANodeModel", remote_side=[id], back_populates="children"
    )
    children: Mapped[List["HTANodeModel"]] = relationship(
        "HTANodeModel", back_populates="parent", cascade="all, delete-orphan"
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    )

    # --- Create indexes for common query patterns ---
    __table_args__ = (
        # For finding nodes in a tree with a specific status
<<<<<<< HEAD
        Index('idx_hta_nodes_tree_id_status', tree_id, status),
        # For finding major phases with a specific status
        Index('idx_hta_nodes_tree_id_is_major_phase_status', tree_id, is_major_phase, status),
        # For finding child nodes of a parent with a specific status
        Index('idx_hta_nodes_parent_id_status', parent_id, status),
=======
        Index("idx_hta_nodes_tree_id_status", tree_id, status),
        # For finding major phases with a specific status
        Index(
            "idx_hta_nodes_tree_id_is_major_phase_status",
            tree_id,
            is_major_phase,
            status,
        ),
        # For finding child nodes of a parent with a specific status
        Index("idx_hta_nodes_parent_id_status", parent_id, status),
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    )


# --- Memory Snapshot Model ---
class MemorySnapshotModel(Base):
    __tablename__ = "memory_snapshots"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
<<<<<<< HEAD
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    snapshot_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    codename: Mapped[Optional[str]] = mapped_column(String, nullable=True) # Added codename field
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
=======
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    snapshot_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType, nullable=True
    )
    codename: Mapped[Optional[str]] = mapped_column(
        String, nullable=True
    )  # Added codename field
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    # --- Relationships ---
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="snapshots")


# --- Task Footprint Model ---
class TaskFootprintModel(Base):
    __tablename__ = "task_footprints"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
<<<<<<< HEAD
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    task_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String, nullable=False) # e.g., 'issued', 'completed', 'failed', 'skipped'
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    snapshot_ref: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True) # Optional snapshot context at time of event
    event_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True) # e.g., {"success": true/false, "reason": "..."}

    # --- Relationships ---
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="task_footprints")
=======
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    task_id: Mapped[str] = mapped_column(String, index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(
        String, nullable=False
    )  # e.g., 'issued', 'completed', 'failed', 'skipped'
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    snapshot_ref: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType, nullable=True
    )  # Optional snapshot context at time of event
    event_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType, nullable=True
    )  # e.g., {"success": true/false, "reason": "..."}

    # --- Relationships ---
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="task_footprints"
    )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)


# --- Reflection Log Model ---
class ReflectionLogModel(Base):
    __tablename__ = "reflection_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
<<<<<<< HEAD
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reflection_text: Mapped[str] = mapped_column(Text, nullable=False) # Use Text for potentially long reflections
    snapshot_ref: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)
    analysis_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONType, nullable=True)

    # --- Relationships ---
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="reflection_logs")
=======
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    reflection_text: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Use Text for potentially long reflections
    snapshot_ref: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType, nullable=True
    )
    analysis_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSONType, nullable=True
    )

    # --- Relationships ---
    user: Mapped["UserModel"] = relationship(
        "UserModel", back_populates="reflection_logs"
    )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
