"""
Unit tests for forest_app.persistence.repository module.
Uses SQLite in-memory database for testing.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from forest_app.persistence.models import Base, User
from forest_app.persistence.repository import UserRepository

# Test fixtures
@pytest.fixture
def test_db():
    """Create an in-memory SQLite database for testing."""
    # Create in-memory SQLite engine with thread check disabled
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    
    # Create all tables in the database
    Base.metadata.create_all(engine)
    
    # Create test session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def user_repository(test_db):
    """Create a UserRepository instance for testing."""
    return UserRepository(test_db)

class TestUserRepository:
    """Tests for UserRepository methods."""
    
    def test_create_user(self, user_repository):
        """Test creating a new user."""
        # Test data
        email = "test@example.com"
        hashed_password = "hashed_password_123"
        
        # Create user
        user = user_repository.create_user(email=email, hashed_password=hashed_password)
        
        # Verify user created successfully
        assert user.email == email
        assert user.hashed_password == hashed_password
        assert user.id is not None
        
    def test_get_user_by_email(self, user_repository):
        """Test retrieving a user by email."""
        # Test data
        email = "get_test@example.com"
        hashed_password = "hashed_password_456"
        
        # Create user first
        user_repository.create_user(email=email, hashed_password=hashed_password)
        
        # Retrieve user
        user = user_repository.get_user_by_email(email=email)
        
        # Verify correct user retrieved
        assert user is not None
        assert user.email == email
        assert user.hashed_password == hashed_password
        
        # Test non-existent user
        nonexistent_user = user_repository.get_user_by_email(email="nonexistent@example.com")
        assert nonexistent_user is None
        
    def test_get_user(self, user_repository):
        """Test retrieving a user by ID."""
        # Test data
        email = "id_test@example.com"
        hashed_password = "hashed_password_789"
        
        # Create user first
        created_user = user_repository.create_user(email=email, hashed_password=hashed_password)
        
        # Retrieve user by ID
        user = user_repository.get_user(user_id=created_user.id)
        
        # Verify correct user retrieved
        assert user is not None
        assert user.id == created_user.id
        assert user.email == email
        
        # Test non-existent user ID
        nonexistent_user = user_repository.get_user(user_id=999)
        assert nonexistent_user is None
