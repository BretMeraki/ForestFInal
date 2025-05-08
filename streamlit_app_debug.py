import streamlit as st
# Set page config must be the first Streamlit command
st.set_page_config(page_title="Forest OS", layout="wide")

import requests
import json
import uuid # Keep for potential fallback or local testing if needed
from datetime import datetime
import logging
from typing import Dict, List, Union, Optional, Any # Added Optional, Any
import graphviz # <<< ADD THIS IMPORT

# Assuming constants are defined in a backend config or a separate constants file
# This frontend version might define fallbacks or load them if needed.
# For now, we define them directly based on the provided code.
class constants: # Placeholder class if not importing from backend
    ONBOARDING_STATUS_NEEDS_GOAL = "needs_goal"
    ONBOARDING_STATUS_NEEDS_CONTEXT = "needs_context"
    ONBOARDING_STATUS_COMPLETED = "completed"
    MIN_PASSWORD_LENGTH = 8 # Example value, ensure it matches backend

# --- Configuration ---
# Use st.secrets for BACKEND_URL in production/sharing
BACKEND_URL = st.secrets.get("BACKEND_URL", "http://localhost:8000") # Default to localhost if secret not set
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# --- Constants (Mirroring backend if possible, or define defaults) ---
KEY_STATUS_CODE = "status_code"
KEY_ERROR = "error"
KEY_DETAIL = "detail"
KEY_DATA = "data"
KEY_ACCESS_TOKEN = "access_token"
KEY_ONBOARDING_STATUS = "onboarding_status"
KEY_USER_INFO_EMAIL = "email"
KEY_USER_INFO_ID = "id"
KEY_SNAPSHOT_ID = "id"
KEY_SNAPSHOT_UPDATED_AT = "updated_at"
KEY_SNAPSHOT_CODENAME = "codename"
KEY_MESSAGES = "messages"
KEY_CURRENT_TASK = "current_task" # Still used internally
KEY_HTA_STATE = "hta_state" # Used for visualization
KEY_PENDING_CONFIRMATION = "pending_confirmation"
KEY_MILESTONES = "milestones_achieved" # Still used internally
KEY_TASK_TITLE = "title"
KEY_TASK_DESC = "description"
KEY_TASK_MAGNITUDE_DESC = "magnitude_description"
KEY_TASK_INTRO_PROMPT = "introspective_prompt"
KEY_COMMAND_RESPONSE = "arbiter_response"
KEY_COMMAND_OFFERING = "offering"
KEY_COMMAND_MASTERY = "mastery_challenge"
KEY_ERROR_MESSAGE = "error_message" # Key for storing global error messages

# --- HTA Node Status Constants (Ensure these match backend HTA models) ---
STATUS_PENDING = "pending"
STATUS_ACTIVE = "active"
STATUS_COMPLETED = "completed"
STATUS_PRUNED = "pruned"
STATUS_BLOCKED = "blocked" # Example, check your actual statuses

# --- API Interaction Logic (More Robust) ---
def call_forest_api(endpoint: str, method: str = "POST", data: dict = None, params: dict = None) -> Dict[str, Any]:
    """
    Helper function to call the backend API. Returns a consistent dictionary format.

    Returns:
        Dict containing:
        {'status_code': int, 'data': Optional[Union[dict, list]], 'error': Optional[str]}
    """
    headers = {}
    api_token = st.session_state.get("token") # Safe get from session state
    if api_token:
        headers["Authorization"] = f"Bearer {api_token}"

    url = f"{BACKEND_URL}{endpoint}"
    response = None
    # Default return structure
    result = {"status_code": 500, KEY_DATA: None, KEY_ERROR: "Initialization error"}

    logger.debug(f"Calling API: {method} {url}")
    # (Logging payload remains similar, using safe gets)
    log_data_repr = "N/A"
    if data:
        is_token_endpoint = endpoint == "/auth/token" # Use correct path
        log_data = {k: v for k, v in data.items() if k != 'password'} if is_token_endpoint else data
        try: log_data_repr = json.dumps(log_data)
        except TypeError: log_data_repr = str(log_data)
        logger.debug(f"Payload ({'Form' if is_token_endpoint else 'JSON'}): {log_data_repr[:500]}{'...' if len(log_data_repr)>500 else ''}")
    if params: logger.debug(f"Params: {params}")

    try:
        if method.upper() == "POST":
            if endpoint == "/auth/token": # Use correct path
                response = requests.post(url, data=data, headers=headers, params=params, timeout=60)
            else:
                response = requests.post(url, json=data, headers=headers, params=params, timeout=60)
        elif method.upper() == "GET":
            response = requests.get(url, headers=headers, params=params, timeout=30)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers, params=params, timeout=30)
        else:
            logger.error(f"Unsupported HTTP method: {method}")
            result = {"status_code": 405, KEY_DATA: None, KEY_ERROR: f"Unsupported method: {method}"}
            return result # Return immediately for unsupported method

        # Store status code immediately
        result["status_code"] = response.status_code
        logger.debug(f"API Raw Response Status: {response.status_code}")

        # Check for non-success status codes first
        if not response.ok: # Checks for status_code < 400
            error_detail = f"HTTP Error {response.status_code}"
            try:
                error_json = response.json()
                # Use 'detail' from FastAPI error, fallback to generic error key, then text
                error_detail = error_json.get(KEY_DETAIL, error_json.get(KEY_ERROR, response.text or f"HTTP Error {response.status_code}"))
                logger.warning(f"HTTP Error {response.status_code} calling {url}. Detail: {error_detail}")
            except json.JSONDecodeError:
                error_detail = response.text or f"HTTP Error {response.status_code} (non-JSON body)"
                logger.warning(f"HTTP Error {response.status_code} calling {url}. Response Text: {error_detail[:500]}")
            result[KEY_ERROR] = str(error_detail) # Ensure error is string
            return result # Return immediately on HTTP error

        # --- Handle Success Cases (2xx) ---
        if response.status_code == 204: # No Content
            logger.debug("API Response: 204 No Content")
            result[KEY_DATA] = None # Explicitly set data to None
            result[KEY_ERROR] = None
        elif not response.content: # Other 2xx with empty body
             logger.warning(f"API Response {response.status_code} with empty body for {url}")
             result[KEY_DATA] = None # Explicitly set data to None
             result[KEY_ERROR] = None
        else: # 2xx with content - attempt JSON parse
            try:
                # Handle potential list response for snapshot list
                response_json = response.json()
                if endpoint == "/snapshots/list" and isinstance(response_json, list):
                     result[KEY_DATA] = response_json # Store the list directly
                elif isinstance(response_json, dict):
                     result[KEY_DATA] = response_json # Store the dict
                else:
                     # Log unexpected format but treat as successful if parse worked
                     logger.warning(f"API Success Response ({response.status_code}) was JSON but not dict/list: {type(response_json)}")
                     result[KEY_DATA] = response_json # Store it anyway
                result[KEY_ERROR] = None
                logger.debug(f"API Success Response Data: {str(result[KEY_DATA])[:500]}{'...' if len(str(result[KEY_DATA]))>500 else ''}")
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON from SUCCESSFUL ({response.status_code}) response from {url}. Response text: {response.text[:500]}{'...' if len(response.text)>500 else ''}")
                result[KEY_DATA] = None
                result[KEY_ERROR] = "Failed to decode JSON response from server, although status was OK."
                # Keep the original success status code, but add the error message

    # --- Handle Network/Request Errors ---
    except requests.exceptions.ConnectionError as conn_err:
        logger.error(f"Connection Error calling {url}: {conn_err}")
        result = {"status_code": 503, KEY_DATA: None, KEY_ERROR: f"Connection error: Could not connect to backend."}
    except requests.exceptions.Timeout as timeout_err:
        logger.error(f"Timeout Error calling {url}: {timeout_err}")
        result = {"status_code": 504, KEY_DATA: None, KEY_ERROR: f"Timeout error: Backend request timed out."}
    except requests.exceptions.RequestException as req_err: # Catch other requests errors
        logger.error(f"Request Exception calling {url}: {req_err}")
        result = {"status_code": 500, KEY_DATA: None, KEY_ERROR: f"Request error: {req_err}"}
    except Exception as e: # Catch-all for unexpected issues
        logger.exception(f"Unexpected error in call_forest_api for {url}: {e}")
        result = {"status_code": 500, KEY_DATA: None, KEY_ERROR: f"An unexpected client-side error occurred: {type(e).__name__}"}

    return result

# --- HTA Fetching Helper ---
def fetch_hta_state():
    """Fetches HTA state, handles errors, updates session state."""
    logger.info("Attempting to fetch HTA state...")
    st.session_state[KEY_ERROR_MESSAGE] = None # Clear previous errors
    hta_response = call_forest_api("/hta/state", method="GET")

    status_code = hta_response.get(KEY_STATUS_CODE)
    error_msg = hta_response.get(KEY_ERROR)
    hta_data = hta_response.get(KEY_DATA)

    if error_msg:
        logger.error(f"Failed to fetch HTA state: {error_msg} (Status: {status_code})")
        st.session_state[KEY_ERROR_MESSAGE] = f"API Error fetching HTA: {error_msg}"
        st.session_state[KEY_HTA_STATE] = None
    elif status_code == 200:
        # Check if data is the expected HTA structure (dict with 'hta_tree')
        # The API seems to return {'hta_tree': {...}} or {'hta_tree': None}
        if isinstance(hta_data, dict) and 'hta_tree' in hta_data:
             hta_tree_content = hta_data.get('hta_tree')
             if isinstance(hta_tree_content, dict): # Check if the inner 'hta_tree' is a dict
                 st.session_state[KEY_HTA_STATE] = hta_tree_content # Store the tree itself
                 logger.info("Successfully fetched and stored HTA state.")
             elif hta_tree_content is None:
                 st.session_state[KEY_HTA_STATE] = None
                 logger.info("Backend indicated no HTA state currently exists (hta_tree is None).")
             else: # hta_tree is not a dict or None
                 logger.warning(f"Fetched HTA state endpoint (200 OK), but 'hta_tree' key has unexpected type: {type(hta_tree_content)}")
                 st.session_state[KEY_HTA_STATE] = None
        else: # Response data is not a dict or missing 'hta_tree' key
            logger.warning(f"Fetched HTA state endpoint (200 OK), but received unexpected data structure: {type(hta_data)}")
            st.session_state[KEY_HTA_STATE] = None
    elif status_code == 404:
        st.session_state[KEY_HTA_STATE] = None
        logger.info("Backend returned 404 for HTA state (No HTA exists yet).")
    else: # Unexpected status code without explicit error
        logger.error(f"Failed to fetch HTA state: Unexpected status {status_code}. Response: {str(hta_data)[:200]}")
        st.session_state[KEY_ERROR_MESSAGE] = f"Unexpected API status for HTA: {status_code}."
        st.session_state[KEY_HTA_STATE] = None


# --- HTA Visualization Helper (RE-IMPLEMENTED) ---

# Define colors for different statuses
STATUS_COLORS = {
    STATUS_PENDING: "#E0E0E0",    # Light Grey
    STATUS_ACTIVE: "#ADD8E6",     # Light Blue
    STATUS_COMPLETED: "#90EE90",  # Light Green
    STATUS_PRUNED: "#D3D3D3",     # Grey
    STATUS_BLOCKED: "#FFB6C1",   # Light Pink/Red
    "default": "#FFFFFF"          # White (fallback)
}

def build_hta_dot_string(node_data: Dict[str, Any], dot: graphviz.Digraph):
    """Recursively builds the DOT string for the Graphviz chart."""
    node_id = node_data.get("id")
    if not node_id:
        # logger.warning("Skipping node without ID in HTA data.") # Optional logging
        return

    node_title = node_data.get("title", "Untitled")
    node_status = node_data.get("status", STATUS_PENDING).lower() # Ensure lowercase for matching
    node_color = STATUS_COLORS.get(node_status, STATUS_COLORS["default"])

    # Add the node to the graph
    dot.node(
        str(node_id), # Ensure node ID is a string for Graphviz
        label=f"{node_title}\\n(Status: {node_status.capitalize()})",
        shape="box",
        style="filled",
        fillcolor=node_color
    )

    # Recursively add children and edges
    children = node_data.get("children", [])
    if isinstance(children, list):
        for child_data in children:
            if isinstance(child_data, dict):
                child_id = child_data.get("id")
                if child_id:
                    # Add edge from parent to child
                    dot.edge(str(node_id), str(child_id)) # Ensure IDs are strings
                    # Recurse for the child node
                    build_hta_dot_string(child_data, dot)

# --- Inside display_hta_visualization function (with st.write debugging) ---
def display_hta_visualization(hta_tree_data: Optional[Dict]):
    """Displays the HTA tree using Graphviz."""
    st.write("DEBUG: Entered display_hta_visualization function.") # <<< ADD st.write

    if not hta_tree_data or not isinstance(hta_tree_data.get('root'), dict):
        st.write(f"DEBUG: HTA data invalid or no root node found.") # <<< ADD st.write
        st.info("🌱 Your skill tree (HTA) is being cultivated...")
        return

    try:
        st.write("DEBUG: Initializing Graphviz Digraph...") # <<< ADD st.write
        dot = graphviz.Digraph(comment='HTA Tree')
        dot.attr(rankdir='TB')

        st.write("DEBUG: Building DOT string...") # <<< ADD st.write
        build_hta_dot_string(hta_tree_data['root'], dot)
        # Optionally print the dot source to the UI for debugging, might be long:
        # st.text_area("DEBUG: Generated DOT string", dot.source, height=200)

        st.write("DEBUG: Calling st.graphviz_chart...") # <<< ADD st.write
        st.graphviz_chart(dot)
        st.write("DEBUG: Successfully called st.graphviz_chart.") # <<< ADD st.write
        st.caption("Skill Tree Visualization...")

    except Exception as e:
        st.write(f"DEBUG: Exception occurred during HTA visualization rendering: {e}") # <<< ADD st.write
        logger.exception("Exception occurred during HTA visualization rendering!") # Keep logger too
        st.error(f"Error generating HTA visualization: {e}")


# --- Completion Confirmation Helper (Still needed for confirmation flow) ---
def handle_completion_confirmation():
    """Displays the UI for confirming goal completion safely."""
    pending_conf = st.session_state.get(KEY_PENDING_CONFIRMATION) # Safe get
    if not isinstance(pending_conf, dict): # Check if it's a dict
        return # Silently do nothing if no valid confirmation pending

    prompt_text = pending_conf.get("prompt", "Confirm completion?") # Safe get
    # --- Use 'hta_node_id' from confirmation details ---
    node_id_to_confirm = pending_conf.get("hta_node_id") # Safe get the HTA node ID

    if not node_id_to_confirm: # Check if node ID is missing
        st.error("Error: Confirmation prompt missing node identifier.")
        st.session_state[KEY_PENDING_CONFIRMATION] = None # Clear invalid state
        return

    st.info(f"**Confirmation Needed:** {prompt_text}")
    col_confirm, col_deny = st.columns(2)

    # --- Confirmation Button Logic ---
    with col_confirm:
        if st.button("✅ Yes, Mark Complete", key=f"confirm_yes_{node_id_to_confirm}"):
            st.session_state[KEY_ERROR_MESSAGE] = None
            # --- Call /core/complete_task endpoint ---
            confirm_endpoint = "/core/complete_task" # Endpoint path - Assuming /core prefix here too!
            payload = {"task_id": node_id_to_confirm, "success": True} # Use node_id as task_id, confirm success
            response = call_forest_api(confirm_endpoint, method="POST", data=payload)
            # --- End API call ---

            if response.get(KEY_ERROR):
                error_msg = response.get(KEY_ERROR, "Failed confirm")
                st.error(f"Confirmation Error: {error_msg}")
                st.session_state[KEY_ERROR_MESSAGE] = f"API Error: {error_msg}"
            # Check for success status (e.g., 200 OK)
            elif response.get(KEY_STATUS_CODE) == 200:
                st.success("Task completion confirmed!")
                st.session_state[KEY_PENDING_CONFIRMATION] = None # Clear state
                # Safely add messages/milestones from response data if provided
                resp_data = response.get(KEY_DATA, {})
                if isinstance(resp_data, dict):
                    # The /complete_task endpoint might return different keys
                    completion_message = resp_data.get("detail", "Task processed.") # Use 'detail'
                    if not isinstance(st.session_state.get(KEY_MESSAGES), list): st.session_state[KEY_MESSAGES] = []
                    st.session_state.messages.append({"role": "assistant", "content": completion_message})
                    # Check if the completion result contains mastery challenge
                    challenge_data = resp_data.get("result", {}).get("mastery_challenge")
                    if isinstance(challenge_data, dict):
                            challenge_content = challenge_data.get("challenge_content", "Consider your progress.")
                            if not isinstance(st.session_state.get(KEY_MESSAGES), list): st.session_state[KEY_MESSAGES] = []
                            st.session_state.messages.append({"role": "assistant", "content": f"✨ Mastery Challenge:\\n{challenge_content}"})
                            # Optionally add to milestones or handle differently
                            if not isinstance(st.session_state.get(KEY_MILESTONES), list): st.session_state[KEY_MILESTONES] = []
                            st.session_state.milestones_achieved.append(f"Mastery Challenge Issued: {challenge_data.get('challenge_type','Integration')}")

                fetch_hta_state() # Refresh HTA after completion
                st.rerun()
            else: # Unexpected success status or format
                st.error(f"Unexpected response during confirmation: Status {response.get(KEY_STATUS_CODE)}")
                st.session_state[KEY_ERROR_MESSAGE] = f"API Error: Unexpected confirmation status {response.get(KEY_STATUS_CODE)}"

    # --- Denial Button Logic ---
    with col_deny:
        if st.button("❌ No, Not Yet", key=f"confirm_no_{node_id_to_confirm}"):
            st.session_state[KEY_ERROR_MESSAGE] = None
            # --- Send update back, maybe just clear state and add message ---
            # Option 1: Call backend to explicitly deny (if needed)
            # confirm_endpoint = f"/core/complete_task" # Need correct endpoint path
            # payload = {"task_id": node_id_to_confirm, "success": False} # Send failure
            # response = call_forest_api(confirm_endpoint, method="POST", data=payload)
            # Handle response...

            # Option 2: Just clear frontend state and add message
            st.info("Okay, task not marked as complete yet.")
            st.session_state[KEY_PENDING_CONFIRMATION] = None # Clear state
            if not isinstance(st.session_state.get(KEY_MESSAGES), list): st.session_state[KEY_MESSAGES] = []
            st.session_state.messages.append({"role": "assistant", "content": "Okay, let me know when you're ready or if you want to reflect further."})
            st.rerun()


# --- Onboarding Handler Functions ---
def handle_set_goal(goal_text):
    """Handles goal submission safely."""
    st.session_state[KEY_ERROR_MESSAGE] = None
    logger.info("Submitting goal during onboarding...")
    # Ensure messages list exists and is a list
    if not isinstance(st.session_state.get(KEY_MESSAGES), list): st.session_state[KEY_MESSAGES] = []
    st.session_state.messages.append({"role": "user", "content": goal_text})
    with st.chat_message("user"): st.markdown(goal_text)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🎯 Setting your goal...")
        response = call_forest_api("/onboarding/set_goal", method="POST", data={"goal_description": goal_text})

        if response.get(KEY_ERROR):
            error_msg = response.get(KEY_ERROR, "Failed set goal")
            logger.error(f"Failed to set goal: {error_msg}")
            st.error(f"Error setting goal: {error_msg}")
            st.session_state[KEY_ERROR_MESSAGE] = f"API Error: {error_msg}"
            # Optionally remove user message on failure:
            # if st.session_state.messages[-1].get("role") == "user": st.session_state.messages.pop()
        elif response.get(KEY_STATUS_CODE) == 200:
            logger.info("Goal set successfully.")
            resp_data = response.get(KEY_DATA, {})
            # Safely get status and message
            new_status = resp_data.get(KEY_ONBOARDING_STATUS, constants.ONBOARDING_STATUS_NEEDS_CONTEXT)
            st.session_state[KEY_ONBOARDING_STATUS] = new_status
            assistant_response = resp_data.get("message", "Goal set! Now add context.")
            message_placeholder.markdown(assistant_response)
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            st.rerun()
        else: # Unexpected status
            logger.error(f"Unexpected status setting goal: {response.get(KEY_STATUS_CODE)}")
            st.error(f"Unexpected error setting goal: Status {response.get(KEY_STATUS_CODE)}")
            st.session_state[KEY_ERROR_MESSAGE] = f"API Error: Unexpected status {response.get(KEY_STATUS_CODE)}"

def handle_add_context(context_text):
    """Handles context submission safely."""
    st.session_state[KEY_ERROR_MESSAGE] = None
    logger.info("Submitting context during onboarding...")
    if not isinstance(st.session_state.get(KEY_MESSAGES), list): st.session_state[KEY_MESSAGES] = []
    st.session_state.messages.append({"role": "user", "content": context_text})
    with st.chat_message("user"): st.markdown(context_text)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("📝 Adding context and generating plan...")
        response = call_forest_api("/onboarding/add_context", method="POST", data={"context_reflection": context_text})

        if response.get(KEY_ERROR):
             error_msg = response.get(KEY_ERROR, "Failed add context")
             logger.error(f"Failed to add context: {error_msg}")
             st.error(f"Error adding context: {error_msg}")
             st.session_state[KEY_ERROR_MESSAGE] = f"API Error: {error_msg}"
        elif response.get(KEY_STATUS_CODE) == 200:
             logger.info("Context added successfully.")
             resp_data = response.get(KEY_DATA, {})
             # Safely get status, message, task
             new_status = resp_data.get(KEY_ONBOARDING_STATUS, constants.ONBOARDING_STATUS_COMPLETED)
             st.session_state[KEY_ONBOARDING_STATUS] = new_status
             assistant_response = resp_data.get("message", "Context added! Let's begin.")
             message_placeholder.markdown(assistant_response)
             st.session_state.messages.append({"role": "assistant", "content": assistant_response})

             fetch_hta_state() # Fetch HTA after onboarding completes

             # The first_task might be part of the onboarding response or need separate fetch/logic
             new_task = resp_data.get("task", resp_data.get("first_task")) # Check both keys
             st.session_state[KEY_CURRENT_TASK] = new_task if isinstance(new_task, dict) else None # Store only if dict

             st.rerun()
        else: # Unexpected status
             logger.error(f"Unexpected status adding context: {response.get(KEY_STATUS_CODE)}")
             st.error(f"Unexpected error adding context: Status {response.get(KEY_STATUS_CODE)}")
             st.session_state[KEY_ERROR_MESSAGE] = f"API Error: Unexpected status {response.get(KEY_STATUS_CODE)}"


# --- Streamlit App Layout ---
# Page config is already set at the top of the file

# --- Initialize Session State ---
# Use .setdefault for cleaner initialization
st.session_state.setdefault("authenticated", False)
st.session_state.setdefault("token", None)
st.session_state.setdefault("user_info", None)
st.session_state.setdefault(KEY_MESSAGES, [])
st.session_state.setdefault(KEY_CURRENT_TASK, None)
st.session_state.setdefault(KEY_ONBOARDING_STATUS, None)
st.session_state.setdefault("snapshots", []) # Holds list of snapshot dicts {id, updated_at, codename}
st.session_state.setdefault(KEY_ERROR_MESSAGE, None)
st.session_state.setdefault(KEY_HTA_STATE, None) # Holds the HTA tree structure dict (the root node)
st.session_state.setdefault(KEY_PENDING_CONFIRMATION, None) # Holds dict: {'prompt':..., 'hta_node_id':...}
st.session_state.setdefault(KEY_MILESTONES, [])

# Main app title
st.title("🌳 Forest OS")

# --- Authentication UI (Sidebar) ---
with st.sidebar:
    st.header("Authentication")
    if st.session_state.get("authenticated"):
        user_info_safe = st.session_state.get("user_info", {}) # Default to empty dict
        user_email = user_info_safe.get(KEY_USER_INFO_EMAIL, "User") # Safe get
        user_id_display = user_info_safe.get(KEY_USER_INFO_ID, "N/A")
        onboarding_status_display = st.session_state.get(KEY_ONBOARDING_STATUS, "Unknown")

        st.write(f"Welcome, {user_email}!")
        st.caption(f"User ID: {user_id_display}")
        st.caption(f"Onboarding Status: {onboarding_status_display}")

        if st.button("Logout"):
            # Clear all session state keys related to the user session
            keys_to_clear = [
                "authenticated", "token", "user_info", KEY_MESSAGES,
                KEY_CURRENT_TASK, KEY_ONBOARDING_STATUS, "snapshots",
                KEY_ERROR_MESSAGE, KEY_HTA_STATE, KEY_PENDING_CONFIRMATION,
                KEY_MILESTONES
            ]
            for key in keys_to_clear:
                if key in st.session_state: del st.session_state[key]
            st.success("Logged out."); st.rerun()
    else: # Login/Register Forms
        login_tab, register_tab = st.tabs(["Login", "Register"])
        with login_tab:
            with st.form("login_form"):
                login_email = st.text_input("Email (Username)", key="login_email_input")
                login_password = st.text_input("Password", type="password", key="login_password_input")
                login_submitted = st.form_submit_button("Login")
                if login_submitted:
                    st.session_state[KEY_ERROR_MESSAGE] = None
                    if not login_email or not login_password: st.error("Enter email and password.")
                    else:
                        auth_data = {"username": login_email, "password": login_password}
                        token_response = call_forest_api("/auth/token", method="POST", data=auth_data)

                        if token_response.get(KEY_ERROR):
                            st.error(f"Login Failed: {token_response.get(KEY_ERROR)}")
                            st.session_state[KEY_ERROR_MESSAGE] = f"Login Failed: {token_response.get(KEY_ERROR)}"
                        elif token_response.get(KEY_STATUS_CODE) == 200 and isinstance(token_response.get(KEY_DATA), dict):
                            token_data = token_response.get(KEY_DATA, {})
                            access_token = token_data.get(KEY_ACCESS_TOKEN)
                            if access_token:
                                st.session_state.token = access_token
                                logger.info("Login successful - token received.")
                                # Get User Details
                                user_details_response = call_forest_api("/users/me", method="GET")
                                if user_details_response.get(KEY_ERROR):
                                    error_msg = user_details_response.get(KEY_ERROR, "Unknown user fetch error")
                                    logger.error(f"Login ok, but failed fetch user details: {error_msg}")
                                    st.error(f"Login ok, but failed fetch user details: {error_msg}. Try again.")
                                    # Clear potentially partial login state
                                    st.session_state.authenticated = False; st.session_state.token = None; st.session_state.user_info = None; st.session_state.onboarding_status = None
                                elif user_details_response.get(KEY_STATUS_CODE) == 200 and isinstance(user_details_response.get(KEY_DATA), dict):
                                    user_data = user_details_response.get(KEY_DATA, {})
                                    st.session_state.user_info = user_data # Store full user data if needed
                                    # Safely get onboarding status
                                    user_onboarding_status = user_data.get(KEY_ONBOARDING_STATUS)
                                    valid_statuses = [constants.ONBOARDING_STATUS_NEEDS_GOAL, constants.ONBOARDING_STATUS_NEEDS_CONTEXT, constants.ONBOARDING_STATUS_COMPLETED]
                                    # Assign status or default to completed if invalid/missing
                                    st.session_state[KEY_ONBOARDING_STATUS] = user_onboarding_status if user_onboarding_status in valid_statuses else constants.ONBOARDING_STATUS_COMPLETED
                                    logger.info(f"User details fetched. Onboarding status: {st.session_state[KEY_ONBOARDING_STATUS]}")
                                    # Reset state (using setdefault ensures keys exist from init)
                                    st.session_state[KEY_MESSAGES] = []
                                    st.session_state[KEY_CURRENT_TASK] = None
                                    st.session_state["snapshots"] = []
                                    st.session_state[KEY_ERROR_MESSAGE] = None
                                    st.session_state[KEY_HTA_STATE] = None
                                    st.session_state[KEY_PENDING_CONFIRMATION] = None
                                    st.session_state[KEY_MILESTONES] = []
                                    st.session_state.authenticated = True # Set last

                                    st.success("Login Successful!")
                                    # Fetch HTA only if onboarding is complete
                                    if st.session_state[KEY_ONBOARDING_STATUS] == constants.ONBOARDING_STATUS_COMPLETED:
                                        fetch_hta_state() # Fetch HTA state on successful login if onboarded
                                    st.rerun()
                                else: # Unexpected user details response
                                    st.error("Login succeeded, but received unexpected user data format.")
                                    # Clear state
                                    st.session_state.authenticated = False; st.session_state.token = None; st.session_state.user_info = None; st.session_state[KEY_ONBOARDING_STATUS] = None
                            else: # Token missing in successful response data
                                st.error("Login succeeded but token was not received.")
                                # Clear state
                                st.session_state.authenticated = False; st.session_state.token = None; st.session_state.user_info = None; st.session_state[KEY_ONBOARDING_STATUS] = None
                        else: # Unexpected token response status/format
                            st.error(f"Login failed: Unexpected response status {token_response.get(KEY_STATUS_CODE)}")
                            st.session_state[KEY_ERROR_MESSAGE] = f"Login Failed: Status {token_response.get(KEY_STATUS_CODE)}"

        with register_tab:
             with st.form("register_form"):
                 reg_email = st.text_input("Email", key="reg_email_input")
                 reg_name = st.text_input("Full Name (Optional)", key="reg_name_input")
                 reg_password = st.text_input(f"Password (min {constants.MIN_PASSWORD_LENGTH} chars)", type="password", key="reg_password_input")
                 reg_submitted = st.form_submit_button("Register")
                 if reg_submitted:
                     st.session_state[KEY_ERROR_MESSAGE] = None
                     if not reg_email or not reg_password: st.error("Provide email and password.")
                     elif len(reg_password) < constants.MIN_PASSWORD_LENGTH: st.error(f"Password must be at least {constants.MIN_PASSWORD_LENGTH} characters.")
                     else:
                         reg_data = {"email": reg_email, "password": reg_password, "full_name": reg_name or None}
                         register_response = call_forest_api("/auth/register", method="POST", data=reg_data)

                         if register_response.get(KEY_ERROR):
                             st.error(f"Registration Failed: {register_response.get(KEY_ERROR)}")
                             st.session_state[KEY_ERROR_MESSAGE] = f"Registration Failed: {register_response.get(KEY_ERROR)}"
                         elif register_response.get(KEY_STATUS_CODE) == 201: # Check for 201 Created
                             st.success("Registration successful! Logging you in...")
                             # --- Auto-Login (with similar robust checks as manual login) ---
                             auth_data = {"username": reg_email, "password": reg_password}
                             token_response = call_forest_api("/auth/token", method="POST", data=auth_data)
                             if token_response.get(KEY_ERROR) or not isinstance(token_response.get(KEY_DATA), dict) or not token_response.get(KEY_DATA,{}).get(KEY_ACCESS_TOKEN):
                                 st.error(f"Registered, but auto-login failed ({token_response.get(KEY_ERROR, 'Token Error')}). Please log in manually.")
                             else:
                                 st.session_state.token = token_response[KEY_DATA][KEY_ACCESS_TOKEN]
                                 user_details_response = call_forest_api("/users/me", method="GET")
                                 if user_details_response.get(KEY_ERROR) or not isinstance(user_details_response.get(KEY_DATA), dict):
                                     st.error(f"Registered, but auto-login failed (User Fetch Error: {user_details_response.get(KEY_ERROR, 'Unknown')}). Please log in manually.")
                                     st.session_state.token = None # Clear token if user fetch fails
                                 else:
                                     user_data = user_details_response[KEY_DATA]
                                     st.session_state.user_info = user_data
                                     # New user starts needing goal
                                     st.session_state[KEY_ONBOARDING_STATUS] = user_data.get(KEY_ONBOARDING_STATUS, constants.ONBOARDING_STATUS_NEEDS_GOAL)
                                     # Reset state
                                     st.session_state[KEY_MESSAGES] = []; st.session_state[KEY_CURRENT_TASK] = None; st.session_state["snapshots"] = []; st.session_state[KEY_ERROR_MESSAGE] = None; st.session_state[KEY_HTA_STATE] = None; st.session_state[KEY_PENDING_CONFIRMATION] = None; st.session_state[KEY_MILESTONES] = []
                                     st.session_state.authenticated = True
                                     st.success("Auto-login successful!")
                                     st.rerun()
                         else: # Unexpected registration status
                             st.error(f"Registration failed: Status {register_response.get(KEY_STATUS_CODE)}")
                             st.session_state[KEY_ERROR_MESSAGE] = f"Registration Failed: Status {register_response.get(KEY_STATUS_CODE)}"

    # --- Snapshot Management UI (Sidebar) ---
    st.divider()
    if st.session_state.get("authenticated"):
        st.header("Snapshots")
        if st.button("Refresh Snapshot List"):
            st.session_state[KEY_ERROR_MESSAGE] = None; st.session_state.snapshots = []
            response = call_forest_api("/snapshots/list", method="GET")

            # Check if the API call itself failed
            if response.get(KEY_ERROR):
                st.error(f"Failed to fetch snapshots: {response.get(KEY_ERROR)}")
                st.session_state[KEY_ERROR_MESSAGE] = f"API Error: {response.get(KEY_ERROR)}"
            # Check if the successful response contains a list (as expected for snapshots)
            elif response.get(KEY_STATUS_CODE) == 200 and isinstance(response.get(KEY_DATA), list):
                snapshot_list_data = response.get(KEY_DATA, [])
                # Further validate items in the list
                valid_snapshots = [item for item in snapshot_list_data if isinstance(item, dict) and KEY_SNAPSHOT_ID in item and KEY_SNAPSHOT_UPDATED_AT in item]
                try:
                    st.session_state.snapshots = sorted(valid_snapshots, key=lambda x: x[KEY_SNAPSHOT_UPDATED_AT], reverse=True)
                    if not st.session_state.snapshots and snapshot_list_data: # Original list had items, but none were valid
                        st.warning("Snapshot list format unexpected or items invalid.")
                    elif not snapshot_list_data: # Original list was empty
                        st.info("No snapshots found.")
                except Exception as sort_e:
                    logger.error("Snapshot sorting failed: %s", sort_e); st.session_state.snapshots = valid_snapshots # Keep unsorted if sorting fails
                    st.warning("Snapshots loaded but could not be sorted by date.")

            else: # Unexpected success status or format
                st.error(f"Failed snapshots: Status {response.get(KEY_STATUS_CODE)}, Format: {type(response.get(KEY_DATA))}")
                st.session_state[KEY_ERROR_MESSAGE] = f"Snapshot API Error: Status {response.get(KEY_STATUS_CODE)}"

        # Display/Load/Delete (uses safe gets internally now)
        if st.session_state.get("snapshots"):
            snapshot_options = {}
            for s in st.session_state.snapshots: # Assumes list of dicts
                snap_id = s.get(KEY_SNAPSHOT_ID)
                if not snap_id: continue # Skip if no ID
                codename = s.get(KEY_SNAPSHOT_CODENAME, 'Untitled'); dt_str = 'N/A'
                updated_at_raw = s.get(KEY_SNAPSHOT_UPDATED_AT)
                # Safer date parsing
                if updated_at_raw:
                    try:
                        dt_obj = datetime.fromisoformat(str(updated_at_raw).replace('Z', '+00:00'))
                        dt_str = dt_obj.strftime('%Y-%m-%d %H:%M UTC')
                    except Exception: pass # Ignore parsing errors, keep dt_str as 'N/A'
                display_key = f"'{codename}' ({dt_str}) - ID: {snap_id}"
                snapshot_options[display_key] = snap_id

            if snapshot_options:
                selected_snapshot_display = st.selectbox("Load or Delete Snapshot:", options=list(snapshot_options.keys()), key="snapshot_select")
                snapshot_id_selected = snapshot_options.get(selected_snapshot_display)

                col_load, col_delete = st.columns(2)
                with col_load: # Load Logic
                    if st.button("Load Selected", key="load_snapshot_btn"):
                        st.session_state[KEY_ERROR_MESSAGE] = None
                        if snapshot_id_selected:
                            load_payload = {"snapshot_id": snapshot_id_selected}
                            response = call_forest_api("/core/session/load", method="POST", data=load_payload) # Assuming this endpoint exists
                            if response.get(KEY_ERROR):
                                st.error(f"Failed load snapshot: {response.get(KEY_ERROR)}")
                                st.session_state[KEY_ERROR_MESSAGE] = f"API Error: {response.get(KEY_ERROR)}"
                            elif response.get(KEY_STATUS_CODE) == 200 and isinstance(response.get(KEY_DATA), dict):
                                load_data = response.get(KEY_DATA, {})
                                st.success(load_data.get("message", "Session loaded!"))
                                # Reset state safely after loading
                                if not isinstance(st.session_state.get(KEY_MESSAGES), list): st.session_state[KEY_MESSAGES] = []
                                st.session_state[KEY_MESSAGES] = load_data.get("history", []) if isinstance(load_data.get("history"), list) else []
                                st.session_state[KEY_CURRENT_TASK] = load_data.get(KEY_CURRENT_TASK) if isinstance(load_data.get(KEY_CURRENT_TASK), dict) else None
                                st.session_state[KEY_ERROR_MESSAGE] = None
                                st.session_state[KEY_ONBOARDING_STATUS] = constants.ONBOARDING_STATUS_COMPLETED # Assume loaded session is complete
                                st.session_state[KEY_HTA_STATE] = None # Clear HTA, needs refresh
                                st.session_state[KEY_PENDING_CONFIRMATION] = None
                                if not isinstance(st.session_state.get(KEY_MILESTONES), list): st.session_state[KEY_MILESTONES] = []
                                st.session_state[KEY_MILESTONES] = load_data.get(KEY_MILESTONES, []) if isinstance(load_data.get(KEY_MILESTONES), list) else []
                                fetch_hta_state() # Fetch HTA after loading
                                st.rerun()
                            else:
                                st.error(f"Failed load snapshot: Status {response.get(KEY_STATUS_CODE)}")
                                st.session_state[KEY_ERROR_MESSAGE] = f"Snapshot Load API Error: Status {response.get(KEY_STATUS_CODE)}"
                        else: st.warning("No snapshot selected.")

                with col_delete: # Delete Logic
                    if st.button("Delete Selected", type="primary", key="delete_snapshot_btn"):
                        st.session_state[KEY_ERROR_MESSAGE] = None
                        if snapshot_id_selected:
                            delete_endpoint = f"/snapshots/{snapshot_id_selected}"
                            response = call_forest_api(delete_endpoint, method="DELETE")
                            if response.get(KEY_ERROR):
                                st.error(f"Failed delete snapshot: {response.get(KEY_ERROR)}")
                                st.session_state[KEY_ERROR_MESSAGE] = f"API Error: {response.get(KEY_ERROR)}"
                            elif response.get(KEY_STATUS_CODE) in [200, 204]: # Allow OK or No Content
                                st.success("Snapshot deleted.")
                                # Remove from local list and rerun
                                if not isinstance(st.session_state.get("snapshots"), list): st.session_state.snapshots = []
                                st.session_state.snapshots = [s for s in st.session_state.snapshots if s.get(KEY_SNAPSHOT_ID) != snapshot_id_selected]
                                st.rerun()
                            else:
                                st.error(f"Failed delete snapshot: Status {response.get(KEY_STATUS_CODE)}")
                                st.session_state[KEY_ERROR_MESSAGE] = f"Snapshot Delete API Error: Status {response.get(KEY_STATUS_CODE)}"
                        else: st.warning("No snapshot selected.")

    # Display global errors
    global_error = st.session_state.get(KEY_ERROR_MESSAGE)
    if global_error: st.sidebar.error(global_error)

# --- Main Area ---
if not st.session_state.get("authenticated"):
    st.warning("Please log in or register using the sidebar.")
else:
    # --- Check/Fetch User Status if missing ---
    if st.session_state.get(KEY_ONBOARDING_STATUS) is None and st.session_state.get("token"):
         logger.warning("Onboarding status missing, refreshing...")
         user_details_response = call_forest_api("/users/me", method="GET")
         if user_details_response.get(KEY_ERROR) or not isinstance(user_details_response.get(KEY_DATA), dict):
             logger.error("Failed refresh user status.")
             st.error("Could not retrieve status. Try logging out/in.")
             st.session_state[KEY_ONBOARDING_STATUS] = "error"
         else:
             user_data = user_details_response[KEY_DATA]
             st.session_state.user_info = user_data # Update user info too
             user_onboarding_status = user_data.get(KEY_ONBOARDING_STATUS)
             valid_statuses = [constants.ONBOARDING_STATUS_NEEDS_GOAL, constants.ONBOARDING_STATUS_NEEDS_CONTEXT, constants.ONBOARDING_STATUS_COMPLETED]
             if user_onboarding_status in valid_statuses:
                 st.session_state[KEY_ONBOARDING_STATUS] = user_onboarding_status
                 logger.info(f"Refreshed onboarding status: {st.session_state[KEY_ONBOARDING_STATUS]}")
                 if st.session_state[KEY_ONBOARDING_STATUS] == constants.ONBOARDING_STATUS_COMPLETED and not st.session_state.get(KEY_HTA_STATE):
                     fetch_hta_state()
                 st.rerun()
             else:
                 logger.error(f"Refreshed, but status invalid: {user_onboarding_status}")
                 st.error("Invalid status received. Try logging out/in.")
                 st.session_state[KEY_ONBOARDING_STATUS] = "error"

    # --- HTA Visualization Section (RE-ADDED with st.write debugging) ---
    st.divider()
    hta_viz_enabled = True # Defaulting to True

    onboarding_status = st.session_state.get(KEY_ONBOARDING_STATUS)
    st.write(f"DEBUG: Checking HTA viz conditions: Onboarding='{onboarding_status}', FlagEnabled={hta_viz_enabled}") # <<< ADDED st.write

    if onboarding_status == constants.ONBOARDING_STATUS_COMPLETED and hta_viz_enabled:
        st.header("Skill Tree (HTA)")
        if st.button("🔄 Refresh Skill Tree"):
             fetch_hta_state()
             st.rerun()

        hta_data_to_display = st.session_state.get(KEY_HTA_STATE)
        st.write(f"DEBUG: Attempting to display HTA. Data type: {type(hta_data_to_display)}") # <<< ADDED st.write
        if isinstance(hta_data_to_display, dict):
            st.write(f"DEBUG: HTA Data Keys: {list(hta_data_to_display.keys())}") # <<< ADDED st.write
        else:
             st.write("DEBUG: HTA data is not a dictionary or is None.") # <<< ADDED st.write


        # Call the display function
        display_hta_visualization(hta_data_to_display)

    elif not hta_viz_enabled:
        st.info("HTA Visualization feature is currently disabled.")
    else:
        # Only show this if not explicitly disabled and onboarding not complete
        if hta_viz_enabled:
            st.info("Complete onboarding to view your Skill Tree.")
    # --- END HTA Visualization Section ---

    # --- Chat History and Input Section ---
    st.divider() # Add divider before chat
    st.header("Conversation") # Changed header
    
    # Display messages safely
    messages_list = st.session_state.get(KEY_MESSAGES, [])
    if isinstance(messages_list, list):
        for message in messages_list:
            if isinstance(message, dict): # Ensure message is dict
                with st.chat_message(message.get("role", "assistant")):
                    # Ensure content is string before display
                    content = message.get("content", "*...*")
                    st.markdown(str(content))
            else: logger.warning("Skipping non-dict item in messages list.")

    # --- Handle Pending Confirmation (Still needed if backend sends it) ---
    handle_completion_confirmation() # Now uses safe gets internally

    # --- Input Handling (Onboarding or Main Chat) ---
    current_status = st.session_state.get(KEY_ONBOARDING_STATUS)
    # Disable chat input if a confirmation is pending
    chat_disabled = st.session_state.get(KEY_PENDING_CONFIRMATION) is not None

    if current_status == constants.ONBOARDING_STATUS_NEEDS_GOAL:
        st.info("Define your primary goal or intention.")
        goal_prompt = st.chat_input("Main goal?", key="goal_input", disabled=chat_disabled)
        if goal_prompt: handle_set_goal(goal_prompt)
    elif current_status == constants.ONBOARDING_STATUS_NEEDS_CONTEXT:
        st.info("Provide context for your goal.")
        context_prompt = st.chat_input("Context?", key="context_input", disabled=chat_disabled)
        if context_prompt: handle_add_context(context_prompt)
    elif current_status == constants.ONBOARDING_STATUS_COMPLETED:
        # --- Standard Chat input ---
        if prompt := st.chat_input("Enter reflection, command, or next action...", disabled=chat_disabled, key="main_chat_input"):
            st.session_state[KEY_ERROR_MESSAGE] = None
            # Ensure messages list exists before appending
            if not isinstance(st.session_state.get(KEY_MESSAGES), list): st.session_state[KEY_MESSAGES] = []
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                message_placeholder.markdown("🌳 Thinking...")

                # --- Call /core/command endpoint (FIXED PATH) ---
                api_endpoint = "/core/command" # <<< FIXED PATH
                payload = {"command": prompt}
                response = call_forest_api(api_endpoint, method="POST", data=payload)
                # --- END API call ---

                # --- Process response safely ---
                assistant_response_content = ""
                # new_task_data = None # We don't display it separately anymore
                action_required = None
                confirmation_details = None
                milestone_feedback = None # Still capture for logging/state if needed

                if response.get(KEY_ERROR):
                    error_msg = response.get(KEY_ERROR, "Command failed")
                    logger.warning(f"Error from {api_endpoint}: {error_msg}") # Use correct endpoint in log
                    assistant_response_content = f"Error: {error_msg}"
                    if response.get(KEY_STATUS_CODE) == 403: # Handle potential desync
                        assistant_response_content = f"Status Error: {error_msg}. Refreshing..."
                        st.session_state[KEY_ONBOARDING_STATUS] = None # Trigger refresh
                    st.session_state[KEY_ERROR_MESSAGE] = assistant_response_content # Show error
                elif response.get(KEY_STATUS_CODE) in [200, 201] and isinstance(response.get(KEY_DATA), dict):
                    resp_data = response.get(KEY_DATA, {})
                    # Safely extract all potential keys
                    # Main response content is the narrative
                    assistant_response_content = resp_data.get(KEY_COMMAND_RESPONSE, resp_data.get("message", ""))
                    # Store next task internally if provided, but don't display separately
                    new_task_data = resp_data.get(KEY_CURRENT_TASK)
                    st.session_state[KEY_CURRENT_TASK] = new_task_data if isinstance(new_task_data, dict) else None

                    action_required = resp_data.get("action_required") # e.g., "confirm_completion"
                    confirmation_details = resp_data.get("confirmation_details")
                    milestone_feedback = resp_data.get("milestone_feedback") # Store internally if needed

                    # Store milestone achievement internally, but don't display separately
                    if milestone_feedback:
                        if not isinstance(st.session_state.get(KEY_MILESTONES), list): st.session_state[KEY_MILESTONES] = []
                        st.session_state.milestones_achieved.append(milestone_feedback)
                        # st.success(f"🎉 Milestone: {milestone_feedback}") # Don't show this popup

                    if action_required == "confirm_completion" and isinstance(confirmation_details, dict):
                        st.session_state[KEY_PENDING_CONFIRMATION] = confirmation_details
                        # Use the prompt from confirmation details if available
                        assistant_response_content = assistant_response_content or confirmation_details.get("prompt", "Confirm?")
                    else:
                        # Clear any stale confirmation if action is different
                        st.session_state[KEY_PENDING_CONFIRMATION] = None

                    if not assistant_response_content: assistant_response_content = "Okay, processed."

                    # Refresh HTA internally if a milestone was hit or task possibly changed
                    if milestone_feedback or new_task_data:
                         fetch_hta_state()

                else: # Unexpected success status or format
                    logger.error(f"Unexpected response from {api_endpoint}: Status {response.get(KEY_STATUS_CODE)}, Type: {type(response.get(KEY_DATA))}") # Use correct endpoint
                    assistant_response_content = f"Received unexpected response from server."
                    st.session_state[KEY_ERROR_MESSAGE] = assistant_response_content

                # Update UI
                message_placeholder.markdown(assistant_response_content)
                if assistant_response_content:
                    # Ensure messages list exists
                    if not isinstance(st.session_state.get(KEY_MESSAGES), list): st.session_state[KEY_MESSAGES] = []
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response_content})

                st.rerun() # Rerun to display new messages and handle confirmations

    elif current_status is None: st.info("Checking status...")
    elif current_status == "error": st.error("Issue determining status. Try logging out/in.")
    else: st.warning(f"Unknown status: '{current_status}'. Try logging out/in.")
