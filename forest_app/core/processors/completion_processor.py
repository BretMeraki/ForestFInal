# forest_app/core/processors/completion_processor.py

import logging
import inspect
from typing import Optional, Dict, Any, List, cast
from sqlalchemy.orm import Session
from datetime import datetime, timezone

# --- Core & Module Imports ---
from forest_app.snapshot.snapshot import MemorySnapshot
from forest_app.core.utils import clamp01
from forest_app.integrations.llm import LLMClient
from forest_app.core.feature_flags import is_enabled
from forest_app.core.logging_tracking import TaskFootprintLogger
from forest_app.modules.resource.xp_mastery import XPMasteryEngine

# --- Feature Flags ---
try:
    from forest_app.core.feature_flags import Feature
except ImportError:
    # Fallback if flags cannot be imported
    class Feature:
        CORE_HTA = "FEATURE_ENABLE_CORE_HTA"
        XP_MASTERY = "FEATURE_ENABLE_XP_MASTERY"

# --- Constants ---
from forest_app.config.constants import WITHERING_COMPLETION_RELIEF

# --- New Imports ---
from forest_app.hta_tree.hta_service import HTAService
from forest_app.hta_tree.task_engine import TaskEngine
from forest_app.hta_tree.hta_tree import HTATree
from forest_app.core.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

# --- Completion Processor Class ---

class CompletionProcessor:
    """Handles the workflow for processing task completions."""

    def __init__(
        self,
        hta_service: HTAService,
        task_engine: TaskEngine,
        memory_manager: MemoryManager,
        xp_engine: Optional[XPMasteryEngine] = None,
        llm_client: Optional[LLMClient] = None,
    ) -> None:
        """Initialize the CompletionProcessor with required and optional dependencies.
        
        Args:
            hta_service: Service for handling HTA (Hierarchical Task Analysis) operations
            task_engine: Engine for task management and generation
            memory_manager: Memory manager for handling memory snapshots
            xp_engine: Optional engine for XP and mastery challenge management
            llm_client: Optional language model client for XP mastery if needed
        
        Raises:
            TypeError: If hta_service or task_engine are invalid types
        """
        self.hta_service = hta_service
        self.task_engine = task_engine
        self.memory_manager = memory_manager
        self.xp_engine = xp_engine
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)

        # Validate critical dependencies
        if not isinstance(self.hta_service, HTAService) or type(self.hta_service).__name__ == 'DummyService':
              logger.critical("CompletionProcessor initialized with invalid or dummy HTAService!")
              raise TypeError("Invalid HTAService provided to CompletionProcessor.")
            
        if not isinstance(self.task_engine, TaskEngine) or type(self.task_engine).__name__ == 'DummyService':
              logger.critical("CompletionProcessor initialized with invalid or dummy TaskEngine!")
              raise TypeError("Invalid TaskEngine provided to CompletionProcessor.")

        # Log warnings for optional engines if they're dummies but features are enabled
        if is_enabled(Feature.XP_MASTERY):
            if not isinstance(self.xp_engine, XPMasteryEngine) or type(self.xp_engine).__name__ == 'DummyService':
              logger.warning("CompletionProcessor: XP_MASTERY feature enabled but XPMastery engine is invalid or dummy.")
            elif not isinstance(self.llm_client, LLMClient) or type(self.llm_client).__name__ == 'DummyService':
                logger.warning("CompletionProcessor: XP_MASTERY feature enabled but LLMClient (required for XPMastery) is invalid or dummy.")

        logger.info("CompletionProcessor initialized successfully.")

    async def process_xp_update(
        self,
        task: Dict[str, Any],
        snapshot: MemorySnapshot,
        success: bool
    ) -> Dict[str, Any]:
        """
        Process XP updates for a completed task.
        
        Args:
            task: The completed task
            snapshot: Current memory snapshot
            success: Whether the task was completed successfully
            
        Returns:
            Dict containing XP update information
        """
        if not self.xp_engine or not is_enabled(Feature.XP_MASTERY):
            return {}

        try:
            # Calculate XP gain
            try:
                xp_gain = self.xp_engine.calculate_xp_gain(task) if success else 0
            except Exception as e:
                # Return 0 XP for any calculation error
                logger.warning(f"Error calculating XP gain for task {task.get('id', 'unknown')}: {e}")
                return {
                    "xp_gained": 0,
                    "error": str(e)
                }
            
            # Get previous stage
            try:
                previous_stage = self.xp_engine.get_current_stage()
            except Exception as e:
                logger.error(f"Error getting previous stage: {e}")
                return {
                    "xp_gained": xp_gain,
                    "error": f"Stage lookup failed: {e}"
                }
            
            # Update XP
            self.xp_engine.current_xp += xp_gain
            
            # Get new stage
            try:
                current_stage = self.xp_engine.get_current_stage()
            except Exception as e:
                logger.error(f"Error getting current stage: {e}")
                self.xp_engine.current_xp -= xp_gain  # Rollback XP update
                return {
                    "xp_gained": 0,
                    "error": f"Stage lookup failed: {e}"
                }
            
            # Check if stage changed
            stage_changed = previous_stage["name"] != current_stage["name"]
            
            # Generate challenge if stage changed
            challenge_content = None
            if stage_changed:
                try:
                    challenge_content = await self.xp_engine.generate_challenge_content(
                        current_stage,
                        snapshot.to_dict()
                    )
                except Exception as e:
                    logger.error(f"Error generating challenge content: {e}")
                    # Don't fail the whole operation if challenge generation fails
            
            return {
                "xp_gained": xp_gain,
                "current_xp": self.xp_engine.current_xp,
                "previous_stage": previous_stage["name"],
                "current_stage": current_stage["name"],
                "stage_changed": stage_changed,
                "challenge": challenge_content
            }
            
        except Exception as e:
            logger.error(f"Error processing XP update: {e}")
            return {
                "xp_gained": 0,
                "error": str(e)
            }

    async def process(
        self,
        task_id: str,
        success: bool,
        snapshot: MemorySnapshot,
        db: Session,
        task_logger: TaskFootprintLogger
    ) -> Dict[str, Any]:
        """Process task completion and update system state."""
        result = {
            "success": success,
            "task_id": task_id,
            "batch_completed": False,
            "tree_evolved": False,
            "reflections_processed": False
        }

        try:
            # Start transaction
            db.begin()

            # Update task status in backlog
            task_updated = False
            completed_task = None
            for task in snapshot.task_backlog:
                if task.get("id") == task_id:
                    task["status"] = "completed" if success else "failed"
                    task["completed_at"] = datetime.now(timezone.utc).isoformat()
                    task_updated = True
                    completed_task = task
                    break

            if not task_updated:
                logger.warning(f"Task {task_id} not found in backlog")
                db.rollback()
                return result

            # Update withering level on successful completion
            if success:
                try:
                    old_withering = snapshot.withering_level
                    snapshot.withering_level = max(0.0, snapshot.withering_level - WITHERING_COMPLETION_RELIEF)
                    logger.info(f"Updated withering level from {old_withering} to {snapshot.withering_level}")
                except Exception as e:
                    logger.error(f"Error updating withering level: {e}")
                    db.rollback()
                    return result

            # Remove task from frontier batch
            try:
                if not isinstance(snapshot.current_frontier_batch_ids, list):
                    snapshot.current_frontier_batch_ids = []
                if task_id in snapshot.current_frontier_batch_ids:
                    snapshot.current_frontier_batch_ids.remove(task_id)
                    logger.info(f"Removed task {task_id} from frontier batch")
            except Exception as e:
                logger.error(f"Error updating frontier batch: {e}")
                db.rollback()
                return result

            # Check if batch is complete
            try:
                batch_completed = len(snapshot.current_frontier_batch_ids) == 0
                result["batch_completed"] = batch_completed

                # If batch is complete, process reflections and evolve tree
                if batch_completed and is_enabled(Feature.CORE_HTA):
                    try:
                        # Get current reflections
                        reflections = getattr(snapshot, "current_batch_reflections", [])
                        if not reflections and completed_task:
                            # Generate default reflection if none exists
                            reflections = [f"Completed task: {completed_task.get('title', 'Unknown task')}"]
                        
                        # Process reflections
                        if reflections:
                            # Add task-specific reflection if available
                            if completed_task:
                                task_reflection = f"Completed task: {completed_task.get('title', 'Unknown task')}"
                                if task_reflection not in reflections:
                                    reflections.append(task_reflection)
                            
                            # Evolve tree with reflections
                            tree = await self.hta_service.load_tree(snapshot)
                            if tree:
                                evolved_tree = await self.hta_service.evolve_tree(tree, reflections)
                                if evolved_tree:
                                    await self.hta_service.save_tree(snapshot, evolved_tree)
                                    result["tree_evolved"] = True
                                    result["reflections_processed"] = True
                                    logger.info("Successfully evolved HTA tree with reflections")
                                    
                                    # Clear batch reflections after successful evolution
                                    if hasattr(snapshot, 'current_batch_reflections'):
                                        snapshot.current_batch_reflections = []
                                        logger.info("Cleared batch reflections after tree evolution")
                                else:
                                    logger.error("Failed to evolve HTA tree")
                                    db.rollback()
                                    return result
                            else:
                                logger.error("Could not load HTA tree for evolution")
                                db.rollback()
                                return result
                    except Exception as e:
                        logger.error(f"Error evolving HTA tree: {e}")
                        db.rollback()
                        return result
            except Exception as e:
                logger.error(f"Error checking batch completion: {e}")
                result["batch_completed"] = False
                db.rollback()
                return result

            # Remove completed task from backlog
            try:
                snapshot.task_backlog = [t for t in snapshot.task_backlog if t.get("id") != task_id]
                logger.info(f"Removed task {task_id} from backlog")
            except Exception as e:
                logger.error(f"Error removing task from backlog: {e}")
                db.rollback()
                return result

            # Save updated snapshot
            try:
                snapshot_repo = MemorySnapshotRepository(db)
                snapshot_repo.save_snapshot(snapshot.user_id, snapshot.to_dict())
                db.commit()
                logger.info("Successfully saved updated snapshot")
            except Exception as e:
                logger.error(f"Error saving snapshot: {e}")
                db.rollback()
                return result

        except Exception as e:
            logger.error(f"Error processing task completion: {e}")
            result["success"] = False
            db.rollback()
            return result

        return result

    def _validate_completion_data(self, completion_data: Dict[str, Any]) -> bool:
        """Validate completion data structure and content."""
        try:
            if not isinstance(completion_data, dict):
                self.logger.error("Invalid completion data type")
                return False

            required_fields = ["task_id", "hta_node_id", "completion_time"]
            for field in required_fields:
                if field not in completion_data:
                    self.logger.error(f"Completion data missing required field: {field}")
                    return False

            if not isinstance(completion_data["completion_time"], (int, float)):
                self.logger.error("Invalid completion time type")
                return False

            if "reflection" in completion_data and not isinstance(completion_data["reflection"], str):
                self.logger.error("Invalid reflection type")
                return False

            return True
        except Exception as e:
            self.logger.error(f"Error validating completion data: {e}")
            return False

    def _validate_reflection(self, reflection: str) -> bool:
        """Validate reflection content."""
        try:
            if not isinstance(reflection, str):
                self.logger.error("Invalid reflection type")
                return False

            if len(reflection.strip()) < 10:
                self.logger.error("Reflection too short")
                return False

            if len(reflection) > 1000:
                self.logger.error("Reflection too long")
                return False

            return True
        except Exception as e:
            self.logger.error(f"Error validating reflection: {e}")
            return False

    def _process_batch_reflection(self, snapshot: Dict[str, Any]) -> None:
        """Process batch reflection with improved validation and error handling."""
        try:
            if not isinstance(snapshot, dict):
                self.logger.error("Invalid snapshot type for batch reflection")
                return

            batch_reflections = snapshot.get('batch_reflections', [])
            if not isinstance(batch_reflections, list):
                self.logger.error("Invalid batch_reflections type")
                return

            # Deduplicate reflections
            seen_reflections = set()
            unique_reflections = []
            for reflection in batch_reflections:
                if not isinstance(reflection, str):
                    continue
                if reflection not in seen_reflections and self._validate_reflection(reflection):
                    seen_reflections.add(reflection)
                    unique_reflections.append(reflection)

            # Update snapshot with unique reflections
            snapshot['batch_reflections'] = unique_reflections
            snapshot['last_reflection_time'] = datetime.now(timezone.utc).isoformat()

            # Mark tree as evolved if we have valid reflections
            if unique_reflections:
                snapshot['tree_evolved'] = True
                self.logger.info(f"Processed {len(unique_reflections)} unique reflections")

        except Exception as e:
            self.logger.error(f"Error processing batch reflection: {e}")

    def complete_task(self, task_id: str, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete a task with enhanced validation and error handling."""
        try:
            if not self._validate_completion_data(completion_data):
                return {"error": "Invalid completion data"}

            snapshot = self.memory_manager.get_snapshot()
            if not snapshot:
                return {"error": "No snapshot available"}

            # Update task status
            tasks = snapshot.get('tasks', [])
            task_found = False
            for task in tasks:
                if task.get('id') == task_id:
                    task['status'] = 'completed'
                    task['completion_time'] = completion_data['completion_time']
                    task_found = True
                    break

            if not task_found:
                return {"error": "Task not found"}

            # Process reflection if present
            if 'reflection' in completion_data:
                if not self._validate_reflection(completion_data['reflection']):
                    return {"error": "Invalid reflection"}
                
                batch_reflections = snapshot.get('batch_reflections', [])
                if not isinstance(batch_reflections, list):
                    batch_reflections = []
                batch_reflections.append(completion_data['reflection'])
                snapshot['batch_reflections'] = batch_reflections

            # Process batch reflection
            self._process_batch_reflection(snapshot)

            # Update snapshot
            self.memory_manager.update_snapshot(snapshot)

            return {"status": "success", "message": "Task completed successfully"}

        except Exception as e:
            self.logger.error(f"Error completing task: {e}")
            return {"error": str(e)}
