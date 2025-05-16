# front_end/auth_ui.py
<<<<<<< HEAD
import streamlit as st
import logging
import json
from typing import Dict, List, Union, Optional, Any
=======
import logging

import streamlit as st
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

# Update relative import to absolute
from forest_app.front_end.api_client import call_forest_api

# Define constants used within this module or import from a central place
# (Duplicating from streamlit_app.py for now, consider centralizing later)
<<<<<<< HEAD
KEY_STATUS_CODE = "status_code"; KEY_ERROR = "error"; KEY_DETAIL = "detail"; KEY_DATA = "data"
KEY_ACCESS_TOKEN = "access_token"; KEY_ONBOARDING_STATUS = "onboarding_status"
KEY_USER_INFO_EMAIL = "email"; KEY_USER_INFO_ID = "id"; KEY_ERROR_MESSAGE = "error_message"
KEY_MESSAGES = "messages"; KEY_CURRENT_TASK = "current_task"; KEY_HTA_STATE = "hta_state"
KEY_PENDING_CONFIRMATION = "pending_confirmation"; KEY_MILESTONES = "milestones_achieved"
class constants: # Placeholder
    ONBOARDING_STATUS_NEEDS_GOAL = "needs_goal"; ONBOARDING_STATUS_NEEDS_CONTEXT = "needs_context";
    ONBOARDING_STATUS_COMPLETED = "completed"; MIN_PASSWORD_LENGTH = 8
=======
KEY_STATUS_CODE = "status_code"
KEY_ERROR = "error"
KEY_DETAIL = "detail"
KEY_DATA = "data"
KEY_ACCESS_TOKEN = "access_token"
KEY_ONBOARDING_STATUS = "onboarding_status"
KEY_USER_INFO_EMAIL = "email"
KEY_USER_INFO_ID = "id"
KEY_ERROR_MESSAGE = "error_message"
KEY_MESSAGES = "messages"
KEY_CURRENT_TASK = "current_task"
KEY_HTA_STATE = "hta_state"
KEY_PENDING_CONFIRMATION = "pending_confirmation"
KEY_MILESTONES = "milestones_achieved"


class constants:  # Placeholder
    ONBOARDING_STATUS_NEEDS_GOAL = "needs_goal"
    ONBOARDING_STATUS_NEEDS_CONTEXT = "needs_context"
    ONBOARDING_STATUS_COMPLETED = "completed"
    MIN_PASSWORD_LENGTH = 8

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

logger = logging.getLogger(__name__)

# --- Internal Helper Functions for Auth Logic ---

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def _handle_login_success(token_response_data: dict, backend_url: str):
    """Processes successful login: stores token, fetches user details, resets state."""
    access_token = token_response_data.get(KEY_ACCESS_TOKEN)
    if not access_token:
        logger.error("Login API call succeeded, but token was missing.")
        st.error("Login succeeded, but auth token was missing. Cannot proceed.")
<<<<<<< HEAD
        return False # Indicate failure

    st.session_state.token = access_token
    logger.info(f"Token received successfully.")
=======
        return False  # Indicate failure

    st.session_state.token = access_token
    logger.info("Token received successfully.")
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    # Fetch User Details (/users/me)
    user_details_response = call_forest_api(
        "/users/me",
        method="GET",
        backend_url=backend_url,
<<<<<<< HEAD
        api_token=st.session_state.token
    )

    if user_details_response.get(KEY_ERROR) or not isinstance(user_details_response.get(KEY_DATA), dict):
        error_msg = user_details_response.get(KEY_ERROR, "Failed to retrieve user data")
        logger.error(f"Login ok, but failed fetch user details: {error_msg}")
        st.error(f"Login succeeded, but failed to fetch details: {error_msg}. Try again.")
        # Clear partial login state
        st.session_state.authenticated = False; st.session_state.token = None
        st.session_state.user_info = None; st.session_state[KEY_ONBOARDING_STATUS] = None
        return False # Indicate failure
=======
        api_token=st.session_state.token,
    )

    if user_details_response.get(KEY_ERROR) or not isinstance(
        user_details_response.get(KEY_DATA), dict
    ):
        error_msg = user_details_response.get(KEY_ERROR, "Failed to retrieve user data")
        logger.error(f"Login ok, but failed fetch user details: {error_msg}")
        st.error(
            f"Login succeeded, but failed to fetch details: {error_msg}. Try again."
        )
        # Clear partial login state
        st.session_state.authenticated = False
        st.session_state.token = None
        st.session_state.user_info = None
        st.session_state[KEY_ONBOARDING_STATUS] = None
        return False  # Indicate failure
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    else:
        # Successfully Fetched User Details
        user_data = user_details_response.get(KEY_DATA, {})
        st.session_state.user_info = user_data
        user_onboarding_status = user_data.get(KEY_ONBOARDING_STATUS)
<<<<<<< HEAD
        valid_statuses = [constants.ONBOARDING_STATUS_NEEDS_GOAL, constants.ONBOARDING_STATUS_NEEDS_CONTEXT, constants.ONBOARDING_STATUS_COMPLETED]
        st.session_state[KEY_ONBOARDING_STATUS] = user_onboarding_status if user_onboarding_status in valid_statuses else constants.ONBOARDING_STATUS_COMPLETED
        logger.info(f"User details fetched. Status: {st.session_state[KEY_ONBOARDING_STATUS]}")

        # Reset Session State for New Login
        st.session_state[KEY_MESSAGES] = []; st.session_state[KEY_CURRENT_TASK] = None
        st.session_state["snapshots"] = []; st.session_state[KEY_ERROR_MESSAGE] = None
        st.session_state[KEY_HTA_STATE] = None; st.session_state[KEY_PENDING_CONFIRMATION] = None
        st.session_state[KEY_MILESTONES] = []
        st.session_state.authenticated = True # Mark authenticated *last*
        st.success("Login Successful!")
        return True # Indicate success
=======
        valid_statuses = [
            constants.ONBOARDING_STATUS_NEEDS_GOAL,
            constants.ONBOARDING_STATUS_NEEDS_CONTEXT,
            constants.ONBOARDING_STATUS_COMPLETED,
        ]
        st.session_state[KEY_ONBOARDING_STATUS] = (
            user_onboarding_status
            if user_onboarding_status in valid_statuses
            else constants.ONBOARDING_STATUS_COMPLETED
        )
        logger.info(
            f"User details fetched. Status: {st.session_state[KEY_ONBOARDING_STATUS]}"
        )

        # Reset Session State for New Login
        st.session_state[KEY_MESSAGES] = []
        st.session_state[KEY_CURRENT_TASK] = None
        st.session_state["snapshots"] = []
        st.session_state[KEY_ERROR_MESSAGE] = None
        st.session_state[KEY_HTA_STATE] = None
        st.session_state[KEY_PENDING_CONFIRMATION] = None
        st.session_state[KEY_MILESTONES] = []
        st.session_state.authenticated = True  # Mark authenticated *last*
        st.success("Login Successful!")
        return True  # Indicate success
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)


def _handle_login_submission(email, password, backend_url):
    """Handles the submission of the login form."""
    st.session_state[KEY_ERROR_MESSAGE] = None
    if not email or not password:
        st.error("Email and password required.")
<<<<<<< HEAD
        return False # Indicate failure (no API call made)
=======
        return False  # Indicate failure (no API call made)
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    with st.spinner("Logging in..."):
        auth_data = {"username": email, "password": password}
        token_response = call_forest_api(
            "/auth/token",
            method="POST",
            data=auth_data,
            backend_url=backend_url,
<<<<<<< HEAD
            api_token=None
=======
            api_token=None,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        )

        if token_response.get(KEY_ERROR):
            error_msg = token_response.get(KEY_ERROR, "Unknown login error")
            st.error(f"Login Failed: {error_msg}")
            st.session_state[KEY_ERROR_MESSAGE] = f"Login Failed: {error_msg}"
<<<<<<< HEAD
            return False # Indicate failure
        elif token_response.get(KEY_STATUS_CODE) == 200 and isinstance(token_response.get(KEY_DATA), dict):
=======
            return False  # Indicate failure
        elif token_response.get(KEY_STATUS_CODE) == 200 and isinstance(
            token_response.get(KEY_DATA), dict
        ):
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            # Delegate processing to the success handler
            return _handle_login_success(token_response.get(KEY_DATA, {}), backend_url)
        else:
            status_code = token_response.get(KEY_STATUS_CODE, "N/A")
            logger.error(f"Login failed: Unexpected API response status {status_code}")
            st.error(f"Login failed (Status: {status_code}).")
            st.session_state[KEY_ERROR_MESSAGE] = f"Login Failed: Status {status_code}"
<<<<<<< HEAD
            return False # Indicate failure
=======
            return False  # Indicate failure
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)


def _handle_register_submission(email, name, password, backend_url):
    """Handles the submission of the registration form."""
    st.session_state[KEY_ERROR_MESSAGE] = None
    if not email or not password:
        st.error("Email and password required.")
        return False
    elif len(password) < constants.MIN_PASSWORD_LENGTH:
        st.error(f"Min password length {constants.MIN_PASSWORD_LENGTH}.")
        return False

    with st.spinner("Registering..."):
        reg_data = {"email": email, "password": password, "full_name": name or None}
        register_response = call_forest_api(
            "/auth/register",
            method="POST",
            data=reg_data,
            backend_url=backend_url,
<<<<<<< HEAD
            api_token=None
=======
            api_token=None,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        )

        if register_response.get(KEY_ERROR):
            error_msg = register_response.get(KEY_ERROR, "Unknown error")
            st.error(f"Reg Fail: {error_msg}")
            st.session_state[KEY_ERROR_MESSAGE] = f"Reg Fail: {error_msg}"
            return False
        elif register_response.get(KEY_STATUS_CODE) == 201:
            st.success("Registered! Auto-logging in...")
            logger.info(f"Reg ok {email}.")
            # Attempt Auto-Login
            auth_data = {"username": email, "password": password}
            token_response = call_forest_api(
                "/auth/token",
                method="POST",
                data=auth_data,
                backend_url=backend_url,
<<<<<<< HEAD
                api_token=None
            )

            if token_response.get(KEY_ERROR) or not isinstance(token_response.get(KEY_DATA), dict) or not token_response.get(KEY_DATA,{}).get(KEY_ACCESS_TOKEN):
                auto_login_error = token_response.get(KEY_ERROR, "Token fetch fail")
                logger.error(f"Auto-login fail {email}: {auto_login_error}")
                st.warning(f"Reg ok, auto-login fail ({auto_login_error}). Log in manually.")
                return False # Indicate auto-login failure, user needs manual login
            else:
                 # Delegate processing to the success handler
                return _handle_login_success(token_response.get(KEY_DATA, {}), backend_url)
=======
                api_token=None,
            )

            if (
                token_response.get(KEY_ERROR)
                or not isinstance(token_response.get(KEY_DATA), dict)
                or not token_response.get(KEY_DATA, {}).get(KEY_ACCESS_TOKEN)
            ):
                auto_login_error = token_response.get(KEY_ERROR, "Token fetch fail")
                logger.error(f"Auto-login fail {email}: {auto_login_error}")
                st.warning(
                    f"Reg ok, auto-login fail ({auto_login_error}). Log in manually."
                )
                return False  # Indicate auto-login failure, user needs manual login
            else:
                # Delegate processing to the success handler
                return _handle_login_success(
                    token_response.get(KEY_DATA, {}), backend_url
                )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        else:
            status_code = register_response.get(KEY_STATUS_CODE, "N/A")
            logger.error(f"Reg fail {email}: Status {status_code}")
            st.error(f"Reg fail (Status: {status_code}).")
            st.session_state[KEY_ERROR_MESSAGE] = f"Reg Fail: Status {status_code}"
            return False


def _handle_logout():
    """Clears session state upon logout."""
<<<<<<< HEAD
    user_email = st.session_state.get("user_info", {}).get(KEY_USER_INFO_EMAIL, "Unknown user")
    logger.info(f"User {user_email} logging out.")
    keys_to_clear = [
        "authenticated", "token", "user_info", KEY_MESSAGES, KEY_CURRENT_TASK, KEY_ONBOARDING_STATUS,
        "snapshots", KEY_ERROR_MESSAGE, KEY_HTA_STATE, KEY_PENDING_CONFIRMATION, KEY_MILESTONES
=======
    user_email = st.session_state.get("user_info", {}).get(
        KEY_USER_INFO_EMAIL, "Unknown user"
    )
    logger.info(f"User {user_email} logging out.")
    keys_to_clear = [
        "authenticated",
        "token",
        "user_info",
        KEY_MESSAGES,
        KEY_CURRENT_TASK,
        KEY_ONBOARDING_STATUS,
        "snapshots",
        KEY_ERROR_MESSAGE,
        KEY_HTA_STATE,
        KEY_PENDING_CONFIRMATION,
        KEY_MILESTONES,
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    st.success("Logged out.")


# --- Main Function to Display Auth UI ---

<<<<<<< HEAD
=======

>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
def display_auth_sidebar(backend_url: str) -> bool:
    """
    Displays the authentication UI (login/register or logged-in info) in the sidebar.

    Args:
        backend_url (str): The base URL for the backend API.

    Returns:
        bool: True if a state change occurred (login, logout, registration success), False otherwise.
              The caller (streamlit_app.py) should use this to trigger st.rerun().
    """
    st.header("Authentication")
<<<<<<< HEAD
    action_taken = False # Flag to indicate if rerun is needed
=======
    action_taken = False  # Flag to indicate if rerun is needed
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    if st.session_state.get("authenticated"):
        # --- Display User Info if Logged In ---
        user_info_safe = st.session_state.get("user_info", {})
        user_email = user_info_safe.get(KEY_USER_INFO_EMAIL, "User")
        user_id_display = user_info_safe.get(KEY_USER_INFO_ID, "N/A")
<<<<<<< HEAD
        onboarding_status_display = str(st.session_state.get(KEY_ONBOARDING_STATUS, "Unknown")).replace('_', ' ').title()
=======
        onboarding_status_display = (
            str(st.session_state.get(KEY_ONBOARDING_STATUS, "Unknown"))
            .replace("_", " ")
            .title()
        )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

        st.write(f"Welcome, **{user_email}**!")
        st.caption(f"User ID: `{user_id_display}`")
        st.caption(f"Status: `{onboarding_status_display}`")

        # --- Logout Button ---
        if st.button("Logout"):
            _handle_logout()
<<<<<<< HEAD
            action_taken = True # Logout is a state change
=======
            action_taken = True  # Logout is a state change
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    else:
        # --- Show Login/Register Forms if Not Logged In ---
        login_tab, register_tab = st.tabs(["Login", "Register"])

        # --- Login Form ---
        with login_tab:
            with st.form("login_form"):
<<<<<<< HEAD
                login_email = st.text_input("Email", key="l_email", autocomplete="email")
                login_password = st.text_input("Password", type="password", key="l_pass", autocomplete="current-password")
                login_submitted = st.form_submit_button("Login")
                if login_submitted:
                    # Call handler, returns True on success
                    if _handle_login_submission(login_email, login_password, backend_url):
                        action_taken = True # Login success is a state change
=======
                login_email = st.text_input(
                    "Email", key="l_email", autocomplete="email"
                )
                login_password = st.text_input(
                    "Password",
                    type="password",
                    key="l_pass",
                    autocomplete="current-password",
                )
                login_submitted = st.form_submit_button("Login")
                if login_submitted:
                    # Call handler, returns True on success
                    if _handle_login_submission(
                        login_email, login_password, backend_url
                    ):
                        action_taken = True  # Login success is a state change
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

        # --- Registration Form ---
        with register_tab:
            with st.form("register_form"):
                reg_email = st.text_input("Email", key="r_email", autocomplete="email")
<<<<<<< HEAD
                reg_name = st.text_input("Name (Optional)", key="r_name", autocomplete="name")
                reg_password = st.text_input(f"Password (min {constants.MIN_PASSWORD_LENGTH})", type="password", key="r_pass", autocomplete="new-password")
                reg_submitted = st.form_submit_button("Register")
                if reg_submitted:
                    # Call handler, returns True on success (including auto-login)
                    if _handle_register_submission(reg_email, reg_name, reg_password, backend_url):
                        action_taken = True # Registration + auto-login success is a state change
=======
                reg_name = st.text_input(
                    "Name (Optional)", key="r_name", autocomplete="name"
                )
                reg_password = st.text_input(
                    f"Password (min {constants.MIN_PASSWORD_LENGTH})",
                    type="password",
                    key="r_pass",
                    autocomplete="new-password",
                )
                reg_submitted = st.form_submit_button("Register")
                if reg_submitted:
                    # Call handler, returns True on success (including auto-login)
                    if _handle_register_submission(
                        reg_email, reg_name, reg_password, backend_url
                    ):
                        action_taken = (
                            True  # Registration + auto-login success is a state change
                        )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    return action_taken
