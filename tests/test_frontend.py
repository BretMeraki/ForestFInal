import importlib
import sys
import os
import pytest

# Add project root to sys.path so 'forest_app' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Ensure project root is in sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def _patch_streamlit_secrets(monkeypatch, app):
    class FakeSecrets(dict):
        def get(self, key, default=None):
            return self[key] if key in self else default
        def __getitem__(self, key):
            return super().get(key, "http://localhost:8000")
    monkeypatch.setattr(app.st, "secrets", FakeSecrets({"BACKEND_URL": "http://localhost:8000"}))


def test_streamlit_app_import(monkeypatch):
    try:
        import forest_app.front_end.streamlit_app
    except Exception as e:
        pytest.fail(f"streamlit_app.py import failed: {e}")


def test_no_duplicate_set_page_config():
    with open("forest_app/front_end/streamlit_app.py") as f:
        lines = f.readlines()
    count = sum(1 for line in lines if "st.set_page_config" in line)
    assert count == 1, f"Expected 1 st.set_page_config call, found {count}"


def test_no_st_cache():
    with open("forest_app/front_end/streamlit_app.py") as f:
        content = f.read()
    assert "@st.cache" not in content, "Deprecated @st.cache found in streamlit_app.py. Use @st.cache_data or @st.cache_resource."


def test_streamlit_login_logic(monkeypatch):
    """
    Simulate starting the Streamlit app and performing a login via code.
    This mocks st.session_state and calls the login logic directly.
    """
    import forest_app.front_end.streamlit_app as app
    import types

    # Mock session_state
    class SessionState(dict):
        def __getattr__(self, item):
            return self[item] if item in self else None
        def __setattr__(self, key, value):
            self[key] = value
        def get(self, key, default=None):
            return super().get(key, default)
        def setdefault(self, key, default=None):
            return super().setdefault(key, default)

    # Patch st.session_state
    monkeypatch.setattr(app.st, "session_state", SessionState())

    # Provide test credentials (ensure these exist in your backend or use test DB)
    test_email = os.environ.get("TEST_USER_EMAIL", "testuser@example.com")
    test_password = os.environ.get("TEST_USER_PASSWORD", "testpassword")

    # Simulate login logic (call the API directly)
    login_data = {"username": test_email, "password": test_password}
    response = app.call_forest_api("/auth/token", method="POST", data=login_data)

    # Check for errors in the response
    assert response[app.KEY_ERROR] is None, f"Login failed: {response[app.KEY_ERROR]}"
    assert response[app.KEY_STATUS_CODE] == 200, f"Unexpected status code: {response[app.KEY_STATUS_CODE]}"
    assert isinstance(response[app.KEY_DATA], dict), "Login response data is not a dict"
    assert app.KEY_ACCESS_TOKEN in response[app.KEY_DATA], "No access token in login response"


def _setup_session_state(monkeypatch, app):
    class SessionState(dict):
        def __getattr__(self, item):
            return self[item] if item in self else None
        def __setattr__(self, key, value):
            self[key] = value
        def get(self, key, default=None):
            return super().get(key, default)
        def setdefault(self, key, default=None):
            return super().setdefault(key, default)
    monkeypatch.setattr(app.st, "session_state", SessionState())
    return app.st.session_state


def test_onboarding_goal_and_context(monkeypatch):
    import forest_app.front_end.streamlit_app as app
    _patch_streamlit_secrets(monkeypatch, app)
    session_state = _setup_session_state(monkeypatch, app)
    # Register and login first (assume test user is new each time)
    test_email = os.environ.get("TEST_USER_EMAIL", "testuser@example.com")
    test_password = os.environ.get("TEST_USER_PASSWORD", "testpassword")
    reg_data = {"email": test_email, "password": test_password, "full_name": "Test User"}
    reg_response = app.call_forest_api("/auth/register", method="POST", data=reg_data)
    # Registration may fail if user exists, so try login if so
    if reg_response[app.KEY_ERROR]:
        login_data = {"username": test_email, "password": test_password}
        login_response = app.call_forest_api("/auth/token", method="POST", data=login_data)
        assert login_response[app.KEY_ERROR] is None, f"Login failed: {login_response[app.KEY_ERROR]}"
        session_state.token = login_response[app.KEY_DATA][app.KEY_ACCESS_TOKEN]
    else:
        assert reg_response[app.KEY_STATUS_CODE] == 201, f"Unexpected registration status: {reg_response[app.KEY_STATUS_CODE]}"
        login_data = {"username": test_email, "password": test_password}
        login_response = app.call_forest_api("/auth/token", method="POST", data=login_data)
        assert login_response[app.KEY_ERROR] is None, f"Login failed: {login_response[app.KEY_ERROR]}"
        session_state.token = login_response[app.KEY_DATA][app.KEY_ACCESS_TOKEN]
    # Set goal
    goal = "Test my goal"
    goal_response = app.call_forest_api("/onboarding/set_goal", method="POST", data={"goal_description": goal})
    assert goal_response[app.KEY_ERROR] is None, f"Set goal failed: {goal_response[app.KEY_ERROR]}"
    # Set context
    context = "Test my context"
    context_response = app.call_forest_api("/onboarding/add_context", method="POST", data={"context_reflection": context})
    assert context_response[app.KEY_ERROR] is None, f"Add context failed: {context_response[app.KEY_ERROR]}"
    assert context_response[app.KEY_STATUS_CODE] == 200, f"Unexpected context status: {context_response[app.KEY_STATUS_CODE]}"


def test_hta_fetch(monkeypatch):
    import forest_app.front_end.streamlit_app as app
    _patch_streamlit_secrets(monkeypatch, app)
    session_state = _setup_session_state(monkeypatch, app)
    # Login first
    test_email = os.environ.get("TEST_USER_EMAIL", "testuser@example.com")
    test_password = os.environ.get("TEST_USER_PASSWORD", "testpassword")
    login_data = {"username": test_email, "password": test_password}
    login_response = app.call_forest_api("/auth/token", method="POST", data=login_data)
    assert login_response[app.KEY_ERROR] is None, f"Login failed: {login_response[app.KEY_ERROR]}"
    session_state.token = login_response[app.KEY_DATA][app.KEY_ACCESS_TOKEN]
    # Fetch HTA state
    hta_response = app.call_forest_api("/hta/state", method="GET")
    assert hta_response[app.KEY_ERROR] is None, f"HTA fetch failed: {hta_response[app.KEY_ERROR]}"
    assert hta_response[app.KEY_STATUS_CODE] in [200, 404], f"Unexpected HTA status: {hta_response[app.KEY_STATUS_CODE]}"


def test_chat_command(monkeypatch):
    import forest_app.front_end.streamlit_app as app
    _patch_streamlit_secrets(monkeypatch, app)
    session_state = _setup_session_state(monkeypatch, app)
    # Login first
    test_email = os.environ.get("TEST_USER_EMAIL", "testuser@example.com")
    test_password = os.environ.get("TEST_USER_PASSWORD", "testpassword")
    login_data = {"username": test_email, "password": test_password}
    login_response = app.call_forest_api("/auth/token", method="POST", data=login_data)
    assert login_response[app.KEY_ERROR] is None, f"Login failed: {login_response[app.KEY_ERROR]}"
    session_state.token = login_response[app.KEY_DATA][app.KEY_ACCESS_TOKEN]
    # Send a command
    command = "Reflect on my progress"
    command_response = app.call_forest_api("/core/command", method="POST", data={"command": command})
    assert command_response[app.KEY_ERROR] is None, f"Command failed: {command_response[app.KEY_ERROR]}"
    assert command_response[app.KEY_STATUS_CODE] in [200, 201], f"Unexpected command status: {command_response[app.KEY_STATUS_CODE]}"


def test_snapshot_list(monkeypatch):
    import forest_app.front_end.streamlit_app as app
    _patch_streamlit_secrets(monkeypatch, app)
    session_state = _setup_session_state(monkeypatch, app)
    # Login first
    test_email = os.environ.get("TEST_USER_EMAIL", "testuser@example.com")
    test_password = os.environ.get("TEST_USER_PASSWORD", "testpassword")
    login_data = {"username": test_email, "password": test_password}
    login_response = app.call_forest_api("/auth/token", method="POST", data=login_data)
    assert login_response[app.KEY_ERROR] is None, f"Login failed: {login_response[app.KEY_ERROR]}"
    session_state.token = login_response[app.KEY_DATA][app.KEY_ACCESS_TOKEN]
    # List snapshots
    snapshot_response = app.call_forest_api("/snapshots/list", method="GET")
    assert snapshot_response[app.KEY_ERROR] is None, f"Snapshot list failed: {snapshot_response[app.KEY_ERROR]}"
    assert snapshot_response[app.KEY_STATUS_CODE] == 200, f"Unexpected snapshot list status: {snapshot_response[app.KEY_STATUS_CODE]}" 