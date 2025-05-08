"""
Models for the Semantic-Episodic Memory System that provides human-like memory
capabilities to the Forest application.
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Set
from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

# --- Enums for Memory Types ---
class MemoryType(str, Enum):
    EPISODIC = "episodic"    # Event-based memories (specific occurrences)
    SEMANTIC = "semantic"    # Conceptual knowledge (facts, concepts, relations)
    PROCEDURAL = "procedural"  # How-to knowledge, skills
    EMOTIONAL = "emotional"  # Associated emotions and feelings
    REFLECTIVE = "reflective"  # Insights, lessons learned


class MemoryStrength(str, Enum):
    STRONG = "strong"        # Frequently accessed, high confidence
    MEDIUM = "medium"        # Occasionally accessed
    WEAK = "weak"            # Rarely accessed, potential for decay
    FADING = "fading"        # Almost forgotten, needs reinforcement


class MemoryPriority(str, Enum):
    CRITICAL = "critical"    # Essential to user's identity/goals
    HIGH = "high"            # Important for multiple contexts
    MEDIUM = "medium"        # Useful in specific contexts
    LOW = "low"              # Peripheral information


# --- Core Memory Models ---
class MemoryEntity(BaseModel):
    """
    An entity that can appear in memories (person, place, concept, etc.)
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    entity_type: str  # person, place, concept, object, etc.
    aliases: List[str] = Field(default_factory=list)
    attributes: Dict[str, Any] = Field(default_factory=dict)
    first_encountered: datetime = Field(default_factory=datetime.now)
    last_encountered: datetime = Field(default_factory=datetime.now)
    importance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    
    def update_encounter(self):
        """Update the last encountered timestamp"""
        self.last_encountered = datetime.now()
    
    class Config:
        extra = "ignore"


class MemoryRelation(BaseModel):
    """
    A relationship between two entities
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    relation_type: str  # friend, colleague, part_of, etc.
    attributes: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    first_observed: datetime = Field(default_factory=datetime.now)
    last_observed: datetime = Field(default_factory=datetime.now)
    
    class Config:
        extra = "ignore"


class EpisodicMemory(BaseModel):
    """
    A memory of a specific event or experience
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    timestamp: datetime = Field(default_factory=datetime.now)
    location: Optional[str] = None
    entities_involved: List[str] = Field(default_factory=list)  # Entity IDs
    related_tasks: List[str] = Field(default_factory=list)  # Task IDs
    related_nodes: List[str] = Field(default_factory=list)  # Node IDs
    emotional_valence: float = Field(default=0.0, ge=-1.0, le=1.0)  # -1 to 1
    emotional_arousal: float = Field(default=0.5, ge=0.0, le=1.0)  # 0 to 1
    memory_strength: MemoryStrength = Field(default=MemoryStrength.MEDIUM)
    access_count: int = Field(default=0)
    last_accessed: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)
    significance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    
    def access(self):
        """Record an access to this memory"""
        self.access_count += 1
        self.last_accessed = datetime.now()
    
    class Config:
        extra = "ignore"


class SemanticConcept(BaseModel):
    """
    A semantic knowledge node representing a concept, fact, or understanding
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    concept_name: str
    definition: str
    category: str  # domain area
    related_concepts: List[str] = Field(default_factory=list)  # Concept IDs
    attributes: Dict[str, Any] = Field(default_factory=dict)
    source_memories: List[str] = Field(default_factory=list)  # Memory IDs
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)
    stability: float = Field(default=0.5, ge=0.0, le=1.0)  # How stable is this knowledge
    last_reinforced: datetime = Field(default_factory=datetime.now)
    priority: MemoryPriority = Field(default=MemoryPriority.MEDIUM)
    
    class Config:
        extra = "ignore"


class MemoryContext(BaseModel):
    """
    The context in which a memory is formed or retrieved
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    location: Optional[str] = None
    activity: Optional[str] = None
    emotional_state: Dict[str, float] = Field(default_factory=dict)
    physical_state: Dict[str, float] = Field(default_factory=dict)
    social_context: List[str] = Field(default_factory=list)  # Entity IDs of people present
    environmental_factors: Dict[str, Any] = Field(default_factory=dict)
    device_context: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        extra = "ignore"


class MemoryInsight(BaseModel):
    """
    An insight derived from analyzing memories
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str
    description: str
    source_memories: List[str] = Field(default_factory=list)  # Memory IDs
    source_concepts: List[str] = Field(default_factory=list)  # Concept IDs
    confidence: float = Field(default=0.7, ge=0.0, le=1.0)
    domain: str  # life area this insight applies to
    generated_at: datetime = Field(default_factory=datetime.now)
    last_reinforced: Optional[datetime] = None
    action_implications: List[str] = Field(default_factory=list)
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    
    class Config:
        extra = "ignore"


class MemoryQuery(BaseModel):
    """
    A query to retrieve memories
    """
    user_id: str
    keywords: List[str] = Field(default_factory=list)
    entities: List[str] = Field(default_factory=list)  # Entity IDs
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    memory_types: List[MemoryType] = Field(default_factory=list)
    emotional_valence_range: Optional[tuple] = None  # (min, max)
    significance_threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    limit: int = Field(default=10)
    
    class Config:
        extra = "ignore"


# --- Make models easily importable ---
__all__ = [
    "MemoryType",
    "MemoryStrength",
    "MemoryPriority",
    "MemoryEntity",
    "MemoryRelation",
    "EpisodicMemory",
    "SemanticConcept",
    "MemoryContext",
    "MemoryInsight",
    "MemoryQuery",
]

logger.debug("Memory System models defined in memory_models.py.")
