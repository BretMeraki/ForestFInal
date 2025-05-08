"""Forest OS - Main Streamlit Application

This is the main entry point for the Forest OS application.  
It handles authentication, user onboarding, and the main interaction interface.

The app supports both local and cloud deployment modes via the USE_CLOUD_MODE environment variable.
"""

import os
import sys
import json
import uuid
import logging
import traceback
import importlib
from datetime import datetime
from typing import Dict, List, Union, Optional, Any
from dotenv import load_dotenv

# Explicitly set project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Load environment variables
env_path = os.path.join(project_root, '.env.example') if not os.path.exists(os.path.join(project_root, '.env')) else os.path.join(project_root, '.env')
load_dotenv(env_path, override=True)

# Configure logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.getcwd(), 'error.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info(f"Loading environment from: {env_path}")

# Check deployment mode
use_cloud_mode = os.getenv("USE_CLOUD_MODE", "False").lower() in ["true", "1", "yes"]
logger.info(f"Deployment mode: {'Cloud' if use_cloud_mode else 'Local'}")

# Ensure page configuration is the first Streamlit command
import streamlit as st
import requests
import graphviz  # For HTA visualization

# Set page configuration
st.set_page_config(page_title="Forest OS", layout="wide", initial_sidebar_state="expanded")

# Define log_exception function
def log_exception(e):
    """Log detailed exception information"""
    logging.error(f"Exception occurred: {str(e)}")
    logging.error(traceback.format_exc())
    
    # Write to a separate error tracking file
    with open(os.path.join(os.getcwd(), 'error.log'), 'a') as f:
        f.write(f"\n{logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s').format(logging.LogRecord('__main__', logging.ERROR, '', 0, f'Fatal error in streamlit_app.py startup:', None, None))}\n")
        f.write(traceback.format_exc())
        f.write("\n")

# --- Constants ---
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
KEY_SNAPSHOT_ID = "id"
KEY_SNAPSHOT_UPDATED_AT = "updated_at"
KEY_SNAPSHOT_CODENAME = "codename"
KEY_TASK_TITLE = "title"
KEY_TASK_DESC = "description"
KEY_COMMAND_RESPONSE = "arbiter_response"
KEY_COMMAND_OFFERING = "offering"
KEY_COMMAND_MASTERY = "mastery_challenge"

# --- HTA Node Status Constants ---
STATUS_PENDING = "pending"
STATUS_ACTIVE = "active"
STATUS_COMPLETED = "completed"
STATUS_PRUNED = "pruned"
STATUS_BLOCKED = "blocked"

class constants:
    """Standard values used across the application"""
    ONBOARDING_STATUS_NEEDS_GOAL = "needs_goal"
    ONBOARDING_STATUS_NEEDS_CONTEXT = "needs_context"
    ONBOARDING_STATUS_COMPLETED = "completed"
    MIN_PASSWORD_LENGTH = 8

# Define status colors for HTA visualization
STATUS_COLORS = {
    STATUS_PENDING: "#E0E0E0",    # Light Grey
    STATUS_ACTIVE: "#ADD8E6",     # Light Blue
    STATUS_COMPLETED: "#90EE90",  # Light Green
    STATUS_PRUNED: "#D3D3D3",     # Grey
    STATUS_BLOCKED: "#FFB6C1",   # Light Pink/Red
    "default": "#FFFFFF"          # White (fallback)
}

# Determine backend URL
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')
logger.info(f"Using Backend URL: {BACKEND_URL}")

try:
    # Import core modules
    from forest_app.core.rotating_error_log import setup_rotating_error_log
    from forest_app.front_end.auth_ui import display_auth_sidebar
    from forest_app.front_end.onboarding_ui import display_onboarding_input
    from forest_app.core.logging_tracking import setup_global_rotating_error_log, log_once_per_session

    # Set up error logging
    setup_rotating_error_log()
    setup_global_rotating_error_log()
    
    # Compatibility layer for query_params
    if not hasattr(st, 'query_params'):
        # For older Streamlit versions, create a compatible empty query_params attribute
        setattr(st, 'query_params', {})

    # Add detailed error logging function
    def log_detailed_error(e):
        """Log detailed exception information and display to user"""
        st.error(f"An error occurred: {str(e)}")
        st.error("Detailed Traceback:")
        st.code(traceback.format_exc())
        logger.error(f"Streamlit App Error: {str(e)}")
        logger.error(traceback.format_exc())
        
    # --- API Interaction Logic ---
    def call_forest_api(endpoint: str, method: str = "POST", data: dict = None, params: dict = None,
                      backend_url: str = BACKEND_URL, api_token: str = None) -> Dict[str, Any]:
        """Enhanced API client function with better error handling and logging.
        
        Args:
            endpoint: API endpoint path (e.g., "/auth/login")
            method: HTTP method ("GET", "POST", "DELETE")
            data: Request payload
            params: URL parameters
            backend_url: Override backend URL
            api_token: Override api token from session state
            
        Returns:
            Dict containing:
            {'status_code': int, 'data': Optional[Union[dict, list]], 'error': Optional[str]}
        """
        # Set up headers with authentication if available
        headers = {}
        if api_token is None:
            api_token = st.session_state.get("token")
        if api_token:
            headers["Authorization"] = f"Bearer {api_token}"

        url = f"{backend_url}{endpoint}"
        response = None
        # Default return structure
        result = {"status_code": 500, KEY_DATA: None, KEY_ERROR: "Initialization error"}

        logger.debug(f"Calling API: {method} {url}")
        # Log payload without sensitive data
        log_data_repr = "N/A"
        if data:
            is_token_endpoint = endpoint == "/auth/token"
            log_data = {k: v for k, v in data.items() if k != 'password'} if is_token_endpoint else data
            try: 
                log_data_repr = json.dumps(log_data)
            except TypeError: 
                log_data_repr = str(log_data)
            logger.debug(f"Payload ({'Form' if is_token_endpoint else 'JSON'}): {log_data_repr[:500]}{'...' if len(log_data_repr)>500 else ''}")
        if params: 
            logger.debug(f"Params: {params}")

        try:
            if method.upper() == "POST":
                if endpoint == "/auth/token":
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
                return result

            # Store status code immediately
            result["status_code"] = response.status_code
            logger.debug(f"API Raw Response Status: {response.status_code}")

            # Handle non-success status codes
            if not response.ok:
                error_detail = f"HTTP Error {response.status_code}"
                try:
                    error_json = response.json()
                    error_detail = error_json.get(KEY_DETAIL, error_json.get(KEY_ERROR, response.text or error_detail))
                except json.JSONDecodeError:
                    error_detail = response.text or error_detail
                
                logger.warning(f"HTTP Error {response.status_code} calling {url}. Detail: {error_detail[:500]}")
                result[KEY_ERROR] = str(error_detail)
                return result

            # Handle success cases (2xx)
            if response.status_code == 204 or not response.content:
                logger.debug(f"API Response: {response.status_code} (No Content)")
                result[KEY_DATA] = None
                result[KEY_ERROR] = None
            else:
                try:
                    response_json = response.json()
                    result[KEY_DATA] = response_json
                    result[KEY_ERROR] = None
                    logger.debug(f"API Success Response Data: {str(result[KEY_DATA])[:500]}{'...' if len(str(result[KEY_DATA]))>500 else ''}")
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode JSON from successful response ({response.status_code}) from {url}")
                    result[KEY_DATA] = None
                    result[KEY_ERROR] = "Failed to decode JSON response from server"

        # Handle network/request errors
        except requests.exceptions.ConnectionError as conn_err:
            logger.error(f"Connection Error calling {url}: {conn_err}")
            result = {"status_code": 503, KEY_DATA: None, KEY_ERROR: f"Connection error: Could not connect to backend."}
        except requests.exceptions.Timeout as timeout_err:
            logger.error(f"Timeout Error calling {url}: {timeout_err}")
            result = {"status_code": 504, KEY_DATA: None, KEY_ERROR: f"Timeout error: Backend request timed out."}
        except requests.exceptions.RequestException as req_err:
            logger.error(f"Request Exception calling {url}: {req_err}")
            result = {"status_code": 500, KEY_DATA: None, KEY_ERROR: f"Request error: {req_err}"}
        except Exception as e:
            logger.exception(f"Unexpected error in call_forest_api for {url}: {e}")
            result = {"status_code": 500, KEY_DATA: None, KEY_ERROR: f"An unexpected client-side error occurred: {type(e).__name__}"}

        return result

    # --- Session State Management ---
    def initialize_session_state():
        """Initialize session state variables if not already set"""
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False
        if "user_info" not in st.session_state:
            st.session_state.user_info = None
        if "token" not in st.session_state:
            st.session_state.token = None
        if KEY_ONBOARDING_STATUS not in st.session_state:
            st.session_state[KEY_ONBOARDING_STATUS] = None
        if KEY_MESSAGES not in st.session_state:
            st.session_state[KEY_MESSAGES] = []
        if KEY_CURRENT_TASK not in st.session_state:
            st.session_state[KEY_CURRENT_TASK] = None
        if KEY_HTA_STATE not in st.session_state:
            st.session_state[KEY_HTA_STATE] = None
        if KEY_PENDING_CONFIRMATION not in st.session_state:
            st.session_state[KEY_PENDING_CONFIRMATION] = None
        if KEY_MILESTONES not in st.session_state:
            st.session_state[KEY_MILESTONES] = []
        if KEY_ERROR_MESSAGE not in st.session_state:
            st.session_state[KEY_ERROR_MESSAGE] = None
            
    # Initialize session state
    initialize_session_state()

    # --- HTA State Management ---
    def fetch_hta_state():
        """Fetches HTA state, handles errors, updates session state."""
        logger.info("Attempting to fetch HTA state...")
        st.session_state[KEY_ERROR_MESSAGE] = None # Clear previous errors
        
        # Check if authenticated
        if not st.session_state.get("authenticated") or not st.session_state.get("token"):
            log_once_per_session('warning', "Not authenticated, cannot fetch HTA state")
            return {}
            
        # Make API call
        hta_response = call_forest_api(
            endpoint="/hta/state", 
            method="GET",
            backend_url=BACKEND_URL,
            api_token=st.session_state.get("token")
        )

        status_code = hta_response.get(KEY_STATUS_CODE)
        error_msg = hta_response.get(KEY_ERROR)
        hta_data = hta_response.get(KEY_DATA)

        if error_msg:
            logger.error(f"Failed to fetch HTA state: {error_msg} (Status: {status_code})")
            st.session_state[KEY_ERROR_MESSAGE] = f"API Error fetching HTA: {error_msg}"
            st.session_state[KEY_HTA_STATE] = None
            return {}
        elif status_code == 200:
            # Check if data is the expected HTA structure (dict with 'hta_tree')
            if isinstance(hta_data, dict) and 'hta_tree' in hta_data:
                hta_tree_content = hta_data.get('hta_tree')
                if isinstance(hta_tree_content, dict): # Check if the inner 'hta_tree' is a dict
                    st.session_state[KEY_HTA_STATE] = hta_tree_content # Store the tree itself
                    logger.info("Successfully fetched and stored HTA state.")
                    return hta_tree_content
                elif hta_tree_content is None:
                    st.session_state[KEY_HTA_STATE] = None
                    logger.info("Backend indicated no HTA state currently exists (hta_tree is None).")
                    return {}
                else: # hta_tree is not a dict or None
                    logger.warning(f"Fetched HTA state endpoint (200 OK), but 'hta_tree' key has unexpected type: {type(hta_tree_content)}")
                    st.session_state[KEY_HTA_STATE] = None
                    return {}
            else: # Response data is not a dict or missing 'hta_tree' key
                logger.warning(f"Fetched HTA state endpoint (200 OK), but received unexpected data structure: {type(hta_data)}")
                st.session_state[KEY_HTA_STATE] = None
                return {}
        elif status_code == 404:
            st.session_state[KEY_HTA_STATE] = None
            logger.info("Backend returned 404 for HTA state (No HTA exists yet).")
            return {}
        else: # Unexpected status code without explicit error
            logger.error(f"Failed to fetch HTA state: Unexpected status {status_code}. Response: {str(hta_data)[:200]}")
            st.session_state[KEY_ERROR_MESSAGE] = f"Unexpected API status for HTA: {status_code}."
            st.session_state[KEY_HTA_STATE] = None
            return {}
            
    # --- HTA Visualization ---
    def build_hta_dot_string(node_data: Dict[str, Any], dot: graphviz.Digraph):
        """Recursively builds the DOT string for the Graphviz chart."""
        node_id = node_data.get("id")
        if not node_id:
            logger.warning("Skipping node without ID in HTA data.")
            return

        node_title = node_data.get("title", "Untitled")
        node_status = node_data.get("status", STATUS_PENDING).lower() # Ensure lowercase for matching
        node_color = STATUS_COLORS.get(node_status, STATUS_COLORS["default"])

        # Add the node to the graph
        dot.node(
            str(node_id), # Ensure node ID is a string for Graphviz
            label=f"{node_title}\n(Status: {node_status.capitalize()})",
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
                        
    def display_hta_visualization(hta_tree_data: Optional[Dict]):
        """Displays the HTA tree using Graphviz."""
        if not hta_tree_data:
            st.info("No HTA tree data available to visualize.")
            return
            
        try:
            # Create a new Digraph instance
            dot = graphviz.Digraph()
            dot.attr(rankdir="TB") # Top to Bottom layout
            
            # Build the graph recursively
            build_hta_dot_string(hta_tree_data, dot)
            
            # Render the graph in Streamlit
            st.graphviz_chart(dot, use_container_width=True)
            
        except Exception as e:
            st.error("Failed to render HTA visualization.")
            logger.error(f"Visualization error: {e}")
            st.exception(e)
            
    # --- Task Completion Confirmation Handler ---
    def handle_completion_confirmation():
        """Displays the UI for confirming goal completion."""
        # If no pending confirmation, just return
        pending_confirmation = st.session_state.get(KEY_PENDING_CONFIRMATION)
        if not pending_confirmation or not isinstance(pending_confirmation, dict):
            return
            
        # Extract task details from confirmation state
        node_id_to_confirm = pending_confirmation.get("id")
        task_title = pending_confirmation.get("title", "this task")
        task_desc = pending_confirmation.get("description", "")
        
        if not node_id_to_confirm:
            logger.error("Missing required task ID in pending confirmation")
            st.session_state[KEY_PENDING_CONFIRMATION] = None
            return

        # Display confirmation UI
        st.markdown("---")
        st.subheader("🎯 Confirm Task Completion", divider="rainbow")
        
        # Show task info
        st.markdown(f"**Task:** {task_title}")
        if task_desc:
            st.markdown(f"**Description:** {task_desc}")
        
        # Create confirmation buttons in columns
        col_confirm, col_deny = st.columns(2)
        
        # --- Confirmation Button Logic ---
        with col_confirm:
            if st.button("✅ Yes, Complete", key=f"confirm_yes_{node_id_to_confirm}", type="primary"):
                st.session_state[KEY_ERROR_MESSAGE] = None
                
                # Call backend to confirm completion
                confirm_endpoint = "/hta/complete_task"  # Adjust based on actual API endpoint
                payload = {"task_id": node_id_to_confirm}
                
                response = call_forest_api(confirm_endpoint, method="POST", data=payload)
                error_msg = response.get(KEY_ERROR)
                
                if error_msg:
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
                        if not isinstance(st.session_state.get(KEY_MESSAGES), list): 
                            st.session_state[KEY_MESSAGES] = []
                        st.session_state.messages.append({"role": "assistant", "content": completion_message})
                        
                        # Check if the completion result contains mastery challenge
                        challenge_data = resp_data.get("result", {}).get("mastery_challenge")
                        if isinstance(challenge_data, dict):
                                challenge_content = challenge_data.get("challenge_content", "Consider your progress.")
                                if not isinstance(st.session_state.get(KEY_MESSAGES), list): 
                                    st.session_state[KEY_MESSAGES] = []
                                st.session_state.messages.append({"role": "assistant", "content": f"✨ Mastery Challenge:\n{challenge_content}"})
                                
                                # Optionally add to milestones or handle differently
                                if not isinstance(st.session_state.get(KEY_MILESTONES), list): 
                                    st.session_state[KEY_MILESTONES] = []
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
                st.info("Okay, task not marked as complete yet.")
                st.session_state[KEY_PENDING_CONFIRMATION] = None # Clear state
                if not isinstance(st.session_state.get(KEY_MESSAGES), list): 
                    st.session_state[KEY_MESSAGES] = []
                st.session_state.messages.append({"role": "assistant", "content": "Okay, let me know when you're ready or if you want to reflect further."})
                st.rerun()

    # Main application logic
    def main():
        # Get deployment mode for UI display
        use_cloud_mode = os.getenv("USE_CLOUD_MODE", "False").lower() in ["true", "1", "yes"]
        deployment_mode = "Cloud" if use_cloud_mode else "Local"
        
        # Diagnostic information in sidebar
        with st.sidebar:
            # App title with mode indicator
            st.title("🌳 Forest OS")
            
            # Show deployment mode with visual indicator
            mode_color = "#4CAF50" if not use_cloud_mode else "#2196F3"  # Green for local, Blue for cloud
            st.markdown(f"<div style='display: flex; align-items: center;'>"
                      f"<div style='background-color: {mode_color}; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px;'></div>"
                      f"<div><b>Mode:</b> {deployment_mode}</div></div>", unsafe_allow_html=True)
            
            # Backend URL information
            st.caption(f"Backend URL: {BACKEND_URL}")
            
            # Clear separation
            st.markdown("---")
            
            # Display auth sidebar (login/registration or user info)
            auth_changed = display_auth_sidebar(backend_url=BACKEND_URL)
            if auth_changed:
                # If auth state changed, rerun the app
                st.rerun()
        
        # Main content area
        try:
            # Display any error messages
            if st.session_state.get(KEY_ERROR_MESSAGE):
                st.error(st.session_state[KEY_ERROR_MESSAGE])
            
            # Check if user is authenticated
            if st.session_state.get("authenticated"):
                # Get current onboarding status
                current_status = st.session_state.get(KEY_ONBOARDING_STATUS)
                
                if current_status in [constants.ONBOARDING_STATUS_NEEDS_GOAL, constants.ONBOARDING_STATUS_NEEDS_CONTEXT]:
                    # User needs to complete onboarding
                    st.title("Welcome to Forest OS - Let's Get Started")
                    
                    # Display onboarding input based on current status
                    onboarding_changed = display_onboarding_input(
                        current_status=current_status,
                        backend_url=BACKEND_URL,
                        fetch_hta_state_func=fetch_hta_state
                    )
                    
                    if onboarding_changed:
                        # If onboarding state changed, rerun the app
                        st.rerun()
                
                elif current_status == constants.ONBOARDING_STATUS_COMPLETED:
                    # User has completed onboarding, show main interface
                    st.title("🌳 Forest OS - Your Personal Growth System")
                    
                    # Handle pending task confirmation if present
                    if st.session_state.get(KEY_PENDING_CONFIRMATION):
                        handle_completion_confirmation()
                    
                    # Main dashboard with tabs
                    tab_hta, tab_journal, tab_settings = st.tabs(["HTA Tree", "Journal", "Settings"])
                    
                    # Tab 1: HTA Tree visualization
                    with tab_hta:
                        st.header("Hierarchical Task Analysis")
                        
                        # Create a "Refresh" button
                        col1, col2 = st.columns([9, 1])
                        with col2:
                            if st.button("↻ Refresh"):
                                fetch_hta_state()
                                st.rerun()
                        
                        # Show deployment mode indicator
                        use_cloud_mode = os.getenv("USE_CLOUD_MODE", "False").lower() in ["true", "1", "yes"]
                        col1.caption(f"Mode: {'☁️ Cloud' if use_cloud_mode else '🖥️ Local'}") 
                        
                        # Get HTA state from session state
                        hta_tree_data = st.session_state.get(KEY_HTA_STATE)
                        
                        if hta_tree_data:
                            # Display the tree visualization
                            display_hta_visualization(hta_tree_data)
                            
                            # Additional HTA statistics
                            active_count = 0
                            completed_count = 0
                            pending_count = 0
                            
                            # Simple recursive counter function
                            def count_status_types(node):
                                nonlocal active_count, completed_count, pending_count
                                if node.get("status") == STATUS_ACTIVE:
                                    active_count += 1
                                elif node.get("status") == STATUS_COMPLETED:
                                    completed_count += 1
                                elif node.get("status") == STATUS_PENDING:
                                    pending_count += 1
                                
                                for child in node.get("children", []):
                                    count_status_types(child)
                            
                            # Count status types
                            count_status_types(hta_tree_data)
                            
                            # Show statistics
                            stat_col1, stat_col2, stat_col3 = st.columns(3)
                            stat_col1.metric("Active Tasks", active_count, delta=None, delta_color="normal")
                            stat_col2.metric("Completed", completed_count, delta=None, delta_color="normal")
                            stat_col3.metric("Pending", pending_count, delta=None, delta_color="normal")
                        else:
                            # No HTA data available
                            st.info("No HTA tree data available yet. Start by setting your goal.")
                            # Option to refresh
                            if st.button("Refresh Data"):
                                fetch_hta_state()
                                st.rerun()
                    
                    # Tab 2: Journal & Messages
                    with tab_journal:
                        st.header("Your Journey")
                        
                        # Display messages
                        messages = st.session_state.get(KEY_MESSAGES, [])
                        if messages and isinstance(messages, list):
                            # Create a scrollable container for messages
                            message_container = st.container(height=400)
                            with message_container:
                                for msg in messages:
                                    role = msg.get("role", "system")
                                    content = msg.get("content", "")
                                    
                                    # Format based on role
                                    if role == "user":
                                        st.markdown(f"**You:** {content}")
                                    elif role == "assistant":
                                        st.markdown(f"**Forest:** {content}")
                                    else: # system or other
                                        st.markdown(f"*{content}*")
                        else:
                            st.info("No journal entries yet. Your progress will be shown here.")
                        
                        # Allow users to add notes
                        with st.expander("Add Personal Note"):
                            note_input = st.text_area("Your reflection or note:", key="note_input")
                            if st.button("Save Note"):
                                if note_input.strip():
                                    if not isinstance(st.session_state.get(KEY_MESSAGES), list):
                                        st.session_state[KEY_MESSAGES] = []
                                    st.session_state[KEY_MESSAGES].append({"role": "user", "content": note_input})
                                    st.success("Note saved!")
                                    st.rerun()
                                else:
                                    st.warning("Please enter a note before saving.")
                    
                    # Tab 3: Settings
                    with tab_settings:
                        st.header("Settings")
                        
                        # Display current deployment mode
                        st.subheader("Deployment Settings")
                        mode_text = "**Cloud Mode**" if use_cloud_mode else "**Local Mode**"
                        st.markdown(f"Current deployment mode: {mode_text}")
                        st.caption("To change the deployment mode, update the USE_CLOUD_MODE environment variable in your .env file.")
                        
                        # Database info
                        st.subheader("Database Configuration")
                        if use_cloud_mode:
                            st.info("Using Cloud SQL database configuration from environment variables.")
                            st.caption("Ensure DB_HOST, DB_USER, and DB_PASSWORD are properly configured in your cloud environment.")
                        else:
                            st.info("Using local PostgreSQL database configuration.")
                            st.caption("Configure local database settings with LOCAL_DB_* environment variables or use the default DB_CONNECTION_STRING.")
                        
                        # Advanced settings
                        with st.expander("Advanced Settings"):
                            st.warning("These settings are for debugging purposes only.")
                            if st.button("Clear Session State", key="clear_session"):
                                for key in list(st.session_state.keys()):
                                    del st.session_state[key]
                                st.success("Session state cleared. Refresh the page to re-initialize.")
                                st.rerun()
                    # Add any additional functionality here if needed
                    messages = st.session_state.get(KEY_MESSAGES, [])
                    for msg in messages:
                        with st.chat_message(msg.get("role")):
                            st.write(msg.get("content"))
                    
                    # Display chat input
                    user_input = st.chat_input("What would you like to do?", key="chat_input")
                    if user_input:
                        # Add user message to chat history
                        st.session_state.messages.append({"role": "user", "content": user_input})
                        with st.chat_message("user"):
                            st.write(user_input)
                        
                        # Process user input (placeholder)
                        with st.chat_message("assistant"):
                            message_placeholder = st.empty()
                            message_placeholder.markdown("Thinking...")
                            # FUTURE: Add actual processing logic here
                            message_placeholder.markdown(f"You said: {user_input}")
                            st.session_state.messages.append({"role": "assistant", "content": f"You said: {user_input}"})
                else:
                    # Unknown status or not set
                    st.warning("Unable to determine your onboarding status. Please contact support.")
            else:
                # User is not authenticated
                st.title("Welcome to Forest OS")
                st.write("Please log in or register to get started.")
                
                # Display a sample of what the app can do
                with st.expander("Why Forest OS?"):
                    st.write("""
                    Forest OS helps you organize your goals and tasks effectively, 
                    providing AI-powered assistance to boost your productivity.
                    """)
        
        except Exception as e:
            log_detailed_error(e)
            st.error("An error occurred while loading the application")

    # Run the main app
    main()

except Exception as e:
    log_exception(e)
    logging.error(f"Error loading application: {str(e)}")
    
    # Display the error in the streamlit UI
    st.error(f"Error loading application: {str(e)}")
    st.error("Please check the error log for more details.")
    
    # Show diagnostic information
    st.subheader("Diagnostic Information")
    st.write(f"Python Version: {sys.version}")
    st.write(f"Working Directory: {os.getcwd()}")
    
    # Display environment variables
    st.subheader("Environment Variables")
    critical_vars = ['BACKEND_URL', 'DATABASE_URL', 'SECRET_KEY']
    for var in critical_vars:
        value = os.getenv(var, 'NOT SET')
        # Mask sensitive information
        if var == 'SECRET_KEY' and value != 'NOT SET':
            value = value[:10] + '...' + value[-5:] if len(value) > 15 else '***'
        st.write(f"{var}: {value}")
