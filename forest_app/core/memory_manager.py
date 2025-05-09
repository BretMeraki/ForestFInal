import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone

from forest_app.snapshot.snapshot import MemorySnapshot
from forest_app.snapshot.repository import MemorySnapshotRepository

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages memory snapshots and their persistence."""

    def __init__(self, snapshot_repository: MemorySnapshotRepository):
        """Initialize the MemoryManager.
        
        Args:
            snapshot_repository: Repository for persisting memory snapshots
        """
        self.snapshot_repository = snapshot_repository
        self.current_snapshot: Optional[MemorySnapshot] = None
        self.logger = logging.getLogger(__name__)

    def get_snapshot(self) -> Optional[Dict[str, Any]]:
        """Get the current memory snapshot."""
        if self.current_snapshot:
            return self.current_snapshot.to_dict()
        return None

    def update_snapshot(self, snapshot_data: Dict[str, Any]) -> bool:
        """Update the current memory snapshot.
        
        Args:
            snapshot_data: New snapshot data
            
        Returns:
            bool: True if update was successful
        """
        try:
            if not isinstance(snapshot_data, dict):
                self.logger.error("Invalid snapshot data type")
                return False

            if not self.current_snapshot:
                self.current_snapshot = MemorySnapshot()

            self.current_snapshot.update_from_dict(snapshot_data)
            self.current_snapshot.timestamp = datetime.now(timezone.utc).isoformat()
            return True
        except Exception as e:
            self.logger.error(f"Error updating snapshot: {e}")
            return False

    def save_snapshot(self, user_id: int) -> bool:
        """Save the current snapshot to persistent storage.
        
        Args:
            user_id: ID of the user owning the snapshot
            
        Returns:
            bool: True if save was successful
        """
        try:
            if not self.current_snapshot:
                self.logger.error("No snapshot to save")
                return False

            snapshot_data = self.current_snapshot.to_dict()
            self.snapshot_repository.save_snapshot(user_id, snapshot_data)
            return True
        except Exception as e:
            self.logger.error(f"Error saving snapshot: {e}")
            return False

    def load_snapshot(self, user_id: int) -> bool:
        """Load the latest snapshot for a user.
        
        Args:
            user_id: ID of the user whose snapshot to load
            
        Returns:
            bool: True if load was successful
        """
        try:
            snapshot_model = self.snapshot_repository.get_latest_snapshot(user_id)
            if not snapshot_model:
                self.logger.warning(f"No snapshot found for user {user_id}")
                return False

            self.current_snapshot = MemorySnapshot.from_dict(snapshot_model.snapshot_data)
            return True
        except Exception as e:
            self.logger.error(f"Error loading snapshot: {e}")
            return False

    def clear_snapshot(self) -> None:
        """Clear the current snapshot."""
        self.current_snapshot = None 