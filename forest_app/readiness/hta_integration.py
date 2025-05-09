# forest_app/readiness/hta_integration.py
"""
Integration between the HTA Tree system and the Contextual Readiness Framework.
This module extends HTANode and HTATree classes with readiness protocol capabilities.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple

from .models import (
    FrontierTask,
    ReadinessProtocol,
    ProtocolType,
    TaskReadiness
)
from .readiness_service import ReadinessService

from ..hta_tree.hta_tree import HTANode, HTATree
from ..hta_tree.hta_models import HTANodeModel

logger = logging.getLogger(__name__)


class ReadinessAwareHTANode(HTANode):
    """
    Extended HTANode with readiness protocol capabilities.
    
    This class adds the ability to generate and manage readiness protocols
    for frontier tasks associated with the node.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.frontier_tasks: List[FrontierTask] = []
        self.readiness_service = None  # Will be initialized when needed
    
    def _ensure_readiness_service(self):
        """Ensure the readiness service is initialized"""
        if self.readiness_service is None:
            self.readiness_service = ReadinessService()
    
    async def generate_frontier_tasks(self, count: int = 5, user_id: str = None) -> List[FrontierTask]:
        """
        Generate frontier tasks with readiness protocols.
        
        Args:
            count: Number of tasks to generate
            user_id: User ID for context awareness
            
        Returns:
            List of generated frontier tasks with readiness protocols
        """
        self._ensure_readiness_service()
        
        # Create base tasks (in a real implementation, this would use the LLM)
        base_tasks = []
        
        for i in range(count):
            task = FrontierTask(
                node_id=self.id,
                title=f"Task {i+1} for {self.title}",
                description=f"Generated task {i+1} related to: {self.description}"
            )
            base_tasks.append(task)
        
        # Enhance with readiness protocols if user_id provided
        if user_id:
            enhanced_tasks = []
            for task in base_tasks:
                enhanced_task = await self.readiness_service.prepare_task(task, user_id)
                enhanced_tasks.append(enhanced_task)
            self.frontier_tasks = enhanced_tasks
            return enhanced_tasks
        else:
            self.frontier_tasks = base_tasks
            return base_tasks
    
    async def update_frontier_task(self, task_id: str, new_status: str = None, 
                                user_id: str = None, protocol_feedback: Dict = None) -> Optional[FrontierTask]:
        """
        Update a frontier task and process any protocol feedback.
        
        Args:
            task_id: ID of the task to update
            new_status: New status to set (optional)
            user_id: User ID for tracking outcomes
            protocol_feedback: Feedback on protocol effectiveness
            
        Returns:
            Updated task or None if not found
        """
        # Find the task
        task = next((t for t in self.frontier_tasks if t.id == task_id), None)
        
        if not task:
            logger.warning(f"Task {task_id} not found for node {self.id}")
            return None
            
        # Update status if provided
        if new_status:
            task.update_status(new_status)
            
        # Process protocol feedback
        if protocol_feedback and user_id:
            self._ensure_readiness_service()
            
            for protocol_type_str, feedback_data in protocol_feedback.items():
                try:
                    protocol_type = ProtocolType(protocol_type_str)
                    
                    if "effectiveness" in feedback_data:
                        self.readiness_service.record_protocol_outcome(
                            task=task,
                            protocol_type=protocol_type,
                            effectiveness=feedback_data["effectiveness"],
                            user_feedback=feedback_data.get("comment"),
                            user_id=user_id
                        )
                except (ValueError, KeyError) as e:
                    logger.error(f"Error processing protocol feedback: {str(e)}")
                
        return task
    
    def get_frontier_tasks(self, status_filter: Optional[str] = None) -> List[FrontierTask]:
        """
        Get frontier tasks, optionally filtered by status.
        
        Args:
            status_filter: Optional status to filter by
            
        Returns:
            List of frontier tasks
        """
        if status_filter:
            return [t for t in self.frontier_tasks if t.status == status_filter]
        return self.frontier_tasks
    
    async def refresh_task_readiness(self, user_id: str) -> int:
        """
        Refresh readiness protocols for all tasks based on current context.
        
        Args:
            user_id: User ID for context awareness
            
        Returns:
            Number of tasks refreshed
        """
        if not self.frontier_tasks:
            return 0
            
        self._ensure_readiness_service()
        
        refreshed_count = 0
        
        for i, task in enumerate(self.frontier_tasks):
            if task.status == "pending" or task.status == "active":
                refreshed_task = await self.readiness_service.prepare_task(task, user_id)
                self.frontier_tasks[i] = refreshed_task
                refreshed_count += 1
                
        return refreshed_count
    
    @classmethod
    def from_hta_node(cls, node: HTANode, copy_children: bool = True) -> 'ReadinessAwareHTANode':
        """Convert a regular HTANode to a ReadinessAwareHTANode"""
        new_node = cls(
            id=node.id,
            title=node.title,
            description=node.description,
            status=node.status,
            priority=node.priority,
            magnitude=node.magnitude,
            is_milestone=node.is_milestone,
            depends_on=node.depends_on.copy() if node.depends_on else None,
            estimated_energy=node.estimated_energy,
            estimated_time=node.estimated_time,
            linked_tasks=node.linked_tasks.copy() if node.linked_tasks else None,
        )
        
        if copy_children and node.children:
            new_node.children = [
                cls.from_hta_node(child) if isinstance(child, HTANode) else child
                for child in node.children
            ]
            
        return new_node


class ReadinessAwareHTATree(HTATree):
    """
    Extended HTATree with readiness protocol capabilities.
    
    This class adds the ability to generate and manage readiness protocols
    for frontier tasks across the tree, with context-aware prioritization.
    """
    
    def __init__(self, root: Optional[ReadinessAwareHTANode] = None):
        super().__init__(root)
        self.readiness_service = ReadinessService()
    
    @classmethod
    def from_hta_tree(cls, tree: HTATree) -> 'ReadinessAwareHTATree':
        """Convert a regular HTATree to a ReadinessAwareHTATree"""
        if not tree or not tree.root:
            return cls()
            
        readiness_root = ReadinessAwareHTANode.from_hta_node(tree.root)
        return cls(root=readiness_root)
    
    async def generate_frontier_tasks_for_node(self, node_id: str, count: int = 5,
                                            user_id: str = None) -> List[FrontierTask]:
        """
        Generate frontier tasks with readiness protocols for a specific node.
        
        Args:
            node_id: ID of the node to generate tasks for
            count: Number of tasks to generate
            user_id: User ID for context awareness
            
        Returns:
            List of generated frontier tasks with readiness protocols
        """
        node = self.find_node_by_id(node_id)
        
        if not node:
            logger.warning(f"Node {node_id} not found")
            return []
            
        if not isinstance(node, ReadinessAwareHTANode):
            logger.warning(f"Node {node_id} is not readiness-aware, converting")
            # Create a converted node but don't replace it in the tree yet
            converted_node = ReadinessAwareHTANode.from_hta_node(node, copy_children=False)
            tasks = await converted_node.generate_frontier_tasks(count, user_id)
            return tasks
            
        return await node.generate_frontier_tasks(count, user_id)
    
    async def generate_all_frontier_tasks(self, leaf_nodes_only: bool = True,
                                       user_id: str = None) -> Dict[str, List[FrontierTask]]:
        """
        Generate frontier tasks for all applicable nodes.
        
        Args:
            leaf_nodes_only: Whether to only generate for leaf nodes
            user_id: User ID for context awareness
            
        Returns:
            Dictionary mapping node IDs to lists of frontier tasks
        """
        if not self.root:
            return {}
            
        tasks_by_node = {}
        
        # Get all nodes
        nodes = self.flatten_tree()
        
        # Filter to leaf nodes if requested
        if leaf_nodes_only:
            nodes = [node for node in nodes if not node.children]
            
        # Generate tasks for each node
        for node in nodes:
            if not isinstance(node, ReadinessAwareHTANode):
                # Convert node to readiness-aware
                node_id = node.id
                node_index = self._find_node_index(nodes, node_id)
                
                if node_index >= 0:
                    nodes[node_index] = ReadinessAwareHTANode.from_hta_node(node, copy_children=True)
                    node = nodes[node_index]
                    
                    # Update node in the tree
                    parent_id = self._find_parent_id(node_id)
                    if parent_id:
                        parent = self.find_node_by_id(parent_id)
                        if parent:
                            for i, child in enumerate(parent.children):
                                if hasattr(child, 'id') and child.id == node_id:
                                    parent.children[i] = node
                    elif node_id == self.root.id:
                        self.root = node
                        
            node_tasks = await node.generate_frontier_tasks(5, user_id)
            tasks_by_node[node.id] = node_tasks
            
        return tasks_by_node
    
    async def update_frontier_task(self, node_id: str, task_id: str, new_status: str = None,
                                user_id: str = None, protocol_feedback: Dict = None) -> Optional[FrontierTask]:
        """
        Update a frontier task in a specific node.
        
        Args:
            node_id: ID of the node containing the task
            task_id: ID of the task to update
            new_status: New status to set (optional)
            user_id: User ID for tracking outcomes
            protocol_feedback: Feedback on protocol effectiveness
            
        Returns:
            Updated task or None if not found
        """
        node = self.find_node_by_id(node_id)
        
        if not node:
            logger.warning(f"Node {node_id} not found")
            return None
            
        if not isinstance(node, ReadinessAwareHTANode):
            logger.warning(f"Node {node_id} is not readiness-aware")
            return None
            
        return await node.update_frontier_task(task_id, new_status, user_id, protocol_feedback)
    
    def get_all_frontier_tasks(self, status_filter: Optional[str] = None) -> Dict[str, List[FrontierTask]]:
        """
        Get all frontier tasks across the tree.
        
        Args:
            status_filter: Optional status to filter by
            
        Returns:
            Dictionary mapping node IDs to lists of frontier tasks
        """
        tasks_by_node = {}
        
        if not self.root:
            return tasks_by_node
            
        # Get all nodes
        nodes = self.flatten_tree()
        
        # Collect tasks from each node
        for node in nodes:
            if isinstance(node, ReadinessAwareHTANode) and node.frontier_tasks:
                if status_filter:
                    filtered_tasks = [t for t in node.frontier_tasks if t.status == status_filter]
                    if filtered_tasks:
                        tasks_by_node[node.id] = filtered_tasks
                else:
                    tasks_by_node[node.id] = node.frontier_tasks
                    
        return tasks_by_node
    
    async def get_prioritized_frontier_tasks(self, user_id: str, 
                                          limit: int = 10) -> List[Tuple[str, FrontierTask]]:
        """
        Get frontier tasks prioritized by relevance to current context.
        
        Args:
            user_id: User ID for context awareness
            limit: Maximum number of tasks to return
            
        Returns:
            List of (node_id, task) tuples sorted by relevance
        """
        # Refresh user context
        await self.readiness_service.context_collector.refresh_context(user_id)
        
        all_tasks = []
        
        # Get all pending and active tasks
        tasks_by_node = self.get_all_frontier_tasks(status_filter=None)
        
        for node_id, tasks in tasks_by_node.items():
            for task in tasks:
                if task.status in ["pending", "active"]:
                    if task.context_relevance is None:
                        # If relevance not calculated yet, use readiness
                        relevance = task.readiness.overall_readiness if task.readiness else 0.5
                    else:
                        relevance = task.context_relevance
                        
                    all_tasks.append((relevance, node_id, task))
        
        # Sort by relevance (descending)
        all_tasks.sort(reverse=True)
        
        # Return limited number of tasks
        return [(node_id, task) for _, node_id, task in all_tasks[:limit]]
    
    async def refresh_all_tasks(self, user_id: str) -> int:
        """
        Refresh readiness protocols for all pending and active tasks.
        
        Args:
            user_id: User ID for context awareness
            
        Returns:
            Number of tasks refreshed
        """
        total_refreshed = 0
        
        if not self.root:
            return total_refreshed
            
        # Get all nodes
        nodes = self.flatten_tree()
        
        # Refresh tasks for each node
        for node in nodes:
            if isinstance(node, ReadinessAwareHTANode):
                node_refreshed = await node.refresh_task_readiness(user_id)
                total_refreshed += node_refreshed
                
        return total_refreshed
    
    def _find_node_index(self, nodes: List[HTANode], node_id: str) -> int:
        """Find the index of a node in a list by ID"""
        for i, node in enumerate(nodes):
            if node.id == node_id:
                return i
        return -1
    
    def _find_parent_id(self, node_id: str) -> Optional[str]:
        """Find the parent ID of a node"""
        if not self.root or self.root.id == node_id:
            return None
            
        queue = [(None, self.root)]
        
        while queue:
            parent_id, current = queue.pop(0)
            
            if current.id == node_id:
                return parent_id
                
            if hasattr(current, 'children'):
                for child in current.children:
                    if isinstance(child, HTANode):
                        queue.append((current.id, child))
                        
        return None
