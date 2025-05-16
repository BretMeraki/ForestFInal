#!/usr/bin/env python3
"""
Debug script to line-by-line check the test file for errors
"""
<<<<<<< HEAD
import sys
import traceback

def test_import_sequence():
    """Test imports one by one to find where the error occurs"""
    print("Starting debug sequence...")
    
    # Basic imports
    print("1. Importing basic modules")
    try:
        import pytest
        import uuid
        import asyncio
        from datetime import datetime
        from typing import Dict, Any, List
        from uuid import UUID
=======

import traceback


def test_import_sequence():
    """Test imports one by one to find where the error occurs"""
    print("Starting debug sequence...")

    # Basic imports
    print("1. Importing basic modules")
    try:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        print("✓ Basic modules imported successfully")
    except Exception as e:
        print(f"✗ Error importing basic modules: {e}")
        traceback.print_exc()
        return
<<<<<<< HEAD
    
    # Import core modules
    print("\n2. Importing core modules")
    try:
        from forest_app.core.schema_contract import HTASchemaContract
        from forest_app.core.context_infused_generator import ContextInfusedNodeGenerator
        from forest_app.persistence.hta_tree_repository import HTATreeRepository
        from forest_app.core.services.enhanced_hta_service import EnhancedHTAService
        from forest_app.core.roadmap_models import RoadmapManifest, RoadmapStep
        from forest_app.persistence.models import HTANodeModel, HTATreeModel, UserModel
        from forest_app.core.session_manager import SessionManager
=======

    # Import core modules
    print("\n2. Importing core modules")
    try:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        print("✓ Core modules imported successfully")
    except Exception as e:
        print(f"✗ Error importing core modules: {e}")
        traceback.print_exc()
        return
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Import test helper modules
    print("\n3. Importing test helper modules")
    try:
        print("Checking if test_helpers directory exists and is initialized...")
        import os
<<<<<<< HEAD
        test_helpers_path = os.path.join("forest_app", "core", "services", "test_helpers")
=======

        test_helpers_path = os.path.join(
            "forest_app", "core", "services", "test_helpers"
        )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        if os.path.exists(test_helpers_path):
            print(f"✓ Directory exists: {test_helpers_path}")
            init_file = os.path.join(test_helpers_path, "__init__.py")
            if os.path.exists(init_file):
<<<<<<< HEAD
                print(f"✓ __init__.py exists in test_helpers directory")
            else:
                print(f"✗ __init__.py missing in test_helpers directory")
                with open(init_file, 'w') as f:
=======
                print("✓ __init__.py exists in test_helpers directory")
            else:
                print("✗ __init__.py missing in test_helpers directory")
                with open(init_file, "w") as f:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
                    f.write("# Test helpers package\n")
                print(f"Created __init__.py in {test_helpers_path}")
        else:
            print(f"✗ Directory does not exist: {test_helpers_path}")
    except Exception as e:
        print(f"Error checking test_helpers directory: {e}")
        traceback.print_exc()
<<<<<<< HEAD
    
    # Try importing the test helpers
    try:
        print("\nAttempting to import test helper functions...")
        from forest_app.core.services.test_helpers.mock_enhanced_hta_service import get_mock_enhanced_hta_service
=======

    # Try importing the test helpers
    try:
        print("\nAttempting to import test helper functions...")

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        print("✓ mock_enhanced_hta_service imported successfully")
    except Exception as e:
        print(f"✗ Error importing mock_enhanced_hta_service: {e}")
        traceback.print_exc()
<<<<<<< HEAD
    
    try:
        from forest_app.core.services.test_helpers.mock_node_generator import get_mock_node_generator
=======

    try:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        print("✓ mock_node_generator imported successfully")
    except Exception as e:
        print(f"✗ Error importing mock_node_generator: {e}")
        traceback.print_exc()
<<<<<<< HEAD
    
    try:
        from forest_app.core.services.test_helpers.mock_repository import get_mock_tree_repository
=======

    try:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        print("✓ mock_repository imported successfully")
    except Exception as e:
        print(f"✗ Error importing mock_repository: {e}")
        traceback.print_exc()
<<<<<<< HEAD
    
    print("\n4. Checking test file fixture imports")
    try:
        import tests.test_enhanced_hta_framework
=======

    print("\n4. Checking test file fixture imports")
    try:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        print("✓ Test file imported successfully")
    except Exception as e:
        print(f"✗ Error importing test file: {e}")
        print("\nDetailed traceback:")
        traceback.print_exc()

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
if __name__ == "__main__":
    test_import_sequence()
