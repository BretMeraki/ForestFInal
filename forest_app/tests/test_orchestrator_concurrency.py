"""Tests for orchestrator concurrency and state isolation."""

import asyncio
import pytest
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional, Type, TypeVar, Union

from forest_app.core.orchestrator import ForestOrchestrator
from forest_app.snapshot.snapshot import MemorySnapshot
from forest_app.core.processors.reflection_processor import ReflectionProcessor
from forest_app.core.processors.completion_processor import CompletionProcessor
from forest_app.core.services.component_state_manager import ComponentStateManager
from forest_app.hta_tree.hta_service import HTAService
from forest_app.hta_tree.seed import SeedManager
from forest_app.core.exceptions import (
    StateLoadError,
    StateSaveError,
    ProcessingError,
    WitheringError
)

T = TypeVar('T')

class MockLLMClient:
    """Mock LLM client for testing."""
    async def generate(
        self,
        prompt_parts: List[Union[str, Dict[str, Any]]],
        response_model: Type[T],
        *,
        use_advanced_model: bool = False,
        temperature: Optional[float] = None,
        top_p: float = 1.0,
        top_k: int = 32,
        max_output_tokens: int = 8192,
        json_mode: bool = True,
        retries: int = 3,
        retry_wait: int = 2,
        attempt_json_repair: bool = True
    ) -> T:
        """Mock generate method that returns a simple response."""
        return {"status": "success", "message": "Mock response"}

class MockTaskEngine:
    """Mock task engine for testing."""
    async def process_task(self, task_id: str) -> Dict[str, Any]:
        return {"status": "completed"}

class MockReflectionProcessor(ReflectionProcessor):
    """Mock reflection processor for testing."""
    def __init__(self):
        # Skip parent initialization
        self.llm_client = MockLLMClient()
        self.task_engine = MockTaskEngine()
    
    async def process(self, user_input: str, snapshot: MemorySnapshot) -> Dict[str, Any]:
        # Simulate processing time
        await asyncio.sleep(0.1)
        return {"processed": True, "input": user_input}

class MockCompletionProcessor(CompletionProcessor):
    """Mock completion processor for testing."""
    def __init__(self):
        # Skip parent initialization
        self.llm_client = MockLLMClient()
        self.task_engine = MockTaskEngine()
    
    async def process(
        self,
        task_id: str,
        success: bool,
        snapshot: MemorySnapshot,
        db: Any,
        task_logger: Any
    ) -> Dict[str, Any]:
        # Simulate processing time
        await asyncio.sleep(0.1)
        return {"completed": True, "task_id": task_id, "success": success}

class MockStateManager(ComponentStateManager):
    """Mock state manager for testing."""
    def __init__(self):
        # Initialize with empty managed engines
        super().__init__(managed_engines={})
    
    def load_states(self, snapshot: MemorySnapshot) -> None:
        # Simulate state loading
        snapshot.component_state = snapshot.component_state or {}
        snapshot.component_state["last_load"] = datetime.now(timezone.utc).isoformat()
    
    def save_states(self, snapshot: MemorySnapshot) -> None:
        # Simulate state saving
        snapshot.component_state = snapshot.component_state or {}
        snapshot.component_state["last_save"] = datetime.now(timezone.utc).isoformat()

class MockHTAService(HTAService):
    """Mock HTA service for testing."""
    def __init__(self):
        # Skip parent initialization
        pass

class MockSeedManager(SeedManager):
    """Mock seed manager for testing."""
    def __init__(self):
        # Skip parent initialization
        pass

@pytest.fixture
def orchestrator():
    """Create a test orchestrator with mock dependencies."""
    return ForestOrchestrator(
        reflection_processor=MockReflectionProcessor(),
        completion_processor=MockCompletionProcessor(),
        state_manager=MockStateManager(),
        hta_service=MockHTAService(),
        seed_manager=MockSeedManager()
    )

@pytest.fixture
def create_snapshot():
    """Create a test snapshot with unique ID."""
    def _create_snapshot(user_id: str, initial_state: Dict[str, Any] = None) -> MemorySnapshot:
        snapshot = MemorySnapshot()
        
        # Set required attributes
        snapshot.id = f"test_snapshot_{user_id}"
        snapshot.user_id = user_id
        snapshot.withering_level = 0.5
        snapshot.component_state = initial_state or {}
        
        # Set additional required attributes
        now = datetime.now(timezone.utc)
        snapshot.last_activity_ts = now
        snapshot.created_at = now
        snapshot.active_tasks = []
        snapshot.completed_tasks = []
        snapshot.current_path = []
        snapshot.feature_flags = {}
        snapshot.batch_tracking = {}
        
        return snapshot
    return _create_snapshot

@pytest.mark.asyncio
async def test_concurrent_reflections(orchestrator, create_snapshot):
    """Test that concurrent reflections are properly isolated."""
    # Create snapshots for different users
    snapshots = [
        create_snapshot(f"user_{i}", {"custom_data": f"data_{i}"})
        for i in range(3)
    ]
    
    # Process reflections concurrently
    async def process_reflection(snapshot: MemorySnapshot, input_text: str):
        return await orchestrator.process_reflection(input_text, snapshot)
    
    # Run concurrent reflections
    tasks = [
        process_reflection(snapshot, f"test_input_{i}")
        for i, snapshot in enumerate(snapshots)
    ]
    results = await asyncio.gather(*tasks)
    
    # Verify results
    for i, (result, snapshot) in enumerate(zip(results, snapshots)):
        assert result["processed"] is True
        assert result["input"] == f"test_input_{i}"
        assert snapshot.component_state["last_load"] is not None
        assert snapshot.component_state["last_save"] is not None
        assert snapshot.component_state["custom_data"] == f"data_{i}"

@pytest.mark.asyncio
async def test_concurrent_task_completions(orchestrator, create_snapshot):
    """Test that concurrent task completions are properly isolated."""
    # Create snapshots for different users
    snapshots = [
        create_snapshot(f"user_{i}", {"task_data": f"task_{i}"})
        for i in range(3)
    ]
    
    # Process task completions concurrently
    async def process_completion(snapshot: MemorySnapshot, task_id: str, success: bool):
        return await orchestrator.process_task_completion(
            task_id=task_id,
            success=success,
            snapshot=snapshot,
            db=None,  # Mock DB
            task_logger=None  # Mock logger
        )
    
    # Run concurrent completions
    tasks = [
        process_completion(snapshot, f"task_{i}", i % 2 == 0)
        for i, snapshot in enumerate(snapshots)
    ]
    results = await asyncio.gather(*tasks)
    
    # Verify results
    for i, (result, snapshot) in enumerate(zip(results, snapshots)):
        assert result["completed"] is True
        assert result["task_id"] == f"task_{i}"
        assert result["success"] == (i % 2 == 0)
        assert snapshot.component_state["last_load"] is not None
        assert snapshot.component_state["last_save"] is not None
        assert snapshot.component_state["task_data"] == f"task_{i}"

@pytest.mark.asyncio
async def test_concurrent_error_handling(orchestrator, create_snapshot):
    """Test that errors in concurrent operations are properly isolated."""
    # Create snapshots
    snapshots = [
        create_snapshot(f"user_{i}")
        for i in range(3)
    ]
    
    # Make one snapshot invalid to trigger an error
    snapshots[1].component_state = None  # This will cause a StateLoadError
    
    # Process reflections concurrently
    async def process_reflection(snapshot: MemorySnapshot, input_text: str):
        try:
            return await orchestrator.process_reflection(input_text, snapshot)
        except Exception as e:
            return {"error": str(e)}
    
    # Run concurrent reflections
    tasks = [
        process_reflection(snapshot, f"test_input_{i}")
        for i, snapshot in enumerate(snapshots)
    ]
    results = await asyncio.gather(*tasks)
    
    # Verify results
    assert "error" not in results[0]  # First request should succeed
    assert "error" in results[1]  # Second request should fail
    assert "error" not in results[2]  # Third request should succeed
    
    # Verify state isolation
    assert snapshots[0].component_state["last_load"] is not None
    assert snapshots[2].component_state["last_load"] is not None

@pytest.mark.asyncio
async def test_withering_isolation(orchestrator, create_snapshot):
    """Test that withering calculations are properly isolated."""
    # Create snapshots with different initial states
    snapshots = [
        create_snapshot(f"user_{i}", {"withering": i * 0.2})
        for i in range(3)
    ]
    
    # Process reflections concurrently
    async def process_reflection(snapshot: MemorySnapshot, input_text: str):
        return await orchestrator.process_reflection(input_text, snapshot)
    
    # Run concurrent reflections
    tasks = [
        process_reflection(snapshot, f"test_input_{i}")
        for i, snapshot in enumerate(snapshots)
    ]
    await asyncio.gather(*tasks)
    
    # Verify withering levels are isolated
    for i, snapshot in enumerate(snapshots):
        assert snapshot.withering_level is not None
        assert snapshot.withering_level != snapshots[(i + 1) % 3].withering_level 