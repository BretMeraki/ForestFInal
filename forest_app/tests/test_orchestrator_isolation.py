"""
Tests to verify that ForestOrchestrator instances are properly isolated between requests.
"""

import pytest
import asyncio
from forest_app.core.orchestrator import ForestOrchestrator
from forest_app.snapshot.snapshot import MemorySnapshot
from forest_app.core.processors.reflection_processor import ReflectionProcessor
from forest_app.core.processors.completion_processor import CompletionProcessor
from forest_app.core.services.component_state_manager import ComponentStateManager
from forest_app.hta_tree.hta_service import HTAService
from forest_app.hta_tree.seed import SeedManager
from forest_app.config.constants import WITHERING_DECAY_FACTOR

class DummyReflectionProcessor(ReflectionProcessor):
    """Dummy reflection processor for testing."""
    def __init__(self):
        pass
    
    async def process(self, user_input: str, snapshot: MemorySnapshot) -> dict:
        return {"response": "dummy reflection"}

class DummyCompletionProcessor(CompletionProcessor):
    """Dummy completion processor for testing."""
    def __init__(self):
        pass
    
    async def process(self, task_id: str, success: bool, snapshot: MemorySnapshot, db=None, task_logger=None) -> dict:
        return {"response": "dummy completion"}

class DummyStateManager(ComponentStateManager):
    """Dummy state manager for testing."""
    def __init__(self):
        self.states = {}
    
    def load_states(self, snapshot: MemorySnapshot):
        pass
    
    def save_states(self, snapshot: MemorySnapshot):
        pass

class DummyHTAService(HTAService):
    """Dummy HTA service for testing."""
    def __init__(self):
        pass

class DummySeedManager(SeedManager):
    """Dummy seed manager for testing."""
    def __init__(self):
        pass
    
    async def get_primary_active_seed(self):
        return None
    
    async def plant_seed(self, intention: str, domain: str, addl_ctx: dict = None):
        return None

@pytest.fixture
def orchestrator():
    """Create a test orchestrator instance."""
    return ForestOrchestrator(
        reflection_processor=DummyReflectionProcessor(),
        completion_processor=DummyCompletionProcessor(),
        state_manager=DummyStateManager(),
        hta_service=DummyHTAService(),
        seed_manager=DummySeedManager()
    )

@pytest.mark.asyncio
async def test_orchestrator_isolation(orchestrator):
    """Test that different orchestrator instances are properly created."""
    # Create two snapshots
    snapshot1 = MemorySnapshot()
    snapshot2 = MemorySnapshot()
    
    # Set different initial states
    snapshot1.withering_level = 0.5
    snapshot2.withering_level = 0.8
    
    # Process reflections concurrently
    async def process_reflection(snapshot):
        return await orchestrator.process_reflection("test input", snapshot)
    
    results = await asyncio.gather(
        process_reflection(snapshot1),
        process_reflection(snapshot2)
    )
    
    # Verify results are independent
    assert results[0]["response"] == "dummy reflection"
    assert results[1]["response"] == "dummy reflection"
    
    # Verify snapshots remain isolated
    assert snapshot1.withering_level == 0.5
    assert snapshot2.withering_level == 0.8

@pytest.mark.asyncio
async def test_orchestrator_no_shared_state(orchestrator):
    """Test that orchestrator instances don't share state."""
    # Create two snapshots
    snapshot1 = MemorySnapshot()
    snapshot2 = MemorySnapshot()
    
    # Set different initial states
    snapshot1.withering_level = 0.5
    snapshot2.withering_level = 0.8
    
    # Process completions concurrently
    async def process_completion(snapshot):
        return await orchestrator.process_task_completion(
            task_id="test_task",
            success=True,
            snapshot=snapshot,
            db=None,
            task_logger=None
        )
    
    results = await asyncio.gather(
        process_completion(snapshot1),
        process_completion(snapshot2)
    )
    
    # Verify results are independent
    assert results[0]["response"] == "dummy completion"
    assert results[1]["response"] == "dummy completion"
    
    # Verify snapshots remain isolated
    assert snapshot1.withering_level == 0.5
    assert snapshot2.withering_level == 0.8

@pytest.mark.asyncio
async def test_withering_isolation(orchestrator):
    """Test that withering calculations are properly isolated."""
    # Create two snapshots with different states
    snapshot1 = MemorySnapshot()
    snapshot2 = MemorySnapshot()
    
    # Set different initial states
    snapshot1.withering_level = 0.5
    snapshot2.withering_level = 0.8
    
    # Process reflections concurrently
    async def process_reflection(snapshot):
        return await orchestrator.process_reflection("test input", snapshot)
    
    results = await asyncio.gather(
        process_reflection(snapshot1),
        process_reflection(snapshot2)
    )
    
    # Verify results are independent
    assert results[0]["response"] == "dummy reflection"
    assert results[1]["response"] == "dummy reflection"
    
    # Verify withering calculations are isolated
    assert snapshot1.withering_level == 0.5
    assert snapshot2.withering_level == 0.8

@pytest.mark.asyncio
async def test_concurrent_error_handling(orchestrator):
    """Test that errors in concurrent operations are properly isolated."""
    # Create two snapshots
    snapshot1 = MemorySnapshot()
    snapshot2 = MemorySnapshot()
    
    # Set different initial states
    snapshot1.withering_level = 0.5
    snapshot2.withering_level = 0.8
    
    # Process reflections concurrently with one failing
    async def process_reflection(snapshot, should_fail=False):
        if should_fail:
            raise Exception("Test error")
        return await orchestrator.process_reflection("test input", snapshot)
    
    # Run concurrent operations with one failing
    with pytest.raises(Exception):
        await asyncio.gather(
            process_reflection(snapshot1),
            process_reflection(snapshot2, should_fail=True)
        )
    
    # Verify the successful operation's snapshot is unchanged
    assert snapshot1.withering_level == 0.5 