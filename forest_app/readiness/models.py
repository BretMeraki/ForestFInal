# forest_app/readiness/models.py
"""
Models for the Contextual Readiness Framework that provides holistic preparation
guidance for tasks based on multi-dimensional context awareness.
"""

import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any

from pydantic import BaseModel, Field, validator

logger = logging.getLogger(__name__)

# --- Enums for Protocol Types ---
class ProtocolType(str, Enum):
    MENTAL = "mental"
    PHYSICAL = "physical"
    EMOTIONAL = "emotional"


class ContextFactorType(str, Enum):
    ENVIRONMENTAL = "environmental"  # Location, time, weather, noise, etc.
    PERSONAL = "personal"  # Sleep, energy, stress, mood
    TASK_HISTORY = "task_history"  # Patterns, ideal conditions
    RELATIONSHIP = "relationship"  # Social obligations, support systems
    GOAL_ALIGNMENT = "goal_alignment"  # Connection to higher goals


class ProtocolEffectiveness(str, Enum):
    HIGHLY_EFFECTIVE = "highly_effective"
    EFFECTIVE = "effective"
    NEUTRAL = "neutral"
    INEFFECTIVE = "ineffective"
    COUNTERPRODUCTIVE = "counterproductive"


# --- Preparation Protocol Models ---
class PrepStep(BaseModel):
    """A single step within a preparation protocol"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Short title of the prep step")
    description: str = Field(..., description="Detailed guidance for the step")
    duration_seconds: int = Field(default=60, description="Estimated time to complete this step")
    optional: bool = Field(default=False, description="Whether this step is optional")
    
    class Config:
        extra = "ignore"


class ReadinessProtocol(BaseModel):
    """A complete protocol for preparing for a task"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    protocol_type: ProtocolType
    steps: List[PrepStep] = Field(default_factory=list)
    estimated_total_time_seconds: int = Field(default=0)
    
    @validator('estimated_total_time_seconds', pre=True, always=True)
    def calculate_total_time(cls, v, values):
        if 'steps' in values and values['steps']:
            return sum(step.duration_seconds for step in values['steps'])
        return v
    
    class Config:
        extra = "ignore"


# --- Context Factor Models ---
class ContextFactor(BaseModel):
    """A single contextual factor that influences task readiness"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: ContextFactorType
    value: Any
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    timestamp: datetime = Field(default_factory=datetime.now)
    influence_score: float = Field(default=0.0, description="How much this factor influences task performance")
    
    class Config:
        extra = "ignore"


class UserContext(BaseModel):
    """The complete context profile for a user"""
    user_id: str
    factors: Dict[str, ContextFactor] = Field(default_factory=dict)
    time_of_day: Optional[str] = None
    location: Optional[str] = None
    device_context: Dict[str, Any] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    def get_factors_by_type(self, factor_type: ContextFactorType) -> List[ContextFactor]:
        """Get all context factors of a specific type"""
        return [factor for factor in self.factors.values() if factor.type == factor_type]
    
    class Config:
        extra = "ignore"


# --- Protocol Effectiveness Tracking ---
class ProtocolOutcome(BaseModel):
    """Records the effectiveness of a protocol for a specific task"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    task_id: str
    protocol_id: str
    protocol_type: ProtocolType
    effectiveness: ProtocolEffectiveness
    user_feedback: Optional[str] = None
    context_snapshot: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        extra = "ignore"


# --- Task Readiness Models ---
class TaskReadiness(BaseModel):
    """Overall readiness assessment for a specific task"""
    task_id: str
    mental_readiness: float = Field(default=0.5, ge=0.0, le=1.0)
    physical_readiness: float = Field(default=0.5, ge=0.0, le=1.0)
    emotional_readiness: float = Field(default=0.5, ge=0.0, le=1.0)
    overall_readiness: float = Field(default=0.5, ge=0.0, le=1.0)
    
    @validator('overall_readiness', pre=True, always=True)
    def calculate_overall_readiness(cls, v, values):
        mental = values.get('mental_readiness', 0.5)
        physical = values.get('physical_readiness', 0.5)
        emotional = values.get('emotional_readiness', 0.5)
        # Simple average but could be weighted based on task requirements
        return (mental + physical + emotional) / 3
    
    class Config:
        extra = "ignore"


# --- Extended FrontierTask Model ---
class FrontierTask(BaseModel):
    """
    A task that represents a concrete action the user can take to progress in their HTA.
    Enhanced with readiness protocols for holistic preparation.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    node_id: str
    title: str
    description: str
    status: str = Field(default="pending")
    priority: float = Field(default=0.5, ge=0.0, le=1.0)
    context_relevance: float = Field(default=0.5, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    is_stale: bool = Field(default=False)
    
    # Readiness-specific fields
    mental_prep_protocol: Optional[ReadinessProtocol] = None
    physical_prep_protocol: Optional[ReadinessProtocol] = None
    emotional_prep_protocol: Optional[ReadinessProtocol] = None
    context_factors: Dict[str, ContextFactor] = Field(default_factory=dict)
    readiness: Optional[TaskReadiness] = None
    
    def update_status(self, new_status: str):
        """Update the task status and the updated timestamp"""
        self.status = new_status
        self.updated_at = datetime.now()
    
    def check_staleness(self, stale_threshold_hours: int = 24):
        """Check if the task is stale based on last update time"""
        hours_since_update = (datetime.now() - self.updated_at).total_seconds() / 3600
        self.is_stale = hours_since_update > stale_threshold_hours
        return self.is_stale
    
    def add_context_factor(self, factor: ContextFactor):
        """Add or update a context factor for this task"""
        self.context_factors[factor.id] = factor
    
    class Config:
        extra = "ignore"


# --- Make models easily importable ---
__all__ = [
    "ProtocolType",
    "ContextFactorType",
    "ProtocolEffectiveness",
    "PrepStep",
    "ReadinessProtocol",
    "ContextFactor",
    "UserContext",
    "ProtocolOutcome",
    "TaskReadiness",
    "FrontierTask",
]

logger.debug("Readiness Framework models defined in models.py.")
