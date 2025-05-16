def test_backoff_import():
    import backoff
<<<<<<< HEAD
    print(f"Backoff version: {backoff.__version__}")
    print(f"Backoff file: {backoff.__file__}")
    assert hasattr(backoff, '__version__')
=======

    print(f"Backoff version: {backoff.__version__}")
    print(f"Backoff file: {backoff.__file__}")
    assert hasattr(backoff, "__version__")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
