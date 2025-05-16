"""
Tests for the trees router, focusing on the POST /trees endpoint.
"""

<<<<<<< HEAD
import pytest
import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import UUID

from fastapi.testclient import TestClient
from fastapi import FastAPI, status

from forest_app.routers.trees import router as trees_router
from forest_app.core.roadmap_models import RoadmapManifest, RoadmapStep
from forest_app.persistence.models import HTATreeModel, Base

=======
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# --- Shared in-memory SQLite engine and session for all tests ---
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

<<<<<<< HEAD
engine = create_engine('sqlite:///:memory:', connect_args={"check_same_thread": False})
=======
from forest_app.persistence.models import Base, HTATreeModel
from forest_app.routers.trees import router as trees_router

engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
connection = engine.connect()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
Base.metadata.create_all(connection)

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
@pytest.fixture
def sample_tree_create_request():
    """Create sample tree request data for testing."""
    # Create a few steps with dependencies
    step1_id = str(uuid.uuid4())
    step2_id = str(uuid.uuid4())
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    return {
        "manifest": {
            "tree_id": str(uuid.uuid4()),
            "user_goal": "Test goal for API",
            "q_and_a_responses": [],
            "steps": [
                {
                    "id": step1_id,
                    "title": "First API step",
                    "description": "This is the first step via API",
                    "status": "pending",
                    "priority": "high",
<<<<<<< HEAD
                    "dependencies": []
=======
                    "dependencies": [],
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                },
                {
                    "id": step2_id,
                    "title": "Second API step",
                    "description": "This is the second step via API",
                    "status": "pending",
                    "priority": "medium",
<<<<<<< HEAD
                    "dependencies": [step1_id]
                }
            ]
        },
        "idempotency_key": f"test-key-{uuid.uuid4()}"
=======
                    "dependencies": [step1_id],
                },
            ],
        },
        "idempotency_key": f"test-key-{uuid.uuid4()}",
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    }


@pytest.fixture
def mock_hta_service():
    """Create a mock HTA service with the necessary methods."""
    mock = AsyncMock()
<<<<<<< HEAD
    
    # Mock generate_initial_hta_from_manifest to return a tree model
    async def mock_generate(*args, **kwargs):
        tree_id = kwargs.get('manifest').tree_id if 'manifest' in kwargs else uuid.uuid4()
        user_id = kwargs.get('user_id', uuid.uuid4())
=======

    # Mock generate_initial_hta_from_manifest to return a tree model
    async def mock_generate(*args, **kwargs):
        tree_id = (
            kwargs.get("manifest").tree_id if "manifest" in kwargs else uuid.uuid4()
        )
        user_id = kwargs.get("user_id", uuid.uuid4())
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        return HTATreeModel(
            id=tree_id,
            user_id=user_id,
            manifest={"steps": [{"id": "test"}]},
            created_at=datetime.now(timezone.utc),
<<<<<<< HEAD
            updated_at=datetime.now(timezone.utc)
        )
    
=======
            updated_at=datetime.now(timezone.utc),
        )

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    mock.generate_initial_hta_from_manifest = mock_generate
    return mock


@pytest.fixture
def mock_hta_tree_repository():
    """Create a mock HTATreeRepository."""
    mock = MagicMock()
<<<<<<< HEAD
    
    # Mock find_by_metadata to return None (no existing tree)
    mock.find_by_metadata.return_value = None
    
    # Mock update_metadata to return True
    mock.update_metadata.return_value = True
    
=======

    # Mock find_by_metadata to return None (no existing tree)
    mock.find_by_metadata.return_value = None

    # Mock update_metadata to return True
    mock.update_metadata.return_value = True

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    return mock


@pytest.fixture
def app(mock_hta_service, mock_hta_tree_repository):
    """Create a test FastAPI app with the trees router."""
    app = FastAPI()

    # Mock dependencies
<<<<<<< HEAD
    from forest_app.persistence.database import get_db
    from forest_app.core.security import get_current_active_user
    from forest_app.dependencies import get_hta_service
=======
    from forest_app.core.security import get_current_active_user
    from forest_app.dependencies import get_hta_service
    from forest_app.persistence.database import get_db
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    # Use the shared session for get_db
    def override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
<<<<<<< HEAD
    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[get_current_active_user] = lambda: type('User', (), {'id': uuid.uuid4()})()
=======

    app.dependency_overrides[get_db] = override_get_db

    app.dependency_overrides[get_current_active_user] = lambda: type(
        "User", (), {"id": uuid.uuid4()}
    )()
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    app.dependency_overrides[get_hta_service] = lambda: mock_hta_service

    # Include the trees router
    app.include_router(trees_router, prefix="/trees", tags=["Trees"])

    return app


@pytest.fixture
def client(app):
    """Create a test client for the FastAPI app."""
    return TestClient(app)


class TestTreesRouter:
    """Tests for the trees router endpoints."""
<<<<<<< HEAD
    
    @patch('forest_app.routers.trees.HTATreeRepository')
    def test_create_tree_success(
        self, mock_repo_class, client, sample_tree_create_request, mock_hta_service, mock_hta_tree_repository
=======

    @patch("forest_app.routers.trees.HTATreeRepository")
    def test_create_tree_success(
        self,
        mock_repo_class,
        client,
        sample_tree_create_request,
        mock_hta_service,
        mock_hta_tree_repository,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    ):
        """Test successful tree creation via POST /trees."""
        mock_repo_class.return_value = mock_hta_tree_repository

        # Set up the mock tree object with real UUIDs and valid fields
        mock_tree = MagicMock()
        mock_tree.id = uuid.uuid4()
        mock_tree.user_id = uuid.uuid4()
        mock_tree.created_at = datetime.now(timezone.utc)
        mock_tree.updated_at = datetime.now(timezone.utc)
        mock_tree.manifest = {"steps": [{"id": "test"}]}

        mock_hta_tree_repository.find_by_metadata.return_value = None
        mock_hta_tree_repository.update_metadata.return_value = True
        mock_hta_tree_repository.get_tree.return_value = mock_tree

        # Act
<<<<<<< HEAD
        response = client.post(
            "/trees/",
            json=sample_tree_create_request
        )
        
=======
        response = client.post("/trees/", json=sample_tree_create_request)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert "tree_id" in response.json()
        assert "user_id" in response.json()
        assert "created_at" in response.json()
        assert "message" in response.json()
        assert response.json()["message"] == "Tree created successfully"
<<<<<<< HEAD
        
        # Verify methods were called with correct arguments
        mock_hta_tree_repository.find_by_metadata.assert_called_once()
        mock_hta_tree_repository.update_metadata.assert_called_once()
    
    @patch('forest_app.routers.trees.HTATreeRepository')
    def test_create_tree_idempotent(
        self, mock_repo_class, client, sample_tree_create_request, mock_hta_service, mock_hta_tree_repository
=======

        # Verify methods were called with correct arguments
        mock_hta_tree_repository.find_by_metadata.assert_called_once()
        mock_hta_tree_repository.update_metadata.assert_called_once()

    @patch("forest_app.routers.trees.HTATreeRepository")
    def test_create_tree_idempotent(
        self,
        mock_repo_class,
        client,
        sample_tree_create_request,
        mock_hta_service,
        mock_hta_tree_repository,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    ):
        """Test idempotent tree creation via POST /trees."""
        # Arrange
        # Set up repository to return an existing tree with the same idempotency key
        existing_tree = HTATreeModel(
            id=UUID(sample_tree_create_request["manifest"]["tree_id"]),
            user_id=uuid.uuid4(),
            manifest={"steps": [{"id": "existing"}]},
            created_at=datetime.now(timezone.utc),
<<<<<<< HEAD
            updated_at=datetime.now(timezone.utc)
        )
        mock_hta_tree_repository.find_by_metadata.return_value = existing_tree
        mock_repo_class.return_value = mock_hta_tree_repository
        
        # Ensure generate_initial_hta_from_manifest is a mock
        mock_hta_service.generate_initial_hta_from_manifest = MagicMock()
        
        # Act
        response = client.post(
            "/trees/",
            json=sample_tree_create_request
        )
        
        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["tree_id"] == str(existing_tree.id)
        assert response.json()["message"] == "Retrieved existing tree with matching idempotency key"
        
        # Verify find_by_metadata was called but update_metadata was not
        mock_hta_tree_repository.find_by_metadata.assert_called_once()
        mock_hta_tree_repository.update_metadata.assert_not_called()
        
        # Verify generate_initial_hta_from_manifest was not called
        mock_hta_service.generate_initial_hta_from_manifest.assert_not_called()
    
    @patch('forest_app.routers.trees.HTATreeRepository')
=======
            updated_at=datetime.now(timezone.utc),
        )
        mock_hta_tree_repository.find_by_metadata.return_value = existing_tree
        mock_repo_class.return_value = mock_hta_tree_repository

        # Ensure generate_initial_hta_from_manifest is a mock
        mock_hta_service.generate_initial_hta_from_manifest = MagicMock()

        # Act
        response = client.post("/trees/", json=sample_tree_create_request)

        # Assert
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["tree_id"] == str(existing_tree.id)
        assert (
            response.json()["message"]
            == "Retrieved existing tree with matching idempotency key"
        )

        # Verify find_by_metadata was called but update_metadata was not
        mock_hta_tree_repository.find_by_metadata.assert_called_once()
        mock_hta_tree_repository.update_metadata.assert_not_called()

        # Verify generate_initial_hta_from_manifest was not called
        mock_hta_service.generate_initial_hta_from_manifest.assert_not_called()

    @patch("forest_app.routers.trees.HTATreeRepository")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    def test_create_tree_invalid_manifest(
        self, mock_repo_class, client, mock_hta_service, mock_hta_tree_repository
    ):
        """Test error handling for invalid manifest structure."""
        # Arrange
        mock_repo_class.return_value = mock_hta_tree_repository
        invalid_request = {
            "manifest": {
                # Missing required fields
                "steps": []
            },
<<<<<<< HEAD
            "idempotency_key": f"test-key-{uuid.uuid4()}"
        }
        
        # Act
        response = client.post(
            "/trees/",
            json=invalid_request
        )
        
=======
            "idempotency_key": f"test-key-{uuid.uuid4()}",
        }

        # Act
        response = client.post("/trees/", json=invalid_request)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        # Assert
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid manifest format" in response.json()["detail"]


# Integration tests - require actual DB connection
@pytest.mark.integration
class TestTreesRouterIntegration:
    """Integration tests for the trees router."""
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    @pytest.mark.asyncio
    async def test_end_to_end_tree_creation(self):
        """
        End-to-end test of tree creation with actual DB.
        Requires database connection to be configured in test environment.
        """
        # This would be implemented in a full test suite with proper DB fixtures
        pass
