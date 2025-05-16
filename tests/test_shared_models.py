"""Tests for shared models."""

<<<<<<< HEAD
import pytest
from datetime import datetime, timezone
from forest_app.modules.shared_models import (
    HTANodeBase,
    DesireBase,
    FinancialMetricsBase,
    PatternBase
)
=======
from datetime import datetime, timezone

import pytest

from forest_app.modules.shared_models import (DesireBase, FinancialMetricsBase,
                                              HTANodeBase, PatternBase)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

def test_hta_node_base_creation():
    """Test creating an HTANodeBase instance."""
    now = datetime.now(timezone.utc)
<<<<<<< HEAD
    node = HTANodeBase(
        id="test_1",
        title="Test Node",
        created_at=now,
        updated_at=now
    )
=======
    node = HTANodeBase(id="test_1", title="Test Node", created_at=now, updated_at=now)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    assert node.id == "test_1"
    assert node.title == "Test Node"
    assert node.parent_id is None
    assert node.description is None
    assert isinstance(node.metadata, dict)
    assert len(node.metadata) == 0

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def test_desire_base_creation():
    """Test creating a DesireBase instance."""
    now = datetime.now(timezone.utc)
    desire = DesireBase(
        id="desire_1",
        strength=0.8,
        category="leisure",
        description="Reading books",
<<<<<<< HEAD
        created_at=now
=======
        created_at=now,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    )
    assert desire.id == "desire_1"
    assert desire.strength == 0.8
    assert desire.category == "leisure"
    assert desire.description == "Reading books"
    assert isinstance(desire.metadata, dict)

<<<<<<< HEAD
def test_financial_metrics_base_creation():
    """Test creating a FinancialMetricsBase instance."""
    now = datetime.now(timezone.utc)
    metrics = FinancialMetricsBase(
        user_id="user_1",
        score=0.75,
        last_updated=now
    )
=======

def test_financial_metrics_base_creation():
    """Test creating a FinancialMetricsBase instance."""
    now = datetime.now(timezone.utc)
    metrics = FinancialMetricsBase(user_id="user_1", score=0.75, last_updated=now)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    assert metrics.user_id == "user_1"
    assert metrics.score == 0.75
    assert isinstance(metrics.metrics, dict)
    assert isinstance(metrics.metadata, dict)

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def test_pattern_base_creation():
    """Test creating a PatternBase instance."""
    pattern = PatternBase(
        id="pattern_1",
        pattern_type="behavioral",
        confidence=0.9,
<<<<<<< HEAD
        description="Recurring behavior pattern"
=======
        description="Recurring behavior pattern",
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    )
    assert pattern.id == "pattern_1"
    assert pattern.pattern_type == "behavioral"
    assert pattern.confidence == 0.9
    assert pattern.description == "Recurring behavior pattern"
    assert isinstance(pattern.metadata, dict)

<<<<<<< HEAD
def test_invalid_hta_node_base():
    """Test that invalid HTANodeBase creation raises ValidationError."""
    with pytest.raises(ValueError):
        HTANodeBase(
            id="test_1",
            title=""  # Empty title should raise error
        )
=======

def test_invalid_hta_node_base():
    """Test that invalid HTANodeBase creation raises ValidationError."""
    with pytest.raises(ValueError):
        HTANodeBase(id="test_1", title="")  # Empty title should raise error

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

def test_invalid_desire_base():
    """Test that invalid DesireBase creation raises ValidationError."""
    with pytest.raises(ValueError):
        DesireBase(
            id="desire_1",
            strength=1.5,  # Should be between 0 and 1
            category="leisure",
            description="Reading books",
<<<<<<< HEAD
            created_at=datetime.now(timezone.utc)
        )

=======
            created_at=datetime.now(timezone.utc),
        )


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def test_invalid_financial_metrics_base():
    """Test that invalid FinancialMetricsBase creation raises ValidationError."""
    with pytest.raises(ValueError):
        FinancialMetricsBase(
            user_id="",  # Empty user_id should raise error
            score=0.75,
<<<<<<< HEAD
            last_updated=datetime.now(timezone.utc)
        )

=======
            last_updated=datetime.now(timezone.utc),
        )


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def test_invalid_pattern_base():
    """Test that invalid PatternBase creation raises ValidationError."""
    with pytest.raises(ValueError):
        PatternBase(
            id="pattern_1",
            pattern_type="",  # Empty pattern_type should raise error
            confidence=-0.1,  # Negative confidence should raise error
<<<<<<< HEAD
            description="Test pattern"
        ) 
=======
            description="Test pattern",
        )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
