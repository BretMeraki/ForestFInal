#!/usr/bin/env python3
"""
Debug script to identify exact errors in test imports
"""
<<<<<<< HEAD
import sys
import traceback

def main():
    print("Attempting to load test module...")
    try:
        import tests.test_enhanced_hta_framework
=======

import traceback


def main():
    print("Attempting to load test module...")
    try:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        print("Successfully imported the test module!")
    except Exception as e:
        print(f"Error importing test module: {e}")
        print("\nDetailed traceback:")
        traceback.print_exc()
<<<<<<< HEAD
        
    print("\nChecking test helpers directory structure...")
    import os
=======

    print("\nChecking test helpers directory structure...")
    import os

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    test_helpers_path = os.path.join("forest_app", "core", "services", "test_helpers")
    if os.path.exists(test_helpers_path):
        print(f"Directory exists: {test_helpers_path}")
        print("Contents:")
        for item in os.listdir(test_helpers_path):
            print(f"  - {item}")
    else:
        print(f"Directory does not exist: {test_helpers_path}")
<<<<<<< HEAD
        
=======


>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
if __name__ == "__main__":
    main()
