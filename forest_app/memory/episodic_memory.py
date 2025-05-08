"""
Episodic Memory Manager for handling event-based memories in the Forest application.
Provides a human-like system for storing and retrieving personal experiences.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

from pydantic import ValidationError

from .memory_models import (
    EpisodicMemory,
    MemoryEntity,
    MemoryContext,
    MemoryRelation,
    MemoryStrength,
    MemoryQuery
)

logger = logging.getLogger(__name__)

class EpisodicMemoryManager:
    """
    Manages the creation, storage, retrieval, and maintenance of episodic memories.
    
    Episodic memories represent specific events or experiences in the user's life
    and work with the Forest app. They capture the narrative quality of human memory
    and form the foundation for deeper insights and patterns.
    """
    
    def __init__(self):
        self._memories: Dict[str, EpisodicMemory] = {}
        self._entity_memory_index: Dict[str, List[str]] = {}  # Entity ID to Memory IDs
        self._task_memory_index: Dict[str, List[str]] = {}    # Task ID to Memory IDs
        self._node_memory_index: Dict[str, List[str]] = {}    # Node ID to Memory IDs
        self._tag_memory_index: Dict[str, List[str]] = {}     # Tag to Memory IDs
        self._time_memory_index: Dict[str, List[str]] = {}    # YYYY-MM-DD to Memory IDs
        logger.info("EpisodicMemoryManager initialized")
    
    async def create_memory(self, 
                           user_id: str,
                           title: str,
                           description: str,
                           entities_involved: Optional[List[str]] = None,
                           related_tasks: Optional[List[str]] = None,
                           related_nodes: Optional[List[str]] = None,
                           location: Optional[str] = None,
                           emotional_valence: float = 0.0,
                           emotional_arousal: float = 0.5,
                           tags: Optional[List[str]] = None,
                           significance_score: float = 0.5,
                           timestamp: Optional[datetime] = None) -> EpisodicMemory:
        """
        Create a new episodic memory and index it appropriately.
        
        Args:
            user_id: The ID of the user this memory belongs to
            title: A short title for the memory
            description: Detailed description of the memory
            entities_involved: List of entity IDs involved in this memory
            related_tasks: List of task IDs related to this memory
            related_nodes: List of node IDs related to this memory
            location: Location where the memory occurred
            emotional_valence: Emotional valence from -1 (negative) to 1 (positive)
            emotional_arousal: Emotional intensity from 0 (low) to 1 (high)
            tags: List of tags for categorizing the memory
            significance_score: How significant this memory is (0.0 to 1.0)
            timestamp: When the memory occurred (defaults to now)
            
        Returns:
            The created EpisodicMemory object
        """
        try:
            # Create memory object
            memory_id = str(uuid.uuid4())
            memory = EpisodicMemory(
                id=memory_id,
                user_id=user_id,
                title=title,
                description=description,
                entities_involved=entities_involved or [],
                related_tasks=related_tasks or [],
                related_nodes=related_nodes or [],
                location=location,
                emotional_valence=emotional_valence,
                emotional_arousal=emotional_arousal,
                tags=tags or [],
                significance_score=significance_score,
                timestamp=timestamp or datetime.now(),
                memory_strength=MemoryStrength.STRONG,  # New memories start strong
                access_count=1,
                last_accessed=datetime.now()
            )
            
            # Store memory
            self._memories[memory_id] = memory
            
            # Index the memory for fast retrieval
            self._index_memory(memory)
            
            logger.info(f"Created episodic memory: {title} (ID: {memory_id})")
            return memory
            
        except ValidationError as e:
            logger.error(f"Failed to create episodic memory: {e}")
            raise
    
    async def retrieve_memory(self, memory_id: str) -> Optional[EpisodicMemory]:
        """
        Retrieve a specific memory by ID and update its access metadata.
        
        Args:
            memory_id: The ID of the memory to retrieve
            
        Returns:
            The memory if found, None otherwise
        """
        memory = self._memories.get(memory_id)
        if memory:
            # Update access metadata
            memory.access()
            self._strengthen_memory(memory)
            return memory
        return None
    
    async def retrieve_memories_by_query(self, query: MemoryQuery) -> List[EpisodicMemory]:
        """
        Retrieve memories matching the given query parameters.
        
        Args:
            query: A MemoryQuery object with search parameters
            
        Returns:
            List of matching memories, ordered by relevance
        """
        # Start with all memories for the user
        candidate_memory_ids = set()
        for memory in self._memories.values():
            if memory.user_id == query.user_id:
                candidate_memory_ids.add(memory.id)
        
        # Filter by entities if specified
        if query.entities:
            entity_memories = set()
            for entity_id in query.entities:
                if entity_id in self._entity_memory_index:
                    entity_memories.update(self._entity_memory_index[entity_id])
            if entity_memories:
                candidate_memory_ids &= entity_memories
        
        # Filter by time range if specified
        if query.start_time or query.end_time:
            time_filtered_ids = set()
            for memory_id in candidate_memory_ids:
                memory = self._memories[memory_id]
                if query.start_time and memory.timestamp < query.start_time:
                    continue
                if query.end_time and memory.timestamp > query.end_time:
                    continue
                time_filtered_ids.add(memory_id)
            candidate_memory_ids = time_filtered_ids
        
        # Filter by location if specified
        if query.location:
            location_filtered_ids = set()
            for memory_id in candidate_memory_ids:
                memory = self._memories[memory_id]
                if memory.location and query.location.lower() in memory.location.lower():
                    location_filtered_ids.add(memory_id)
            candidate_memory_ids = location_filtered_ids
        
        # Filter by significance threshold
        if query.significance_threshold > 0:
            significance_filtered_ids = set()
            for memory_id in candidate_memory_ids:
                memory = self._memories[memory_id]
                if memory.significance_score >= query.significance_threshold:
                    significance_filtered_ids.add(memory_id)
            candidate_memory_ids = significance_filtered_ids
        
        # Filter by keywords (in title or description)
        if query.keywords:
            keyword_filtered_ids = set()
            for memory_id in candidate_memory_ids:
                memory = self._memories[memory_id]
                text = f"{memory.title.lower()} {memory.description.lower()}"
                if any(keyword.lower() in text for keyword in query.keywords):
                    keyword_filtered_ids.add(memory_id)
            candidate_memory_ids = keyword_filtered_ids
        
        # Get the actual memory objects
        result_memories = [self._memories[memory_id] for memory_id in candidate_memory_ids]
        
        # Sort by significance and recency
        result_memories.sort(key=lambda m: (m.significance_score, m.timestamp), reverse=True)
        
        # Limit results
        result_memories = result_memories[:query.limit]
        
        # Update access metadata for returned memories
        for memory in result_memories:
            memory.access()
            self._strengthen_memory(memory)
        
        return result_memories
    
    async def update_memory(self, memory_id: str, **updates) -> Optional[EpisodicMemory]:
        """
        Update fields of an existing memory.
        
        Args:
            memory_id: The ID of the memory to update
            **updates: Fields to update and their new values
            
        Returns:
            The updated memory if found, None otherwise
        """
        memory = self._memories.get(memory_id)
        if not memory:
            return None
            
        # Remove the memory from indexes
        self._remove_from_indexes(memory)
        
        # Update memory fields
        for key, value in updates.items():
            if hasattr(memory, key):
                setattr(memory, key, value)
        
        # Re-index the memory
        self._index_memory(memory)
        
        # Mark as accessed
        memory.access()
        
        logger.info(f"Updated episodic memory: {memory.title} (ID: {memory_id})")
        return memory
    
    async def delete_memory(self, memory_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            memory_id: The ID of the memory to delete
            
        Returns:
            True if deleted, False if not found
        """
        memory = self._memories.get(memory_id)
        if not memory:
            return False
            
        # Remove from indexes
        self._remove_from_indexes(memory)
        
        # Delete the memory
        del self._memories[memory_id]
        
        logger.info(f"Deleted episodic memory: {memory.title} (ID: {memory_id})")
        return True
    
    async def get_related_memories(self, memory_id: str, limit: int = 5) -> List[EpisodicMemory]:
        """
        Find memories related to the given memory based on shared entities, tasks, etc.
        
        Args:
            memory_id: The ID of the memory to find related memories for
            limit: Maximum number of related memories to return
            
        Returns:
            List of related memories
        """
        memory = self._memories.get(memory_id)
        if not memory:
            return []
            
        related_memory_ids = set()
        
        # Find memories with shared entities
        for entity_id in memory.entities_involved:
            if entity_id in self._entity_memory_index:
                related_memory_ids.update(self._entity_memory_index[entity_id])
        
        # Find memories with shared tasks
        for task_id in memory.related_tasks:
            if task_id in self._task_memory_index:
                related_memory_ids.update(self._task_memory_index[task_id])
        
        # Find memories with shared nodes
        for node_id in memory.related_nodes:
            if node_id in self._node_memory_index:
                related_memory_ids.update(self._node_memory_index[node_id])
        
        # Find memories with shared tags
        for tag in memory.tags:
            if tag in self._tag_memory_index:
                related_memory_ids.update(self._tag_memory_index[tag])
        
        # Remove the original memory from results
        related_memory_ids.discard(memory_id)
        
        # Get the actual memory objects
        related_memories = [self._memories[mid] for mid in related_memory_ids if mid in self._memories]
        
        # Sort by similarity (count of shared elements) and significance
        def similarity_score(mem):
            shared_entities = len(set(mem.entities_involved) & set(memory.entities_involved))
            shared_tasks = len(set(mem.related_tasks) & set(memory.related_tasks))
            shared_nodes = len(set(mem.related_nodes) & set(memory.related_nodes))
            shared_tags = len(set(mem.tags) & set(memory.tags))
            return (shared_entities + shared_tasks + shared_nodes + shared_tags, mem.significance_score)
            
        related_memories.sort(key=similarity_score, reverse=True)
        
        # Limit results
        related_memories = related_memories[:limit]
        
        return related_memories
    
    async def run_maintenance(self, user_id: str) -> Dict[str, Any]:
        """
        Perform maintenance on the memory system:
        - Update memory strengths based on recency and access frequency
        - Identify memories that might need reinforcement
        
        Args:
            user_id: The ID of the user whose memories to maintain
            
        Returns:
            Statistics about the maintenance operation
        """
        now = datetime.now()
        memory_count = 0
        strengthened = 0
        weakened = 0
        needs_reinforcement = []
        
        for memory in self._memories.values():
            if memory.user_id != user_id:
                continue
                
            memory_count += 1
            
            # Calculate days since last access
            days_since_access = float('inf')
            if memory.last_accessed:
                days_since_access = (now - memory.last_accessed).days
            
            # Adjust memory strength based on recency and access patterns
            old_strength = memory.memory_strength
            
            if days_since_access > 180 and memory.access_count < 3:
                # Rarely accessed old memories become fading
                memory.memory_strength = MemoryStrength.FADING
                weakened += 1
            elif days_since_access > 90 and memory.access_count < 5:
                # Old, infrequently accessed memories become weak
                memory.memory_strength = MemoryStrength.WEAK
                weakened += 1
            elif days_since_access < 30 and memory.access_count > 5:
                # Recently and frequently accessed memories become strong
                memory.memory_strength = MemoryStrength.STRONG
                strengthened += 1
            elif days_since_access < 60:
                # Recently accessed memories become at least medium
                if memory.memory_strength == MemoryStrength.WEAK or memory.memory_strength == MemoryStrength.FADING:
                    memory.memory_strength = MemoryStrength.MEDIUM
                    strengthened += 1
            
            # Identify memories that might need reinforcement
            if memory.significance_score > 0.7 and memory.memory_strength in [MemoryStrength.WEAK, MemoryStrength.FADING]:
                needs_reinforcement.append(memory.id)
        
        result = {
            "memory_count": memory_count,
            "strengthened": strengthened,
            "weakened": weakened,
            "needs_reinforcement": needs_reinforcement
        }
        
        logger.info(f"Memory maintenance completed for user {user_id}: {result}")
        return result
    
    # ---- Internal helper methods ----
    
    def _index_memory(self, memory: EpisodicMemory):
        """Add a memory to all relevant indexes."""
        # Index by entity
        for entity_id in memory.entities_involved:
            if entity_id not in self._entity_memory_index:
                self._entity_memory_index[entity_id] = []
            if memory.id not in self._entity_memory_index[entity_id]:
                self._entity_memory_index[entity_id].append(memory.id)
        
        # Index by task
        for task_id in memory.related_tasks:
            if task_id not in self._task_memory_index:
                self._task_memory_index[task_id] = []
            if memory.id not in self._task_memory_index[task_id]:
                self._task_memory_index[task_id].append(memory.id)
        
        # Index by node
        for node_id in memory.related_nodes:
            if node_id not in self._node_memory_index:
                self._node_memory_index[node_id] = []
            if memory.id not in self._node_memory_index[node_id]:
                self._node_memory_index[node_id].append(memory.id)
        
        # Index by tag
        for tag in memory.tags:
            if tag not in self._tag_memory_index:
                self._tag_memory_index[tag] = []
            if memory.id not in self._tag_memory_index[tag]:
                self._tag_memory_index[tag].append(memory.id)
        
        # Index by date (YYYY-MM-DD)
        date_key = memory.timestamp.strftime("%Y-%m-%d")
        if date_key not in self._time_memory_index:
            self._time_memory_index[date_key] = []
        if memory.id not in self._time_memory_index[date_key]:
            self._time_memory_index[date_key].append(memory.id)
    
    def _remove_from_indexes(self, memory: EpisodicMemory):
        """Remove a memory from all indexes."""
        # Remove from entity index
        for entity_id in memory.entities_involved:
            if entity_id in self._entity_memory_index and memory.id in self._entity_memory_index[entity_id]:
                self._entity_memory_index[entity_id].remove(memory.id)
        
        # Remove from task index
        for task_id in memory.related_tasks:
            if task_id in self._task_memory_index and memory.id in self._task_memory_index[task_id]:
                self._task_memory_index[task_id].remove(memory.id)
        
        # Remove from node index
        for node_id in memory.related_nodes:
            if node_id in self._node_memory_index and memory.id in self._node_memory_index[node_id]:
                self._node_memory_index[node_id].remove(memory.id)
        
        # Remove from tag index
        for tag in memory.tags:
            if tag in self._tag_memory_index and memory.id in self._tag_memory_index[tag]:
                self._tag_memory_index[tag].remove(memory.id)
        
        # Remove from date index
        date_key = memory.timestamp.strftime("%Y-%m-%d")
        if date_key in self._time_memory_index and memory.id in self._time_memory_index[date_key]:
            self._time_memory_index[date_key].remove(memory.id)
    
    def _strengthen_memory(self, memory: EpisodicMemory):
        """Strengthen a memory based on access."""
        # Recently accessed memories should have at least medium strength
        if memory.memory_strength == MemoryStrength.WEAK or memory.memory_strength == MemoryStrength.FADING:
            memory.memory_strength = MemoryStrength.MEDIUM
            logger.debug(f"Memory strengthened due to access: {memory.title} (ID: {memory.id})")
        
        # Frequently accessed memories become strong
        if memory.access_count > 5 and memory.memory_strength != MemoryStrength.STRONG:
            memory.memory_strength = MemoryStrength.STRONG
            logger.debug(f"Memory strengthened due to frequent access: {memory.title} (ID: {memory.id})")
