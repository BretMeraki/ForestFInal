"""
Forest App - A personal growth and task management application.
"""

__version__ = "1.0.0"

# Import core components
try:
<<<<<<< HEAD
    from forest_app.core.processors import ReflectionProcessor, CompletionProcessor
    from forest_app.core.services import HTAService, ComponentStateManager
    __all__ = [
        'ReflectionProcessor',
        'CompletionProcessor',
        'HTAService',
        'ComponentStateManager'
    ]
except ImportError as e:
=======
    from forest_app.core.processors import (CompletionProcessor,
                                            ReflectionProcessor)
    from forest_app.core.services import ComponentStateManager, HTAService

    __all__ = [
        "ReflectionProcessor",
        "CompletionProcessor",
        "HTAService",
        "ComponentStateManager",
    ]
except ImportError:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # If core components can't be imported, don't include them in __all__
    __all__ = []
