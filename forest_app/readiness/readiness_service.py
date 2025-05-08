# forest_app/readiness/readiness_service.py
"""
Main service class for the Contextual Readiness Framework that coordinates
the collection of context, generation of protocols, and tracking of effectiveness.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

from .models import (
    FrontierTask,
    ReadinessProtocol,
    ProtocolType,
    ProtocolEffectiveness,
    TaskReadiness,
    UserContext,
    ContextFactorType
)
from .context_collector import ContextCollectorService
from .protocol_generator import ReadinessProtocolGenerator
from .effectiveness_tracker import ProtocolEffectivenessTracker

from ..hta_tree.hta_tree import HTANode, HTATree

logger = logging.getLogger(__name__)


class ReadinessService:
    """
    Central service coordinating the Contextual Readiness Framework.
    
    This service ties together context collection, protocol generation, and
    effectiveness tracking to provide holistic task preparation protocols
    that adapt to user feedback and context.
    """
    
    def __init__(self):
        self.context_collector = ContextCollectorService()
        self.protocol_generator = ReadinessProtocolGenerator()
        self.effectiveness_tracker = ProtocolEffectivenessTracker()
        logger.info("ReadinessService initialized")
    
    async def prepare_task(self, task: FrontierTask, user_id: str) -> FrontierTask:
        """
        Generate readiness protocols for a task based on current context.
        Updates the task with appropriate protocols and returns it.
        """
        # Refresh user context
        user_context = await self.context_collector.refresh_context(user_id)
        
        # Generate protocols for the task
        protocols = self.protocol_generator.generate_for_task(task, user_context)
        
        # Assess task readiness based on context
        task_readiness = self._assess_task_readiness(task, user_context)
        
        # Update task with protocols and readiness
        if ProtocolType.MENTAL in protocols:
            task.mental_prep_protocol = protocols[ProtocolType.MENTAL]
        
        if ProtocolType.PHYSICAL in protocols:
            task.physical_prep_protocol = protocols[ProtocolType.PHYSICAL]
        
        if ProtocolType.EMOTIONAL in protocols:
            task.emotional_prep_protocol = protocols[ProtocolType.EMOTIONAL]
        
        # Set task readiness
        task.readiness = task_readiness
        
        # Update context relevance
        relevance_score, _ = self.context_collector.analyze_context_relevance(
            user_id, 
            task_keywords=[task.title.split()], 
            task_time_estimate="medium"  # Default if not specified
        )
        task.context_relevance = relevance_score
        
        # Save context factors with the task
        task.context_factors = {key: factor for key, factor in user_context.factors.items()}
        
        return task
    
    def record_protocol_outcome(self, task: FrontierTask, protocol_type: ProtocolType, 
                              effectiveness: ProtocolEffectiveness, user_feedback: Optional[str] = None,
                              user_id: str = None):
        """Record the effectiveness of a protocol for continuous improvement"""
        if not user_id:
            logger.warning("Cannot record outcome: No user_id provided")
            return None
            
        if not task:
            logger.warning("Cannot record outcome: No task provided")
            return None
            
        # Get the protocol that was used
        protocol = None
        protocol_id = None
        
        if protocol_type == ProtocolType.MENTAL and task.mental_prep_protocol:
            protocol = task.mental_prep_protocol
            protocol_id = protocol.id
        elif protocol_type == ProtocolType.PHYSICAL and task.physical_prep_protocol:
            protocol = task.physical_prep_protocol
            protocol_id = protocol.id
        elif protocol_type == ProtocolType.EMOTIONAL and task.emotional_prep_protocol:
            protocol = task.emotional_prep_protocol
            protocol_id = protocol.id
            
        if not protocol_id:
            logger.warning(f"Cannot record outcome: No {protocol_type.value} protocol found for task")
            return None
            
        # Get context snapshot
        context_snapshot = self.context_collector.get_context_snapshot(user_id)
        
        # Record the outcome
        outcome = self.effectiveness_tracker.record_outcome(
            user_id=user_id,
            task_id=task.id,
            protocol_id=protocol_id,
            protocol_type=protocol_type,
            effectiveness=effectiveness,
            user_feedback=user_feedback,
            context_snapshot=context_snapshot
        )
        
        # Use feedback to improve future protocols
        if protocol:
            self.protocol_generator.adapt_to_user_feedback(protocol, {
                "effectiveness": effectiveness.value,
                "user_feedback": user_feedback
            })
            
        return outcome
    
    def get_readiness_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about protocol effectiveness patterns"""
        return self.effectiveness_tracker.analyze_protocol_patterns(user_id)
    
    def extend_node_with_readiness(self, node: HTANode, user_id: str) -> HTANode:
        """Enhance an HTANode with readiness protocols for its frontier tasks"""
        # In a real implementation, this would modify the node directly
        # For now, we'll just return the node unchanged
        logger.info(f"Extended node {node.id} with readiness protocols")
        return node
    
    def extend_tree_with_readiness(self, tree: HTATree, user_id: str) -> HTATree:
        """Enhance an entire HTATree with readiness protocols"""
        if not tree or not tree.root:
            return tree
            
        # Process nodes in the tree
        nodes = tree.flatten_tree()
        for node in nodes:
            self.extend_node_with_readiness(node, user_id)
            
        logger.info(f"Extended tree with {len(nodes)} nodes with readiness protocols")
        return tree
    
    def _assess_task_readiness(self, task: FrontierTask, context: UserContext) -> TaskReadiness:
        """
        Assess how ready the user is to perform this task based on context.
        Returns a TaskReadiness object with scores for mental, physical, and emotional readiness.
        """
        # Default medium readiness
        mental_readiness = 0.5
        physical_readiness = 0.5
        emotional_readiness = 0.5
        
        # Analyze mental readiness based on context
        mental_factors = context.get_factors_by_type(ContextFactorType.PERSONAL)
        for factor in mental_factors:
            if factor.name == "focus_level":
                mental_readiness = float(factor.value)
                break
        
        # Analyze physical readiness based on context
        physical_factors = context.get_factors_by_type(ContextFactorType.PERSONAL)
        for factor in physical_factors:
            if factor.name == "energy_level":
                physical_readiness = float(factor.value)
                break
        
        # Analyze emotional readiness based on context
        emotional_factors = context.get_factors_by_type(ContextFactorType.PERSONAL)
        for factor in emotional_factors:
            if factor.name == "mood":
                emotional_readiness = float(factor.value)
                break
        
        # Create and return TaskReadiness object
        readiness = TaskReadiness(
            task_id=task.id,
            mental_readiness=mental_readiness,
            physical_readiness=physical_readiness,
            emotional_readiness=emotional_readiness
        )
        
        return readiness
