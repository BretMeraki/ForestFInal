"""
Memory Service for coordinating all memory systems in the Forest application.
Acts as the primary interface between the app and the memory subsystems.
"""

import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set

from pydantic import ValidationError

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
    MemoryQuery
)
from .episodic_memory import EpisodicMemoryManager
from .semantic_memory import SemanticMemoryManager

from ..readiness.models import FrontierTask, UserContext, ContextFactor
from ..hta_tree.hta_tree import HTANode, HTATree

logger = logging.getLogger(__name__)

class MemoryService:
    """
    Central service coordinating all memory subsystems in the Forest application.
    
    This service provides a unified interface for the application to interact with
    both episodic and semantic memory systems, and integrates memory with other
    components like HTA trees, frontier tasks, and readiness protocols.
    """
    
    def __init__(self):
        self.episodic = EpisodicMemoryManager()
        self.semantic = SemanticMemoryManager()
        logger.info("MemoryService initialized")
    
    # ----- Life Co-Founder Memory Creation -----
    
    async def remember_task_experience(self, 
                                    user_id: str,
                                    task: FrontierTask,
                                    outcome: str,
                                    user_feedback: Optional[str] = None,
                                    context: Optional[UserContext] = None,
                                    emotional_valence: float = 0.0,
                                    emotional_arousal: float = 0.5) -> Dict[str, Any]:
        """
        Create a memory of a task experience.
        
        Args:
            user_id: The ID of the user
            task: The FrontierTask that was performed
            outcome: Description of what happened
            user_feedback: User's commentary on the experience
            context: The context in which the task was performed
            emotional_valence: Emotional valence from -1 (negative) to 1 (positive)
            emotional_arousal: Emotional intensity from 0 (low) to 1 (high)
            
        Returns:
            Dictionary with created memory IDs
        """
        # Create a descriptive title
        title = f"Task: {task.title}"
        
        # Create a detailed description
        description = f"Worked on task '{task.title}' with outcome: {outcome}.\n"
        if user_feedback:
            description += f"User feedback: {user_feedback}\n"
        
        if context:
            # Add contextual details
            description += "\nContext details:\n"
            if context.time_of_day:
                description += f"- Time of day: {context.time_of_day}\n"
            if context.location:
                description += f"- Location: {context.location}\n"
            
            # Add notable context factors
            notable_factors = []
            for factor in context.factors.values():
                if isinstance(factor.value, (int, float)) and factor.value > 0.7:
                    notable_factors.append(f"- High {factor.name}: {factor.value}")
                elif isinstance(factor.value, (int, float)) and factor.value < 0.3:
                    notable_factors.append(f"- Low {factor.name}: {factor.value}")
            
            if notable_factors:
                description += "\nNotable context factors:\n"
                description += "\n".join(notable_factors)
        
        # Determine significance based on task priority and user feedback
        significance_score = task.priority
        if user_feedback:
            # If user provided feedback, this is likely more significant
            significance_score = max(significance_score, 0.7)
        
        # Create tags
        tags = ["task", task.status]
        
        if task.mental_prep_protocol:
            tags.append("mental_preparation")
        if task.physical_prep_protocol:
            tags.append("physical_preparation")
        if task.emotional_prep_protocol:
            tags.append("emotional_preparation")
        
        # Create the episodic memory
        memory = await self.episodic.create_memory(
            user_id=user_id,
            title=title,
            description=description,
            related_tasks=[task.id],
            related_nodes=[task.node_id],
            location=context.location if context else None,
            emotional_valence=emotional_valence,
            emotional_arousal=emotional_arousal,
            tags=tags,
            significance_score=significance_score
        )
        
        # Extract entities and concepts for semantic memory
        results = {
            "episodic_memory_id": memory.id,
            "semantic_entities": [],
            "semantic_concepts": []
        }
        
        # Create semantic entities and concepts
        if "completed" in task.status.lower():
            # Create or update semantic concept for successful task patterns
            concept = await self.semantic.create_concept(
                user_id=user_id,
                concept_name=f"Effective approach for {task.title}",
                definition=f"Based on successful completion of task '{task.title}'. {outcome}",
                category="task_patterns",
                source_memories=[memory.id],
                confidence=0.7,
                priority=MemoryPriority.MEDIUM
            )
            results["semantic_concepts"].append(concept.id)
        
        # Extract insights about work patterns
        if context and user_feedback:
            # This might contain valuable insights about work preferences
            insight_concept = await self.semantic.create_concept(
                user_id=user_id,
                concept_name=f"Work insight from {task.title}",
                definition=f"Insight from task '{task.title}': {user_feedback}",
                category="work_insights",
                source_memories=[memory.id],
                confidence=0.6,
                priority=MemoryPriority.MEDIUM
            )
            results["semantic_concepts"].append(insight_concept.id)
        
        return results
    
    async def remember_node_interaction(self,
                                     user_id: str,
                                     node: HTANode,
                                     interaction_type: str,
                                     details: str,
                                     context: Optional[UserContext] = None) -> Dict[str, Any]:
        """
        Create a memory of an interaction with an HTA node.
        
        Args:
            user_id: The ID of the user
            node: The HTANode that was interacted with
            interaction_type: Type of interaction (e.g., "created", "updated", "completed")
            details: Details about the interaction
            context: The context in which the interaction occurred
            
        Returns:
            Dictionary with created memory IDs
        """
        # Create a descriptive title
        title = f"Node {interaction_type}: {node.title}"
        
        # Create a detailed description
        description = f"{interaction_type.capitalize()} node '{node.title}'.\n"
        description += f"Details: {details}\n"
        
        if context:
            # Add contextual details
            description += "\nContext details:\n"
            if context.time_of_day:
                description += f"- Time of day: {context.time_of_day}\n"
            if context.location:
                description += f"- Location: {context.location}\n"
        
        # Determine significance based on node priority and milestone status
        significance_score = node.priority
        if node.is_milestone:
            significance_score = max(significance_score, 0.8)
        
        # Create tags
        tags = ["node", interaction_type.lower()]
        if node.is_milestone:
            tags.append("milestone")
        
        # Create the episodic memory
        memory = await self.episodic.create_memory(
            user_id=user_id,
            title=title,
            description=description,
            related_nodes=[node.id],
            location=context.location if context else None,
            tags=tags,
            significance_score=significance_score
        )
        
        # Extract entities and concepts for semantic memory
        results = {
            "episodic_memory_id": memory.id,
            "semantic_entities": [],
            "semantic_concepts": []
        }
        
        # For milestone nodes or completed nodes, create semantic concepts
        if node.is_milestone or interaction_type.lower() == "completed":
            # Create or update semantic concept
            concept = await self.semantic.create_concept(
                user_id=user_id,
                concept_name=f"Knowledge about {node.title}",
                definition=f"Knowledge about '{node.title}' based on {interaction_type}. {details}",
                category="hta_knowledge",
                source_memories=[memory.id],
                confidence=0.7,
                priority=MemoryPriority.MEDIUM
            )
            results["semantic_concepts"].append(concept.id)
        
        return results
    
    async def remember_user_preference(self,
                                    user_id: str,
                                    preference_type: str,
                                    preference_value: Any,
                                    source: str,
                                    confidence: float = 0.8) -> Dict[str, Any]:
        """
        Remember a user preference as semantic knowledge.
        
        Args:
            user_id: The ID of the user
            preference_type: Type of preference (e.g., "work_style", "communication")
            preference_value: The actual preference value
            source: Where this preference was observed/stated
            confidence: Confidence in this preference (0.0 to 1.0)
            
        Returns:
            Dictionary with created memory IDs
        """
        # Create a concept for this preference
        concept_name = f"Preference: {preference_type}"
        
        # Format the definition based on the type of preference value
        if isinstance(preference_value, dict):
            definition = f"User preference for {preference_type}:\n"
            for key, value in preference_value.items():
                definition += f"- {key}: {value}\n"
        else:
            definition = f"User preference for {preference_type}: {preference_value}"
        
        definition += f"\nSource: {source}"
        
        # Create or update the concept
        concept = await self.semantic.create_concept(
            user_id=user_id,
            concept_name=concept_name,
            definition=definition,
            category="user_preferences",
            confidence=confidence,
            priority=MemoryPriority.HIGH  # Preferences are high priority
        )
        
        # Create an entity for the preference type if it doesn't exist
        entity = await self.semantic.create_entity(
            name=preference_type,
            entity_type="preference_category",
            importance_score=0.7
        )
        
        return {
            "semantic_concept_id": concept.id,
            "semantic_entity_id": entity.id
        }
    
    async def remember_conversation(self,
                                 user_id: str,
                                 conversation_topic: str,
                                 highlights: List[str],
                                 node_id: Optional[str] = None,
                                 emotional_valence: float = 0.0) -> Dict[str, Any]:
        """
        Remember key points from a conversation with the user.
        
        Args:
            user_id: The ID of the user
            conversation_topic: The main topic of conversation
            highlights: List of important points or quotes
            node_id: Optional ID of the node being discussed
            emotional_valence: Emotional tone from -1 (negative) to 1 (positive)
            
        Returns:
            Dictionary with created memory IDs
        """
        # Create a descriptive title
        title = f"Conversation: {conversation_topic}"
        
        # Create a detailed description
        description = f"Conversation about {conversation_topic}.\n\nKey points:\n"
        for i, point in enumerate(highlights, 1):
            description += f"{i}. {point}\n"
        
        # Determine significance based on length of highlights
        significance_score = min(0.5 + (len(highlights) * 0.1), 0.9)
        
        # Create tags
        tags = ["conversation", conversation_topic.lower().replace(" ", "_")]
        
        # Related nodes if applicable
        related_nodes = [node_id] if node_id else []
        
        # Create the episodic memory
        memory = await self.episodic.create_memory(
            user_id=user_id,
            title=title,
            description=description,
            related_nodes=related_nodes,
            emotional_valence=emotional_valence,
            emotional_arousal=0.6,  # Conversations tend to be engaging
            tags=tags,
            significance_score=significance_score
        )
        
        # Extract entities and concepts for semantic memory
        results = {
            "episodic_memory_id": memory.id,
            "semantic_entities": [],
            "semantic_concepts": []
        }
        
        # Create semantic concept for significant conversations
        if significance_score > 0.7:
            concept = await self.semantic.create_concept(
                user_id=user_id,
                concept_name=f"Insights from conversation about {conversation_topic}",
                definition=description,
                category="conversation_insights",
                source_memories=[memory.id],
                confidence=0.7,
                priority=MemoryPriority.MEDIUM
            )
            results["semantic_concepts"].append(concept.id)
        
        return results
    
    async def generate_memory_insight(self,
                                   user_id: str,
                                   domain: str,
                                   related_memories: Optional[List[str]] = None) -> Optional[MemoryInsight]:
        """
        Generate an insight by analyzing patterns across memories.
        
        Args:
            user_id: The ID of the user
            domain: The domain or life area to generate insight for
            related_memories: Optional list of specific memory IDs to analyze
            
        Returns:
            A MemoryInsight object if successful, None otherwise
        """
        # Collect relevant memories
        if related_memories:
            memories = []
            for memory_id in related_memories:
                memory = await self.episodic.retrieve_memory(memory_id)
                if memory and memory.user_id == user_id:
                    memories.append(memory)
        else:
            # Search for relevant memories in the domain
            query = MemoryQuery(
                user_id=user_id,
                keywords=[domain],
                significance_threshold=0.6,
                limit=20
            )
            memories = await self.episodic.retrieve_memories_by_query(query)
        
        if not memories:
            logger.warning(f"Cannot generate insight: No relevant memories found for domain '{domain}'")
            return None
        
        # Create an initial basic insight description
        insight_title = f"Insight: Patterns in {domain}"
        insight_description = f"Based on analyzing {len(memories)} memories related to {domain}:\n\n"
        
        # Extract patterns (simplified implementation)
        # In a full implementation, this would use more sophisticated pattern recognition
        task_patterns = {}
        context_patterns = {}
        outcome_patterns = {}
        
        for memory in memories:
            # Analyze task-related memories
            for task_id in memory.related_tasks:
                task_patterns[task_id] = task_patterns.get(task_id, 0) + 1
            
            # Extract context patterns
            if "time of day" in memory.description.lower():
                for time in ["morning", "afternoon", "evening", "night"]:
                    if time in memory.description.lower():
                        context_patterns[time] = context_patterns.get(time, 0) + 1
            
            # Extract outcome patterns
            for outcome in ["successful", "completed", "struggled", "failed"]:
                if outcome in memory.description.lower():
                    outcome_patterns[outcome] = outcome_patterns.get(outcome, 0) + 1
        
        # Format the insight based on the patterns found
        if task_patterns:
            most_common_tasks = sorted(task_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
            insight_description += "Most common tasks:\n"
            for task_id, count in most_common_tasks:
                insight_description += f"- Task ID {task_id}: {count} occurrences\n"
            insight_description += "\n"
        
        if context_patterns:
            most_common_contexts = sorted(context_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
            insight_description += "Common contexts:\n"
            for context, count in most_common_contexts:
                insight_description += f"- {context.capitalize()}: {count} occurrences\n"
            insight_description += "\n"
        
        if outcome_patterns:
            most_common_outcomes = sorted(outcome_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
            insight_description += "Common outcomes:\n"
            for outcome, count in most_common_outcomes:
                insight_description += f"- {outcome.capitalize()}: {count} occurrences\n"
            insight_description += "\n"
        
        # Add action implications
        insight_description += "Potential implications:\n"
        
        if context_patterns:
            best_time = max(context_patterns.items(), key=lambda x: x[1])[0]
            insight_description += f"- Consider scheduling {domain} activities during the {best_time}\n"
        
        if outcome_patterns and "completed" in outcome_patterns and "failed" in outcome_patterns:
            if outcome_patterns["completed"] > outcome_patterns["failed"]:
                insight_description += f"- Current approach to {domain} seems effective\n"
            else:
                insight_description += f"- May need to revise approach to {domain}\n"
        
        # Create the insight
        insight = MemoryInsight(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=insight_title,
            description=insight_description,
            source_memories=[memory.id for memory in memories],
            confidence=0.7,
            domain=domain,
            generated_at=datetime.now(),
            action_implications=[],
            relevance_score=0.8
        )
        
        logger.info(f"Generated memory insight for domain '{domain}'")
        return insight
    
    # ----- Memory Retrieval and Integration -----
    
    async def retrieve_node_memories(self, user_id: str, node_id: str, limit: int = 5) -> List[EpisodicMemory]:
        """
        Retrieve memories related to a specific HTA node.
        
        Args:
            user_id: The ID of the user
            node_id: The ID of the node to retrieve memories for
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of EpisodicMemory objects related to the node
        """
        query = MemoryQuery(
            user_id=user_id,
            keywords=[],
            entities=[],
            memory_types=[],
            limit=limit
        )
        
        memories = await self.episodic.retrieve_memories_by_query(query)
        
        # Filter to only memories related to this node
        node_memories = [memory for memory in memories if node_id in memory.related_nodes]
        
        return node_memories
    
    async def retrieve_task_memories(self, user_id: str, task_id: str, limit: int = 5) -> List[EpisodicMemory]:
        """
        Retrieve memories related to a specific frontier task.
        
        Args:
            user_id: The ID of the user
            task_id: The ID of the task to retrieve memories for
            limit: Maximum number of memories to retrieve
            
        Returns:
            List of EpisodicMemory objects related to the task
        """
        query = MemoryQuery(
            user_id=user_id,
            keywords=[],
            entities=[],
            memory_types=[],
            limit=limit
        )
        
        memories = await self.episodic.retrieve_memories_by_query(query)
        
        # Filter to only memories related to this task
        task_memories = [memory for memory in memories if task_id in memory.related_tasks]
        
        return task_memories
    
    async def retrieve_domain_insights(self, user_id: str, domain: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieve insights and knowledge related to a specific domain.
        
        Args:
            user_id: The ID of the user
            domain: The domain to retrieve insights for
            limit: Maximum number of insights to retrieve
            
        Returns:
            List of dictionaries with insight information
        """
        # Find concepts in this domain
        concepts = await self.semantic.find_concepts_by_category(domain)
        
        # Filter to this user's concepts
        user_concepts = [concept for concept in concepts if concept.user_id == user_id]
        
        # Sort by priority and confidence
        user_concepts.sort(key=lambda c: (c.priority.value, c.confidence), reverse=True)
        
        # Format as insights
        insights = []
        for concept in user_concepts[:limit]:
            insights.append({
                "id": concept.id,
                "title": concept.concept_name,
                "content": concept.definition,
                "confidence": concept.confidence,
                "priority": concept.priority.value,
                "last_reinforced": concept.last_reinforced
            })
        
        return insights
    
    async def enhance_task_with_memory(self, user_id: str, task: FrontierTask) -> FrontierTask:
        """
        Enhance a frontier task with relevant memories and insights.
        
        Args:
            user_id: The ID of the user
            task: The FrontierTask to enhance
            
        Returns:
            The enhanced FrontierTask
        """
        # Get related memories
        memories = await self.retrieve_task_memories(user_id, task.id)
        
        # Extract insights from memories
        if not task.attributes:
            task.attributes = {}
        
        if memories:
            memory_summaries = []
            for memory in memories:
                summary = {
                    "memory_id": memory.id,
                    "title": memory.title,
                    "summary": memory.description[:100] + "..." if len(memory.description) > 100 else memory.description,
                    "emotional_valence": memory.emotional_valence
                }
                memory_summaries.append(summary)
            
            task.attributes["related_memories"] = memory_summaries
        
        # Add relevant domain insights if available
        # This could be based on the task title or description
        domain_keywords = [word.lower() for word in task.title.split() if len(word) > 3]
        
        for keyword in domain_keywords:
            insights = await self.retrieve_domain_insights(user_id, keyword)
            if insights:
                if "domain_insights" not in task.attributes:
                    task.attributes["domain_insights"] = []
                task.attributes["domain_insights"].extend(insights)
        
        return task
    
    async def enhance_node_with_memory(self, user_id: str, node: HTANode) -> HTANode:
        """
        Enhance an HTA node with relevant memories and insights.
        
        Args:
            user_id: The ID of the user
            node: The HTANode to enhance
            
        Returns:
            The enhanced HTANode
        """
        # This would typically modify the node's attributes
        # For now, we'll just simulate this
        
        # Get related memories
        memories = await self.retrieve_node_memories(user_id, node.id)
        
        # Extract insights from memories
        if memories:
            logger.info(f"Enhanced node {node.id} ({node.title}) with {len(memories)} memories")
        
        return node
    
    async def retrieve_memory_based_context(self, user_id: str, current_context: UserContext) -> Dict[str, Any]:
        """
        Retrieve memories and insights relevant to the current context.
        
        Args:
            user_id: The ID of the user
            current_context: The current user context
            
        Returns:
            Dictionary with relevant memories and insights
        """
        relevant_memories = []
        relevant_insights = []
        
        # Find memories with similar context
        if current_context.location:
            query = MemoryQuery(
                user_id=user_id,
                location=current_context.location,
                limit=5
            )
            location_memories = await self.episodic.retrieve_memories_by_query(query)
            relevant_memories.extend(location_memories)
        
        if current_context.time_of_day:
            # Find memories from similar time of day
            query = MemoryQuery(
                user_id=user_id,
                keywords=[current_context.time_of_day],
                limit=5
            )
            time_memories = await self.episodic.retrieve_memories_by_query(query)
            
            # Add only new memories
            existing_ids = [memory.id for memory in relevant_memories]
            for memory in time_memories:
                if memory.id not in existing_ids:
                    relevant_memories.append(memory)
        
        # Format memory information
        memory_info = []
        for memory in relevant_memories:
            memory_info.append({
                "id": memory.id,
                "title": memory.title,
                "summary": memory.description[:100] + "..." if len(memory.description) > 100 else memory.description,
                "relevance": "location" if current_context.location and current_context.location in memory.description else "time"
            })
        
        # Find relevant domain insights based on context factors
        factor_domains = set()
        for factor in current_context.factors.values():
            if isinstance(factor.value, (int, float)) and factor.value > 0.7:
                factor_domains.add(factor.name)
        
        for domain in factor_domains:
            insights = await self.retrieve_domain_insights(user_id, domain, limit=2)
            relevant_insights.extend(insights)
        
        return {
            "memories": memory_info,
            "insights": relevant_insights
        }
