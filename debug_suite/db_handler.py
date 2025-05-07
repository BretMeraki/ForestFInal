"""
Database Handler Module

This module manages the persistence of error data, providing functions to
store, retrieve, filter, and analyze error records.
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import uuid

class ErrorDatabase:
    """
    Handles storage and retrieval of error data in a simple JSON file.
    For production use, consider switching to an SQLite or proper database.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize the database handler.
        
        Args:
            db_path: Path to the JSON database file
        """
        self.db_path = db_path
        self.data = self._load_data()
        # Track the last position in the error log that was processed
        if 'meta' not in self.data:
            self.data['meta'] = {
                'last_line_position': 0,
                'last_update': datetime.now().isoformat()
            }
        if 'errors' not in self.data:
            self.data['errors'] = []
    
    def _load_data(self) -> Dict:
        """Load data from the JSON file or create a new structure if it doesn't exist."""
        if os.path.exists(self.db_path):
            try:
                with open(self.db_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted or can't be read, create new data
                pass
        
        # Default empty structure
        return {
            'meta': {
                'last_line_position': 0,
                'last_update': datetime.now().isoformat()
            },
            'errors': []
        }
    
    def _save_data(self):
        """Save the current data to the JSON file."""
        # Update metadata
        self.data['meta']['last_update'] = datetime.now().isoformat()
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Save to file
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_last_line_position(self) -> int:
        """Get the last processed position in the error log file."""
        return self.data['meta'].get('last_line_position', 0)
    
    def set_last_line_position(self, position: int):
        """Set the last processed position in the error log file."""
        self.data['meta']['last_line_position'] = position
        self._save_data()
    
    def add_error(self, 
                  timestamp: str, 
                  level: str, 
                  module: str, 
                  message: str, 
                  error_type: str, 
                  explanation: str,
                  stack_trace: str = "",
                  file_path: str = "",
                  line_number: str = "") -> str:
        """
        Add a new error record to the database.
        
        Args:
            timestamp: Error timestamp
            level: Error level (CRITICAL, ERROR, WARNING, INFO)
            module: Module name where the error occurred
            message: Error message
            error_type: Classification of the error
            explanation: Human-readable explanation
            stack_trace: Stack trace if available
            file_path: Path to the file where the error occurred
            line_number: Line number where the error occurred
            
        Returns:
            The ID of the newly added error
        """
        # Check if this error already exists (same message, module, and timestamp)
        for error in self.data['errors']:
            if (error['message'] == message and 
                error['module'] == module and 
                error['timestamp'] == timestamp):
                # Update existing error instead of adding a duplicate
                error['last_seen'] = datetime.now().isoformat()
                error['occurrences'] += 1
                self._save_data()
                return error['id']
        
        # Generate a unique ID
        error_id = str(uuid.uuid4())
        
        # Create the error record
        error = {
            'id': error_id,
            'timestamp': timestamp,
            'level': level.upper(),
            'module': module,
            'message': message,
            'error_type': error_type,
            'explanation': explanation,
            'stack_trace': stack_trace,
            'file_path': file_path,
            'line_number': line_number,
            'status': 'New',
            'created_at': datetime.now().isoformat(),
            'last_seen': datetime.now().isoformat(),
            'occurrences': 1,
            'notes': ''
        }
        
        # Add to the database
        self.data['errors'].append(error)
        self._save_data()
        
        return error_id
    
    def update_error_status(self, error_id: str, status: str) -> bool:
        """
        Update the status of an error.
        
        Args:
            error_id: The ID of the error to update
            status: New status (New, In Progress, Fixed, Ignored)
            
        Returns:
            True if successful, False if error not found
        """
        for error in self.data['errors']:
            if error['id'] == error_id:
                error['status'] = status
                error['updated_at'] = datetime.now().isoformat()
                self._save_data()
                return True
        
        return False
    
    def update_error_notes(self, error_id: str, notes: str) -> bool:
        """
        Update the notes for an error.
        
        Args:
            error_id: The ID of the error to update
            notes: New notes text
            
        Returns:
            True if successful, False if error not found
        """
        for error in self.data['errors']:
            if error['id'] == error_id:
                error['notes'] = notes
                error['updated_at'] = datetime.now().isoformat()
                self._save_data()
                return True
        
        return False
    
    def delete_error(self, error_id: str) -> bool:
        """
        Delete an error from the database.
        
        Args:
            error_id: The ID of the error to delete
            
        Returns:
            True if successful, False if error not found
        """
        for i, error in enumerate(self.data['errors']):
            if error['id'] == error_id:
                del self.data['errors'][i]
                self._save_data()
                return True
        
        return False
    
    def get_filtered_errors(self, 
                           status: str = "All", 
                           severity: str = "All", 
                           search_query: str = "",
                           limit: int = 100) -> List[Dict]:
        """
        Get errors filtered by status, severity, and search query.
        
        Args:
            status: Filter by status (All, New, In Progress, Fixed, Ignored)
            severity: Filter by severity level (All, CRITICAL, ERROR, WARNING, INFO)
            search_query: Text to search in error messages and modules
            limit: Maximum number of errors to return
            
        Returns:
            List of filtered error dictionaries
        """
        filtered = []
        
        for error in self.data['errors']:
            # Apply status filter
            if status != "All" and error['status'] != status:
                continue
                
            # Apply severity filter
            if severity != "All" and error['level'] != severity:
                continue
                
            # Apply search filter
            if search_query:
                search_query_lower = search_query.lower()
                message_lower = error['message'].lower()
                module_lower = error['module'].lower()
                error_type_lower = error['error_type'].lower()
                
                if (search_query_lower not in message_lower and 
                    search_query_lower not in module_lower and
                    search_query_lower not in error_type_lower):
                    continue
            
            filtered.append(error)
        
        # Sort by timestamp (newest first) and apply limit
        filtered.sort(key=lambda x: x['timestamp'], reverse=True)
        return filtered[:limit]
    
    def get_all_errors(self, limit: int = 500) -> List[Dict]:
        """
        Get all errors in the database.
        
        Args:
            limit: Maximum number of errors to return
            
        Returns:
            List of all error dictionaries
        """
        errors = self.data['errors'].copy()
        errors.sort(key=lambda x: x['timestamp'], reverse=True)
        return errors[:limit]
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the errors in the database.
        
        Returns:
            Dictionary of statistics
        """
        today = datetime.now().date()
        
        # Initialize stats
        stats = {
            'total': len(self.data['errors']),
            'new': 0,
            'in_progress': 0,
            'fixed': 0,
            'ignored': 0,
            'critical': 0,
            'error': 0,
            'warning': 0,
            'info': 0,
            'new_today': 0
        }
        
        # Compile statistics
        for error in self.data['errors']:
            # Count by status
            status = error['status'].lower().replace(' ', '_')
            if status in stats:
                stats[status] += 1
            
            # Count by severity
            level = error['level'].lower()
            if level in stats:
                stats[level] += 1
            
            # Count errors from today
            try:
                error_date = datetime.fromisoformat(error['created_at']).date()
                if error_date == today:
                    stats['new_today'] += 1
            except (ValueError, KeyError):
                pass
        
        return stats
    
    def get_error_trends(self, days: int = 7) -> Dict:
        """
        Get error trends over the past days.
        
        Args:
            days: Number of days to include in the trend
            
        Returns:
            Dictionary with dates as keys and counts as values
        """
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Initialize the dates dictionary
        dates = {}
        current_date = start_date
        while current_date <= end_date:
            dates[current_date.isoformat()] = {
                'total': 0,
                'critical': 0,
                'error': 0,
                'warning': 0
            }
            current_date += timedelta(days=1)
        
        # Count errors by date
        for error in self.data['errors']:
            try:
                error_date = datetime.fromisoformat(error['created_at']).date()
                date_str = error_date.isoformat()
                
                if date_str in dates:
                    dates[date_str]['total'] += 1
                    level = error['level'].lower()
                    if level in ['critical', 'error', 'warning']:
                        dates[date_str][level] += 1
            except (ValueError, KeyError):
                pass
        
        return dates
