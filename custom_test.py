#!/usr/bin/env python3
"""
Custom test runner that will execute the test_roadmap_models.py tests
with full tracebacks and more detailed error reporting.
"""
<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
import os
import sys
import traceback

# Add project root to path
<<<<<<< HEAD
sys.path.insert(0, os.path.abspath('.'))

try:
    from forest_app.core.roadmap_models import RoadmapStep, RoadmapManifest
    from forest_app.tests.test_roadmap_models import (
        test_roadmapstep_dependencies_frozenset,
        test_roadmapstep_timestamps,
        test_manifest_step_index_and_lookup,
        test_manifest_add_step_and_status_update,
        test_manifest_circular_dependency_detection
    )
    
    print("==== Running RoadmapModels Tests ====")
    
=======
sys.path.insert(0, os.path.abspath("."))

try:
    from forest_app.core.roadmap_models import RoadmapManifest, RoadmapStep
    from forest_app.tests.test_roadmap_models import (
        test_manifest_add_step_and_status_update,
        test_manifest_circular_dependency_detection,
        test_manifest_step_index_and_lookup,
        test_roadmapstep_dependencies_frozenset, test_roadmapstep_timestamps)

    print("==== Running RoadmapModels Tests ====")

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Test 1
    print("\n1. Test RoadmapStep dependencies frozenset")
    try:
        test_roadmapstep_dependencies_frozenset()
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Test 2
    print("\n2. Test RoadmapStep timestamps")
    try:
        test_roadmapstep_timestamps()
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Test 3
    print("\n3. Test manifest step index and lookup")
    try:
        test_manifest_step_index_and_lookup()
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Test 4
    print("\n4. Test manifest add step and status update")
    try:
        test_manifest_add_step_and_status_update()
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
<<<<<<< HEAD
    
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    # Test 5
    print("\n5. Test manifest circular dependency detection")
    try:
        test_manifest_circular_dependency_detection()
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ FAILED: {type(e).__name__}: {str(e)}")
        traceback.print_exc()
<<<<<<< HEAD
    
    print("\n==== Test Summary ====")
    
=======

    print("\n==== Test Summary ====")

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
except ImportError as e:
    print(f"Import Error: {str(e)}")
    traceback.print_exc()
except Exception as e:
    print(f"Unexpected error: {str(e)}")
    traceback.print_exc()
