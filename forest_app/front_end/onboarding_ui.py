# front_end/onboarding_ui.py
<<<<<<< HEAD
import streamlit as st
import logging
from typing import Dict, List, Union, Optional, Any, Callable
import json
=======
import logging
from typing import Callable, Optional

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

# --- Internal Handler Functions (modified from streamlit_app.py) ---

<<<<<<< HEAD
def _handle_set_goal(goal_text: str, backend_url: str) -> bool:
    """Handles goal submission during the 'needs_goal' onboarding phase. Returns True on success."""
    st.session_state[KEY_ERROR_MESSAGE] = None # Clear previous errors
    logger.info("Submitting goal during onboarding...")

    if not isinstance(st.session_state.get(KEY_MESSAGES), list): st.session_state[KEY_MESSAGES] = []
    st.session_state.messages.append({"role": "user", "content": goal_text})
    # Display immediately in the main app's chat history area (caller handles this)

    with st.chat_message("assistant"): # Show thinking message here
=======

def _handle_set_goal(goal_text: str, backend_url: str) -> bool:
    """Handles goal submission during the 'needs_goal' onboarding phase. Returns True on success."""
    st.session_state[KEY_ERROR_MESSAGE] = None  # Clear previous errors
    logger.info("Submitting goal during onboarding...")

    if not isinstance(st.session_state.get(KEY_MESSAGES), list):
        st.session_state[KEY_MESSAGES] = []
    st.session_state.messages.append({"role": "user", "content": goal_text})
    # Display immediately in the main app's chat history area (caller handles this)

    with st.chat_message("assistant"):  # Show thinking message here
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        message_placeholder = st.empty()
        message_placeholder.markdown("🎯 Setting your goal...")
        response = call_forest_api(
            "/onboarding/set_goal",
            method="POST",
            data={"goal_description": goal_text},
            backend_url=backend_url,
<<<<<<< HEAD
            api_token=st.session_state.get("token")
=======
            api_token=st.session_state.get("token"),
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        )

        if response.get(KEY_ERROR):
            error_msg = response.get(KEY_ERROR, "Unknown error")
            logger.error(f"API Fail set_goal: {error_msg}")
            message_placeholder.error(f"Error: {error_msg}")
            st.session_state[KEY_ERROR_MESSAGE] = f"API Error: {error_msg}"
<<<<<<< HEAD
            return False # Indicate failure
        elif response.get(KEY_STATUS_CODE) == 200:
            logger.info("Goal set via API.")
            resp_data = response.get(KEY_DATA, {})
            new_status = resp_data.get(KEY_ONBOARDING_STATUS, constants.ONBOARDING_STATUS_NEEDS_CONTEXT)
            st.session_state[KEY_ONBOARDING_STATUS] = new_status # Update state
            assistant_response = resp_data.get("message", "Goal set! Provide context?")
            message_placeholder.markdown(assistant_response) # Show response
            st.session_state.messages.append({"role": "assistant", "content": assistant_response}) # Add to history
            return True # Indicate success
=======
            return False  # Indicate failure
        elif response.get(KEY_STATUS_CODE) == 200:
            logger.info("Goal set via API.")
            resp_data = response.get(KEY_DATA, {})
            new_status = resp_data.get(
                KEY_ONBOARDING_STATUS, constants.ONBOARDING_STATUS_NEEDS_CONTEXT
            )
            st.session_state[KEY_ONBOARDING_STATUS] = new_status  # Update state
            assistant_response = resp_data.get("message", "Goal set! Provide context?")
            message_placeholder.markdown(assistant_response)  # Show response
            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_response}
            )  # Add to history
            return True  # Indicate success
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        else:
            status_code = response.get(KEY_STATUS_CODE, "N/A")
            logger.error(f"Unexpected status {status_code} set_goal.")
            message_placeholder.error(f"Unexpected error (Status: {status_code}).")
            st.session_state[KEY_ERROR_MESSAGE] = f"API Error: Status {status_code}"
<<<<<<< HEAD
            return False # Indicate failure


def _handle_add_context(context_text: str, backend_url: str, fetch_hta_state_func: Callable[[], None]) -> bool:
=======
            return False  # Indicate failure


def _handle_add_context(
    context_text: str, backend_url: str, fetch_hta_state_func: Callable[[], None]
) -> bool:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    """Handles context submission. Returns True on success."""
    st.session_state[KEY_ERROR_MESSAGE] = None
    logger.info("Submitting context during onboarding...")

<<<<<<< HEAD
    if not isinstance(st.session_state.get(KEY_MESSAGES), list): st.session_state[KEY_MESSAGES] = []
    st.session_state.messages.append({"role": "user", "content": context_text})
    # Display immediately in the main app's chat history area (caller handles this)

    with st.chat_message("assistant"): # Show thinking message here
=======
    if not isinstance(st.session_state.get(KEY_MESSAGES), list):
        st.session_state[KEY_MESSAGES] = []
    st.session_state.messages.append({"role": "user", "content": context_text})
    # Display immediately in the main app's chat history area (caller handles this)

    with st.chat_message("assistant"):  # Show thinking message here
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        message_placeholder = st.empty()
        message_placeholder.markdown("📝 Adding context...")
        response = call_forest_api(
            "/onboarding/add_context",
            method="POST",
            data={"context_reflection": context_text},
            backend_url=backend_url,
<<<<<<< HEAD
            api_token=st.session_state.get("token")
=======
            api_token=st.session_state.get("token"),
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        )

        if response.get(KEY_ERROR):
            error_msg = response.get(KEY_ERROR, "Unknown error")
            logger.error(f"API Fail add_context: {error_msg}")
            message_placeholder.error(f"Error: {error_msg}")
            st.session_state[KEY_ERROR_MESSAGE] = f"API Error: {error_msg}"
            return False
        elif response.get(KEY_STATUS_CODE) == 200:
            logger.info("Context added via API.")
            resp_data = response.get(KEY_DATA, {})
<<<<<<< HEAD
            new_status = resp_data.get(KEY_ONBOARDING_STATUS, constants.ONBOARDING_STATUS_COMPLETED)
            st.session_state[KEY_ONBOARDING_STATUS] = new_status # Update state
            assistant_response = resp_data.get("message", "Context added!")
            message_placeholder.markdown(assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
=======
            new_status = resp_data.get(
                KEY_ONBOARDING_STATUS, constants.ONBOARDING_STATUS_COMPLETED
            )
            st.session_state[KEY_ONBOARDING_STATUS] = new_status  # Update state
            assistant_response = resp_data.get("message", "Context added!")
            message_placeholder.markdown(assistant_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": assistant_response}
            )
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
            # --- Fetch HTA state using the passed function ---
            fetch_hta_state_func()
            # Update current task state
            new_task = resp_data.get("task", resp_data.get("first_task"))
<<<<<<< HEAD
            st.session_state[KEY_CURRENT_TASK] = new_task if isinstance(new_task, dict) else None
            return True # Indicate success
=======
            st.session_state[KEY_CURRENT_TASK] = (
                new_task if isinstance(new_task, dict) else None
            )
            return True  # Indicate success
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
        else:
            status_code = response.get(KEY_STATUS_CODE, "N/A")
            logger.error(f"Unexpected status {status_code} add_context.")
            message_placeholder.error(f"Unexpected error (Status: {status_code}).")
            st.session_state[KEY_ERROR_MESSAGE] = f"API Error: Status {status_code}"
            return False


# --- Main Function to Display Onboarding Input ---

<<<<<<< HEAD
def display_onboarding_input(current_status: Optional[str], backend_url: str, fetch_hta_state_func: Callable[[], None]) -> bool:
=======

def display_onboarding_input(
    current_status: Optional[str],
    backend_url: str,
    fetch_hta_state_func: Callable[[], None],
) -> bool:
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)
    """
    Displays the correct chat input and handles submission during onboarding.

    Args:
        current_status (Optional[str]): The user's current onboarding status.
        backend_url (str): The base URL for the backend API.
        fetch_hta_state_func (Callable): Function to call to refresh HTA state.

    Returns:
        bool: True if an onboarding action was successfully processed (requires rerun), False otherwise.
    """
    action_processed = False
<<<<<<< HEAD
    chat_disabled = st.session_state.get(KEY_PENDING_CONFIRMATION) is not None # Check if confirmation pending

    if current_status == constants.ONBOARDING_STATUS_NEEDS_GOAL:
        st.info("Let's start by defining your primary goal or intention for using Forest OS.")
        input_placeholder = "Enter your main goal here..."
        goal_prompt = st.chat_input(input_placeholder, key="goal_input", disabled=chat_disabled)
        if goal_prompt:
             # Display user message immediately (handled by main app loop)
             # Call handler
             if _handle_set_goal(goal_prompt, backend_url):
                 action_processed = True

    elif current_status == constants.ONBOARDING_STATUS_NEEDS_CONTEXT:
        st.info("Great! Now, provide some context about your goal. What's the background? What resources do you have? Any constraints?")
        input_placeholder = "Add context for your goal..."
        context_prompt = st.chat_input(input_placeholder, key="context_input", disabled=chat_disabled)
        if context_prompt:
             # Display user message immediately (handled by main app loop)
             # Call handler
             if _handle_add_context(context_prompt, backend_url, fetch_hta_state_func):
                 action_processed = True
=======
    chat_disabled = (
        st.session_state.get(KEY_PENDING_CONFIRMATION) is not None
    )  # Check if confirmation pending

    if current_status == constants.ONBOARDING_STATUS_NEEDS_GOAL:
        st.info(
            "Let's start by defining your primary goal or intention for using Forest OS."
        )
        input_placeholder = "Enter your main goal here..."
        goal_prompt = st.chat_input(
            input_placeholder, key="goal_input", disabled=chat_disabled
        )
        if goal_prompt:
            # Display user message immediately (handled by main app loop)
            # Call handler
            if _handle_set_goal(goal_prompt, backend_url):
                action_processed = True

    elif current_status == constants.ONBOARDING_STATUS_NEEDS_CONTEXT:
        st.info(
            "Great! Now, provide some context about your goal. What's the background? What resources do you have? Any constraints?"
        )
        input_placeholder = "Add context for your goal..."
        context_prompt = st.chat_input(
            input_placeholder, key="context_input", disabled=chat_disabled
        )
        if context_prompt:
            # Display user message immediately (handled by main app loop)
            # Call handler
            if _handle_add_context(context_prompt, backend_url, fetch_hta_state_func):
                action_processed = True
>>>>>>> cede20c (Fix Pylint critical errors: update BaseSettings import for Pydantic v1, ensure dependency_injector and uvicorn are installed)

    # Returns True if _handle_set_goal or _handle_add_context returned True
    return action_processed
