"""
Log Watcher Module

This module provides functionality to monitor the error log file for changes
and process new error entries in real-time.
"""
import os
import time
import threading
from typing import Callable, Any, Optional
from pathlib import Path
from datetime import datetime

class LogWatcher:
    """
    Watches a log file for changes and processes new lines.
    """
    
    def __init__(self, log_path: str, callback: Callable[[str, int], Any], check_interval: float = 1.0):
        """
        Initialize the log watcher.
        
        Args:
            log_path: Path to the log file to watch
            callback: Function to call with (log_path, file_position) when new content is detected
            check_interval: How often to check for changes, in seconds
        """
        self.log_path = log_path
        self.callback = callback
        self.check_interval = check_interval
        self.last_position = 0
        self.running = False
        self.thread = None
        self.last_error = None
        
    def start(self):
        """Start watching the log file."""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.thread.start()
        
    def stop(self):
        """Stop watching the log file."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
            self.thread = None
            
    def set_position(self, position: int):
        """Set the current position in the file."""
        self.last_position = position
        
    def _watch_loop(self):
        """Main watch loop that checks for file changes."""
        while self.running:
            try:
                if not os.path.exists(self.log_path):
                    time.sleep(self.check_interval)
                    continue
                    
                # Get the current file size
                file_size = os.path.getsize(self.log_path)
                
                # If file size changed, process new content
                if file_size > self.last_position:
                    try:
                        self.callback(self.log_path, self.last_position)
                        self.last_position = file_size
                        self.last_error = None
                    except Exception as e:
                        self.last_error = str(e)
                
                # If file was truncated, reset position
                elif file_size < self.last_position:
                    self.last_position = 0
                    
                # Wait before next check
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.last_error = str(e)
                time.sleep(self.check_interval * 2)  # Wait longer on error
        
    @property
    def status(self) -> dict:
        """Get the current status of the watcher."""
        return {
            'running': self.running and (self.thread is not None and self.thread.is_alive()),
            'last_position': self.last_position,
            'last_error': self.last_error,
            'log_path': self.log_path,
            'last_check': datetime.now().isoformat()
        }
