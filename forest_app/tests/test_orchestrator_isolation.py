"""
Tests to verify that ForestOrchestrator instances are properly isolated between requests.
"""

import pytest
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
    
    async def process(self, *args, **kwargs):
        return {}

class DummyCompletionProcessor(CompletionProcessor):
    """Dummy completion processor for testing."""
    def __init__(self):
        pass
    
    async def process(self, *args, **kwargs):
        return {}

class DummyStateManager(ComponentStateManager):
    """Dummy state manager for testing."""
    def __init__(self):
        pass
    
    def load_states(self, *args, **kwargs):
        pass
    
    def save_states(self, *args, **kwargs):
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
    
    async def plant_seed(self, *args, **kwargs):
        return None
    
    async def evolve_seed(self, *args, **kwargs):
        return False

@pytest.fixture
def orchestrator1():
    """Create first orchestrator instance."""
    return ForestOrchestrator(
        reflection_processor=DummyReflectionProcessor(),
        completion_processor=DummyCompletionProcessor(),
        state_manager=DummyStateManager(),
        hta_service=DummyHTAService(),
        seed_manager=DummySeedManager()
    )

@pytest.fixture
def orchestrator2():
    """Create second orchestrator instance."""
    return ForestOrchestrator(
        reflection_processor=DummyReflectionProcessor(),
        completion_processor=DummyCompletionProcessor(),
        state_manager=DummyStateManager(),
        hta_service=DummyHTAService(),
        seed_manager=DummySeedManager()
    )

def test_orchestrator_isolation(orchestrator1, orchestrator2):
    """Test that different orchestrator instances are created."""
    assert orchestrator1 is not orchestrator2, "Orchestrator instances should be different"
    assert id(orchestrator1) != id(orchestrator2), "Orchestrator instances should have different IDs"

@pytest.mark.asyncio
async def test_orchestrator_no_shared_state(orchestrator1, orchestrator2):
    """Test that orchestrator instances don't share state."""
    # Create two snapshots with different states
    snapshot1 = MemorySnapshot()
    snapshot1.withering_level = 0.5
    snapshot1.component_state = {"test_key": "value1"}
    
    snapshot2 = MemorySnapshot()
    snapshot2.withering_level = 0.7
    snapshot2.component_state = {"test_key": "value2"}
    
    # Process both snapshots
    await orchestrator1.process_reflection("test", snapshot1)
    await orchestrator2.process_reflection("test", snapshot2)
    
    # Verify states remain isolated
    # Account for withering decay
    expected_withering1 = 0.5 * WITHERING_DECAY_FACTOR
    expected_withering2 = 0.7 * WITHERING_DECAY_FACTOR
    
    assert abs(snapshot1.withering_level - expected_withering1) < 0.01, "First snapshot's withering level was modified unexpectedly"
    assert abs(snapshot2.withering_level - expected_withering2) < 0.01, "Second snapshot's withering level was modified unexpectedly"
    assert snapshot1.component_state["test_key"] == "value1", "First snapshot's state was modified"
    assert snapshot2.component_state["test_key"] == "value2", "Second snapshot's state was modified"

@pytest.mark.asyncio
async def test_withering_isolation(orchestrator1, orchestrator2):
    """Test that withering calculations are isolated between instances."""
    # Create two identical snapshots
    snapshot1 = MemorySnapshot()
    snapshot2 = MemorySnapshot()
    
    # Set different initial withering levels
    snapshot1.withering_level = 0.3
    snapshot2.withering_level = 0.6
    
    # Update withering on both
    orchestrator1._update_withering(snapshot1)
    orchestrator2._update_withering(snapshot2)
    
    # Verify they remain different
    assert snapshot1.withering_level != snapshot2.withering_level, "Withering levels should remain different"
    
    # Account for withering decay
    expected_withering1 = 0.3 * WITHERING_DECAY_FACTOR
    expected_withering2 = 0.6 * WITHERING_DECAY_FACTOR
    
    assert abs(snapshot1.withering_level - expected_withering1) < 0.01, "First withering level changed unexpectedly"
    assert abs(snapshot2.withering_level - expected_withering2) < 0.01, "Second withering level changed unexpectedly" 