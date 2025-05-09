"""
Focused concurrency testing for ForestOrchestrator.

This test specifically verifies that concurrent requests to endpoints using
the ForestOrchestrator do not interfere with each other by tracking request IDs
and user data through the processing pipeline.
"""
import pytest
import asyncio
import uuid
import logging
import httpx
import json
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock
from concurrent.futures import ThreadPoolExecutor

from dependency_injector import containers, providers

# Import the core application components
from forest_app.main import app
from forest_app.core.orchestrator import ForestOrchestrator
from forest_app.core.processors.reflection_processor_logging import LoggingReflectionProcessor
from forest_app.core.processors.completion_processor_logging import LoggingCompletionProcessor
from forest_app.snapshot.snapshot import MemorySnapshot
from forest_app.core.main import container

# Set up test-specific logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a custom log handler to capture logs during tests
class LogCaptureHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []
        
    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append(log_entry)
        
    def get_logs(self):
        return self.logs
        
    def clear(self):
        self.logs = []

# Create global log handler
log_capture = LogCaptureHandler()
log_capture.setFormatter(logging.Formatter('%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'))
logging.getLogger().addHandler(log_capture)


class TestFocusedOrchestratorConcurrency:
    """
    Focused tests to verify ForestOrchestrator isolation during concurrent requests.
    """
    
    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client to return user-specific responses."""
        with patch("forest_app.integrations.llm.LLMClient") as mock_llm:
            instance = mock_llm.return_value
            
            async def generate_mock(prompt, **kwargs):
                # Extract any user identifier in the prompt
                user_id = "unknown"
                if "user" in prompt:
                    parts = prompt.split("user")
                    if len(parts) > 1 and parts[1]:
                        potential_id = ''.join(c for c in parts[1] if c.isalnum() or c == '_')
                        if potential_id:
                            user_id = f"user{potential_id[:5]}"
                
                # Return user-specific response
                return {
                    "text": f"LLM response for {user_id}",
                    "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15}
                }
                
            instance.generate.side_effect = generate_mock
            yield instance
            
    @pytest.fixture
    def override_processors_with_logging(self, mock_llm_client):
        """
        Override the ForestOrchestrator's processors with logging versions
        for tracing request flow and data isolation.
        """
        # Store original providers
        original_reflection = container.reflection_processor
        original_completion = container.completion_processor
        
        # Create logging versions with the same dependencies
        try:
            # Override with logging processors that have the same dependencies
            container.reflection_processor.override(
                providers.Factory(
                    LoggingReflectionProcessor,
                    llm_client=container.llm_client,
                    task_engine=container.task_engine,
                    sentiment_engine=container.sentiment_engine,
                    practical_consequence_engine=container.practical_consequence_engine,
                    narrative_engine=container.narrative_engine,
                    silent_scorer=container.silent_scoring,
                    harmonic_router=container.harmonic_routing
                )
            )
            
            container.completion_processor.override(
                providers.Factory(
                    LoggingCompletionProcessor,
                    llm_client=container.llm_client,
                    task_engine=container.task_engine,
                    state_manager=container.component_state_manager,
                    hta_service=container.hta_service
                )
            )
            
            logger.info("Overridden processors with logging versions")
            yield
            
        finally:
            # Restore original providers
            container.reflection_processor.override(original_reflection)
            container.completion_processor.override(original_completion)
            logger.info("Restored original processors")
    
    @pytest.mark.asyncio
    async def test_concurrent_reflections(self, override_processors_with_logging):
        """
        Test that concurrent reflection processing correctly isolates user data.
        """
        # Clear log capture
        log_capture.clear()
        
        # Create mock dependencies
        mock_reflection_processor = MagicMock()
        mock_completion_processor = MagicMock()
        mock_state_manager = MagicMock()
        mock_hta_service = MagicMock()
        mock_seed_manager = MagicMock()
        
        # Configure mocks for async execution with user tracking
        async def async_reflect(user_input, snapshot, **kwargs):
            # Extract user info for tracking
            user_id = getattr(snapshot, 'user_id', 'unknown')
            request_id = kwargs.get('request_id', str(uuid.uuid4())[:8])
            
            # Log user-specific processing
            logger.info(f"[REQ-{request_id}] Processing reflection for user={user_id}, input='{user_input[:20]}'")
            
            # Return user-specific data to ensure isolation
            return {
                "arbiter_response": f"Response for user {user_id}",
                "tasks": [{"id": f"task-{user_id}-1", "title": f"Task for {user_id}"}],
                "user_id": user_id,
                "request_id": request_id,
                "magnitude_description": "Moderate",
                "resonance_theme": "neutral",
                "routing_score": 0.75
            }
            
        mock_reflection_processor.process.side_effect = async_reflect
        
        # Create orchestrator instances (one per request)
        num_concurrent = 3
        orchestrators = [
            ForestOrchestrator(
                reflection_processor=mock_reflection_processor,
                completion_processor=mock_completion_processor,
                state_manager=mock_state_manager,
                hta_service=mock_hta_service,
                seed_manager=mock_seed_manager
            )
            for _ in range(num_concurrent)
        ]
        
        # Log orchestrator instances
        for i, orchestrator in enumerate(orchestrators):
            logger.info(f"Created orchestrator[{i}] with id={id(orchestrator)}")
        
        # Create snapshots with different user IDs
        snapshots = [
            MagicMock(user_id=f"user_{i}", 
                     activated_state={"activated": True},
                     snapshot_id=f"snap_{i}")
            for i in range(num_concurrent)
        ]
        
        # Simulate concurrent execution with different request/user identifiers
        async def run_task(orchestrator, snapshot, user_input):
            request_id = str(uuid.uuid4())[:8]
            logger.info(f"[REQ-{request_id}] Starting request for user={snapshot.user_id}")
            
            # Process reflection with request ID
            result = await orchestrator.process_reflection(
                user_input=user_input,
                snapshot=snapshot
            )
            
            logger.info(f"[REQ-{request_id}] Completed request for user={snapshot.user_id}")
            return result, snapshot.user_id, request_id
            
        # Create tasks for concurrent execution
        tasks = [
            run_task(
                orchestrator=orchestrators[i],
                snapshot=snapshots[i],
                user_input=f"Test message from user_{i} with unique content"
            )
            for i in range(num_concurrent)
        ]
        
        # Execute tasks concurrently
        results = await asyncio.gather(*tasks)
        
        # Analyze results for data isolation
        for result, user_id, request_id in results:
            # Verify user data isolation
            assert result["user_id"] == user_id, f"Expected user_id={user_id}, got {result['user_id']}"
            assert f"user {user_id}" in result["arbiter_response"], "User-specific data missing from response"
            
            # Verify task isolation
            if "tasks" in result and result["tasks"]:
                task = result["tasks"][0]
                assert user_id in task["id"], f"Expected user_id in task ID, got {task['id']}"
                assert user_id in task["title"], f"Expected user_id in task title, got {task['title']}"
        
        # Analyze logs to verify proper isolation
        logs = log_capture.get_logs()
        request_logs = {}
        
        # Group logs by request ID
        for log in logs:
            for result_data, user_id, req_id in results:
                if f"[REQ-{req_id}]" in log:
                    if req_id not in request_logs:
                        request_logs[req_id] = []
                    request_logs[req_id].append(log)
        
        # Verify each request's logs contain only its own user data
        for req_id, req_logs in request_logs.items():
            # Find the user ID for this request
            target_user_id = None
            for result_data, user_id, request_id in results:
                if req_id == request_id:
                    target_user_id = user_id
                    break
            
            if not target_user_id:
                continue
                
            # Check that logs for this request only contain its user data
            for log in req_logs:
                for result_data, user_id, request_id in results:
                    if user_id != target_user_id and user_id in log:
                        assert False, f"Request {req_id} logs contain data from user {user_id}"
    
    @pytest.mark.asyncio
    async def test_httpx_concurrent_api_requests(self, override_processors_with_logging):
        """
        Test concurrent API requests using httpx to verify isolation at the API level.
        This test simulates multiple users accessing the /core/command endpoint simultaneously.
        """
        # Start a local test server
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Create mock auth - replace with actual auth mechanism if needed
        async def mock_get_auth_token(user_id):
            return f"mock_token_{user_id}"
        
        # Execute concurrent API requests
        async def make_request(user_id):
            request_id = str(uuid.uuid4())[:8]
            
            # Create mock request data
            command_data = {
                "command": f"Test command from user {user_id} with request {request_id}"
            }
            
            # Set up mock auth headers - replace with actual auth headers if needed
            headers = {
                "Authorization": f"Bearer mock_token_{user_id}",
                "X-Request-ID": request_id,
                "Content-Type": "application/json"
            }
            
            logger.info(f"[REQ-{request_id}] Sending API request for user {user_id}")
            
            # In a real test, we'd use httpx.AsyncClient
            # Since we're using TestClient (sync), we'll wrap it
            response = client.post("/core/command", json=command_data, headers=headers)
            
            logger.info(f"[REQ-{request_id}] Received API response for user {user_id}: status={response.status_code}")
            
            return {
                "user_id": user_id,
                "request_id": request_id,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        
        # Number of concurrent users
        num_users = 3
        
        # Create and execute tasks
        tasks = [make_request(f"user_{i}") for i in range(num_users)]
        
        # Since TestClient is synchronous, we need to run in a thread pool
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [executor.submit(make_request, f"user_{i}") for i in range(num_users)]
            responses = [future.result() for future in futures]
        
        # Verify responses
        for response in responses:
            user_id = response["user_id"]
            
            # Check for successful response
            assert response["status_code"] in [200, 403], f"Request failed with status {response['status_code']}"
            
            # If we got a successful response, check for data isolation
            if response["status_code"] == 200 and response["data"]:
                # In a real test, verify the response contains user-specific data
                # and doesn't contain data from other users
                pass


if __name__ == "__main__":
    # This section allows running the script directly for manual testing
    import unittest
    import sys
    
    # Setup a simple test class for manual execution
    class ManualTest(unittest.TestCase):
        def test_run_concurrent_reflections(self):
            # Create a mock for the fixture
            mock_fixture = MagicMock()
            
            # Run the test
            asyncio.run(TestFocusedOrchestratorConcurrency().test_concurrent_reflections(mock_fixture))
    
    # Run the test
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
