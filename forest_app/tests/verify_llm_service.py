"""
Simple verification script for the LLM service implementation.
This script avoids test framework complexities and just verifies imports and basic instantiation.
"""

<<<<<<< HEAD
import sys
import os
from unittest.mock import patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

print("Attempting to import LLM service modules...")
try:
    from forest_app.integrations.llm_service import (
        BaseLLMService,
        GoogleGeminiService,
        create_llm_service,
        get_llm_service
    )
    print("✅ Successfully imported llm_service module")
    
    from forest_app.integrations.context_trimmer import ContextTrimmer
    print("✅ Successfully imported context_trimmer module")
    
    from forest_app.integrations.prompt_augmentation import PromptAugmentationService
    print("✅ Successfully imported prompt_augmentation module")
    
=======
import os
import sys
from unittest.mock import patch

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

print("Attempting to import LLM service modules...")
try:
    # Only import what is actually used in the test body
    from forest_app.integrations.llm_service import create_llm_service

    print("✅ Successfully imported llm_service module")

    from forest_app.integrations.context_trimmer import ContextTrimmer

    print("✅ Successfully imported context_trimmer module")

    from forest_app.integrations.prompt_augmentation import \
        PromptAugmentationService

    print("✅ Successfully imported prompt_augmentation module")

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

print("\nVerifying class instantiation...")
try:
    # Mock the necessary Google API calls
    with patch("google.generativeai.configure") as mock_configure:
        with patch("google.generativeai.GenerativeModel") as mock_generative_model:
            # Create the service
<<<<<<< HEAD
            service = create_llm_service(
                provider="gemini",
                api_key="test_key"
            )
            
=======
            service = create_llm_service(provider="gemini", api_key="test_key")

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            print(f"✅ Successfully created LLM service: {service.__class__.__name__}")
            print(f"   - Service name: {service.service_name}")
            print(f"   - Default model: {service.default_model}")
            print(f"   - Advanced model: {service.advanced_model_name}")
            print(f"   - Max retries: {service.max_retries}")
            print(f"   - Cache enabled: {service._cache_enabled}")
<<<<<<< HEAD
            
            # Create auxiliary services
            trimmer = ContextTrimmer()
            print(f"✅ Successfully created ContextTrimmer")
            print(f"   - Max tokens: {trimmer.config.max_tokens}")
            
            augmentation = PromptAugmentationService()
            print(f"✅ Successfully created PromptAugmentationService")
            print(f"   - Available templates: {', '.join(augmentation.templates.keys())}")
    
=======

            # Create auxiliary services
            trimmer = ContextTrimmer()
            print("✅ Successfully created ContextTrimmer")
            print(f"   - Max tokens: {trimmer.config.max_tokens}")

            augmentation = PromptAugmentationService()
            print("✅ Successfully created PromptAugmentationService")
            print(
                f"   - Available templates: {', '.join(augmentation.templates.keys())}"
            )

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
except Exception as e:
    print(f"❌ Error during verification: {e}")
    raise

<<<<<<< HEAD
print("\n✅ All verifications passed! The LLM service implementation appears to be working correctly.")
print("Note: This is a basic verification and does not test the actual functionality with real API calls.")
=======
print(
    "\n✅ All verifications passed! The LLM service implementation appears to be working correctly."
)
print(
    "Note: This is a basic verification and does not test the actual functionality with real API calls."
)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
