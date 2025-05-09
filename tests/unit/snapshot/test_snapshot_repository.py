"""
Unit tests for forest_app.snapshot.repository module.
Uses in-memory SQLite database for testing to avoid external dependencies.
"""
import pytest
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from forest_app.snapshot.models import Base, MemorySnapshot
from forest_app.snapshot.repository import SnapshotRepository

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
def snapshot_repository(test_db):
    """Create a SnapshotRepository instance for testing."""
    return SnapshotRepository(test_db)

class TestSnapshotRepository:
    """Tests for SnapshotRepository methods."""
    
    def test_create_snapshot(self, snapshot_repository):
        """Test creating a new snapshot."""
        # Test data
        user_id = 1
        timestamp = datetime.utcnow()
        metadata = {"test_key": "test_value"}
        component_state = {"engine_state": {"param1": 1, "param2": "test"}}
        messages = [{"role": "user", "content": "Test message"}]
        
        # Create snapshot
        snapshot = snapshot_repository.create_snapshot(
            user_id=user_id,
            timestamp=timestamp,
            metadata=metadata,
            component_state=component_state,
            messages=messages
        )
        
        # Verify snapshot created successfully
        assert snapshot.user_id == user_id
        assert snapshot.timestamp == timestamp
        assert json.loads(snapshot.metadata) == metadata
        assert json.loads(snapshot.component_state) == component_state
        assert json.loads(snapshot.messages) == messages
        assert snapshot.id is not None
        
    def test_get_snapshot_by_id(self, snapshot_repository):
        """Test retrieving a snapshot by ID."""
        # Test data
        user_id = 1
        timestamp = datetime.utcnow()
        metadata = {"test_key": "test_value"}
        component_state = {"engine_state": {"param1": 1, "param2": "test"}}
        messages = [{"role": "user", "content": "Test message"}]
        
        # Create snapshot first
        created_snapshot = snapshot_repository.create_snapshot(
            user_id=user_id,
            timestamp=timestamp,
            metadata=metadata,
            component_state=component_state,
            messages=messages
        )
        
        # Retrieve snapshot by ID
        snapshot = snapshot_repository.get_snapshot(snapshot_id=created_snapshot.id)
        
        # Verify correct snapshot retrieved
        assert snapshot is not None
        assert snapshot.id == created_snapshot.id
        assert snapshot.user_id == user_id
        assert json.loads(snapshot.metadata) == metadata
        
        # Test non-existent snapshot ID
        nonexistent_snapshot = snapshot_repository.get_snapshot(snapshot_id=999)
        assert nonexistent_snapshot is None
        
    def test_get_latest_user_snapshot(self, snapshot_repository):
        """Test retrieving the latest snapshot for a user."""
        # Test data for multiple snapshots
        user_id = 2
        
        # Create multiple snapshots for same user
        for i in range(3):
            timestamp = datetime.utcnow()
            metadata = {"test_key": f"value_{i}"}
            component_state = {"engine_state": {"counter": i}}
            messages = [{"role": "user", "content": f"Message {i}"}]
            
            snapshot_repository.create_snapshot(
                user_id=user_id,
                timestamp=timestamp,
                metadata=metadata,
                component_state=component_state,
                messages=messages
            )
        
        # Retrieve latest snapshot
        latest = snapshot_repository.get_latest_user_snapshot(user_id=user_id)
        
        # Verify latest snapshot retrieved
        assert latest is not None
        assert latest.user_id == user_id
        assert json.loads(latest.component_state)["engine_state"]["counter"] == 2
        
        # Test for non-existent user
        nonexistent_user_snapshot = snapshot_repository.get_latest_user_snapshot(user_id=999)
        assert nonexistent_user_snapshot is None
