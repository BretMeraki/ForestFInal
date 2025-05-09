"""
Manages the withering level calculations for user sessions.
This is a pure functional class with no internal state.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any

from forest_app.snapshot.snapshot import MemorySnapshot
from forest_app.config.constants import (
    MAGNITUDE_THRESHOLDS,
    WITHERING_COMPLETION_RELIEF,
    WITHERING_IDLE_COEFF,
    WITHERING_OVERDUE_COEFF,
    WITHERING_DECAY_FACTOR
)
from forest_app.core.soft_deadline_manager import hours_until_deadline
from forest_app.core.exceptions import WitheringError

logger = logging.getLogger(__name__)

class WitheringManager:
    """
    Pure functional class for calculating and updating withering levels.
    No internal state - all state is passed in and returned.
    """
    
    @staticmethod
    def calculate_withering(snapshot: MemorySnapshot) -> float:
        """
        Calculate the new withering level based on the current state.
        Returns the new withering level without modifying the snapshot.
        """
        try:
            current_level = snapshot.withering_level
            if current_level is None:
                current_level = 0.0
                
            # Apply decay based on time since last activity
            now = datetime.now(timezone.utc)
            last_activity = snapshot.last_activity_ts or now
            hours_idle = (now - last_activity).total_seconds() / 3600
            decay = WITHERING_DECAY_FACTOR * hours_idle
            
            # Calculate new level
            new_level = current_level + decay
            
            # Check for overdue tasks
            if snapshot.active_tasks:
                for task in snapshot.active_tasks:
                    if task.deadline:
                        hours_remaining = hours_until_deadline(task.deadline)
                        if hours_remaining < 0:  # Task is overdue
                            new_level += abs(hours_remaining) * WITHERING_OVERDUE_COEFF
            
            # Clamp between 0 and 1
            new_level = max(0.0, min(1.0, new_level))
            
            return new_level
            
        except Exception as e:
            logger.exception("Error calculating withering level: %s", e)
            raise WitheringError("Failed to calculate withering level") from e
    
    @staticmethod
    def update_withering(snapshot: MemorySnapshot) -> None:
        """Updates the withering level in the snapshot."""
        new_level = WitheringManager.calculate_withering(snapshot)
        snapshot.withering_level = new_level
        
        # Update last activity timestamp
        snapshot.component_state["last_activity_ts"] = datetime.now(timezone.utc).isoformat(timespec='seconds')
    
    @staticmethod
    def describe_magnitude(value: float) -> str:
        """
        Describe a magnitude value using configured thresholds.
        
        Args:
            value: The magnitude value to describe
            
        Returns:
            A string description of the magnitude
            
        Raises:
            WitheringError: If the value cannot be processed
        """
        try:
            float_value = float(value)
            valid_thresholds = {
                k: float(v) for k, v in MAGNITUDE_THRESHOLDS.items()
                if isinstance(v, (int, float))
            }
            if not valid_thresholds:
                return "Unknown"
                
            sorted_thresholds = sorted(
                valid_thresholds.items(),
                key=lambda item: item[1],
                reverse=True
            )
            
            for label, thresh in sorted_thresholds:
                if float_value >= thresh:
                    return str(label)
                    
            return str(sorted_thresholds[-1][0]) if sorted_thresholds else "Dormant"
            
        except (ValueError, TypeError) as e:
            logger.error("Error converting value/threshold for magnitude: %s (Value: %s)", e, value)
            raise WitheringError(f"Invalid magnitude value: {value}") from e
        except Exception as e:
            logger.exception("Error describing magnitude for value %s: %s", value, e)
            raise WitheringError(f"Failed to describe magnitude: {value}") from e 