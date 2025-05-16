"""Common test fixtures for Forest App tests."""

<<<<<<< HEAD
import pytest
from datetime import datetime, timezone
from typing import Dict, Any

# --- Windows event loop policy fix for pytest-asyncio ---
import sys
import asyncio
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

@pytest.fixture
def mock_feature_flags(mocker):
    """Mock feature flags to always return True."""
    mock_feature = mocker.patch('forest_app.core.feature_flags.Feature')
    mock_is_enabled = mocker.patch('forest_app.core.feature_flags.is_enabled')
    mock_is_enabled.return_value = True
    return mock_is_enabled

=======
import asyncio
# --- Windows event loop policy fix for pytest-asyncio ---
import sys
from datetime import datetime, timezone

import pytest

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


@pytest.fixture
def mock_feature_flags(mocker):
    """Mock feature flags to always return True."""
    mock_feature = mocker.patch("forest_app.core.feature_flags.Feature")
    mock_is_enabled = mocker.patch("forest_app.core.feature_flags.is_enabled")
    mock_is_enabled.return_value = True
    return mock_is_enabled


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
@pytest.fixture
def sample_hta_node():
    """Create a sample HTA node for testing."""
    return {
        "id": "test_node_1",
        "parent_id": None,
        "title": "Test Node",
        "description": "A test node for testing",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "status": "pending",
        "priority": 0.7,
        "magnitude": 5.0,
<<<<<<< HEAD
        "metadata": {}
    }

=======
        "metadata": {},
    }


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
@pytest.fixture
def sample_snapshot():
    """Create a sample memory snapshot for testing."""
    return {
        "core_state": {
<<<<<<< HEAD
            "hta_tree": {
                "root": {
                    "id": "root",
                    "title": "Root Node",
                    "children": []
                }
            }
=======
            "hta_tree": {"root": {"id": "root", "title": "Root Node", "children": []}}
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        },
        "capacity": 0.8,
        "shadow_score": 0.3,
        "reflection_log": [],
        "task_footprints": [],
        "totems": [],
<<<<<<< HEAD
        "component_state": {}
    }

=======
        "component_state": {},
    }


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
@pytest.fixture
def mock_llm_client(mocker):
    """Mock LLM client for testing."""
    mock_client = mocker.Mock()
    mock_client.generate.return_value = {"text": "Test response"}
<<<<<<< HEAD
    return mock_client 
=======
    return mock_client
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
