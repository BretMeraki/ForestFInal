"""
Tests for the WitheringManager class.
"""

import pytest
from datetime import datetime, timedelta, timezone
from forest_app.core.services.withering_manager import WitheringManager
from forest_app.snapshot.snapshot import MemorySnapshot
from forest_app.config.constants import (
    WITHERING_COMPLETION_RELIEF,
    WITHERING_IDLE_COEFF,
    WITHERING_OVERDUE_COEFF,
    WITHERING_DECAY_FACTOR
)

def test_withering_manager_initialization():
    """Test that WitheringManager initializes correctly."""
    snapshot = MemorySnapshot()
    WitheringManager.update_withering(snapshot)
    assert hasattr(snapshot, 'withering_level')
    assert snapshot.withering_level == 0.0
    assert hasattr(snapshot, 'component_state')
    assert isinstance(snapshot.component_state, dict)
    assert 'last_activity_ts' in snapshot.component_state

def test_withering_idle_penalty():
    """Test that idle time increases withering level."""
    snapshot = MemorySnapshot()
    snapshot.component_state = {
        'last_activity_ts': (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
    }
    snapshot.current_path = 'structured'
    
    WitheringManager.update_withering(snapshot)
    
    # Calculate expected withering
    idle_hours = 2.0
    idle_coeff = WITHERING_IDLE_COEFF['structured']
    expected_withering = idle_hours * idle_coeff * WITHERING_DECAY_FACTOR
    
    assert snapshot.withering_level > 0
    assert abs(snapshot.withering_level - expected_withering) < 0.001

def test_withering_completion_relief():
    """Test that task completion reduces withering level."""
    snapshot = MemorySnapshot()
    snapshot.withering_level = 0.5
    snapshot.task_backlog = [
        {'status': 'completed'},
        {'status': 'completed'},
        {'status': 'pending'}
    ]
    
    WitheringManager.update_withering(snapshot)
    
    # Calculate expected relief
    completion_ratio = 2/3
    expected_relief = WITHERING_COMPLETION_RELIEF * completion_ratio
    expected_withering = (0.5 * WITHERING_DECAY_FACTOR) - expected_relief
    
    assert snapshot.withering_level < 0.5
    assert abs(snapshot.withering_level - expected_withering) < 0.001

def test_withering_clamping():
    """Test that withering level is clamped between 0 and 1."""
    snapshot = MemorySnapshot()
    
    # Test lower bound
    snapshot.withering_level = -0.5
    WitheringManager.update_withering(snapshot)
    assert snapshot.withering_level == 0.0
    
    # Test upper bound
    snapshot.withering_level = 1.5
    WitheringManager.update_withering(snapshot)
    assert snapshot.withering_level == 1.0

def test_withering_path_specific_coefficients():
    """Test that different paths use different coefficients."""
    snapshot = MemorySnapshot()
    snapshot.component_state = {
        'last_activity_ts': (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    }
    
    # Test structured path
    snapshot.current_path = 'structured'
    WitheringManager.update_withering(snapshot)
    structured_withering = snapshot.withering_level
    
    # Test open path
    snapshot.current_path = 'open'
    WitheringManager.update_withering(snapshot)
    open_withering = snapshot.withering_level
    
    assert structured_withering != open_withering
    assert structured_withering > open_withering  # Structured path should have higher coefficient

def test_withering_invalid_timestamps():
    """Test handling of invalid timestamps."""
    snapshot = MemorySnapshot()
    
    # Test invalid timestamp format
    snapshot.component_state = {'last_activity_ts': 'invalid-timestamp'}
    WitheringManager.update_withering(snapshot)
    assert snapshot.withering_level == 0.0
    
    # Test non-string timestamp
    snapshot.component_state = {'last_activity_ts': 123}
    WitheringManager.update_withering(snapshot)
    assert snapshot.withering_level == 0.0 