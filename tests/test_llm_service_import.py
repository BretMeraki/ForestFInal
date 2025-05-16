import sys

<<<<<<< HEAD
def test_llm_service_import():
    print('sys.path:', sys.path)
    try:
        import forest_app.integrations.llm_service
        print('Import succeeded')
    except Exception as e:
        print('Import failed:', e)
=======

def test_llm_service_import():
    print("sys.path:", sys.path)
    try:
        print("Import succeeded")
    except Exception as e:
        print("Import failed:", e)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        raise
