"""
Test routes for verifying orchestrator isolation.
"""

from fastapi import APIRouter, Depends, Request
from forest_app.core.dependencies import get_orchestrator
from forest_app.core.orchestrator import ForestOrchestrator
from forest_app.snapshot.snapshot import MemorySnapshot

router = APIRouter(prefix="/test")

@router.get("/orchestrator1")
async def get_orchestrator1(request: Request, orchestrator: ForestOrchestrator = Depends(get_orchestrator)):
    """Test endpoint that returns the orchestrator instance ID."""
    return {"orchestrator_id": id(orchestrator)}

@router.get("/orchestrator2")
async def get_orchestrator2(request: Request, orchestrator: ForestOrchestrator = Depends(get_orchestrator)):
    """Test endpoint that returns the orchestrator instance ID."""
    return {"orchestrator_id": id(orchestrator)}

@router.post("/set_state")
async def set_state(request: Request, data: dict, orchestrator: ForestOrchestrator = Depends(get_orchestrator)):
    """Test endpoint that sets state in the orchestrator."""
    # Create a snapshot with the test state
    snapshot = MemorySnapshot()
    snapshot.component_state = data
    # Process the snapshot
    await orchestrator.process_reflection("test", snapshot)
    return {"state": snapshot.component_state}

@router.get("/get_state")
async def get_state(request: Request, orchestrator: ForestOrchestrator = Depends(get_orchestrator)):
    """Test endpoint that gets state from the orchestrator."""
    # Create a fresh snapshot
    snapshot = MemorySnapshot()
    # Process the snapshot
    await orchestrator.process_reflection("test", snapshot)
    return {"state": snapshot.component_state}

@router.post("/process_snapshot")
async def process_snapshot(request: Request, snapshot_data: dict, orchestrator: ForestOrchestrator = Depends(get_orchestrator)):
    """Test endpoint that processes a snapshot through the orchestrator."""
    # Create a snapshot from the input data
    snapshot = MemorySnapshot(**snapshot_data)
    # Process the snapshot
    await orchestrator.process_reflection("test", snapshot)
    return {"processed_state": snapshot.dict()} 