import streamlit as st
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
st.set_page_config(page_title="Forest OS", layout="wide")
st.title("🌳 Forest OS")

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
st.set_page_config(page_title="Forest OS", layout="wide")
st.title("🌳 Forest OS")

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

