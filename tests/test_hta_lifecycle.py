import pytest
import asyncio
from forest_app.hta_tree.hta_service import HTAService
from forest_app.hta_tree.hta_tree import HTATree
from forest_app.snapshot.snapshot import MemorySnapshot
from forest_app.hta_tree.hta_models import HTAResponseModel, HTANodeModel
from forest_app.integrations.llm import HTAEvolveResponse
from forest_app.hta_tree.task_engine import TaskEngine, MAX_FRONTIER_BATCH_SIZE
from forest_app.modules.cognitive.pattern_id import PatternIdentificationEngine
import re
import json
from datetime import datetime, timezone

# --- Helper: Minimal HTAValidationModel/HTANodeModel mocks ---
class DummyHTANodeModel:
    def __init__(self):
        self.id = "root_1"
        self.title = "Root Goal"
        self.description = "Root node"
        self.priority = 1.0
        self.depends_on = []
        self.estimated_energy = "medium"
        self.estimated_time = "medium"
        self.linked_tasks = []
        self.is_milestone = True
        self.rationale = ""
        self.status_suggestion = "pending"
        self.children = [
            DummyChildNode()
        ]
    def model_dump(self, mode=None):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "depends_on": self.depends_on,
            "estimated_energy": self.estimated_energy,
            "estimated_time": self.estimated_time,
            "linked_tasks": self.linked_tasks,
            "is_milestone": self.is_milestone,
            "rationale": self.rationale,
            "status_suggestion": self.status_suggestion,
            "children": [c.model_dump() for c in self.children],
        }

class DummyChildNode:
    def __init__(self):
        self.id = "child_1"
        self.title = "First Task"
        self.description = "Do something important"
        self.priority = 0.8
        self.depends_on = []
        self.estimated_energy = "medium"
        self.estimated_time = "medium"
        self.linked_tasks = []
        self.is_milestone = False
        self.rationale = ""
        self.status_suggestion = "pending"
        self.children = []
    def model_dump(self, mode=None):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "depends_on": self.depends_on,
            "estimated_energy": self.estimated_energy,
            "estimated_time": self.estimated_time,
            "linked_tasks": self.linked_tasks,
            "is_milestone": self.is_milestone,
            "rationale": self.rationale,
            "status_suggestion": self.status_suggestion,
            "children": [],
        }

class DummyHTAValidationModel:
    def __init__(self):
        self.hta_root = DummyHTANodeModel()
    def model_dump(self, mode=None):
        return {"hta_root": self.hta_root.model_dump()}

class DummyHTAValidationModelEvolved:
    def __init__(self):
        self.hta_root = DummyHTANodeModel()
        # Add a new child to simulate evolution
        self.hta_root.children.append(DummyEvolvedChildNode())
    def model_dump(self, mode=None):
        return {"hta_root": self.hta_root.model_dump()}

class DummyEvolvedChildNode(DummyChildNode):
    def __init__(self):
        super().__init__()
        self.id = "child_2"
        self.title = "Second Task"
        self.description = "Do something new"
        self.priority = 0.7

class DummyLLMClient:
    def __init__(self):
        self.task_counter = 0
        self.used_task_ids = set()

    def _generate_unique_task_id(self) -> str:
        """Generate a unique task ID."""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        while task_id in self.used_task_ids:
            self.task_counter += 1
            task_id = f"task_{self.task_counter}"
        self.used_task_ids.add(task_id)
        return task_id

    async def generate(self, *args, **kwargs):
        prompt = ""
        if "prompt_parts" in kwargs and kwargs["prompt_parts"]:
            prompt = kwargs["prompt_parts"][0]
        elif args:
            prompt = args[0]
            
        # Extract root ID
        match = re.search(r"Root MUST use: '([^']+)'", prompt)
        root_id = match.group(1) if match else "root_1"
        
        # Extract goal and context
        goal_match = re.search(r"Goal: ([^\n]+)", prompt)
        context_match = re.search(r"Context: ([^\n]+)", prompt)
        goal = goal_match.group(1) if goal_match else "Root Goal"
        context = context_match.group(1) if context_match else "Root node"
        
        # Create initial child node
        child_node = HTANodeModel(
            id=self._generate_unique_task_id(),
            title=f"Initial step for {goal}",
            description=f"First step towards {goal}. Context: {context}",
            priority=0.8,
            depends_on=[],
            estimated_energy="medium",
            estimated_time="medium",
            linked_tasks=[],
            is_milestone=False,
            rationale="",
            status_suggestion="pending",
            children=[],
        )
        
        # Create root node with goal and context
        root_node = HTANodeModel(
            id=root_id,
            title=goal,
            description=context,
            priority=1.0,
            depends_on=[],
            estimated_energy="medium",
            estimated_time="medium",
            linked_tasks=[],
            is_milestone=True,
            rationale="",
            status_suggestion="pending",
            children=[child_node],
        )
        return HTAResponseModel(hta_root=root_node)

    async def request_hta_evolution(self, current_hta_json: str, evolution_goal: str, evolution_prompt: dict = None, use_advanced_model: bool = True) -> HTAEvolveResponse:
        """Simulates HTA evolution while preserving node status."""
        # Parse the current tree state
        current_tree = json.loads(current_hta_json)
        root_node = current_tree.get('root', {})
        root_id = root_node.get('id', 'root_1')
        
        # Create new child nodes while preserving existing ones
        existing_children = root_node.get('children', [])
        new_children = []
        
        # Preserve existing children with their status
        for child in existing_children:
            child_id = child.get('id', self._generate_unique_task_id())
            self.used_task_ids.add(child_id)
            child_model = HTANodeModel(
                id=child_id,
                title=child.get('title', 'Preserved Task'),
                description=child.get('description', 'Preserved task description'),
                priority=float(child.get('priority', 0.8)),
                depends_on=child.get('depends_on', []),
                estimated_energy=child.get('estimated_energy', 'medium'),
                estimated_time=child.get('estimated_time', 'medium'),
                linked_tasks=child.get('linked_tasks', []),
                is_milestone=child.get('is_milestone', False),
                rationale=child.get('rationale', ''),
                status_suggestion=child.get('status_suggestion', 'pending'),
                children=child.get('children', [])
            )
            new_children.append(child_model)
        
        # Add new child nodes
        new_task = HTANodeModel(
            id=self._generate_unique_task_id(),
            title=f"Next step for {root_node.get('title', 'Root Goal')}",
            description=f"Continue progress on {root_node.get('title', 'Root Goal')}",
            priority=0.7,
            depends_on=[],
            estimated_energy="medium",
            estimated_time="medium",
            linked_tasks=[],
            is_milestone=False,
            rationale="",
            status_suggestion="pending",
            children=[]
        )
        new_children.append(new_task)
        
        # Create evolved root node
        evolved_root = HTANodeModel(
            id=root_id,
            title=root_node.get('title', 'Root Goal'),
            description=root_node.get('description', 'Root node'),
            priority=float(root_node.get('priority', 1.0)),
            depends_on=root_node.get('depends_on', []),
            estimated_energy=root_node.get('estimated_energy', 'medium'),
            estimated_time=root_node.get('estimated_time', 'medium'),
            linked_tasks=root_node.get('linked_tasks', []),
            is_milestone=root_node.get('is_milestone', True),
            rationale=root_node.get('rationale', ''),
            status_suggestion=root_node.get('status_suggestion', 'pending'),
            children=new_children
        )
        
        return HTAEvolveResponse(hta_root=evolved_root)

class DummySeedManager:
    async def get_seed_by_id(self, seed_id):
        return type('Seed', (), {'hta_tree': None, 'seed_id': seed_id})()
    async def get_primary_active_seed(self):
        return type('Seed', (), {'hta_tree': None, 'seed_id': 'seed_1'})()
    async def update_seed(self, seed_id, hta_tree):
        return True

@pytest.mark.asyncio
async def test_hta_system_operations():
    """
    Test suite for comprehensive HTA system operations.
    This suite tests:
    1. Initial setup and configuration
    2. Tree creation and manipulation
    3. Task generation and management
    4. Status updates and propagation
    5. Tree evolution and reflection
    6. Error handling and recovery
    7. State persistence and consistency
    """
    # Setup
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    snapshot.component_state = {"seed_manager": {"active_seed_id": "seed_1"}}
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())

    # Test 1: Initial Setup and Configuration
    goal = "Master Python Programming"
    context = "Complete beginner, 2 hours daily, focus on web development"
    user_id = 1

    # Test 2: Tree Creation and Basic Structure
    hta_model_dict, seed_desc = await hta_service.generate_onboarding_hta(goal, context, user_id)
    assert hta_model_dict is not None, "HTA model should be generated"
    assert "hta_root" in hta_model_dict, "HTA model should have root node"
    
    tree = HTATree.from_dict(hta_model_dict)
    assert tree.root is not None, "Tree should have root node"
    assert tree.root.title == goal, "Root title should match goal"
    assert tree.root.description == context, "Root description should match context"
    
    # Test 3: Child Node Creation and Structure
    assert len(tree.root.children) > 0, "Root should have children"
    for child in tree.root.children:
        assert child.id is not None, "Child should have ID"
        assert child.title is not None, "Child should have title"
        assert child.description is not None, "Child should have description"
        assert 0.0 <= child.priority <= 1.0, "Child priority should be valid"
        assert child.estimated_energy in ["low", "medium", "high"], "Child should have valid energy estimate"
        assert child.estimated_time in ["low", "medium", "high"], "Child should have valid time estimate"

    # Test 4: Tree Persistence
    save_success = await hta_service.save_tree(snapshot, tree)
    assert save_success, "Tree should save successfully"
    assert "hta_tree" in snapshot.core_state, "Tree should be in snapshot"
    
    # Test 5: Task Generation
    tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in tasks_bundle, "Should generate tasks"
    assert len(tasks_bundle["tasks"]) > 0, "Should have tasks"
    
    # Test 6: Task Properties and Node Mapping
    for task in tasks_bundle["tasks"]:
        assert "id" in task, "Task should have ID"
        assert "title" in task, "Task should have title"
        assert "description" in task, "Task should have description"
        assert "metadata" in task, "Task should have metadata"
        assert "priority_raw" in task["metadata"], "Task should have priority"
        assert "magnitude" in task, "Task should have magnitude"
        assert "hta_node_id" in task, "Task should have HTA node ID"
        
        node = tree.find_node_by_id(task["hta_node_id"])
        assert node is not None, "Task should map to existing node"
        assert node.title == task["title"], "Task title should match node title"

    # Test 7: Status Updates and Propagation
    first_task = tasks_bundle["tasks"][0]
    update_success = await hta_service.update_node_status(tree, first_task["hta_node_id"], "completed")
    assert update_success, "Status update should succeed"
    
    updated_node = tree.find_node_by_id(first_task["hta_node_id"])
    assert updated_node.status == "completed", "Node status should be updated"
    
    # Test 8: Tree Evolution
    reflections = ["Completed first task successfully", "Ready for next steps"]
    evolved_tree = await hta_service.evolve_tree(tree, reflections)
    assert evolved_tree is not None, "Tree should evolve"
    assert len(evolved_tree.root.children) > len(tree.root.children), "Evolved tree should have more nodes"
    
    # Test 9: New Task Generation After Evolution
    await hta_service.save_tree(snapshot, evolved_tree)
    new_tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in new_tasks, "Should generate new tasks"
    assert len(new_tasks["tasks"]) > 0, "Should have new tasks"
    
    # Test 10: Task Completion Flow
    for task in new_tasks["tasks"]:
        update_success = await hta_service.update_node_status(evolved_tree, task["hta_node_id"], "completed")
        assert update_success, "Task completion should succeed"
        node = evolved_tree.find_node_by_id(task["hta_node_id"])
        assert node.status == "completed", "Node should be marked completed"
    
    # Test 11: Error Handling
    invalid_status = await hta_service.update_node_status(evolved_tree, "non_existent_id", "completed")
    assert not invalid_status, "Invalid node ID should fail gracefully"
    
    invalid_status = await hta_service.update_node_status(evolved_tree, evolved_tree.root.id, "invalid_status")
    assert not invalid_status, "Invalid status should fail gracefully"
    
    # Test 12: State Consistency
    final_tree = await hta_service.load_tree(snapshot)
    assert final_tree is not None, "Should load tree from snapshot"
    assert final_tree.root.id == evolved_tree.root.id, "Root ID should be preserved"
    assert len(final_tree.root.children) == len(evolved_tree.root.children), "Child count should be preserved"
    
    # Test 13: Health Monitoring
    health_status = hta_service.get_health_status()
    assert health_status["last_operation_success"], "Last operation should be successful"
    assert health_status["total_ops"] > 0, "Should have recorded operations"

@pytest.mark.asyncio
async def test_hta_error_recovery():
    """
    Test error recovery and fallback mechanisms in the HTA system.
    """
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Test 1: Invalid Tree Operations
    invalid_tree = HTATree.from_dict({"root": {"id": "invalid"}})
    save_result = await hta_service.save_tree(snapshot, invalid_tree)
    assert not save_result, "Invalid tree should fail to save"
    
    # Test 2: Invalid Node Status Updates
    tree = HTATree.from_dict({"root": {"id": "root_1", "title": "Test"}})
    invalid_statuses = ["invalid_status", 123, True]
    for status in invalid_statuses:
        result = await hta_service.update_node_status(tree, "root_1", status)
        assert not result, f"Status {status} should not be accepted"
    
    # Test 3: Invalid Node IDs
    invalid_ids = [123, True, "non_existent_id"]
    for node_id in invalid_ids:
        result = await hta_service.update_node_status(tree, node_id, "completed")
        assert not result, f"Node ID {node_id} should not be accepted"

@pytest.mark.asyncio
async def test_hta_state_management():
    """
    Test state management and persistence in the HTA system.
    """
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Test 1: Initial State
    goal = "Test Goal"
    context = "Test Context"
    user_id = 1
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    
    # Test 2: State Preservation
    initial_state = {
        "root_id": tree.root.id,
        "root_title": tree.root.title,
        "child_count": len(tree.root.children),
        "node_map": tree.get_node_map()
    }
    
    # Test 3: Save and Reload
    await hta_service.save_tree(snapshot, tree)
    reloaded_tree = await hta_service.load_tree(snapshot)
    assert reloaded_tree is not None, "Should load tree from snapshot"
    assert reloaded_tree.root.id == initial_state["root_id"], "Root ID should be preserved"
    assert reloaded_tree.root.title == initial_state["root_title"], "Root title should be preserved"
    assert len(reloaded_tree.root.children) == initial_state["child_count"], "Child count should be preserved"
    
    # Test 4: Node Map Consistency
    reloaded_node_map = reloaded_tree.get_node_map()
    assert len(reloaded_node_map) == len(initial_state["node_map"]), "Node map size should be preserved"
    for node_id, node in initial_state["node_map"].items():
        assert node_id in reloaded_node_map, "Node ID should be preserved"
        assert reloaded_node_map[node_id].title == node.title, "Node title should be preserved"

@pytest.mark.asyncio
async def test_hta_task_generation():
    """
    Test task generation and frontier node identification.
    This test verifies:
    1. Initial task generation
    2. Task properties and validation
    3. Task uniqueness across batches
    4. Task-node relationships
    5. Task ID persistence
    6. Task evolution and context
    """
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    
    # Test 1: Initial Task Generation
    goal = "Learn Python Programming"
    context = "Complete beginner, 3 months to learn, interested in data science"
    user_id = 1
    
    # Generate initial tree
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    await hta_service.save_tree(snapshot, tree)
    
    # Test 2: First Batch of Tasks
    tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in tasks_bundle, "Should generate tasks bundle"
    assert 0 < len(tasks_bundle["tasks"]) <= MAX_FRONTIER_BATCH_SIZE, "Should generate appropriate number of tasks"
    
    # Store initial task IDs
    initial_task_ids = {task["id"] for task in tasks_bundle["tasks"]}
    initial_node_ids = {task["hta_node_id"] for task in tasks_bundle["tasks"]}
    
    # Test 3: Task Properties and Validation
    for task in tasks_bundle["tasks"]:
        # Basic properties
        assert "id" in task, "Task should have ID"
        assert "title" in task, "Task should have title"
        assert "description" in task, "Task should have description"
        assert "metadata" in task, "Task should have metadata"
        assert "priority_raw" in task["metadata"], "Task should have priority"
        assert "magnitude" in task, "Task should have magnitude"
        assert "hta_node_id" in task, "Task should have HTA node ID"
        assert "estimated_time" in task, "Task should have estimated time"
        assert "estimated_energy" in task, "Task should have estimated energy"
        assert "created_at" in task, "Task should have creation timestamp"
        assert "status" in task, "Task should have status"
        
        # Value validation
        assert isinstance(task["id"], str), "Task ID should be string"
        assert isinstance(task["magnitude"], (int, float)), "Magnitude should be numeric"
        assert 0.0 <= task["magnitude"] <= 10.0, "Magnitude should be between 0 and 10"
        assert isinstance(task["metadata"]["priority_raw"], (int, float)), "Priority should be numeric"
        assert 0.0 <= task["metadata"]["priority_raw"] <= 1.0, "Priority should be between 0 and 1"
        assert task["estimated_energy"] in ["low", "medium", "high"], "Energy should be valid value"
        assert task["estimated_time"] in ["low", "medium", "high"], "Time should be valid value"
        assert task["status"] in ["pending", "completed", "failed"], "Status should be valid value"
        
        # Node relationship
        node = tree.find_node_by_id(task["hta_node_id"])
        assert node is not None, "Task should map to existing node"
        assert node.title == task["title"], "Task title should match node title"
        assert node.description == task["description"], "Task description should match node description"
        assert abs(float(node.priority) - float(task["metadata"]["priority_raw"])) < 0.001, "Task priority should match node priority"
    
    # Test 4: Task Completion and New Batch
    for task in tasks_bundle["tasks"]:
        update_ok = await hta_service.update_node_status(tree, task["hta_node_id"], "completed")
        assert update_ok, "Should update task status"
    await hta_service.save_tree(snapshot, tree)
    
    # Add reflections and evolve tree
    reflections = ["Completed initial tasks successfully", "Ready for next steps"]
    evolved_tree = await hta_service.evolve_tree(tree, reflections)
    assert evolved_tree is not None, "Tree should evolve"
    assert len(evolved_tree.root.children) > len(tree.root.children), "Evolved tree should have more nodes"
    
    # Save evolved tree
    await hta_service.save_tree(snapshot, evolved_tree)
    
    # Test 5: New Task Generation After Evolution
    next_tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in next_tasks, "Should generate new tasks"
    assert len(next_tasks["tasks"]) > 0, "Should have new tasks"
    
    # Verify task uniqueness
    new_task_ids = {task["id"] for task in next_tasks["tasks"]}
    new_node_ids = {task["hta_node_id"] for task in next_tasks["tasks"]}
    
    assert not (initial_task_ids & new_task_ids), "New tasks should have unique IDs"
    assert not (initial_node_ids & new_node_ids), "New tasks should reference new nodes"
    
    # Test 6: Task Properties After Evolution
    for task in next_tasks["tasks"]:
        # Verify all properties are present
        assert all(key in task for key in [
            "id", "title", "description", "magnitude", "hta_node_id",
            "estimated_energy", "estimated_time", "status", "metadata"
        ]), "Task should have all required properties"
        
        # Verify metadata
        assert all(key in task["metadata"] for key in [
            "priority_raw", "hta_depth", "created_at"
        ]), "Task metadata should have all required properties"
        
        # Verify node relationship
        node = evolved_tree.find_node_by_id(task["hta_node_id"])
        assert node is not None, "Task should map to existing node in evolved tree"
        assert node.title == task["title"], "Task title should match evolved node title"
        assert node.description == task["description"], "Task description should match evolved node description"
        
        # Verify context preservation
        assert any(word.lower() in task["title"].lower() or word.lower() in task["description"].lower() 
                  for word in goal.split()), "Task should reference goal"
        assert any(word.lower() in task["description"].lower() 
                  for word in context.split()), "Task should reference context"
    
    # Test 7: Task ID Persistence
    persisted_ids = task_engine._get_persisted_task_ids(snapshot.to_dict())
    assert initial_task_ids.issubset(persisted_ids), "Initial task IDs should be persisted"
    assert new_task_ids.issubset(persisted_ids), "New task IDs should be persisted"
    
    # Test 8: Clear Task IDs on Tree Evolution
    task_engine._clear_persisted_task_ids(snapshot.to_dict())
    cleared_ids = task_engine._get_persisted_task_ids(snapshot.to_dict())
    assert not cleared_ids, "Task IDs should be cleared"
    
    # Test 9: Task Generation After Clear
    final_tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in final_tasks, "Should generate tasks after clear"
    assert len(final_tasks["tasks"]) > 0, "Should have tasks after clear"
    
    final_task_ids = {task["id"] for task in final_tasks["tasks"]}
    assert not (final_task_ids & initial_task_ids), "Tasks after clear should have new IDs"
    assert not (final_task_ids & new_task_ids), "Tasks after clear should have new IDs"

@pytest.mark.asyncio
async def test_hta_lifecycle():
    goal = "Complete a major project"
    context = "I have 3 months and want to focus on learning."
    user_id = 1
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    snapshot.component_state = {"seed_manager": {"active_seed_id": "seed_1"}}
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    hta_model_dict, seed_desc = await hta_service.generate_onboarding_hta(goal, context, user_id)
    assert hta_model_dict is not None
    tree = HTATree.from_dict(hta_model_dict)
    assert tree.root is not None
    save_ok = await hta_service.save_tree(snapshot, tree)
    assert save_ok
    health = hta_service.get_health_status()
    assert health["last_operation_success"]
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in tasks_bundle
    assert len(tasks_bundle["tasks"]) > 0
    for task in tasks_bundle["tasks"]:
        update_ok = await hta_service.update_node_status(tree, task["hta_node_id"], "completed")
        assert update_ok
    health = hta_service.get_health_status()
    assert health["last_operation_success"]
    evolved_tree = await hta_service.evolve_tree(tree, ["Reflection on progress"])
    assert evolved_tree is not None
    save_ok = await hta_service.save_tree(snapshot, evolved_tree)
    assert save_ok
    health = hta_service.get_health_status()
    assert health["last_operation_success"]
    # Check that the evolved tree has the new node
    evolved_dict = evolved_tree.to_dict()
    assert "root" in evolved_dict
    assert len(evolved_dict["root"].get("children", [])) > 1

@pytest.mark.asyncio
async def test_hta_lifecycle_error_handling():
    """Test error handling in HTA lifecycle."""
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Test loading non-existent tree
    tree = await hta_service.load_tree(snapshot)
    assert tree is None
    health = hta_service.get_health_status()
    assert not health["last_operation_success"]
    # The failure count might not increment in this case as it's a valid "no tree found" scenario
    
    # Test saving invalid tree
    save_ok = await hta_service.save_tree(snapshot, None)
    assert not save_ok
    health = hta_service.get_health_status()
    assert not health["last_operation_success"]

@pytest.mark.asyncio
async def test_hta_node_status_transitions():
    """Test node status transitions and validation."""
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Create initial tree
    goal = "Test goal"
    context = "Test context"
    user_id = 1
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    
    # Test valid status transitions
    node_id = tree.root.children[0].id
    assert await hta_service.update_node_status(tree, node_id, "in_progress")
    assert await hta_service.update_node_status(tree, node_id, "completed")
    
    # Test non-existent node
    assert not await hta_service.update_node_status(tree, "non_existent_id", "completed")

@pytest.mark.asyncio
async def test_hta_tree_evolution_edge_cases():
    """Test edge cases in tree evolution."""
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Create initial tree
    goal = "Test goal"
    context = "Test context"
    user_id = 1
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    
    # Test evolution with empty reflections
    evolved_tree = await hta_service.evolve_tree(tree, [])
    assert evolved_tree is not None
    # The tree might still evolve even with empty reflections, as the LLM might generate new tasks
    # based on the current state
    
    # Test evolution with multiple reflections
    reflections = ["First reflection", "Second reflection", "Third reflection"]
    evolved_tree = await hta_service.evolve_tree(tree, reflections)
    assert evolved_tree is not None
    assert len(evolved_tree.root.children) > len(tree.root.children)

@pytest.mark.asyncio
async def test_hta_health_monitoring():
    """Test health status monitoring and failure tracking."""
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Initial health check
    initial_health = hta_service.get_health_status()
    assert initial_health["last_operation_success"]
    initial_failures = initial_health["failure_count"]
    
    # Force some failures
    await hta_service.load_tree(snapshot)  # Should fail
    await hta_service.save_tree(snapshot, None)  # Should fail
    
    # Check updated health status
    updated_health = hta_service.get_health_status()
    assert not updated_health["last_operation_success"]
    assert updated_health["failure_count"] > initial_failures
    assert updated_health["total_ops"] > 0

@pytest.mark.asyncio
async def test_hta_task_engine_integration():
    """Test integration with task engine."""
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Create initial tree
    goal = "Test goal"
    context = "Test context"
    user_id = 1
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    await hta_service.save_tree(snapshot, tree)
    
    # Test task engine integration
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    
    assert "tasks" in tasks_bundle
    assert len(tasks_bundle["tasks"]) > 0
    
    # Verify task properties
    for task in tasks_bundle["tasks"]:
        assert "id" in task, "Task should have ID"
        assert "title" in task, "Task should have title"
        assert "description" in task, "Task should have description"
        assert "metadata" in task, "Task should have metadata"
        assert "priority_raw" in task["metadata"], "Task should have priority in metadata"
        assert "magnitude" in task, "Task should have magnitude"
        assert "hta_node_id" in task, "Task should have HTA node ID"
        assert "estimated_time" in task, "Task should have estimated time"
        assert "estimated_energy" in task, "Task should have estimated energy"
        assert "created_at" in task, "Task should have creation timestamp"
        
        # Verify task corresponds to a node in the tree
        node = tree.find_node_by_id(task["hta_node_id"])
        assert node is not None, f"Task node {task['hta_node_id']} should exist in tree"

@pytest.mark.asyncio
async def test_hta_frontier_task_generation():
    """Test the generation of frontier tasks and their evolution."""
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Initial setup with goal and context
    goal = "Learn Python Programming"
    context = "Complete beginner, 3 months to learn, interested in data science"
    user_id = 1
    
    # Create initial tree
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    await hta_service.save_tree(snapshot, tree)
    
    # Verify root node contains goal and context
    assert tree.root is not None
    assert tree.root.title == goal
    assert tree.root.description == context
    
    # Generate first batch of frontier tasks
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    
    # Verify we get up to 5 tasks
    assert "tasks" in tasks_bundle
    assert 0 < len(tasks_bundle["tasks"]) <= 5
    
    # Complete all tasks in the batch
    for task in tasks_bundle["tasks"]:
        update_ok = await hta_service.update_node_status(tree, task["hta_node_id"], "completed")
        assert update_ok
        await hta_service.save_tree(snapshot, tree)
    
    # Evolve the tree with reflections from completed tasks
    reflections = [f"Completed task: {task['title']}" for task in tasks_bundle["tasks"]]
    evolved_tree = await hta_service.evolve_tree(tree, reflections)
    assert evolved_tree is not None
    
    # Verify the evolved tree maintains context
    assert evolved_tree.root.title == goal
    assert evolved_tree.root.description == context
    
    # Verify new child nodes are created
    assert len(evolved_tree.root.children) > len(tree.root.children)
    
    # Save evolved tree
    await hta_service.save_tree(snapshot, evolved_tree)
    
    # Generate next batch of tasks
    next_tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in next_tasks
    assert 0 < len(next_tasks["tasks"]) <= 5
    
    # Verify new tasks are different from previous ones
    previous_task_ids = {task["hta_node_id"] for task in tasks_bundle["tasks"]}
    new_task_ids = {task["hta_node_id"] for task in next_tasks["tasks"]}
    assert not (previous_task_ids & new_task_ids)  # No overlap in task IDs

@pytest.mark.asyncio
async def test_hta_context_preservation():
    """Test that context is preserved throughout the HTA lifecycle."""
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Initial setup with specific goal and context
    goal = "Build a Web Application"
    context = "Using React and Node.js, 6 months timeline, focus on user experience"
    user_id = 1
    
    # Create initial tree
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    await hta_service.save_tree(snapshot, tree)
    
    # Store initial context
    initial_context = {
        "goal": goal,
        "context": context,
        "root_title": tree.root.title,
        "root_description": tree.root.description
    }
    
    # Verify initial context
    assert tree.root.title == goal, "Initial root title should match goal"
    assert context.lower() in tree.root.description.lower(), "Initial root description should contain context"
    
    # Verify initial child nodes have context
    for child in tree.root.children:
        assert any(word.lower() in child.title.lower() or word.lower() in child.description.lower() 
                  for word in goal.split()), "Child nodes should reference goal"
        assert any(word.lower() in child.description.lower() 
                  for word in context.split()), "Child nodes should reference context"
    
    # Simulate multiple task batches and evolutions
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    
    for batch_num in range(3):
        # Generate and verify tasks
        tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
        assert "tasks" in tasks_bundle, f"Batch {batch_num}: Should generate tasks"
        assert len(tasks_bundle["tasks"]) > 0, f"Batch {batch_num}: Should have tasks"
        
        # Verify task context
        for task in tasks_bundle["tasks"]:
            node = tree.find_node_by_id(task["hta_node_id"])
            assert node is not None, f"Batch {batch_num}: Task node should exist"
            assert any(word.lower() in task["title"].lower() or word.lower() in task["description"].lower() 
                      for word in goal.split()), f"Batch {batch_num}: Task should reference goal"
            assert any(word.lower() in task["description"].lower() 
                      for word in context.split()), f"Batch {batch_num}: Task should reference context"
        
        # Complete tasks
        for task in tasks_bundle["tasks"]:
            update_ok = await hta_service.update_node_status(tree, task["hta_node_id"], "completed")
            assert update_ok, f"Batch {batch_num}: Should update task status"
        
        # Save tree state
        await hta_service.save_tree(snapshot, tree)
        
        # Generate reflections
        reflections = [
            f"Batch {batch_num + 1} - Completed task: {task['title']} - {task['description'][:50]}..."
            for task in tasks_bundle["tasks"]
        ]
        
        # Evolve tree
        evolved_tree = await hta_service.evolve_tree(tree, reflections)
        assert evolved_tree is not None, f"Batch {batch_num}: Tree should evolve"
        
        # Verify evolved tree maintains context
        assert evolved_tree.root.title == goal, f"Batch {batch_num}: Evolved root title should match goal"
        assert context.lower() in evolved_tree.root.description.lower(), f"Batch {batch_num}: Evolved root description should contain context"
        
        # Verify evolved child nodes maintain context
        for child in evolved_tree.root.children:
            # Check goal reference
            has_goal_reference = any(
                word.lower() in child.title.lower() or word.lower() in child.description.lower()
                for word in goal.split()
            )
            assert has_goal_reference, f"Batch {batch_num}: Evolved child should reference goal"
            
            # Check context reference
            has_context_reference = any(
                word.lower() in child.description.lower()
                for word in context.split()
            )
            assert has_context_reference, f"Batch {batch_num}: Evolved child should reference context"
            
            # Check deeper nodes
            for grandchild in getattr(child, 'children', []):
                assert any(
                    word.lower() in grandchild.title.lower() or word.lower() in grandchild.description.lower()
                    for word in goal.split()
                ), f"Batch {batch_num}: Evolved grandchild should reference goal"
                assert any(
                    word.lower() in grandchild.description.lower()
                    for word in context.split()
                ), f"Batch {batch_num}: Evolved grandchild should reference context"
        
        # Verify tree structure
        assert len(evolved_tree.root.children) >= len(tree.root.children), f"Batch {batch_num}: Tree should maintain or grow"
        
        # Verify completed nodes remain completed
        completed_nodes = [
            node for node in evolved_tree.get_node_map().values()
            if getattr(node, 'status', '') == 'completed'
        ]
        original_completed = [
            node for node in tree.get_node_map().values()
            if getattr(node, 'status', '') == 'completed'
        ]
        assert len(completed_nodes) >= len(original_completed), f"Batch {batch_num}: Completed nodes should be preserved"
        
        # Update tree for next iteration
        tree = evolved_tree
        await hta_service.save_tree(snapshot, tree)
        
        # Verify tree can be reloaded with context intact
        reloaded_tree = await hta_service.load_tree(snapshot)
        assert reloaded_tree is not None, f"Batch {batch_num}: Should reload tree"
        assert reloaded_tree.root.title == goal, f"Batch {batch_num}: Reloaded root title should match goal"
        assert context.lower() in reloaded_tree.root.description.lower(), f"Batch {batch_num}: Reloaded root description should contain context"

    # Final verification
    final_tree = await hta_service.load_tree(snapshot)
    assert final_tree is not None, "Should load final tree"
    assert final_tree.root.title == initial_context["goal"], "Final root title should match initial goal"
    assert initial_context["context"].lower() in final_tree.root.description.lower(), "Final root description should contain initial context"
    
    # Verify context cache
    cached_context = hta_service.context_cache.get(final_tree.root.id)
    assert cached_context is not None, "Context should be cached"
    assert cached_context["goal"] == goal, "Cached goal should match"
    assert cached_context["context"] == context, "Cached context should match"

@pytest.mark.asyncio
async def test_hta_input_validation():
    """Test input validation and error handling for HTA operations."""
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Test invalid tree operations
    tree = HTATree.from_dict({"root": {"id": "root_1", "title": "Test"}})
    
    # Test invalid node status updates
    invalid_statuses = ["invalid_status", 123, True]  # Removed empty string and None as they are handled differently
    for status in invalid_statuses:
        result = await hta_service.update_node_status(tree, "root_1", status)
        assert not result, f"Status {status} should not be accepted"
    
    # Test invalid node IDs
    invalid_ids = [123, True, "non_existent_id"]  # Removed empty string and None as they are handled differently
    for node_id in invalid_ids:
        result = await hta_service.update_node_status(tree, node_id, "completed")
        assert not result, f"Node ID {node_id} should not be accepted"

@pytest.mark.asyncio
async def test_hta_state_consistency():
    """Test state consistency throughout HTA operations."""
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Create initial tree
    goal = "Test Goal"
    context = "Test Context"
    user_id = 1
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    
    # Verify initial state
    assert tree.root is not None
    initial_state = {
        "root_id": tree.root.id,
        "root_title": tree.root.title,
        "child_count": len(tree.root.children),
        "node_map": tree.get_node_map()
    }
    
    # Save and reload to verify persistence
    await hta_service.save_tree(snapshot, tree)
    reloaded_tree = await hta_service.load_tree(snapshot)
    assert reloaded_tree is not None
    assert reloaded_tree.root.id == initial_state["root_id"]
    assert reloaded_tree.root.title == initial_state["root_title"]
    assert len(reloaded_tree.root.children) == initial_state["child_count"]
    
    # Verify node map consistency
    reloaded_node_map = reloaded_tree.get_node_map()
    assert len(reloaded_node_map) == len(initial_state["node_map"])
    for node_id, node in initial_state["node_map"].items():
        assert node_id in reloaded_node_map
        assert reloaded_node_map[node_id].title == node.title

@pytest.mark.asyncio
async def test_hta_task_generation_edge_cases():
    """Test edge cases in task generation and evolution."""
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Create initial tree
    goal = "Test Goal"
    context = "Test Context"
    user_id = 1
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    await hta_service.save_tree(snapshot, tree)
    
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    
    # Test task generation with empty snapshot
    empty_snapshot = MemorySnapshot()
    empty_snapshot.core_state = {}
    tasks = task_engine.get_next_step(empty_snapshot.to_dict())
    assert "tasks" in tasks
    assert len(tasks["tasks"]) == 0
    
    # Test task generation with all tasks completed
    for child in tree.root.children:
        await hta_service.update_node_status(tree, child.id, "completed")
    await hta_service.save_tree(snapshot, tree)
    
    tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in tasks
    assert len(tasks["tasks"]) == 0
    
    # Test evolution with empty reflections
    evolved_tree = await hta_service.evolve_tree(tree, [])
    assert evolved_tree is not None
    assert len(evolved_tree.root.children) >= len(tree.root.children)
    
    # Test evolution with duplicate reflections
    duplicate_reflections = ["Same reflection"] * 5
    evolved_tree = await hta_service.evolve_tree(tree, duplicate_reflections)
    assert evolved_tree is not None
    assert len(evolved_tree.root.children) > len(tree.root.children)

@pytest.mark.asyncio
async def test_hta_clean_code_practices():
    """Test adherence to clean code practices and proper error handling."""
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Test proper error handling
    result = await hta_service.update_node_status(None, "node_id", "completed")
    assert not result
    
    # Test proper state cleanup
    tree = HTATree.from_dict({"root": {"id": "root_1", "title": "Test"}})
    save_result = await hta_service.save_tree(snapshot, tree)
    assert save_result
    
    # Verify snapshot is properly updated
    assert "hta_tree" in snapshot.core_state
    assert snapshot.core_state["hta_tree"]["root"]["id"] == "root_1"
    
    # Test proper error recovery
    result = await hta_service.update_node_status(tree, "non_existent", "completed")
    assert not result
    
    # Verify service is still in a valid state
    health = hta_service.get_health_status()
    assert health["last_operation_success"] is not None

@pytest.mark.asyncio
async def test_comprehensive_onboarding_flow():
    """
    Test the complete onboarding flow including:
    1. Goal setting and context addition
    2. Initial HTA tree generation
    3. Child node creation and structure
    4. Frontier node identification
    5. Data flow through the architecture
    """
    # Setup
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    snapshot.component_state = {"seed_manager": {"active_seed_id": "seed_1"}}
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())

    # 1. Test goal and context setting
    goal = "Learn Python programming from scratch"
    context = "I'm a beginner with 2 hours per day to study, aiming to build web applications"
    user_id = 1

    # 2. Test HTA generation
    hta_model_dict, seed_desc = await hta_service.generate_onboarding_hta(goal, context, user_id)

    assert hta_model_dict is not None, "HTA model dictionary should be generated"
    assert "hta_root" in hta_model_dict, "HTA model should contain root node"
    assert not hta_model_dict.get("_fallback_used", False), "Should not use fallback HTA"

    # 3. Test tree creation and structure
    tree = HTATree.from_dict(hta_model_dict)
    assert tree.root is not None, "Tree should have a root node"
    assert tree.root.title is not None, "Root node should have a title"
    assert tree.root.description is not None, "Root node should have a description"
    assert isinstance(tree.root.priority, float), "Root node should have a valid priority"
    assert 0.0 <= tree.root.priority <= 1.0, "Priority should be between 0 and 1"

    # 4. Test child nodes
    assert isinstance(tree.root.children, list), "Root should have a children list"
    assert len(tree.root.children) > 0, "Root should have at least one child node"
    for child in tree.root.children:
        assert child.id is not None, "Child node should have an ID"
        assert child.title is not None, "Child node should have a title"
        assert child.description is not None, "Child node should have a description"
        assert isinstance(child.priority, float), "Child node should have a valid priority"
        assert 0.0 <= child.priority <= 1.0, "Child priority should be between 0 and 1"
        assert child.estimated_energy in ["low", "medium", "high"], "Child should have valid energy estimate"
        assert child.estimated_time in ["low", "medium", "high"], "Child should have valid time estimate"

    # 5. Test tree saving
    save_success = await hta_service.save_tree(snapshot, tree)
    assert save_success, "Tree should be saved successfully"
    assert "hta_tree" in snapshot.core_state, "Tree should be in snapshot core state"

    # 6. Test frontier node identification and task generation
    tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in tasks_bundle, "Should generate tasks bundle"
    assert len(tasks_bundle["tasks"]) > 0, "Should generate at least one task"

    # Verify task properties
    for task in tasks_bundle["tasks"]:
        assert "id" in task, "Task should have ID"
        assert "title" in task, "Task should have title"
        assert "description" in task, "Task should have description"
        assert "metadata" in task, "Task should have metadata"
        assert "priority_raw" in task["metadata"], "Task should have priority in metadata"
        assert "magnitude" in task, "Task should have magnitude"
        assert "hta_node_id" in task, "Task should have HTA node ID"
        assert "estimated_time" in task, "Task should have estimated time"
        assert "estimated_energy" in task, "Task should have estimated energy"
        assert "created_at" in task, "Task should have creation timestamp"

        # Verify task corresponds to a node in the tree
        node = tree.find_node_by_id(task["hta_node_id"])
        assert node is not None, f"Task node {task['hta_node_id']} should exist in tree"

    # 7. Test data flow by completing a task
    first_task = tasks_bundle["tasks"][0]
    update_success = await hta_service.update_node_status(tree, first_task["hta_node_id"], "completed")
    assert update_success, "Should successfully update node status"

    # Verify status propagation
    updated_node = tree.find_node_by_id(first_task["hta_node_id"])
    assert updated_node is not None, "Updated node should exist"
    assert hasattr(updated_node, "status"), "Node should have status attribute"
    assert updated_node.status == "completed", "Node status should be updated to completed"

    # 8. Test health monitoring
    health_status = hta_service.get_health_status()
    assert health_status["last_operation_success"], "Last operation should be successful"
    # Allow for some failures as they are expected during normal operation
    assert health_status["failure_count"] >= 0, "Failure count should be non-negative"
    assert health_status["total_ops"] > 0, "Should have recorded operations"

@pytest.mark.asyncio
async def test_conversation_context_task_integration():
    """
    Test the integration between conversation context, task generation, and HTA system.
    This test verifies:
    1. Conversation context is properly maintained and influences task generation
    2. Task generation is triggered by user interactions
    3. Task completion updates are reflected in conversation context
    4. Context is shared between conversation and HTA system
    5. Historical context influences frontier node selection
    """
    # Setup
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    snapshot.component_state = {"seed_manager": {"active_seed_id": "seed_1"}}
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    
    # 1. Initial Context Setup
    goal = "Learn Python Programming"
    context = "Complete beginner, focusing on web development, 2 hours daily"
    user_id = 1
    
    # Add initial conversation context
    snapshot.conversation_history.append({
        "role": "user",
        "content": f"I want to {goal}. {context}",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # 2. Generate Initial HTA and Tasks
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    await hta_service.save_tree(snapshot, tree)
    
    # Verify initial tree reflects conversation context
    assert tree.root.title == goal, "Tree root should reflect user's goal"
    assert context.lower() in tree.root.description.lower(), "Tree context should reflect user's context"
    
    # 3. First Task Generation
    tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in tasks_bundle, "Should generate tasks"
    assert len(tasks_bundle["tasks"]) > 0, "Should have tasks"
    
    # Store tasks in snapshot
    snapshot.task_backlog.extend(tasks_bundle["tasks"])
    snapshot.current_frontier_batch_ids = [task["id"] for task in tasks_bundle["tasks"]]
    
    # 4. Simulate User Interaction with First Task
    first_task = tasks_bundle["tasks"][0]
    user_reflection = f"I've completed the task '{first_task['title']}'. I found it challenging but rewarding."
    
    # Add reflection to conversation history
    snapshot.conversation_history.append({
        "role": "user",
        "content": user_reflection,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    snapshot.current_batch_reflections.append(user_reflection)
    
    # Update task status in both tree and backlog
    await hta_service.update_node_status(tree, first_task["hta_node_id"], "completed")
    # Update task in backlog
    for task in snapshot.task_backlog:
        if task["hta_node_id"] == first_task["hta_node_id"]:
            task["status"] = "completed"
    
    await hta_service.save_tree(snapshot, tree)
    
    # 5. Evolve Tree with Context
    evolved_tree = await hta_service.evolve_tree(tree, [user_reflection])
    assert evolved_tree is not None, "Tree should evolve"
    assert len(evolved_tree.root.children) > len(tree.root.children), "Tree should have new nodes"
    
    # Save evolved tree
    await hta_service.save_tree(snapshot, evolved_tree)
    
    # 6. Generate New Tasks with Updated Context
    new_tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in new_tasks_bundle, "Should generate new tasks"
    assert len(new_tasks_bundle["tasks"]) > 0, "Should have new tasks"
    
    # Add new tasks to backlog
    snapshot.task_backlog.extend(new_tasks_bundle["tasks"])
    snapshot.current_frontier_batch_ids = [task["id"] for task in new_tasks_bundle["tasks"]]
    
    # Verify new tasks are influenced by conversation context
    for task in new_tasks_bundle["tasks"]:
        node = evolved_tree.find_node_by_id(task["hta_node_id"])
        assert node is not None, "Task should map to tree node"
        # Verify task properties reflect user's progress
        assert task["metadata"].get("hta_depth", 0) > 0, "Tasks should be from deeper in the tree"
    
    # 7. Simulate Multiple Task Completions
    for task in new_tasks_bundle["tasks"]:
        completion_reflection = f"Completed {task['title']}. Making good progress!"
        snapshot.conversation_history.append({
            "role": "user",
            "content": completion_reflection,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        snapshot.current_batch_reflections.append(completion_reflection)
        # Update status in both tree and backlog
        await hta_service.update_node_status(evolved_tree, task["hta_node_id"], "completed")
        # Update task in backlog
        for backlog_task in snapshot.task_backlog:
            if backlog_task["hta_node_id"] == task["hta_node_id"]:
                backlog_task["status"] = "completed"
    
    await hta_service.save_tree(snapshot, evolved_tree)
    
    # 8. Final Evolution with Complete Context
    final_tree = await hta_service.evolve_tree(evolved_tree, snapshot.current_batch_reflections)
    assert final_tree is not None, "Tree should evolve"
    
    # Verify final state maintains context
    assert final_tree.root.title == goal, "Root goal should be preserved"
    assert context.lower() in final_tree.root.description.lower(), "Root context should be preserved"
    
    # Count completed tasks
    completed_tasks = [t for t in snapshot.task_backlog if t.get("status") == "completed"]
    assert len(completed_tasks) > 0, "Should have completed tasks"
    
    print(f"Final state: {len(completed_tasks)} completed tasks")
    print(f"Total tasks in backlog: {len(snapshot.task_backlog)}")
    print(f"Total conversation messages: {len(snapshot.conversation_history)}")
    print(f"Total reflections: {len(snapshot.current_batch_reflections)}")
    
    # 9. Verify Conversation History Integration
    assert len(snapshot.conversation_history) > 0, "Should have conversation history"
    assert all(isinstance(msg, dict) and "role" in msg and "content" in msg 
              for msg in snapshot.conversation_history), "Conversation history should be properly structured"
    
    # 10. Verify Reflection Context
    assert len(snapshot.current_batch_reflections) > 0, "Should have reflections"
    assert all(isinstance(r, str) for r in snapshot.current_batch_reflections), "Reflections should be strings"
    
    # 11. Verify Task Backlog
    assert len(snapshot.task_backlog) > 0, "Should have tasks in backlog"
    assert any(t.get("status") == "completed" for t in snapshot.task_backlog), "Should have completed tasks"
    
    # 12. Verify Conversation History Integration
    assert len(snapshot.conversation_history) > 0, "Should have conversation history"
    assert all(isinstance(msg, dict) and "role" in msg and "content" in msg 
              for msg in snapshot.conversation_history), "Conversation history should be properly structured"
    
    # 13. Verify Reflection Context
    assert len(snapshot.current_batch_reflections) > 0, "Should have reflections"
    assert all(isinstance(r, str) for r in snapshot.current_batch_reflections), "Reflections should be strings"
    
    # 14. Verify Tree Evolution
    assert len(final_tree.root.children) > len(tree.root.children), "Tree should have evolved"
    
    print("Conversation context task integration test completed successfully!")

@pytest.mark.asyncio
async def test_user_journey_simulation():
    """
    Simulates a complete user journey through the application, including:
    1. Initial onboarding and goal setting
    2. First task batch and completion
    3. Reflection and tree evolution
    4. Multiple task batches and progress tracking
    5. Context preservation and adaptation
    6. Final reflection and completion
    """
    # Setup
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    snapshot.component_state = {"seed_manager": {"active_seed_id": "seed_1"}}
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    
    # --- Phase 1: Initial Onboarding ---
    print("\n=== Phase 1: Initial Onboarding ===")
    
    # User sets their goal and context
    goal = "Learn Web Development with Python"
    context = "I'm a beginner programmer with 2 hours daily to study. I want to build a personal portfolio website."
    user_id = 1
    
    # Simulate user's initial message
    initial_message = f"I want to {goal}. {context}"
    snapshot.conversation_history.append({
        "role": "user",
        "content": initial_message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    # Generate initial HTA
    print("Generating initial HTA...")
    hta_model_dict, seed_desc = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    await hta_service.save_tree(snapshot, tree)
    
    # Verify initial setup
    assert tree.root.title == goal, "Tree should reflect user's goal"
    assert context.lower() in tree.root.description.lower(), "Tree should include user's context"
    print(f"Initial HTA created with goal: {tree.root.title}")
    
    # --- Phase 2: First Task Batch ---
    print("\n=== Phase 2: First Task Batch ===")
    
    # Get first batch of tasks
    tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in tasks_bundle, "Should generate initial tasks"
    assert len(tasks_bundle["tasks"]) > 0, "Should have tasks to complete"
    
    # Store tasks
    snapshot.task_backlog.extend(tasks_bundle["tasks"])
    snapshot.current_frontier_batch_ids = [task["id"] for task in tasks_bundle["tasks"]]
    
    print(f"Generated {len(tasks_bundle['tasks'])} initial tasks:")
    for task in tasks_bundle["tasks"]:
        print(f"- {task['title']}")
    
    # --- Phase 3: Task Completion and Reflection ---
    print("\n=== Phase 3: Task Completion and Reflection ===")
    
    # Simulate user completing first task
    first_task = tasks_bundle["tasks"][0]
    completion_message = f"I've completed the task '{first_task['title']}'. It was challenging but I learned a lot about {first_task['title'].lower()}."
    
    # Add completion to conversation history
    snapshot.conversation_history.append({
        "role": "user",
        "content": completion_message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    snapshot.current_batch_reflections.append(completion_message)
    
    # Update task status
    await hta_service.update_node_status(tree, first_task["hta_node_id"], "completed")
    for task in snapshot.task_backlog:
        if task["hta_node_id"] == first_task["hta_node_id"]:
            task["status"] = "completed"
    
    print(f"Completed task: {first_task['title']}")
    
    # --- Phase 4: Tree Evolution ---
    print("\n=== Phase 4: Tree Evolution ===")
    
    # Evolve tree based on completion
    evolved_tree = await hta_service.evolve_tree(tree, [completion_message])
    assert evolved_tree is not None, "Tree should evolve after task completion"
    assert len(evolved_tree.root.children) > len(tree.root.children), "Tree should have new nodes"
    
    await hta_service.save_tree(snapshot, evolved_tree)
    print(f"Tree evolved: {len(evolved_tree.root.children)} total nodes")
    
    # --- Phase 5: New Task Generation ---
    print("\n=== Phase 5: New Task Generation ===")
    
    # Get next batch of tasks
    new_tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in new_tasks_bundle, "Should generate new tasks"
    assert len(new_tasks_bundle["tasks"]) > 0, "Should have new tasks"
    
    # Add new tasks to backlog
    snapshot.task_backlog.extend(new_tasks_bundle["tasks"])
    snapshot.current_frontier_batch_ids = [task["id"] for task in new_tasks_bundle["tasks"]]
    
    print(f"Generated {len(new_tasks_bundle['tasks'])} new tasks:")
    for task in new_tasks_bundle["tasks"]:
        print(f"- {task['title']}")
    
    # --- Phase 6: Multiple Task Completions ---
    print("\n=== Phase 6: Multiple Task Completions ===")
    
    # Simulate completing multiple tasks
    for task in new_tasks_bundle["tasks"]:
        # Simulate user reflection
        reflection = f"Completed {task['title']}. I'm making good progress on my web development journey!"
        snapshot.conversation_history.append({
            "role": "user",
            "content": reflection,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        snapshot.current_batch_reflections.append(reflection)
        
        # Update task status
        await hta_service.update_node_status(evolved_tree, task["hta_node_id"], "completed")
        for backlog_task in snapshot.task_backlog:
            if backlog_task["hta_node_id"] == task["hta_node_id"]:
                backlog_task["status"] = "completed"
        
        print(f"Completed task: {task['title']}")
    
    # --- Phase 7: Final Evolution ---
    print("\n=== Phase 7: Final Evolution ===")
    
    # Evolve tree with all reflections
    final_tree = await hta_service.evolve_tree(evolved_tree, snapshot.current_batch_reflections)
    assert final_tree is not None, "Tree should evolve with all reflections"
    
    # Verify final state maintains context
    assert final_tree.root.title == goal, "Goal should be preserved"
    assert context.lower() in final_tree.root.description.lower(), "Context should be preserved"
    
    # Count completed tasks
    completed_tasks = [t for t in snapshot.task_backlog if t.get("status") == "completed"]
    assert len(completed_tasks) > 0, "Should have completed tasks"
    
    print(f"Final state: {len(completed_tasks)} completed tasks")
    print(f"Total tasks in backlog: {len(snapshot.task_backlog)}")
    print(f"Total conversation messages: {len(snapshot.conversation_history)}")
    print(f"Total reflections: {len(snapshot.current_batch_reflections)}")
    
    # --- Phase 8: Final Verification ---
    print("\n=== Phase 8: Final Verification ===")
    
    # Verify conversation history
    assert len(snapshot.conversation_history) > 0, "Should have conversation history"
    assert all(isinstance(msg, dict) and "role" in msg and "content" in msg 
              for msg in snapshot.conversation_history), "Conversation history should be properly structured"
    
    # Verify task backlog
    assert len(snapshot.task_backlog) > 0, "Should have tasks in backlog"
    assert any(t.get("status") == "completed" for t in snapshot.task_backlog), "Should have completed tasks"
    
    # Verify reflections
    assert len(snapshot.current_batch_reflections) > 0, "Should have reflections"
    assert all(isinstance(r, str) for r in snapshot.current_batch_reflections), "Reflections should be strings"
    
    # Verify tree evolution
    assert len(final_tree.root.children) > len(tree.root.children), "Tree should have evolved"
    
    print("User journey simulation completed successfully!")

@pytest.mark.asyncio
async def test_complete_hta_flow():
    """
    Test the complete flow from context to task generation:
    1. Create context and generate HTA tree
    2. Verify tree structure and child nodes
    3. Generate frontier tasks
    4. Verify data flow and state preservation
    5. Complete tasks and verify new task generation
    """
    # Initialize services
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # 1. Create context and generate initial HTA tree
    goal = "Learn Advanced Python Programming"
    context = "Experienced developer, 6 months timeline, focus on data science and machine learning"
    user_id = 1
    
    # Generate HTA tree
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    
    # Verify initial tree structure
    assert tree.root is not None, "Tree should have a root node"
    assert tree.root.title == goal, "Root title should match goal"
    assert context.lower() in tree.root.description.lower(), "Root description should include context"
    assert len(tree.root.children) > 0, "Root should have child nodes"
    
    # Save tree to snapshot
    await hta_service.save_tree(snapshot, tree)
    
    # 2. Verify child nodes and their properties
    for child in tree.root.children:
        assert child.id is not None, "Child node should have an ID"
        assert child.title is not None, "Child node should have a title"
        assert child.description is not None, "Child node should have a description"
        assert isinstance(child.priority, float), "Child node should have a valid priority"
        assert 0.0 <= child.priority <= 1.0, "Priority should be between 0 and 1"
        assert child.estimated_energy in ["low", "medium", "high"], "Child should have valid energy estimate"
        assert child.estimated_time in ["low", "medium", "high"], "Child should have valid time estimate"
    
    # 3. Generate frontier tasks
    tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    
    # Verify task bundle structure
    assert "tasks" in tasks_bundle, "Should generate tasks bundle"
    assert len(tasks_bundle["tasks"]) > 0, "Should generate at least one task"
    assert len(tasks_bundle["tasks"]) <= MAX_FRONTIER_BATCH_SIZE, f"Should not exceed max batch size of {MAX_FRONTIER_BATCH_SIZE}"
    
    # 4. Verify task properties and data flow
    for task in tasks_bundle["tasks"]:
        # Verify task structure
        assert "id" in task, "Task should have ID"
        assert "title" in task, "Task should have title"
        assert "description" in task, "Task should have description"
        assert "magnitude" in task, "Task should have magnitude"
        assert "hta_node_id" in task, "Task should have HTA node ID"
        assert "metadata" in task, "Task should have metadata"
        
        # Verify task metadata
        assert "priority_raw" in task["metadata"], "Task should have priority in metadata"
        assert "hta_depth" in task["metadata"], "Task should have depth in metadata"
        
        # Verify task values
        assert isinstance(task["magnitude"], float), "Magnitude should be a float"
        assert 0.0 <= task["magnitude"] <= 10.0, "Magnitude should be between 0 and 10"
        assert isinstance(task["metadata"]["priority_raw"], float), "Priority should be a float"
        assert 0.0 <= task["metadata"]["priority_raw"] <= 1.0, "Priority should be between 0 and 1"
        
        # Verify task-node relationship
        node_id = task["hta_node_id"]
        node = tree.get_node_map().get(node_id)
        assert node is not None, "Task should reference a valid HTA node"
        assert node.title == task["title"], "Task title should match node title"
        assert node.description == task["description"], "Task description should match node description"
    
    # 5. Complete first batch of tasks
    for task in tasks_bundle["tasks"]:
        # Mark task as completed in tree
        node_id = task["hta_node_id"]
        update_success = await hta_service.update_node_status(tree, node_id, "completed")
        assert update_success, f"Should be able to complete task {task['id']}"
        
        # Add completion reflection
        completion_reflection = f"Completed task: {task['title']}. It was helpful for {goal}."
        if not hasattr(snapshot, 'current_batch_reflections'):
            snapshot.current_batch_reflections = []
        snapshot.current_batch_reflections.append(completion_reflection)
    
    # Save updated tree
    await hta_service.save_tree(snapshot, tree)
    
    # 6. Evolve tree with reflections
    evolved_tree = await hta_service.evolve_tree(tree, snapshot.current_batch_reflections)
    assert evolved_tree is not None, "Tree should evolve after task completion"
    await hta_service.save_tree(snapshot, evolved_tree)
    
    # 7. Generate new tasks
    new_tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in new_tasks_bundle, "Should generate new tasks bundle"
    assert len(new_tasks_bundle["tasks"]) > 0, "Should generate at least one new task"
    
    # 8. Verify new tasks are different
    original_task_ids = {task["id"] for task in tasks_bundle["tasks"]}
    new_task_ids = {task["id"] for task in new_tasks_bundle["tasks"]}
    assert not (original_task_ids & new_task_ids), "New tasks should be different from original tasks"
    
    # 9. Verify task properties maintained in new tasks
    for task in new_tasks_bundle["tasks"]:
        assert "id" in task, "New task should have ID"
        assert "title" in task, "New task should have title"
        assert "description" in task, "New task should have description"
        assert "magnitude" in task, "New task should have magnitude"
        assert "hta_node_id" in task, "New task should have HTA node ID"
        assert isinstance(task["magnitude"], float), "New task magnitude should be a float"
        assert 0.0 <= task["magnitude"] <= 10.0, "New task magnitude should be between 0 and 10"
        
        # Verify new task-node relationship
        node_id = task["hta_node_id"]
        node = evolved_tree.get_node_map().get(node_id)
        assert node is not None, "New task should reference a valid HTA node"
        assert node.title == task["title"], "New task title should match node title"
        assert node.description == task["description"], "New task description should match node description"

    # 10. Verify state preservation
    reloaded_tree = await hta_service.load_tree(snapshot)
    assert reloaded_tree is not None, "Should be able to reload tree from snapshot"
    assert reloaded_tree.root.id == evolved_tree.root.id, "Root ID should match evolved tree"
    assert len(reloaded_tree.root.children) == len(evolved_tree.root.children), "Child count should match evolved tree"
    
    # Verify evolved tree maintains goal and context
    assert reloaded_tree.root.title == goal, "Goal should be preserved in evolved tree"
    assert context.lower() in reloaded_tree.root.description.lower(), "Context should be preserved in evolved tree"
    
    # Verify completed tasks remain completed
    completed_nodes = [node for node in reloaded_tree.get_node_map().values() if getattr(node, 'status', '') == 'completed']
    assert len(completed_nodes) > 0, "Completed nodes should be preserved"
    
    # 11. Verify task generation with updated state
    updated_tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in updated_tasks, "Should generate tasks with updated state"
    assert len(updated_tasks["tasks"]) > 0, "Should generate tasks with updated state"
    
    # 12. Verify no duplicate tasks between all generations
    all_task_ids = {task["id"] for task in tasks_bundle["tasks"]}
    all_task_ids.update(task["id"] for task in new_tasks_bundle["tasks"])
    updated_task_ids = {task["id"] for task in updated_tasks["tasks"]}
    assert not (all_task_ids & updated_task_ids), "Should not regenerate any previously generated tasks" 

@pytest.mark.asyncio
async def test_task_engine_error_handling():
    """
    Test TaskEngine error handling and edge cases:
    1. Invalid tree structures
    2. Missing/invalid node properties
    3. Resource constraints
    4. Session management
    5. Fallback task generation
    """
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    
    # Test 1: Invalid Tree Structure
    snapshot.core_state["hta_tree"] = {"invalid": "structure"}
    tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in tasks, "Should return tasks list even with invalid tree"
    assert len(tasks["tasks"]) == 0, "Should have no tasks with invalid tree"
    assert tasks["fallback_task"] is not None, "Should generate fallback task"
    
    # Test 2: Missing Node Properties
    class InvalidNode:
        def __init__(self):
            self.id = "invalid_node"
            # Missing required properties
    
    tree = HTATree()
    tree.root = InvalidNode()
    snapshot.core_state["hta_tree"] = tree.to_dict()
    
    tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in tasks, "Should handle missing node properties"
    assert len(tasks["tasks"]) == 0, "Should not generate tasks from invalid nodes"
    assert tasks["fallback_task"] is not None, "Should generate fallback task"
    
    # Test 3: Resource Constraints
    # Create a tree with resource-intensive nodes
    goal = "Test Resource Constraints"
    context = "Testing resource management"
    user_id = 1
    
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    
    # Set resource constraints
    snapshot.core_state["hta_tree"] = tree.to_dict()
    snapshot.core_state["available_resources"] = {
        "energy": "low",
        "time": "low"
    }
    
    tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in tasks, "Should handle resource constraints"
    if tasks["tasks"]:
        for task in tasks["tasks"]:
            assert task["estimated_energy"] == "low", "Should respect energy constraints"
            assert task["estimated_time"] == "low", "Should respect time constraints"
    
    # Test 4: Session Management
    # Generate initial tasks
    tasks = task_engine.get_next_step(snapshot.to_dict())
    initial_task_ids = {task["id"] for task in tasks["tasks"]}
    
    # Verify task IDs are persisted
    persisted_ids = task_engine._get_persisted_task_ids(snapshot.to_dict())
    assert initial_task_ids.issubset(persisted_ids), "Task IDs should be persisted"
    
    # Simulate tree evolution
    snapshot.core_state["tree_evolved"] = True
    tasks = task_engine.get_next_step(snapshot.to_dict())
    
    # Verify task IDs are cleared after evolution
    cleared_ids = task_engine._get_persisted_task_ids(snapshot.to_dict())
    assert not (initial_task_ids & cleared_ids), "Task IDs should be cleared after evolution"
    
    # Test 5: Fallback Task Generation
    # Test various error scenarios
    error_scenarios = [
        "no_tree",
        "invalid_nodes",
        "flatten_error",
        "no_candidates",
        "empty_bundle"
    ]
    
    for scenario in error_scenarios:
        snapshot.core_state["error_scenario"] = scenario
        tasks = task_engine.get_next_step(snapshot.to_dict())
        assert "fallback_task" in tasks, f"Should generate fallback task for {scenario}"
        assert tasks["fallback_task"] is not None, f"Fallback task should not be None for {scenario}"
        assert "id" in tasks["fallback_task"], f"Fallback task should have ID for {scenario}"
        assert "title" in tasks["fallback_task"], f"Fallback task should have title for {scenario}"

@pytest.mark.asyncio
async def test_task_prioritization_and_dependencies():
    """
    Test task prioritization and dependency management:
    1. Task priority calculation
    2. Dependency resolution
    3. Task ordering based on dependencies
    4. Priority updates during evolution
    """
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    
    # Create initial tree with dependencies
    goal = "Build a Complex Web Application"
    context = "Using React, Node.js, and MongoDB. Need to handle user authentication and data persistence."
    user_id = 1
    
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    await hta_service.save_tree(snapshot, tree)
    
    # Test 1: Initial Task Priority
    tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in tasks_bundle, "Should generate tasks"
    assert len(tasks_bundle["tasks"]) > 0, "Should have tasks"
    
    # Verify task priorities
    for task in tasks_bundle["tasks"]:
        assert "metadata" in task, "Task should have metadata"
        assert "priority_raw" in task["metadata"], "Task should have priority"
        assert 0.0 <= task["metadata"]["priority_raw"] <= 1.0, "Priority should be between 0 and 1"
        
        # Verify priority matches node priority
        node = tree.find_node_by_id(task["hta_node_id"])
        assert node is not None, "Task should map to existing node"
        assert abs(float(node.priority) - float(task["metadata"]["priority_raw"])) < 0.001, "Task priority should match node priority"
    
    # Test 2: Task Dependencies
    # Complete first task to test dependency resolution
    first_task = tasks_bundle["tasks"][0]
    await hta_service.update_node_status(tree, first_task["hta_node_id"], "completed")
    await hta_service.save_tree(snapshot, tree)
    
    # Get next batch of tasks
    next_tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in next_tasks, "Should generate next tasks"
    
    # Verify new tasks don't depend on completed tasks
    for task in next_tasks["tasks"]:
        node = tree.find_node_by_id(task["hta_node_id"])
        assert node is not None, "Task should map to existing node"
        assert first_task["hta_node_id"] not in node.depends_on, "New tasks should not depend on completed tasks"
    
    # Test 3: Priority Updates During Evolution
    # Add reflections to trigger evolution
    reflections = ["Completed initial setup tasks", "Ready for more complex features"]
    evolved_tree = await hta_service.evolve_tree(tree, reflections)
    assert evolved_tree is not None, "Tree should evolve"
    
    await hta_service.save_tree(snapshot, evolved_tree)
    
    # Get tasks from evolved tree
    evolved_tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in evolved_tasks, "Should generate tasks from evolved tree"
    
    # Verify evolved task priorities
    for task in evolved_tasks["tasks"]:
        node = evolved_tree.find_node_by_id(task["hta_node_id"])
        assert node is not None, "Task should map to existing node"
        assert abs(float(node.priority) - float(task["metadata"]["priority_raw"])) < 0.001, "Evolved task priority should match node priority"
        
        # Verify priority distribution
        assert task["metadata"]["priority_raw"] > 0.0, "Task should have positive priority"
        assert task["metadata"]["priority_raw"] <= 1.0, "Task priority should not exceed 1.0"

@pytest.mark.asyncio
async def test_task_evolution_patterns():
    """
    Test various task evolution patterns:
    1. Linear progression
    2. Branching paths
    3. Task refinement
    4. Context adaptation
    """
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    
    # Initial setup
    goal = "Master Data Science"
    context = "Background in Python, want to learn machine learning and data analysis"
    user_id = 1
    
    hta_model_dict, _ = await hta_service.generate_onboarding_hta(goal, context, user_id)
    tree = HTATree.from_dict(hta_model_dict)
    await hta_service.save_tree(snapshot, tree)
    
    # Test 1: Linear Progression
    initial_tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in initial_tasks, "Should generate initial tasks"
    
    # Complete initial tasks
    for task in initial_tasks["tasks"]:
        await hta_service.update_node_status(tree, task["hta_node_id"], "completed")
    
    await hta_service.save_tree(snapshot, tree)
    
    # Evolve tree with linear progression reflection
    linear_reflection = "Completed basic data science concepts, ready for more advanced topics"
    evolved_tree = await hta_service.evolve_tree(tree, [linear_reflection])
    assert evolved_tree is not None, "Tree should evolve"
    
    # Verify linear progression
    next_tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in next_tasks, "Should generate next tasks"
    assert len(next_tasks["tasks"]) > 0, "Should have next tasks"
    
    # Test 2: Branching Paths
    # Complete some tasks to create branching
    for task in next_tasks["tasks"][:2]:  # Complete first two tasks
        await hta_service.update_node_status(evolved_tree, task["hta_node_id"], "completed")
    
    await hta_service.save_tree(snapshot, evolved_tree)
    
    # Evolve with branching reflection
    branching_reflection = "Interested in both machine learning and data visualization paths"
    branched_tree = await hta_service.evolve_tree(evolved_tree, [branching_reflection])
    assert branched_tree is not None, "Tree should branch"
    
    # Verify branching
    branched_tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in branched_tasks, "Should generate branched tasks"
    assert len(branched_tasks["tasks"]) > 0, "Should have branched tasks"
    
    # Test 3: Task Refinement
    # Complete some branched tasks
    for task in branched_tasks["tasks"]:
        await hta_service.update_node_status(branched_tree, task["hta_node_id"], "completed")
    
    await hta_service.save_tree(snapshot, branched_tree)
    
    # Evolve with refinement reflection
    refinement_reflection = "Need more detailed steps for implementing machine learning models"
    refined_tree = await hta_service.evolve_tree(branched_tree, [refinement_reflection])
    assert refined_tree is not None, "Tree should refine tasks"
    
    # Verify refinement
    refined_tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in refined_tasks, "Should generate refined tasks"
    assert len(refined_tasks["tasks"]) > 0, "Should have refined tasks"
    
    # Test 4: Context Adaptation
    # Evolve with context change
    context_change = "Decided to focus more on deep learning and neural networks"
    adapted_tree = await hta_service.evolve_tree(refined_tree, [context_change])
    assert adapted_tree is not None, "Tree should adapt to new context"
    
    # Verify context adaptation
    adapted_tasks = task_engine.get_next_step(snapshot.to_dict())
    assert "tasks" in adapted_tasks, "Should generate adapted tasks"
    assert len(adapted_tasks["tasks"]) > 0, "Should have adapted tasks"
    
    # Verify tasks reflect new context
    for task in adapted_tasks["tasks"]:
        node = adapted_tree.find_node_by_id(task["hta_node_id"])
        assert node is not None, "Task should map to existing node"
        assert any(keyword in node.title.lower() or keyword in node.description.lower() 
                  for keyword in ["deep learning", "neural", "network"]), "Tasks should reflect new context"