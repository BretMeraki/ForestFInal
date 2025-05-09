"""
Integration tests for auth endpoints using FastAPI TestClient.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from forest_app.main import app
from forest_app.persistence.models import User

@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)

@pytest.fixture
def mock_user_repository():
    """Create a mock user repository."""
    with patch("forest_app.routers.auth.get_user_repository") as mock_get_repo:
        # Create mock repository
        mock_repo = mock_get_repo.return_value
        
        # Configure mock for get_user_by_email
        mock_repo.get_user_by_email.return_value = None
        
        # Configure mock for create_user
        def mock_create_user(email, hashed_password):
            user = User(id=1, email=email, hashed_password=hashed_password)
            return user
        mock_repo.create_user.side_effect = mock_create_user
        
        yield mock_repo

@pytest.fixture
def mock_token_verification():
    """Mock JWT token verification."""
    with patch("forest_app.routers.auth.create_access_token") as mock_create_token:
        mock_create_token.return_value = "test_access_token"
        yield mock_create_token

class TestAuthEndpoints:
    """Tests for authentication endpoints."""
    
    def test_register_user(self, client, mock_user_repository):
        """Test user registration endpoint."""
        # Test data
        user_data = {
            "email": "test@example.com",
            "password": "securepassword123"
        }
        
        # Make request to register endpoint
        response = client.post("/auth/register", json=user_data)
        
        # Verify response
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert "id" in data
        
        # Verify repository was called correctly
        mock_user_repository.get_user_by_email.assert_called_once_with(email=user_data["email"])
        mock_user_repository.create_user.assert_called_once()
        
    def test_register_existing_user(self, client, mock_user_repository):
        """Test registering a user that already exists."""
        # Configure mock to return an existing user
        existing_user = User(id=1, email="existing@example.com", hashed_password="hashed_pw")
        mock_user_repository.get_user_by_email.return_value = existing_user
        
        # Test data
        user_data = {
            "email": "existing@example.com",
            "password": "securepassword123"
        }
        
        # Make request to register endpoint
        response = client.post("/auth/register", json=user_data)
        
        # Verify response indicates conflict
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
        
    def test_login_for_access_token(self, client, mock_user_repository, mock_token_verification):
        """Test login endpoint for obtaining access token."""
        # Configure mock to return a user with valid credentials
        user = User(id=1, email="user@example.com", hashed_password="hashed_password")
        mock_user_repository.get_user_by_email.return_value = user
        
        # Mock password verification
        with patch("forest_app.routers.auth.verify_password") as mock_verify:
            mock_verify.return_value = True
            
            # Test data
            login_data = {
                "username": "user@example.com",
                "password": "password123"
            }
            
            # Make request to token endpoint
            response = client.post("/auth/token", data=login_data)
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            assert data["access_token"] == "test_access_token"
            assert data["token_type"] == "bearer"
            
            # Verify repository was called correctly
            mock_user_repository.get_user_by_email.assert_called_once_with(email=login_data["username"])
            mock_verify.assert_called_once()
            
    def test_login_invalid_credentials(self, client, mock_user_repository):
        """Test login with invalid credentials."""
        # Configure mock to return a user
        user = User(id=1, email="user@example.com", hashed_password="hashed_password")
        mock_user_repository.get_user_by_email.return_value = user
        
        # Mock password verification to fail
        with patch("forest_app.routers.auth.verify_password") as mock_verify:
            mock_verify.return_value = False
            
            # Test data
            login_data = {
                "username": "user@example.com",
                "password": "wrong_password"
            }
            
            # Make request to token endpoint
            response = client.post("/auth/token", data=login_data)
            
            # Verify response indicates unauthorized
            assert response.status_code == 401
            assert "incorrect" in response.json()["detail"].lower()
