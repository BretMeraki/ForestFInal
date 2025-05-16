import pytest
<<<<<<< HEAD
from forest_app.integrations.prompt_augmentation import PromptAugmentationService, AugmentationTemplate
=======

from forest_app.integrations.prompt_augmentation import (
    AugmentationTemplate, PromptAugmentationService)

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

def test_default_template_exists():
    service = PromptAugmentationService()
    assert "json_generation" in service.templates
    template = service.templates["json_generation"]
    assert isinstance(template, AugmentationTemplate)

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def test_format_prompt_with_examples():
    template = AugmentationTemplate(
        name="test",
        description="Test template",
        system_prompt="System context.",
        prompt_format="Hello, {name}!",
<<<<<<< HEAD
        examples=[{"input": "Hi", "output": "Hello!"}]
=======
        examples=[{"input": "Hi", "output": "Hello!"}],
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    )
    result = template.format_prompt(name="World")
    assert isinstance(result, list)
    assert result[0]["role"] == "system"
    assert result[-1]["content"] == "Hello, World!"

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def test_format_prompt_missing_param():
    template = AugmentationTemplate(
        name="test",
        description="Test template",
        system_prompt="System context.",
<<<<<<< HEAD
        prompt_format="Hello, {name}!"
=======
        prompt_format="Hello, {name}!",
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    )
    with pytest.raises(ValueError):
        template.format_prompt()
