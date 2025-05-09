"""
Semantic Memory Manager for handling conceptual knowledge in the Forest application.
Provides a human-like system for storing and retrieving conceptual understanding.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set

from pydantic import ValidationError

from .memory_models import (
    SemanticConcept,
    MemoryPriority,
    MemoryEntity,
    MemoryRelation,
    MemoryQuery
)

logger = logging.getLogger(__name__)

class SemanticMemoryManager:
    """
    Manages the creation, storage, retrieval, and maintenance of semantic knowledge.
    
    Semantic memory represents concepts, facts, and relationships that the system has 
    learned about the user's life, work patterns, preferences, and environment. 
    It forms the foundation for insight generation and personalized assistance.
    """
    
    def __init__(self):
        self._concepts: Dict[str, SemanticConcept] = {}
        self._entities: Dict[str, MemoryEntity] = {}
        self._relations: Dict[str, MemoryRelation] = {}
        
        # Indexes for efficient retrieval
        self._concept_name_index: Dict[str, str] = {}  # Lowercase name to concept ID
        self._concept_category_index: Dict[str, List[str]] = {}  # Category to concept IDs
        self._entity_name_index: Dict[str, str] = {}  # Lowercase name to entity ID
        self._entity_type_index: Dict[str, List[str]] = {}  # Entity type to entity IDs
        self._relation_type_index: Dict[str, List[str]] = {}  # Relation type to relation IDs
        
        logger.info("SemanticMemoryManager initialized")
    
    async def create_concept(self,
                           user_id: str,
                           concept_name: str,
                           definition: str,
                           category: str,
                           related_concepts: Optional[List[str]] = None,
                           attributes: Optional[Dict[str, Any]] = None,
                           source_memories: Optional[List[str]] = None,
                           confidence: float = 0.8,
                           priority: MemoryPriority = MemoryPriority.MEDIUM) -> SemanticConcept:
        """
        Create a new semantic concept.
        
        Args:
            user_id: The ID of the user this concept belongs to
            concept_name: Name of the concept
            definition: Definition or explanation of the concept
            category: The category or domain of the concept
            related_concepts: List of IDs of related concepts
            attributes: Dictionary of additional attributes
            source_memories: List of memory IDs that contributed to this concept
            confidence: Confidence level in this concept (0.0 to 1.0)
            priority: The importance of this concept
            
        Returns:
            The created SemanticConcept object
        """
        try:
            # Check if concept already exists with this name
            concept_id = self._concept_name_index.get(concept_name.lower())
            if concept_id:
                # Return existing concept
                return await self.retrieve_concept(concept_id)
            
            # Create new concept
            concept_id = str(uuid.uuid4())
            concept = SemanticConcept(
                id=concept_id,
                user_id=user_id,
                concept_name=concept_name,
                definition=definition,
                category=category,
                related_concepts=related_concepts or [],
                attributes=attributes or {},
                source_memories=source_memories or [],
                confidence=confidence,
                stability=0.5,  # Initial stability is medium
                last_reinforced=datetime.now(),
                priority=priority
            )
            
            # Store concept
            self._concepts[concept_id] = concept
            
            # Index the concept
            self._index_concept(concept)
            
            # Update related concepts to include this one
            for related_id in concept.related_concepts:
                related = self._concepts.get(related_id)
                if related and concept_id not in related.related_concepts:
                    related.related_concepts.append(concept_id)
            
            logger.info(f"Created semantic concept: {concept_name} (ID: {concept_id})")
            return concept
            
        except ValidationError as e:
            logger.error(f"Failed to create semantic concept: {e}")
            raise
    
    async def retrieve_concept(self, concept_id: str) -> Optional[SemanticConcept]:
        """
        Retrieve a specific concept by ID and update its metadata.
        
        Args:
            concept_id: The ID of the concept to retrieve
            
        Returns:
            The concept if found, None otherwise
        """
        concept = self._concepts.get(concept_id)
        if concept:
            # Update last reinforcement time
            concept.last_reinforced = datetime.now()
            
            # Increase stability slightly with each access
            concept.stability = min(1.0, concept.stability + 0.01)
            
            return concept
        return None
    
    async def find_concept_by_name(self, concept_name: str) -> Optional[SemanticConcept]:
        """
        Find a concept by its name.
        
        Args:
            concept_name: The name of the concept to find
            
        Returns:
            The concept if found, None otherwise
        """
        concept_id = self._concept_name_index.get(concept_name.lower())
        if concept_id:
            return await self.retrieve_concept(concept_id)
        return None
    
    async def find_concepts_by_category(self, category: str, limit: int = 20) -> List[SemanticConcept]:
        """
        Find concepts by their category.
        
        Args:
            category: The category to search for
            limit: Maximum number of concepts to return
            
        Returns:
            List of concepts in the specified category
        """
        concept_ids = self._concept_category_index.get(category.lower(), [])
        concepts = []
        
        for concept_id in concept_ids[:limit]:
            concept = await self.retrieve_concept(concept_id)
            if concept:
                concepts.append(concept)
        
        return concepts
    
    async def update_concept(self, concept_id: str, **updates) -> Optional[SemanticConcept]:
        """
        Update fields of an existing concept.
        
        Args:
            concept_id: The ID of the concept to update
            **updates: Fields to update and their new values
            
        Returns:
            The updated concept if found, None otherwise
        """
        concept = self._concepts.get(concept_id)
        if not concept:
            return None
            
        # Remove from indexes
        self._remove_concept_from_indexes(concept)
        
        # Store old name for relation updates
        old_name = concept.concept_name
        
        # Update concept fields
        for key, value in updates.items():
            if hasattr(concept, key):
                setattr(concept, key, value)
        
        # Re-index the concept
        self._index_concept(concept)
        
        # Update last reinforcement time
        concept.last_reinforced = datetime.now()
        
        logger.info(f"Updated semantic concept: {concept.concept_name} (ID: {concept_id})")
        return concept
    
    async def merge_concepts(self, primary_id: str, secondary_id: str) -> Optional[SemanticConcept]:
        """
        Merge two concepts, keeping the primary and updating it with info from the secondary.
        The secondary concept will be deleted after the merge.
        
        Args:
            primary_id: The ID of the primary concept to keep
            secondary_id: The ID of the secondary concept to merge into the primary
            
        Returns:
            The merged concept if successful, None otherwise
        """
        primary = self._concepts.get(primary_id)
        secondary = self._concepts.get(secondary_id)
        
        if not primary or not secondary:
            return None
        
        # Combine related concepts
        related_concepts = set(primary.related_concepts)
        related_concepts.update(secondary.related_concepts)
        related_concepts.discard(primary_id)  # Remove self-reference if any
        related_concepts.discard(secondary_id)  # Remove soon-to-be-deleted concept
        
        # Combine source memories
        source_memories = set(primary.source_memories)
        source_memories.update(secondary.source_memories)
        
        # Combine attributes (primary takes precedence for conflicts)
        combined_attributes = secondary.attributes.copy()
        combined_attributes.update(primary.attributes)
        
        # Update primary with combined data
        await self.update_concept(
            primary_id,
            related_concepts=list(related_concepts),
            source_memories=list(source_memories),
            attributes=combined_attributes,
            # Take the higher confidence and stability
            confidence=max(primary.confidence, secondary.confidence),
            stability=max(primary.stability, secondary.stability),
            # Take the higher priority
            priority=max(primary.priority, secondary.priority)
        )
        
        # Update the definition if secondary has a more detailed one
        if len(secondary.definition) > len(primary.definition):
            await self.update_concept(primary_id, definition=secondary.definition)
        
        # For all concepts that referred to the secondary, now point to the primary
        for concept_id, concept in self._concepts.items():
            if secondary_id in concept.related_concepts:
                concept.related_concepts.remove(secondary_id)
                if primary_id not in concept.related_concepts and concept_id != primary_id:
                    concept.related_concepts.append(primary_id)
        
        # Delete the secondary concept
        await self.delete_concept(secondary_id)
        
        logger.info(f"Merged concepts: {secondary.concept_name} into {primary.concept_name}")
        return primary
    
    async def delete_concept(self, concept_id: str) -> bool:
        """
        Delete a concept by ID.
        
        Args:
            concept_id: The ID of the concept to delete
            
        Returns:
            True if deleted, False if not found
        """
        concept = self._concepts.get(concept_id)
        if not concept:
            return False
            
        # Remove from indexes
        self._remove_concept_from_indexes(concept)
        
        # Remove references from related concepts
        for related_id in concept.related_concepts:
            related = self._concepts.get(related_id)
            if related and concept_id in related.related_concepts:
                related.related_concepts.remove(concept_id)
        
        # Delete the concept
        del self._concepts[concept_id]
        
        logger.info(f"Deleted semantic concept: {concept.concept_name} (ID: {concept_id})")
        return True
    
    async def create_entity(self,
                          name: str,
                          entity_type: str,
                          aliases: Optional[List[str]] = None,
                          attributes: Optional[Dict[str, Any]] = None,
                          importance_score: float = 0.5) -> MemoryEntity:
        """
        Create a new entity in the semantic network.
        
        Args:
            name: Name of the entity
            entity_type: Type of entity (person, place, concept, etc.)
            aliases: Alternative names for the entity
            attributes: Additional attributes of the entity
            importance_score: Importance of this entity (0.0 to 1.0)
            
        Returns:
            The created MemoryEntity object
        """
        try:
            # Check if entity already exists with this name
            entity_id = self._entity_name_index.get(name.lower())
            if entity_id:
                # Return existing entity
                entity = self._entities[entity_id]
                entity.update_encounter()
                return entity
            
            # Check aliases
            if aliases:
                for alias in aliases:
                    entity_id = self._entity_name_index.get(alias.lower())
                    if entity_id:
                        # Return existing entity, add the new name as an alias
                        entity = self._entities[entity_id]
                        if name not in entity.aliases:
                            entity.aliases.append(name)
                        entity.update_encounter()
                        return entity
            
            # Create new entity
            entity_id = str(uuid.uuid4())
            entity = MemoryEntity(
                id=entity_id,
                name=name,
                entity_type=entity_type,
                aliases=aliases or [],
                attributes=attributes or {},
                importance_score=importance_score
            )
            
            # Store entity
            self._entities[entity_id] = entity
            
            # Index the entity
            self._index_entity(entity)
            
            logger.info(f"Created entity: {name} (ID: {entity_id})")
            return entity
            
        except ValidationError as e:
            logger.error(f"Failed to create entity: {e}")
            raise
    
    async def retrieve_entity(self, entity_id: str) -> Optional[MemoryEntity]:
        """
        Retrieve a specific entity by ID.
        
        Args:
            entity_id: The ID of the entity to retrieve
            
        Returns:
            The entity if found, None otherwise
        """
        entity = self._entities.get(entity_id)
        if entity:
            entity.update_encounter()
            return entity
        return None
    
    async def find_entity_by_name(self, name: str) -> Optional[MemoryEntity]:
        """
        Find an entity by its name or alias.
        
        Args:
            name: The name or alias to search for
            
        Returns:
            The entity if found, None otherwise
        """
        entity_id = self._entity_name_index.get(name.lower())
        if entity_id:
            return await self.retrieve_entity(entity_id)
        return None
    
    async def create_relation(self,
                            source_id: str,
                            target_id: str,
                            relation_type: str,
                            attributes: Optional[Dict[str, Any]] = None,
                            confidence: float = 1.0) -> Optional[MemoryRelation]:
        """
        Create a relationship between two entities.
        
        Args:
            source_id: The ID of the source entity
            target_id: The ID of the target entity
            relation_type: Type of relationship
            attributes: Additional attributes of the relationship
            confidence: Confidence in this relationship (0.0 to 1.0)
            
        Returns:
            The created MemoryRelation object or None if entities don't exist
        """
        # Verify that both entities exist
        source = self._entities.get(source_id)
        target = self._entities.get(target_id)
        
        if not source or not target:
            logger.warning(f"Cannot create relation: entities not found")
            return None
        
        try:
            # Check if relation already exists
            for relation in self._relations.values():
                if (relation.source_id == source_id and 
                    relation.target_id == target_id and
                    relation.relation_type == relation_type):
                    # Update existing relation
                    relation.last_observed = datetime.now()
                    relation.confidence = max(relation.confidence, confidence)
                    if attributes:
                        relation.attributes.update(attributes)
                    return relation
            
            # Create new relation
            relation_id = str(uuid.uuid4())
            relation = MemoryRelation(
                id=relation_id,
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                attributes=attributes or {},
                confidence=confidence
            )
            
            # Store relation
            self._relations[relation_id] = relation
            
            # Index the relation
            if relation_type not in self._relation_type_index:
                self._relation_type_index[relation_type] = []
            self._relation_type_index[relation_type].append(relation_id)
            
            logger.info(f"Created relation: {source.name} -{relation_type}-> {target.name}")
            return relation
            
        except ValidationError as e:
            logger.error(f"Failed to create relation: {e}")
            raise
    
    async def find_relations_for_entity(self, entity_id: str) -> Dict[str, List[MemoryRelation]]:
        """
        Find all relations involving an entity.
        
        Args:
            entity_id: The ID of the entity
            
        Returns:
            Dictionary with "outgoing" and "incoming" relations
        """
        outgoing = []
        incoming = []
        
        for relation in self._relations.values():
            if relation.source_id == entity_id:
                outgoing.append(relation)
            elif relation.target_id == entity_id:
                incoming.append(relation)
        
        return {
            "outgoing": outgoing,
            "incoming": incoming
        }
    
    async def find_related_entities(self, entity_id: str, relation_type: Optional[str] = None) -> List[Tuple[MemoryEntity, str]]:
        """
        Find entities related to the given entity.
        
        Args:
            entity_id: The ID of the entity to find relations for
            relation_type: Optional filter for relation type
            
        Returns:
            List of tuples (related_entity, relation_description)
        """
        results = []
        
        # Find entities that this entity points to
        for relation in self._relations.values():
            if relation.source_id == entity_id:
                if relation_type is None or relation.relation_type == relation_type:
                    target = self._entities.get(relation.target_id)
                    if target:
                        results.append((target, f"{relation.relation_type}"))
        
        # Find entities that point to this entity
        for relation in self._relations.values():
            if relation.target_id == entity_id:
                if relation_type is None or relation.relation_type == relation_type:
                    source = self._entities.get(relation.source_id)
                    if source:
                        results.append((source, f"is {relation.relation_type} of"))
        
        return results
    
    # ---- Internal helper methods ----
    
    def _index_concept(self, concept: SemanticConcept):
        """Add a concept to all relevant indexes."""
        # Index by name
        self._concept_name_index[concept.concept_name.lower()] = concept.id
        
        # Index by category
        category = concept.category.lower()
        if category not in self._concept_category_index:
            self._concept_category_index[category] = []
        if concept.id not in self._concept_category_index[category]:
            self._concept_category_index[category].append(concept.id)
    
    def _remove_concept_from_indexes(self, concept: SemanticConcept):
        """Remove a concept from all indexes."""
        # Remove from name index
        name_key = concept.concept_name.lower()
        if name_key in self._concept_name_index and self._concept_name_index[name_key] == concept.id:
            del self._concept_name_index[name_key]
        
        # Remove from category index
        category = concept.category.lower()
        if category in self._concept_category_index and concept.id in self._concept_category_index[category]:
            self._concept_category_index[category].remove(concept.id)
    
    def _index_entity(self, entity: MemoryEntity):
        """Add an entity to all relevant indexes."""
        # Index by name
        self._entity_name_index[entity.name.lower()] = entity.id
        
        # Index aliases
        for alias in entity.aliases:
            self._entity_name_index[alias.lower()] = entity.id
        
        # Index by type
        entity_type = entity.entity_type.lower()
        if entity_type not in self._entity_type_index:
            self._entity_type_index[entity_type] = []
        if entity.id not in self._entity_type_index[entity_type]:
            self._entity_type_index[entity_type].append(entity.id)
    
    def _remove_entity_from_indexes(self, entity: MemoryEntity):
        """Remove an entity from all indexes."""
        # Remove from name index
        name_key = entity.name.lower()
        if name_key in self._entity_name_index and self._entity_name_index[name_key] == entity.id:
            del self._entity_name_index[name_key]
        
        # Remove aliases from name index
        for alias in entity.aliases:
            alias_key = alias.lower()
            if alias_key in self._entity_name_index and self._entity_name_index[alias_key] == entity.id:
                del self._entity_name_index[alias_key]
        
        # Remove from type index
        entity_type = entity.entity_type.lower()
        if entity_type in self._entity_type_index and entity.id in self._entity_type_index[entity_type]:
            self._entity_type_index[entity_type].remove(entity.id)
