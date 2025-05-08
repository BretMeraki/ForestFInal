"""
Examples demonstrating the integration of the Semantic-Episodic Memory System
with the existing Forest app components.

These examples show how the memory system serves as the foundation for
transforming Forest into a true life co-founder.
"""

import asyncio
import uuid
from datetime import datetime, timedelta

from ..hta_tree.hta_tree import HTANode, HTATree
from ..readiness.models import FrontierTask, UserContext, ContextFactor, ContextFactorType
from ..readiness.readiness_service import ReadinessService

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
from .memory_service import MemoryService

# Create a sample user and context
SAMPLE_USER_ID = "user-123"

async def create_sample_context():
    """Create a sample user context"""
    context = UserContext(
        user_id=SAMPLE_USER_ID,
        time_of_day="morning",
        location="home office",
        device_context={"device": "laptop", "apps_running": ["browser", "calendar"]}
    )
    
    # Add some context factors
    focus_factor = ContextFactor(
        id=str(uuid.uuid4()),
        name="focus_level",
        type=ContextFactorType.PERSONAL,
        value=0.8,
        confidence=0.9,
        influence_score=0.7
    )
    
    energy_factor = ContextFactor(
        id=str(uuid.uuid4()),
        name="energy_level",
        type=ContextFactorType.PERSONAL,
        value=0.7,
        confidence=0.8,
        influence_score=0.6
    )
    
    weather_factor = ContextFactor(
        id=str(uuid.uuid4()),
        name="weather",
        type=ContextFactorType.ENVIRONMENTAL,
        value="sunny",
        confidence=1.0,
        influence_score=0.3
    )
    
    context.factors = {
        focus_factor.id: focus_factor,
        energy_factor.id: energy_factor,
        weather_factor.id: weather_factor
    }
    
    return context

async def example_memory_task_integration():
    """
    Example: Integrating memory with frontier tasks
    
    Shows how memory enriches task experiences and builds 
    a narrative of the user's journey.
    """
    print("\n=== Example: Memory-Task Integration ===")
    
    # Initialize services
    memory_service = MemoryService()
    readiness_service = ReadinessService()
    
    # Create a sample context
    context = await create_sample_context()
    
    # Create a sample task
    task = FrontierTask(
        id=str(uuid.uuid4()),
        node_id="node-abc",
        title="Complete project proposal",
        description="Finalize the project proposal document with executive summary",
        status="pending",
        priority=0.8
    )
    
    # First, let's prepare the task with readiness protocols
    prepared_task = await readiness_service.prepare_task(task, SAMPLE_USER_ID)
    print(f"Task prepared: {prepared_task.title} with readiness: {prepared_task.readiness}")
    
    # Now, let's record a memory of working on this task
    memory_result = await memory_service.remember_task_experience(
        user_id=SAMPLE_USER_ID,
        task=prepared_task,
        outcome="Completed the proposal ahead of schedule with positive feedback",
        user_feedback="I found I was much more productive in the morning with fewer distractions",
        context=context,
        emotional_valence=0.7,  # Positive experience
        emotional_arousal=0.6   # Moderately engaging
    )
    
    print(f"Created memory: {memory_result['episodic_memory_id']}")
    if memory_result['semantic_concepts']:
        print(f"Extracted concepts: {len(memory_result['semantic_concepts'])}")
    
    # Later, when we encounter a similar task, we can enhance it with memories
    # Create another similar task
    new_task = FrontierTask(
        id=str(uuid.uuid4()),
        node_id="node-def",
        title="Draft marketing proposal",
        description="Create a marketing proposal for the new product launch",
        status="pending",
        priority=0.7
    )
    
    # Enhance the new task with relevant memories
    enhanced_task = await memory_service.enhance_task_with_memory(SAMPLE_USER_ID, new_task)
    
    print("\nEnhanced task with memories:")
    if enhanced_task.attributes and 'related_memories' in enhanced_task.attributes:
        for memory in enhanced_task.attributes['related_memories']:
            print(f"- Related memory: {memory['title']}")
    if enhanced_task.attributes and 'domain_insights' in enhanced_task.attributes:
        for insight in enhanced_task.attributes['domain_insights']:
            print(f"- Insight: {insight['title']}")
    
    return memory_service, enhanced_task

async def example_memory_node_integration():
    """
    Example: Integrating memory with HTA nodes
    
    Shows how memory creates a rich context around HTA nodes
    and helps build strategic understanding.
    """
    print("\n=== Example: Memory-Node Integration ===")
    
    # Initialize services
    memory_service = MemoryService()
    
    # Create a sample HTA node
    node = HTANode(
        id="node-xyz",
        title="Launch new product",
        description="Oversee the launch of the new product line",
        status="active",
        priority=0.9,
        magnitude=8.0,
        is_milestone=True
    )
    
    # Record a memory of a significant interaction with this node
    memory_result = await memory_service.remember_node_interaction(
        user_id=SAMPLE_USER_ID,
        node=node,
        interaction_type="milestone_planning",
        details="Broke down the product launch into 5 key phases with success criteria",
        context=await create_sample_context()
    )
    
    print(f"Created node memory: {memory_result['episodic_memory_id']}")
    
    # Now imagine we're coming back to this node later
    # Let's retrieve memories related to this node
    node_memories = await memory_service.retrieve_node_memories(SAMPLE_USER_ID, node.id)
    
    print("\nMemories related to this node:")
    for memory in node_memories:
        print(f"- {memory.title}: {memory.description[:100]}...")
    
    # Let's also enhance the node with memory
    enhanced_node = await memory_service.enhance_node_with_memory(SAMPLE_USER_ID, node)
    
    return memory_service, enhanced_node

async def example_semantic_memory_building():
    """
    Example: Building semantic memory of user preferences
    
    Shows how the system builds an understanding of the user's
    preferences, patterns, and knowledge.
    """
    print("\n=== Example: Semantic Memory Building ===")
    
    # Initialize services
    memory_service = MemoryService()
    
    # Record various user preferences
    work_style_result = await memory_service.remember_user_preference(
        user_id=SAMPLE_USER_ID,
        preference_type="work_style",
        preference_value="Prefers focused deep work in the morning with no interruptions",
        source="Observed work patterns and explicit statement",
        confidence=0.9
    )
    
    communication_result = await memory_service.remember_user_preference(
        user_id=SAMPLE_USER_ID,
        preference_type="communication_style",
        preference_value="Prefers concise, direct communication with visual aids",
        source="Response to different communication approaches",
        confidence=0.8
    )
    
    print(f"Created work style preference: {work_style_result['semantic_concept_id']}")
    print(f"Created communication preference: {communication_result['semantic_concept_id']}")
    
    # Record a conversation that reveals more preferences
    conversation_result = await memory_service.remember_conversation(
        user_id=SAMPLE_USER_ID,
        conversation_topic="Project management approach",
        highlights=[
            "Prefers agile approach with 2-week sprints",
            "Wants more frequent check-ins for high-priority projects",
            "Values documentation but doesn't want it to slow down progress"
        ],
        emotional_valence=0.4  # Slightly positive
    )
    
    print(f"Recorded conversation: {conversation_result['episodic_memory_id']}")
    
    # Generate an insight about work patterns
    insight = await memory_service.generate_memory_insight(
        user_id=SAMPLE_USER_ID,
        domain="work_effectiveness"
    )
    
    if insight:
        print(f"\nGenerated insight: {insight.title}")
        print(f"Description: {insight.description[:150]}...")
    
    return memory_service

async def example_contextual_retrieval():
    """
    Example: Context-based memory retrieval
    
    Shows how the system can retrieve relevant memories based on
    the current context, enabling it to function as a co-founder.
    """
    print("\n=== Example: Contextual Memory Retrieval ===")
    
    # Initialize services
    memory_service = MemoryService()
    
    # Create a current context
    current_context = await create_sample_context()
    
    # Retrieve memories relevant to this context
    context_memories = await memory_service.retrieve_memory_based_context(
        user_id=SAMPLE_USER_ID,
        current_context=current_context
    )
    
    print("\nMemories relevant to current context:")
    if 'memories' in context_memories and context_memories['memories']:
        for memory in context_memories['memories']:
            print(f"- {memory['title']} (Relevance: {memory['relevance']})")
    else:
        print("No relevant memories found for this context")
    
    print("\nInsights relevant to current context:")
    if 'insights' in context_memories and context_memories['insights']:
        for insight in context_memories['insights']:
            print(f"- {insight['title']}")
    else:
        print("No relevant insights found for this context")
    
    # Now demonstrate natural language memory query
    memory_retrieval = memory_service.episodic.memory_retrieval
    
    # Example NL queries (these would work if we had populated more memories)
    print("\nExample natural language memory queries (no results expected in demo):")
    queries = [
        "What did I work on yesterday?",
        "Show me my progress on the product launch",
        "When did I last feel stressed about a deadline?",
        "What projects have I completed successfully this month?"
    ]
    
    for query in queries:
        print(f"- '{query}'")
    
    return memory_service, current_context

async def run_all_examples():
    """Run all memory integration examples"""
    print("\n=== FOREST MEMORY SYSTEM INTEGRATION EXAMPLES ===")
    print("Demonstrating how semantic-episodic memory transforms Forest into a life co-founder")
    
    try:
        # Run all examples
        await example_memory_task_integration()
        await example_memory_node_integration()
        await example_semantic_memory_building()
        await example_contextual_retrieval()
        
        print("\n=== All examples completed successfully ===")
        print("The memory system is now ready to be integrated with the Forest application")
        
    except Exception as e:
        print(f"Error running examples: {e}")

if __name__ == "__main__":
    # Run the examples
    asyncio.run(run_all_examples())
