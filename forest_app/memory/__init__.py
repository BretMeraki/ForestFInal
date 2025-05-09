"""
Forest App Memory System

A robust semantic-episodic memory framework that gives the application 
human-like memory capabilities, enabling it to function as a true life co-founder.
"""

from .memory_models import (
    MemoryType,
    MemoryStrength,
    MemoryPriority,
    MemoryEntity,
    MemoryRelation,
    EpisodicMemory,
    SemanticConcept,
    MemoryContext,
    MemoryInsight,
    MemoryQuery,
)

from .memory_service import MemoryService
from .episodic_memory import EpisodicMemoryManager
from .semantic_memory import SemanticMemoryManager
from .memory_retrieval import MemoryRetrieval

__all__ = [
    # Models
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
    
    # Services
    "MemoryService",
    "EpisodicMemoryManager",
    "SemanticMemoryManager",
    "MemoryRetrieval",
]
