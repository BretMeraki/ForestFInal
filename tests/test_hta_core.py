import pytest
from forest_app.hta_tree.hta_service import HTAService
from forest_app.hta_tree.hta_tree import HTATree, HTANode
from forest_app.snapshot.snapshot import MemorySnapshot
from forest_app.hta_tree.hta_models import HTANodeModel

class MockLLMClient:
    async def generate(self, *args, **kwargs):
        return HTANodeModel(
            id="test_node",
            title="Test Task",
            description="Test Description",
            priority=0.8,
            magnitude=5.0,
            depends_on=[],
            estimated_energy="medium",
            estimated_time="medium",
            linked_tasks=[],
            is_milestone=False,
            rationale="Test rationale",
            status_suggestion="pending",
            children=[]
        )

    async def request_hta_evolution(self, *args, **kwargs):
        return HTANodeModel(
            id="evolved_node",
            title="Evolved Task",
            description="Evolved Description",
            priority=0.9,
            magnitude=6.0,
            depends_on=[],
            estimated_energy="medium",
            estimated_time="medium",
            linked_tasks=[],
            is_milestone=False,
            rationale="Evolved rationale",
            status_suggestion="pending",
            children=[]
        )

@pytest.mark.asyncio
async def test_core_hta_functionality():
    """Test core HTA functionality without complex setup"""
    # Initialize service with mock LLM client
    service = HTAService(llm_client=MockLLMClient())
    snapshot = MemorySnapshot()
    
    # Test 1: Create initial HTA tree
    initial_tree = await service.generate_onboarding_hta(
        goal="Test Goal",
        context="Test Context",
        user_id=1,
        snapshot=snapshot
    )
    assert initial_tree is not None
    assert isinstance(initial_tree, tuple)
    tree, _ = initial_tree
    assert isinstance(tree, dict)
    assert "root" in tree
    
    # Test 2: Load tree
    loaded_tree = await service.load_tree(snapshot)
    assert loaded_tree is not None
    assert isinstance(loaded_tree, HTATree)
    
    # Test 3: Update node status
    success = await service.update_node_status(
        tree=loaded_tree,
        node_id="test_node",
        new_status="in_progress"
    )
    assert success is True
    
    # Test 4: Evolve tree
    evolved_tree = await service.evolve_tree(
        tree=loaded_tree,
        reflections=["Test reflection"],
        snapshot=snapshot,
        goal="Test Goal",
        context="Test Context",
        user_id=1
    )
    assert evolved_tree is not None
    assert isinstance(evolved_tree, HTATree)
    
    # Test 5: Health status
    health = service.get_health_status()
    assert isinstance(health, dict)
    assert "failure_count" in health
    assert "total_ops" in health
    assert "last_operation_success" in health 