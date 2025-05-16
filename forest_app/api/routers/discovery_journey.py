"""
Discovery Journey API Router

<<<<<<< HEAD
This module provides API endpoints for the Discovery Journey system, 
=======
This module provides API endpoints for the Discovery Journey system,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
facilitating the user's transition from abstract goals to concrete needs
through an adaptive and personalized experience.
"""

import logging
<<<<<<< HEAD
from typing import Dict, Any, List, Optional
from uuid import UUID
=======
from typing import Any, Dict, List, Optional
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel

<<<<<<< HEAD
from forest_app.core.integrations.discovery_integration import get_discovery_journey_service
from forest_app.api.dependencies import get_current_user
from forest_app.models.user import UserModel
=======
from forest_app.core.integrations.discovery_integration import \
    get_discovery_journey_service
from forest_app.dependencies import get_current_user
from forest_app.persistence.models import UserModel
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

logger = logging.getLogger(__name__)

# ----- Pydantic Models -----

<<<<<<< HEAD
class ReflectionInput(BaseModel):
    """User reflection input for the discovery journey."""
    content: str
    emotion_level: Optional[int] = None  # 1-10 scale
    context: Optional[Dict[str, Any]] = None
    
class PatternResponse(BaseModel):
    """Response containing discovered patterns in the user's journey."""
    patterns: List[Dict[str, Any]]
    insights: List[str]
    recommended_tasks: List[Dict[str, Any]]
    
class ExploratoryTaskResponse(BaseModel):
    """Response containing exploratory tasks for the user."""
=======

class ReflectionInput(BaseModel):
    """User reflection input for the discovery journey."""

    content: str
    emotion_level: Optional[int] = None  # 1-10 scale
    context: Optional[Dict[str, Any]] = None


class PatternResponse(BaseModel):
    """Response containing discovered patterns in the user's journey."""

    patterns: List[Dict[str, Any]]
    insights: List[str]
    recommended_tasks: List[Dict[str, Any]]


class ExploratoryTaskResponse(BaseModel):
    """Response containing exploratory tasks for the user."""

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    tasks: List[Dict[str, Any]]
    context: Dict[str, Any]
    emotional_framing: Optional[Dict[str, Any]] = None

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
# ----- Router -----

router = APIRouter(
    prefix="/discovery",
    tags=["discovery-journey"],
    responses={404: {"description": "Discovery service not found"}},
)

# ----- Endpoints -----

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
@router.post("/reflection", status_code=status.HTTP_201_CREATED)
async def add_reflection(
    reflection: ReflectionInput,
    request: Request,
<<<<<<< HEAD
    current_user: UserModel = Depends(get_current_user)
):
    """
    Add a new reflection to the user's discovery journey.
    
=======
    current_user: UserModel = Depends(get_current_user),
):
    """
    Add a new reflection to the user's discovery journey.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    This endpoint captures the user's reflections on their journey, including emotional
    responses, which help the system refine its understanding of their needs.
    """
    discovery_service = get_discovery_journey_service(request.app)
<<<<<<< HEAD
    
    if not discovery_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discovery journey service unavailable"
        )
    
=======

    if not discovery_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discovery journey service unavailable",
        )

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    try:
        result = await discovery_service.process_reflection(
            user_id=current_user.id,
            reflection_content=reflection.content,
            emotion_level=reflection.emotion_level,
<<<<<<< HEAD
            context=reflection.context
        )
        
=======
            context=reflection.context,
        )

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        return {
            "status": "success",
            "message": "Reflection processed successfully",
            "insights": result.get("insights", []),
<<<<<<< HEAD
            "has_new_pattern": result.get("has_new_pattern", False)
=======
            "has_new_pattern": result.get("has_new_pattern", False),
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        }
    except Exception as e:
        logger.error(f"Error processing reflection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
            detail=f"Failed to process reflection: {str(e)}"
        )

@router.get("/patterns", response_model=PatternResponse)
async def get_patterns(
    request: Request,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get the currently identified patterns in the user's journey.
    
=======
            detail=f"Failed to process reflection: {str(e)}",
        )


@router.get("/patterns", response_model=PatternResponse)
async def get_patterns(
    request: Request, current_user: UserModel = Depends(get_current_user)
):
    """
    Get the currently identified patterns in the user's journey.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    This endpoint provides insights into patterns detected in the user's reflections
    and interactions, helping them understand their evolving needs and goals.
    """
    discovery_service = get_discovery_journey_service(request.app)
<<<<<<< HEAD
    
    if not discovery_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discovery journey service unavailable"
        )
    
=======

    if not discovery_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discovery journey service unavailable",
        )

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    try:
        patterns = await discovery_service.get_patterns_for_user(current_user.id)
        return patterns
    except Exception as e:
        logger.error(f"Error retrieving patterns: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
            detail=f"Failed to retrieve patterns: {str(e)}"
        )

=======
            detail=f"Failed to retrieve patterns: {str(e)}",
        )


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
@router.get("/exploratory-tasks", response_model=ExploratoryTaskResponse)
async def get_exploratory_tasks(
    request: Request,
    task_count: int = 3,
<<<<<<< HEAD
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get exploratory tasks to help the user clarify their goals.
    
=======
    current_user: UserModel = Depends(get_current_user),
):
    """
    Get exploratory tasks to help the user clarify their goals.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    This endpoint generates tasks specifically designed to help users explore different
    aspects of their abstract goals, guiding them toward more concrete understanding.
    """
    discovery_service = get_discovery_journey_service(request.app)
<<<<<<< HEAD
    
    if not discovery_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discovery journey service unavailable"
        )
    
    try:
        tasks = await discovery_service.generate_exploratory_tasks(
            user_id=current_user.id,
            count=task_count
=======

    if not discovery_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discovery journey service unavailable",
        )

    try:
        tasks = await discovery_service.generate_exploratory_tasks(
            user_id=current_user.id, count=task_count
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        )
        return tasks
    except Exception as e:
        logger.error(f"Error generating exploratory tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
            detail=f"Failed to generate exploratory tasks: {str(e)}"
        )

=======
            detail=f"Failed to generate exploratory tasks: {str(e)}",
        )


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
@router.post("/task-completion/{task_id}")
async def complete_exploratory_task(
    task_id: str,
    request: Request,
    feedback: Optional[Dict[str, Any]] = None,
<<<<<<< HEAD
    current_user: UserModel = Depends(get_current_user)
):
    """
    Mark an exploratory task as completed and provide feedback.
    
=======
    current_user: UserModel = Depends(get_current_user),
):
    """
    Mark an exploratory task as completed and provide feedback.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    This endpoint records completion of a discovery task and processes any feedback
    from the user, further refining the system's understanding of their needs.
    """
    discovery_service = get_discovery_journey_service(request.app)
<<<<<<< HEAD
    
    if not discovery_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discovery journey service unavailable"
        )
    
    try:
        result = await discovery_service.process_task_completion(
            user_id=current_user.id,
            task_id=task_id,
            feedback=feedback or {}
        )
        
=======

    if not discovery_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discovery journey service unavailable",
        )

    try:
        result = await discovery_service.process_task_completion(
            user_id=current_user.id, task_id=task_id, feedback=feedback or {}
        )

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        return {
            "status": "success",
            "message": "Task completion processed",
            "next_steps": result.get("next_steps", []),
<<<<<<< HEAD
            "insights_gained": result.get("insights_gained", [])
=======
            "insights_gained": result.get("insights_gained", []),
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        }
    except Exception as e:
        logger.error(f"Error processing task completion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
            detail=f"Failed to process task completion: {str(e)}"
        )

@router.get("/progress-summary")
async def get_journey_progress(
    request: Request,
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get a summary of the user's discovery journey progress.
    
=======
            detail=f"Failed to process task completion: {str(e)}",
        )


@router.get("/progress-summary")
async def get_journey_progress(
    request: Request, current_user: UserModel = Depends(get_current_user)
):
    """
    Get a summary of the user's discovery journey progress.

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    This endpoint provides a comprehensive view of the user's journey from abstract
    goal to concrete needs, highlighting key insights, patterns, and evolution.
    """
    discovery_service = get_discovery_journey_service(request.app)
<<<<<<< HEAD
    
    if not discovery_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discovery journey service unavailable"
        )
    
    try:
        summary = await discovery_service.get_journey_progress(current_user.id)
        
=======

    if not discovery_service:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discovery journey service unavailable",
        )

    try:
        summary = await discovery_service.get_journey_progress(current_user.id)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        return {
            "starting_point": summary.get("starting_point", {}),
            "current_understanding": summary.get("current_understanding", {}),
            "key_insights": summary.get("key_insights", []),
            "progress_metrics": summary.get("progress_metrics", {}),
            "clarity_level": summary.get("clarity_level", 0),
<<<<<<< HEAD
            "journey_highlights": summary.get("journey_highlights", [])
=======
            "journey_highlights": summary.get("journey_highlights", []),
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        }
    except Exception as e:
        logger.error(f"Error retrieving journey progress: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
<<<<<<< HEAD
            detail=f"Failed to retrieve journey progress: {str(e)}"
=======
            detail=f"Failed to retrieve journey progress: {str(e)}",
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        )
