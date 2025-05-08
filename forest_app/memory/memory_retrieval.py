"""
Memory Retrieval System for the Forest application.
Provides advanced memory search and retrieval capabilities.
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set

from .memory_models import (
    MemoryQuery,
    EpisodicMemory,
    SemanticConcept,
    MemoryEntity,
    MemoryInsight
)
from .episodic_memory import EpisodicMemoryManager
from .semantic_memory import SemanticMemoryManager

logger = logging.getLogger(__name__)

class MemoryRetrieval:
    """
    Advanced memory retrieval system that enables natural language queries
    and contextual memory searches across both episodic and semantic memory.
    """
    
    def __init__(self, episodic: EpisodicMemoryManager, semantic: SemanticMemoryManager):
        self.episodic = episodic
        self.semantic = semantic
        logger.info("MemoryRetrieval system initialized")
    
    async def search_by_natural_query(self, user_id: str, query_text: str, limit: int = 10) -> Dict[str, Any]:
        """
        Search memories using a natural language query.
        
        Args:
            user_id: The ID of the user
            query_text: Natural language query
            limit: Maximum number of results to return
            
        Returns:
            Dictionary with search results by category
        """
        # Parse query for entities, time references, etc.
        time_range = self._extract_time_range(query_text)
        entities = await self._extract_entities(query_text)
        keywords = self._extract_keywords(query_text)
        
        # Build memory query
        memory_query = MemoryQuery(
            user_id=user_id,
            keywords=keywords,
            entities=[e.id for e in entities],
            start_time=time_range[0],
            end_time=time_range[1],
            limit=limit
        )
        
        # Get episodic memories
        episodic_memories = await self.episodic.retrieve_memories_by_query(memory_query)
        
        # Get related semantic concepts
        semantic_concepts = []
        for keyword in keywords:
            concept = await self.semantic.find_concept_by_name(keyword)
            if concept and concept.user_id == user_id:
                semantic_concepts.append(concept)
        
        # If no exact matches, try partial matches
        if not semantic_concepts:
            for keyword in keywords:
                # This is a simplified approach - in a real implementation,
                # you would use more sophisticated partial matching
                for concept_name, concept_id in self.semantic._concept_name_index.items():
                    if keyword.lower() in concept_name and len(keyword) > 3:
                        concept = await self.semantic.retrieve_concept(concept_id)
                        if concept and concept.user_id == user_id and concept not in semantic_concepts:
                            semantic_concepts.append(concept)
        
        # Format results
        return {
            "query": query_text,
            "episodic_memories": [self._format_memory(memory) for memory in episodic_memories],
            "semantic_concepts": [self._format_concept(concept) for concept in semantic_concepts],
            "entities": [self._format_entity(entity) for entity in entities]
        }
    
    async def retrieve_recent_memories(self, user_id: str, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve recent memories.
        
        Args:
            user_id: The ID of the user
            days: Number of days to look back
            limit: Maximum number of memories to return
            
        Returns:
            List of dictionaries with memory information
        """
        # Calculate start time
        start_time = datetime.now() - timedelta(days=days)
        
        # Build memory query
        memory_query = MemoryQuery(
            user_id=user_id,
            start_time=start_time,
            limit=limit
        )
        
        # Get episodic memories
        memories = await self.episodic.retrieve_memories_by_query(memory_query)
        
        # Format results
        return [self._format_memory(memory) for memory in memories]
    
    async def retrieve_memories_by_emotion(self, 
                                        user_id: str, 
                                        valence_min: float = -1.0,
                                        valence_max: float = 1.0,
                                        limit: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve memories by emotional valence.
        
        Args:
            user_id: The ID of the user
            valence_min: Minimum emotional valence (-1.0 to 1.0)
            valence_max: Maximum emotional valence (-1.0 to 1.0)
            limit: Maximum number of memories to return
            
        Returns:
            List of dictionaries with memory information
        """
        # Build memory query
        memory_query = MemoryQuery(
            user_id=user_id,
            emotional_valence_range=(valence_min, valence_max),
            limit=limit
        )
        
        # Get episodic memories
        memories = await self.episodic.retrieve_memories_by_query(memory_query)
        
        # Format results
        return [self._format_memory(memory) for memory in memories]
    
    async def retrieve_task_patterns(self, user_id: str) -> Dict[str, Any]:
        """
        Retrieve patterns in task completion and experiences.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            Dictionary with task pattern information
        """
        # Find task-related concepts
        task_concepts = []
        for concept_id, concept in self.semantic._concepts.items():
            if (concept.user_id == user_id and 
                ("task" in concept.category.lower() or "work" in concept.category.lower())):
                task_concepts.append(concept)
        
        # Sort by priority
        task_concepts.sort(key=lambda c: c.priority.value, reverse=True)
        
        # Extract patterns
        effective_patterns = []
        ineffective_patterns = []
        preferences = []
        
        for concept in task_concepts:
            if "effective" in concept.concept_name.lower():
                effective_patterns.append(self._format_concept(concept))
            elif "ineffective" in concept.concept_name.lower() or "struggle" in concept.concept_name.lower():
                ineffective_patterns.append(self._format_concept(concept))
            elif "preference" in concept.concept_name.lower():
                preferences.append(self._format_concept(concept))
        
        return {
            "effective_patterns": effective_patterns[:5],
            "ineffective_patterns": ineffective_patterns[:5],
            "preferences": preferences[:5]
        }
    
    async def retrieve_entity_memories(self, user_id: str, entity_name: str, limit: int = 10) -> Dict[str, Any]:
        """
        Retrieve memories and knowledge related to a specific entity.
        
        Args:
            user_id: The ID of the user
            entity_name: The name of the entity to retrieve memories for
            limit: Maximum number of memories to return
            
        Returns:
            Dictionary with entity information and related memories
        """
        # Find the entity
        entity = await self.semantic.find_entity_by_name(entity_name)
        if not entity:
            return {"error": f"Entity '{entity_name}' not found"}
        
        # Get related entities
        related_entities = await self.semantic.find_related_entities(entity.id)
        
        # Build memory query
        memory_query = MemoryQuery(
            user_id=user_id,
            entities=[entity.id],
            limit=limit
        )
        
        # Get episodic memories
        memories = await self.episodic.retrieve_memories_by_query(memory_query)
        
        # Format results
        return {
            "entity": self._format_entity(entity),
            "related_entities": [
                {
                    "entity": self._format_entity(related_entity),
                    "relation": relation
                }
                for related_entity, relation in related_entities
            ],
            "memories": [self._format_memory(memory) for memory in memories]
        }
    
    # ----- Helper methods -----
    
    def _extract_time_range(self, query_text: str) -> Tuple[Optional[datetime], Optional[datetime]]:
        """Extract time range references from query text."""
        start_time = None
        end_time = None
        
        # Look for relative time references
        if "yesterday" in query_text.lower():
            start_time = datetime.now() - timedelta(days=1)
            end_time = datetime.now()
        elif "last week" in query_text.lower():
            start_time = datetime.now() - timedelta(days=7)
            end_time = datetime.now()
        elif "last month" in query_text.lower():
            start_time = datetime.now() - timedelta(days=30)
            end_time = datetime.now()
        
        # Simple pattern for date ranges like "between Jan 1 and Feb 1"
        # In a real implementation, you would use a more sophisticated date parser
        
        return (start_time, end_time)
    
    async def _extract_entities(self, query_text: str) -> List[MemoryEntity]:
        """Extract entity references from query text."""
        entities = []
        
        # Split query into words and check each one
        words = re.findall(r'\b\w+\b', query_text)
        for word in words:
            if len(word) > 3:  # Only check substantial words
                entity = await self.semantic.find_entity_by_name(word)
                if entity and entity not in entities:
                    entities.append(entity)
        
        # Also check multi-word phrases (simplified approach)
        for i in range(len(words) - 1):
            phrase = words[i] + " " + words[i + 1]
            entity = await self.semantic.find_entity_by_name(phrase)
            if entity and entity not in entities:
                entities.append(entity)
        
        return entities
    
    def _extract_keywords(self, query_text: str) -> List[str]:
        """Extract keywords from query text."""
        # Remove common stop words (simplified approach)
        stop_words = {"the", "a", "an", "in", "on", "at", "to", "for", "with", "about", "from", "when", "where"}
        
        # Split into words, convert to lowercase, and filter out stop words
        words = re.findall(r'\b\w+\b', query_text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        return keywords
    
    def _format_memory(self, memory: EpisodicMemory) -> Dict[str, Any]:
        """Format an episodic memory for output."""
        return {
            "id": memory.id,
            "title": memory.title,
            "description": memory.description,
            "timestamp": memory.timestamp.isoformat(),
            "tags": memory.tags,
            "emotional_valence": memory.emotional_valence,
            "significance": memory.significance_score,
            "strength": memory.memory_strength.value
        }
    
    def _format_concept(self, concept: SemanticConcept) -> Dict[str, Any]:
        """Format a semantic concept for output."""
        return {
            "id": concept.id,
            "name": concept.concept_name,
            "definition": concept.definition,
            "category": concept.category,
            "confidence": concept.confidence,
            "priority": concept.priority.value,
            "last_reinforced": concept.last_reinforced.isoformat()
        }
    
    def _format_entity(self, entity: MemoryEntity) -> Dict[str, Any]:
        """Format an entity for output."""
        return {
            "id": entity.id,
            "name": entity.name,
            "type": entity.entity_type,
            "aliases": entity.aliases,
            "importance": entity.importance_score,
            "first_encountered": entity.first_encountered.isoformat(),
            "last_encountered": entity.last_encountered.isoformat()
        }
