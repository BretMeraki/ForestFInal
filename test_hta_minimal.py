import asyncio
import pytest
from forest_app.hta_tree.hta_service import HTAService
from forest_app.hta_tree.hta_tree import HTATree
from forest_app.snapshot.snapshot import MemorySnapshot
from forest_app.hta_tree.task_engine import TaskEngine
from forest_app.modules.cognitive.pattern_id import PatternIdentificationEngine
from forest_app.hta_tree.hta_models import HTAResponseModel, HTANodeModel
from forest_app.integrations.llm import HTAEvolveResponse

# Dummy classes for testing
class DummyLLMClient:
    def __init__(self):
        self.task_counter = 0

    async def generate(self, *args, **kwargs):
        # Extract goal and context from prompt
        prompt = kwargs.get('prompt_parts', [None])[0] if 'prompt_parts' in kwargs else args[0] if args else None
        if prompt:
            import re
            goal_match = re.search(r"Goal: ([^\n]+)", prompt)
            context_match = re.search(r"Context: ([^\n]+)", prompt)
            root_id_match = re.search(r"Root MUST use: '([^']+)'", prompt)
            
            goal = goal_match.group(1) if goal_match else "Test Goal"
            context = context_match.group(1) if context_match else "Test Description"
            root_id = root_id_match.group(1) if root_id_match else "root_1"
        else:
            goal = "Test Goal"
            context = "Test Description"
            root_id = "root_1"
        
        # Create root node using HTANodeModel
        root_node = HTANodeModel(
            id=root_id,
            title=goal,
            description=f"Initial plan for: {goal}. Context: {context}",
            priority=1.0,
            depends_on=[],
            estimated_energy="medium",
            estimated_time="medium",
            linked_tasks=[],
            is_milestone=True,
            rationale="",
            status_suggestion="pending",
            children=[
                HTANodeModel(
                    id="child_1",
                    title=f"First step for {goal}",
                    description=f"Begin with {context}",
                    priority=0.8,
                    depends_on=[],
                    estimated_energy="medium",
                    estimated_time="medium",
                    linked_tasks=[],
                    is_milestone=False,
                    rationale="",
                    status_suggestion="pending",
                    children=[]
                )
            ]
        )
        
        # Create and return response using HTAResponseModel
        response = HTAResponseModel(hta_root=root_node)
        return response

    async def request_hta_evolution(self, current_hta_json: str, evolution_goal: str, evolution_prompt: dict = None, use_advanced_model: bool = True) -> HTAEvolveResponse:
        """Mock implementation of HTA evolution request."""
        import json
        
        # Parse the current HTA tree and evolution prompt
        current_hta = json.loads(current_hta_json)
        root_node = current_hta.get("root", {})
        root_id = root_node.get("id", "root_1")
        goal = evolution_prompt.get('goal', 'Test Goal') if evolution_prompt else 'Test Goal'
        context = evolution_prompt.get('context', 'Test Description') if evolution_prompt else 'Test Description'
        
        def convert_node_to_model(node_dict):
            """Recursively convert a node dictionary to HTANodeModel."""
            # First convert all children
            children = [convert_node_to_model(child) for child in node_dict.get("children", [])]
            
            # Create the node model with all properties from the original node
            node_model = HTANodeModel(
                id=node_dict["id"],
                title=node_dict["title"],
                description=node_dict.get("description", "") if "description" in node_dict else f"Task related to {goal}. Context: {context}",
                priority=node_dict.get("priority", 0.8),
                magnitude=node_dict.get("magnitude", 5.0),
                depends_on=node_dict.get("depends_on", []),
                estimated_energy=node_dict.get("estimated_energy", "medium"),
                estimated_time=node_dict.get("estimated_time", "medium"),
                linked_tasks=node_dict.get("linked_tasks", []),
                is_milestone=node_dict.get("is_milestone", False),
                rationale=node_dict.get("rationale", ""),
                status_suggestion=node_dict.get("status_suggestion", "pending"),
                status=node_dict.get("status", "pending"),
                children=children
            )
            return node_model
        
        # Convert the root tree to a model while preserving its ID
        root_model = convert_node_to_model(root_node)
        
        # Make sure root title is still the original goal
        root_model.title = goal
        
        # Ensure root description contains the context
        if context and context.lower() not in root_model.description.lower():
            root_model.description = f"{root_model.description} Context: {context}"
        
        # Add two new children to simulate tree evolution
        self.task_counter += 1
        
        # Add a new evolved child
        root_model.children.append(
            HTANodeModel(
                id=f"evolved_child_{self.task_counter}",
                title=f"Next phase for {goal}",
                description=f"Evolved task based on reflections. Context: {context}",
                priority=0.9,
                depends_on=[],
                estimated_energy="medium",
                estimated_time="medium",
                linked_tasks=[],
                is_milestone=False,
                rationale="Added during evolution",
                status_suggestion="pending",
                status="pending",
                children=[]
            )
        )
        
        # Add another child to ensure evolution shows growth
        self.task_counter += 1
        root_model.children.append(
            HTANodeModel(
                id=f"evolved_child_{self.task_counter}",
                title=f"Additional task for {goal}",
                description=f"Second evolved task with context: {context}",
                priority=0.7,
                depends_on=[],
                estimated_energy="low",
                estimated_time="low",
                linked_tasks=[],
                is_milestone=False,
                rationale="Added during evolution to show progress",
                status_suggestion="pending",
                status="pending",
                children=[]
            )
        )
        
        # Create HTAEvolveResponse with the root model
        return HTAEvolveResponse(hta_root=root_model)
        
        # The model is already properly structured for response

class DummySeedManager:
    async def get_seed_by_id(self, seed_id):
        return type('Seed', (), {'hta_tree': None, 'seed_id': seed_id})()
    
    async def get_primary_active_seed(self):
        return type('Seed', (), {'hta_tree': None, 'seed_id': 'seed_1'})()
    
    async def update_seed(self, seed_id, hta_tree):
        return True

@pytest.mark.asyncio
async def test_basic_hta_flow():
    """Test the basic HTA flow with enhanced assertions and error handling."""
    print("Starting basic HTA flow test...")
    
    # Initialize services
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    task_engine = TaskEngine(pattern_engine=PatternIdentificationEngine())
    
    try:
        # Test 1: Generate initial HTA
        print("\nTest 1: Generating initial HTA...")
        goal = "Learn Python"
        context = "Beginner programmer"
        user_id = 1
        
        hta_model_dict, seed_desc = await hta_service.generate_onboarding_hta(goal, context, user_id)
        assert hta_model_dict is not None, "HTA model dictionary should be generated"
        assert "hta_root" in hta_model_dict, "HTA model should contain root node"
        
        root_node = hta_model_dict["hta_root"]
        assert root_node["title"] == goal, "Root title should match goal"
        assert context.lower() in root_node["description"].lower(), "Root description should include context"
        assert len(root_node["children"]) > 0, "Root should have at least one child"
        print(f"Generated HTA with {len(root_node['children'])} initial tasks")
        
        # Test 2: Create and save tree
        print("\nTest 2: Creating and saving tree...")
        tree = HTATree.from_dict({"root": root_node})
        assert tree.root is not None, "Tree should have root node"
        assert tree.root.title == goal, "Tree root title should match goal"
        
        save_success = await hta_service.save_tree(snapshot, tree)
        assert save_success, "Tree should save successfully"
        assert "hta_tree" in snapshot.core_state, "Tree should be in snapshot"
        print(f"Tree saved successfully: {save_success}")
        
        # Test 3: Generate tasks
        print("\nTest 3: Generating tasks...")
        tasks_bundle = task_engine.get_next_step(snapshot.to_dict())
        assert "tasks" in tasks_bundle, "Should generate tasks bundle"
        assert len(tasks_bundle["tasks"]) > 0, "Should have at least one task"
        
        # Verify task properties
        first_task = tasks_bundle["tasks"][0]
        assert "id" in first_task, "Task should have ID"
        assert "title" in first_task, "Task should have title"
        assert "description" in first_task, "Task should have description"
        assert "hta_node_id" in first_task, "Task should have HTA node ID"
        print(f"Generated {len(tasks_bundle['tasks'])} tasks")
        
        # Test 4: Update task status
        print("\nTest 4: Updating task status...")
        if tasks_bundle['tasks']:
            update_success = await hta_service.update_node_status(tree, first_task['hta_node_id'], "completed")
            assert update_success, "Task status should update successfully"
            
            # Verify node status was updated
            updated_node = tree.find_node_by_id(first_task['hta_node_id'])
            assert updated_node is not None, "Updated node should exist"
            assert updated_node.status == "completed", "Node status should be updated to completed"
            
            await hta_service.save_tree(snapshot, tree)
            print(f"Task status updated successfully: {update_success}")
        
        # Test 5: Evolve tree
        print("\nTest 5: Evolving tree...")
        reflections = ["Completed first task successfully"]
        
        # Enable more detailed debugging for evolution
        print(f"\nTree before evolution - Root ID: {tree.root.id}, Title: {tree.root.title}")
        print(f"Children count: {len(tree.root.children)}")
        print(f"Goal: {goal}, Context: {context}")
        
        # Pass all parameters including snapshot and user_id
        evolved_tree = await hta_service.evolve_tree(tree, reflections, snapshot=snapshot, goal=goal, context=context, user_id=user_id)
        
        if evolved_tree is None:
            print(f"\nEVOLUTION FAILED - last_error: {hta_service.last_error}")
        
        assert evolved_tree is not None, "Tree should evolve successfully"
        assert len(evolved_tree.root.children) > len(tree.root.children), "Evolved tree should have more nodes"
        
        # Verify evolved tree maintains context
        assert evolved_tree.root.title == goal, "Evolved tree should maintain goal"
        assert context.lower() in evolved_tree.root.description.lower(), "Evolved tree should maintain context"
        
        # Save evolved tree
        save_success = await hta_service.save_tree(snapshot, evolved_tree)
        assert save_success, "Evolved tree should save successfully"
        print(f"Tree evolved with {len(evolved_tree.root.children)} total tasks")
        
        # Test 6: Load tree from snapshot
        print("\nTest 6: Loading tree from snapshot...")
        loaded_tree = await hta_service.load_tree(snapshot)
        assert loaded_tree is not None, "Should load tree from snapshot"
        assert loaded_tree.root.id == evolved_tree.root.id, "Loaded tree should match evolved tree"
        assert len(loaded_tree.root.children) == len(evolved_tree.root.children), "Loaded tree should have same number of children"
        
        print("\nBasic HTA flow test completed successfully!")
        return True
    
    except Exception as e:
        print(f"\nError during test: {str(e)}")
        raise

@pytest.mark.asyncio
async def test_hta_error_handling():
    """Test error handling in HTA operations."""
    hta_service = HTAService(llm_client=DummyLLMClient(), seed_manager=DummySeedManager())
    snapshot = MemorySnapshot()
    snapshot.core_state = {}
    
    # Test invalid tree operations
    tree = HTATree.from_dict({"root": {"id": "root_1", "title": "Test"}})
    
    # Test invalid node status updates
    invalid_statuses = ["invalid_status", 123, True]
    for status in invalid_statuses:
        result = await hta_service.update_node_status(tree, "root_1", status)
        assert not result, f"Status {status} should not be accepted"
    
    # Test invalid node IDs
    invalid_ids = [123, True, "non_existent_id"]
    for node_id in invalid_ids:
        result = await hta_service.update_node_status(tree, node_id, "completed")
        assert not result, f"Node ID {node_id} should not be accepted"

if __name__ == "__main__":
    asyncio.run(test_basic_hta_flow()) 