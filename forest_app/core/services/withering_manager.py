"""
Manages the withering level calculations for user sessions.
This is a pure functional class with no internal state.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from forest_app.snapshot.snapshot import MemorySnapshot
from forest_app.config.constants import (
    WITHERING_COMPLETION_RELIEF,
    WITHERING_IDLE_COEFF,
    WITHERING_OVERDUE_COEFF,
    WITHERING_DECAY_FACTOR
)
from forest_app.core.soft_deadline_manager import hours_until_deadline

logger = logging.getLogger(__name__)

class WitheringManager:
    """
    Pure functional class for calculating and updating withering levels.
    No internal state - all state is passed in and returned.
    """
    
    @staticmethod
    def update_withering(snapshot: MemorySnapshot) -> None:
        """
        Adjusts withering level based on inactivity and deadlines.
        Pure function - takes snapshot state and updates it in place.
        """
        if not hasattr(snapshot, 'withering_level'): 
            snapshot.withering_level = 0.0
        if not hasattr(snapshot, 'component_state') or not isinstance(snapshot.component_state, dict): 
            snapshot.component_state = {}
        if not hasattr(snapshot, 'task_backlog') or not isinstance(snapshot.task_backlog, list): 
            snapshot.task_backlog = []

        current_path = getattr(snapshot, "current_path", "structured")
        now_utc = datetime.now(timezone.utc)
        last_iso = snapshot.component_state.get("last_activity_ts")
        idle_hours = 0.0
        
        if last_iso and isinstance(last_iso, str):
            try:
                # Ensure TZ info for comparison
                last_dt_aware = datetime.fromisoformat(last_iso.replace("Z", "+00:00"))
                if last_dt_aware.tzinfo is None: 
                    last_dt_aware = last_dt_aware.replace(tzinfo=timezone.utc)
                idle_delta = now_utc - last_dt_aware
                idle_hours = max(0.0, idle_delta.total_seconds() / 3600.0)
            except ValueError: 
                logger.warning("Could not parse last_activity_ts: %s", last_iso)
            except Exception as ts_err: 
                logger.exception("Error processing last_activity_ts: %s", ts_err)
        elif last_iso is not None: 
            logger.warning("last_activity_ts is not a string: %s", type(last_iso))

        idle_coeff = WITHERING_IDLE_COEFF.get(current_path, WITHERING_IDLE_COEFF["structured"])
        idle_penalty = idle_coeff * idle_hours

        # Calculate overdue penalty
        overdue_hours = 0.0
        if hasattr(snapshot, 'estimated_completion_date') and snapshot.estimated_completion_date:
            try:
                overdue_hours = hours_until_deadline(snapshot.estimated_completion_date)
                if overdue_hours < 0:  # Past deadline
                    overdue_hours = abs(overdue_hours)
                else:
                    overdue_hours = 0.0  # Not overdue
            except Exception as e:
                logger.exception("Error calculating overdue hours: %s", e)

        overdue_coeff = WITHERING_OVERDUE_COEFF.get(current_path, WITHERING_OVERDUE_COEFF["structured"])
        overdue_penalty = overdue_coeff * overdue_hours

        # Calculate completion relief
        completion_relief = 0.0
        if snapshot.task_backlog:
            completed_tasks = sum(1 for task in snapshot.task_backlog if task.get('status') == 'completed')
            total_tasks = len(snapshot.task_backlog)
            if total_tasks > 0:
                completion_ratio = completed_tasks / total_tasks
                completion_relief = WITHERING_COMPLETION_RELIEF * completion_ratio

        # Update withering level with decay
        new_withering = (
            snapshot.withering_level * WITHERING_DECAY_FACTOR +  # Decay existing
            idle_penalty +  # Add idle penalty
            overdue_penalty -  # Add overdue penalty
            completion_relief  # Subtract completion relief
        )
        
        # Clamp to valid range
        snapshot.withering_level = max(0.0, min(1.0, new_withering))
        
        # Update last activity timestamp
        snapshot.component_state["last_activity_ts"] = now_utc.isoformat(timespec='seconds') 