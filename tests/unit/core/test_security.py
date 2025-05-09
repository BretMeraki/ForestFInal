"""
Unit tests for the forest_app.core.security module.
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

from jose import jwt
from passlib.context import CryptContext

from forest_app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    get_password_context
)
from forest_app.config import constants

# Test fixture for password context
@pytest.fixture
def pwd_context():
    return CryptContext(schemes=["bcrypt"], deprecated="auto")

class TestSecurity:
    """Tests for security utility functions."""
    
    def test_get_password_context(self):
        """Test that password context is properly configured."""
        context = get_password_context()
        assert context.schemes == ["bcrypt"]
        assert "auto" in context.deprecated
    
    def test_password_hashing(self, pwd_context):
        """Test password hashing and verification."""
        # Test with a sample password
        password = "secure-test-password123"
        
        # Get hashed password
        hashed = get_password_hash(password)
        
        # Verify the hash is not the same as the original password
        assert hashed != password
        
        # Verify that we can validate the password correctly
        assert verify_password(password, hashed) is True
        
        # Verify that incorrect passwords fail validation
        assert verify_password("wrong-password", hashed) is False
    
    @patch("forest_app.core.security.SECRET_KEY", "test_secret_key_for_tests")
    def test_create_access_token(self):
        """Test JWT token creation and validation."""
        # Test data
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        
        # Create token
        token = create_access_token(data, expires_delta=expires_delta)
        
        # Verify token is a string
        assert isinstance(token, str)
        
        # Decode and verify token
        payload = jwt.decode(
            token, 
            "test_secret_key_for_tests", 
            algorithms=[constants.ALGORITHM]
        )
        
        # Check payload
        assert payload["sub"] == "test@example.com"
        
        # Verify expiration is set correctly
        # Allow 5 seconds of test execution time
        now = datetime.utcnow().timestamp()
        expected_exp = (datetime.utcnow() + expires_delta).timestamp()
        assert abs(payload["exp"] - expected_exp) < 5
        assert payload["exp"] > now
