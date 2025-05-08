# forest_app/readiness/examples.py
"""
Examples demonstrating the use of the Contextual Readiness Framework
to enhance the HTA Tree system with holistic task preparation guidance.
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Any

from .models import (
    FrontierTask,
    ContextFactor,
    ContextFactorType,
    ProtocolType,
    ProtocolEffectiveness
)
from .readiness_service import ReadinessService
from .context_collector import ContextCollectorService
from ..hta_tree.hta_tree import HTANode, HTATree

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def simulate_basic_readiness_flow():
    """Demonstrate the basic flow of the Contextual Readiness Framework"""
    print("\n=== Basic Readiness Flow Example ===")
    
    # Initialize services
    readiness_service = ReadinessService()
    
    # Create a simulated user ID
    user_id = "test_user_123"
    
    # Add some manual context factors
    await add_sample_context(readiness_service, user_id)
    
    # Create a sample frontier task
    task = FrontierTask(
        node_id="sample_node_1",
        title="Write a project proposal",
        description="Draft a 2-page proposal for the new client project, focusing on deliverables and timeline."
    )
    
    # Prepare the task with readiness protocols
    prepared_task = await readiness_service.prepare_task(task, user_id)
    
    # Print the task with its protocols
    print_task_with_protocols(prepared_task)
    
    # Simulate user feedback on protocol effectiveness
    if prepared_task.mental_prep_protocol:
        readiness_service.record_protocol_outcome(
            prepared_task,
            ProtocolType.MENTAL,
            ProtocolEffectiveness.EFFECTIVE,
            user_feedback="The mental preparation helped me focus",
            user_id=user_id
        )
    
    if prepared_task.physical_prep_protocol:
        readiness_service.record_protocol_outcome(
            prepared_task,
            ProtocolType.PHYSICAL,
            ProtocolEffectiveness.HIGHLY_EFFECTIVE,
            user_feedback="The workspace setup made a big difference",
            user_id=user_id
        )
    
    if prepared_task.emotional_prep_protocol:
        readiness_service.record_protocol_outcome(
            prepared_task,
            ProtocolType.EMOTIONAL,
            ProtocolEffectiveness.NEUTRAL,
            user_feedback="Didn't really need emotional prep for this task",
            user_id=user_id
        )
    
    # Get readiness insights after some usage
    insights = readiness_service.get_readiness_insights(user_id)
    print("\n=== Readiness Insights ===")
    print(f"Total protocols used: {insights.get('total_protocols_used', 0)}")
    print("Insights:")
    for insight in insights.get('insights', []):
        print(f"- {insight}")


async def simulate_hta_integration():
    """Demonstrate integration with the HTA Tree system"""
    print("\n=== HTA Integration Example ===")
    
    # Initialize the readiness service
    readiness_service = ReadinessService()
    
    # Create a simulated user ID
    user_id = "test_user_123"
    
    # Create a simple HTA tree
    root = HTANode(
        id="root",
        title="Complete Project X",
        description="Finish Project X by the end of the quarter",
        status="active",
        priority=0.9,
        magnitude=9.0
    )
    
    child1 = HTANode(
        id="child1",
        title="Research Phase",
        description="Complete initial research for Project X",
        status="active",
        priority=0.8,
        magnitude=6.0
    )
    
    child2 = HTANode(
        id="child2",
        title="Development Phase",
        description="Build the core functionality",
        status="pending",
        priority=0.7,
        magnitude=8.0
    )
    
    root.children = [child1, child2]
    
    # Create the tree
    tree = HTATree(root=root)
    
    # Enhance the tree with readiness protocols
    enhanced_tree = readiness_service.extend_tree_with_readiness(tree, user_id)
    
    # Create frontier tasks for a node
    tasks = generate_sample_frontier_tasks(child1)
    
    # Prepare each task with readiness protocols
    for i, task in enumerate(tasks):
        prepared_task = await readiness_service.prepare_task(task, user_id)
        print(f"\n--- Frontier Task {i+1}: {prepared_task.title} ---")
        print(f"Mental Readiness: {prepared_task.readiness.mental_readiness:.2f}")
        print(f"Physical Readiness: {prepared_task.readiness.physical_readiness:.2f}")
        print(f"Emotional Readiness: {prepared_task.readiness.emotional_readiness:.2f}")
        print(f"Overall Readiness: {prepared_task.readiness.overall_readiness:.2f}")
        print(f"Context Relevance: {prepared_task.context_relevance:.2f}")


async def add_sample_context(readiness_service: ReadinessService, user_id: str):
    """Add sample context factors for demonstration"""
    # Add personal factors
    readiness_service.context_collector.add_manual_context(
        user_id, ContextFactorType.PERSONAL, "energy_level", 0.7
    )
    
    readiness_service.context_collector.add_manual_context(
        user_id, ContextFactorType.PERSONAL, "focus_level", 0.8
    )
    
    readiness_service.context_collector.add_manual_context(
        user_id, ContextFactorType.PERSONAL, "mood", 0.6
    )
    
    # Add environmental factors
    readiness_service.context_collector.add_manual_context(
        user_id, ContextFactorType.ENVIRONMENTAL, "noise_level", "low"
    )
    
    readiness_service.context_collector.add_manual_context(
        user_id, ContextFactorType.ENVIRONMENTAL, "location", "home_office"
    )
    
    # Add task history factor
    readiness_service.context_collector.add_manual_context(
        user_id, ContextFactorType.TASK_HISTORY, "similar_task_success_rate", 0.85
    )


def generate_sample_frontier_tasks(node: HTANode) -> List[FrontierTask]:
    """Generate sample frontier tasks for a node"""
    tasks = []
    
    # Create 5 sample tasks
    tasks.append(FrontierTask(
        node_id=node.id,
        title=f"Review literature on {node.title}",
        description=f"Find and read 3-5 research papers related to {node.title}"
    ))
    
    tasks.append(FrontierTask(
        node_id=node.id,
        title=f"Create outline for {node.title}",
        description=f"Develop a structured outline for {node.title} including key points to address"
    ))
    
    tasks.append(FrontierTask(
        node_id=node.id,
        title=f"Collect data for {node.title}",
        description=f"Gather and organize necessary data to support {node.title}"
    ))
    
    tasks.append(FrontierTask(
        node_id=node.id,
        title=f"Draft initial findings for {node.title}",
        description=f"Write up preliminary findings based on the research for {node.title}"
    ))
    
    tasks.append(FrontierTask(
        node_id=node.id,
        title=f"Schedule review meeting for {node.title}",
        description=f"Set up a meeting with stakeholders to review progress on {node.title}"
    ))
    
    return tasks


def print_task_with_protocols(task: FrontierTask):
    """Print a task with its readiness protocols"""
    print(f"\n=== Task: {task.title} ===")
    print(f"Description: {task.description}")
    print(f"Context Relevance: {task.context_relevance:.2f}")
    
    if task.readiness:
        print(f"Overall Readiness Score: {task.readiness.overall_readiness:.2f}")
    
    # Print mental protocol
    if task.mental_prep_protocol:
        print("\n--- Mental Preparation Protocol ---")
        print(f"Estimated Time: {task.mental_prep_protocol.estimated_total_time_seconds // 60} minutes")
        for i, step in enumerate(task.mental_prep_protocol.steps):
            print(f"{i+1}. {step.title} ({step.duration_seconds // 60} min)")
            print(f"   {step.description}")
    
    # Print physical protocol
    if task.physical_prep_protocol:
        print("\n--- Physical Preparation Protocol ---")
        print(f"Estimated Time: {task.physical_prep_protocol.estimated_total_time_seconds // 60} minutes")
        for i, step in enumerate(task.physical_prep_protocol.steps):
            print(f"{i+1}. {step.title} ({step.duration_seconds // 60} min)")
            print(f"   {step.description}")
    
    # Print emotional protocol
    if task.emotional_prep_protocol:
        print("\n--- Emotional Preparation Protocol ---")
        print(f"Estimated Time: {task.emotional_prep_protocol.estimated_total_time_seconds // 60} minutes")
        for i, step in enumerate(task.emotional_prep_protocol.steps):
            print(f"{i+1}. {step.title} ({step.duration_seconds // 60} min)")
            print(f"   {step.description}")


async def main():
    """Run all example simulations"""
    await simulate_basic_readiness_flow()
    await simulate_hta_integration()


if __name__ == "__main__":
    asyncio.run(main())
