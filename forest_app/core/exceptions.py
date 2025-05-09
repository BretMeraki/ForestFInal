"""Custom exceptions for the Forest application."""

class StateLoadError(Exception):
    """Raised when there is an error loading component states."""
    pass

class StateSaveError(Exception):
    """Raised when there is an error saving component states."""
    pass

class ProcessingError(Exception):
    """Raised when there is an error during processing."""
    pass

class WitheringError(Exception):
    """Raised when there is an error during withering calculations."""
    pass 