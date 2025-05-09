"""
Integration tests for verifying thread safety in the ForestOrchestrator.
Tests multiple concurrent requests to ensure no state bleed between users.
"""
import pytest
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from forest_app.main import app
from forest_app.core.orchestrator import ForestOrchestrator

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_llm_responses():
    """Mock LLM client to return deterministic responses."""
    with patch("forest_app.core.llm.client.LLMClient.generate") as mock_generate:
        # Configure each call to return a unique response based on input
        def side_effect(prompt, *args, **kwargs):
            return f"Response for: {prompt[:20]}..."
        
        mock_generate.side_effect = side_effect
        yield mock_generate

class TestOrchestratorConcurrency:
    """Tests for ForestOrchestrator thread safety."""
    
    def test_orchestrator_thread_safety(self, client, mock_llm_responses):
        """
        Test that ForestOrchestrator is thread-safe by making multiple concurrent requests.
        This verifies our Factory pattern implementation prevents state bleed between requests.
        """
        # Number of concurrent requests to simulate
        num_concurrent = 5
        
        # Track orchestrator instances seen in each thread
        orchestrator_ids = []
        orchestrator_lock = threading.Lock()
        
        # Track results from each thread
        results = []
        results_lock = threading.Lock()
        
        # Patch the get_orchestrator dependency to track instances
        original_get_orchestrator = app.dependency_overrides.get("get_orchestrator", None)
        
        def track_orchestrator(request):
            # Get actual orchestrator
            orig_get = app.dependency_overrides.get("get_orchestrator", None)
            if orig_get:
                orchestrator = orig_get(request)
            else:
                # Import the actual function if no override
                from forest_app.core.dependencies import get_orchestrator
                orchestrator = get_orchestrator(request)
                
            # Track this instance
            instance_id = id(orchestrator)
            with orchestrator_lock:
                orchestrator_ids.append(instance_id)
                
            return orchestrator
            
        app.dependency_overrides["get_orchestrator"] = track_orchestrator
        
        try:
            # Function to make a request in a separate thread
            def make_request(user_id):
                # Create a command for the ForestOrchestrator
                command_data = {
                    "user_id": user_id,
                    "command": f"Test command from user {user_id}",
                    "context": {"test": True}
                }
                
                response = client.post("/core/command", json=command_data)
                
                with results_lock:
                    results.append({
                        "user_id": user_id,
                        "status_code": response.status_code,
                        "response": response.json() if response.status_code == 200 else None
                    })
            
            # Execute concurrent requests
            with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
                futures = [executor.submit(make_request, i) for i in range(num_concurrent)]
                # Wait for all to complete
                for future in futures:
                    future.result()
            
            # Verify each request got a different orchestrator instance
            assert len(orchestrator_ids) == num_concurrent
            assert len(set(orchestrator_ids)) == num_concurrent, "Some requests shared the same orchestrator instance!"
            
            # Verify all requests were successful
            assert len(results) == num_concurrent
            for result in results:
                assert result["status_code"] == 200, f"Request failed for user {result['user_id']}"
                assert result["response"] is not None
                
        finally:
            # Restore the original dependency
            if original_get_orchestrator:
                app.dependency_overrides["get_orchestrator"] = original_get_orchestrator
            else:
                app.dependency_overrides.pop("get_orchestrator", None)
    
    @pytest.mark.asyncio
    async def test_concurrent_async_execution(self):
        """
        Test that ForestOrchestrator can handle multiple asynchronous executions 
        without state bleed between them.
        """
        # Create mock dependencies
        mock_reflection_processor = MagicMock()
        mock_completion_processor = MagicMock()
        mock_state_manager = MagicMock()
        mock_hta_service = MagicMock()
        mock_seed_manager = MagicMock()
        
        # Configure mocks for async execution
        async def async_reflect(*args, **kwargs):
            # Simulate reflection processing with user-specific data
            user_id = kwargs.get("user_id", "unknown")
            return {"reflection_result": f"Reflection for user {user_id}", "user_id": user_id}
            
        mock_reflection_processor.process_reflection.side_effect = async_reflect
        
        # Create multiple orchestrator instances
        orchestrators = [
            ForestOrchestrator(
                reflection_processor=mock_reflection_processor,
                completion_processor=mock_completion_processor,
                state_manager=mock_state_manager,
                hta_service=mock_hta_service,
                seed_manager=mock_seed_manager
            )
            for _ in range(3)  # Create 3 instances
        ]
        
        # Simulate concurrent execution with different user contexts
        async def run_task(orchestrator, user_id):
            result = await orchestrator.process_user_input(
                user_id=user_id,
                message=f"Test message from user {user_id}",
                snapshot=MagicMock()
            )
            return result, user_id
            
        # Execute tasks concurrently
        tasks = [
            run_task(orchestrator, f"user_{i}")
            for i, orchestrator in enumerate(orchestrators)
        ]
        
        # Wait for all tasks to complete
        results = await asyncio.gather(*tasks)
        
        # Verify each task produced correct user-specific results without state bleed
        for result, user_id in results:
            assert result["user_id"] == user_id, f"State bleed detected! Expected {user_id} but got {result['user_id']}"
            assert f"user {user_id}" in result["reflection_result"]
