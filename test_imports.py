"""
Import verification script for Forest App.
Ensures all critical imports are available and working.
"""

import importlib
<<<<<<< HEAD
import sys
import logging
from typing import List, Dict, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

=======
import logging
import sys
from typing import Any, Dict, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def test_import(module_path: str) -> Tuple[bool, str]:
    """Test if a module can be imported."""
    try:
        importlib.import_module(module_path)
        return True, "Success"
    except ImportError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

<<<<<<< HEAD
def verify_imports() -> Dict[str, List[Dict[str, Any]]]:
    """Verify all critical imports for the Forest App."""
    results = {
        "success": [],
        "failure": []
    }
=======

def verify_imports() -> Dict[str, List[Dict[str, Any]]]:
    """Verify all critical imports for the Forest App."""
    results = {"success": [], "failure": []}
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    # Core imports
    core_modules = [
        "forest_app.core.snapshot",
        "forest_app.core.utils",
        "forest_app.core.processors",
        "forest_app.core.services",
        "forest_app.core.feature_flags",
        "forest_app.core.harmonic_framework",
<<<<<<< HEAD
        "forest_app.core.orchestrator"
=======
        "forest_app.core.orchestrator",
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    ]

    # Module imports
    module_imports = [
        "forest_app.modules.seed",
        "forest_app.modules.logging_tracking",
        "forest_app.modules.soft_deadline_manager",
        "forest_app.modules.types",
        "forest_app.modules.sentiment",
        "forest_app.modules.pattern_id",
        "forest_app.modules.practical_consequence",
        "forest_app.modules.metrics_specific",
        "forest_app.modules.relational",
        "forest_app.modules.narrative_modes",
        "forest_app.modules.offering_reward",
        "forest_app.modules.xp_mastery",
        "forest_app.modules.emotional_integrity",
        "forest_app.modules.task_engine",
        "forest_app.modules.snapshot_flow",
        "forest_app.modules.desire_engine",
<<<<<<< HEAD
        "forest_app.modules.financial_readiness"
    ]

    # Integration imports
    integration_imports = [
        "forest_app.integrations.llm"
    ]

    # Config imports
    config_imports = [
        "forest_app.config.settings",
        "forest_app.config.constants"
    ]
=======
        "forest_app.modules.financial_readiness",
    ]

    # Integration imports
    integration_imports = ["forest_app.integrations.llm"]

    # Config imports
    config_imports = ["forest_app.config.settings", "forest_app.config.constants"]
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    # Test all imports
    all_imports = {
        "Core": core_modules,
        "Modules": module_imports,
        "Integrations": integration_imports,
<<<<<<< HEAD
        "Config": config_imports
=======
        "Config": config_imports,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    }

    for category, modules in all_imports.items():
        logger.info(f"\nTesting {category} imports...")
        for module in modules:
            success, message = test_import(module)
<<<<<<< HEAD
            result = {
                "module": module,
                "category": category,
                "message": message
            }
=======
            result = {"module": module, "category": category, "message": message}
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            if success:
                results["success"].append(result)
                logger.info(f"✓ {module}")
            else:
                results["failure"].append(result)
                logger.error(f"✗ {module}: {message}")

    return results

<<<<<<< HEAD
def verify_protocol_implementations():
    """Verify that all Protocol implementations match their interfaces."""
    from forest_app.modules.types import SemanticMemoryProtocol
    from forest_app.core.services.semantic_memory import SemanticMemoryManager
    from forest_app.containers import DummySemanticMemoryManager
    
    logger.info("\nVerifying Protocol implementations...")
    
    # Get all required methods from the Protocol
    protocol_methods = [
        method for method in dir(SemanticMemoryProtocol)
        if not method.startswith('_')
    ]
    
=======

def verify_protocol_implementations():
    """Verify that all Protocol implementations match their interfaces."""
    from forest_app.containers import DummySemanticMemoryManager
    from forest_app.core.services.semantic_memory import SemanticMemoryManager
    from forest_app.modules.types import SemanticMemoryProtocol

    logger.info("\nVerifying Protocol implementations...")

    # Get all required methods from the Protocol
    protocol_methods = [
        method for method in dir(SemanticMemoryProtocol) if not method.startswith("_")
    ]

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Check SemanticMemoryManager
    logger.info("\nChecking SemanticMemoryManager implementation:")
    for method in protocol_methods:
        if hasattr(SemanticMemoryManager, method):
            logger.info(f"✓ {method}")
        else:
            logger.error(f"✗ Missing method: {method}")
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Check DummySemanticMemoryManager
    logger.info("\nChecking DummySemanticMemoryManager implementation:")
    for method in protocol_methods:
        if hasattr(DummySemanticMemoryManager, method):
            logger.info(f"✓ {method}")
        else:
            logger.error(f"✗ Missing method: {method}")

<<<<<<< HEAD
def main():
    """Main entry point for import verification."""
    logger.info("Starting import verification...")
    
    # Test all imports
    results = verify_imports()
    
    # Verify Protocol implementations
    verify_protocol_implementations()
    
    # Summary
    total_imports = len(results["success"]) + len(results["failure"])
    success_rate = (len(results["success"]) / total_imports) * 100
    
=======

def main():
    """Main entry point for import verification."""
    logger.info("Starting import verification...")

    # Test all imports
    results = verify_imports()

    # Verify Protocol implementations
    verify_protocol_implementations()

    # Summary
    total_imports = len(results["success"]) + len(results["failure"])
    success_rate = (len(results["success"]) / total_imports) * 100

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    logger.info("\nImport Verification Summary:")
    logger.info(f"Total imports tested: {total_imports}")
    logger.info(f"Successful imports: {len(results['success'])}")
    logger.info(f"Failed imports: {len(results['failure'])}")
    logger.info(f"Success rate: {success_rate:.1f}%")
<<<<<<< HEAD
    
    if results["failure"]:
        logger.error("\nFailed imports:")
        for failure in results["failure"]:
            logger.error(f"{failure['category']} - {failure['module']}: {failure['message']}")
=======

    if results["failure"]:
        logger.error("\nFailed imports:")
        for failure in results["failure"]:
            logger.error(
                f"{failure['category']} - {failure['module']}: {failure['message']}"
            )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        sys.exit(1)
    else:
        logger.info("\nAll imports successful!")
        sys.exit(0)

<<<<<<< HEAD
if __name__ == "__main__":
    main() 
=======

if __name__ == "__main__":
    main()
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
