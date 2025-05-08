import os
import sys
import logging
import traceback
import importlib
from dotenv import load_dotenv

# Ensure page configuration is the first Streamlit command
import streamlit as st
st.set_page_config(page_title="Forest OS", layout="wide", initial_sidebar_state="expanded")

# Define log_exception function first
def log_exception(e):
    """Log detailed exception information"""
    logging.error(f"Exception occurred: {str(e)}")
    logging.error(traceback.format_exc())
    
    # Write to a separate error tracking file
    with open(os.path.join(os.getcwd(), 'error.log'), 'a') as f:
        f.write(f"\n{logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s').format(logging.LogRecord('__main__', logging.ERROR, '', 0, f'Fatal error in streamlit_app.py startup:', None, None))}\n")
        f.write(traceback.format_exc())
        f.write("\n")

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

# Log environment variable loading
logger.info(f"Loading environment from: {env_path}")

try:
    # Import core modules
    from forest_app.core.rotating_error_log import setup_rotating_error_log
    
    # Set up error logging
    setup_rotating_error_log()
    
    # Compatibility layer for query_params
    if not hasattr(st, 'query_params'):
        # For older Streamlit versions, create a compatible empty query_params attribute
        setattr(st, 'query_params', {})
    
    # Import required modules
    import json
    import uuid
    from datetime import datetime
    from typing import Dict, List, Union, Optional, Any, Callable
    from forest_app.front_end.auth_ui import display_auth_sidebar
    from forest_app.front_end.api_client import call_forest_api
    from forest_app.front_end.onboarding_ui import display_onboarding_input
    from forest_app.core.logging_tracking import setup_global_rotating_error_log, log_once_per_session

    # Set up global rotating error log for the Streamlit app
    setup_global_rotating_error_log()

    # Determine backend URL
    BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

    # Add detailed error logging
    def log_detailed_error(e):
        st.error(f"An error occurred: {str(e)}")
        st.error("Detailed Traceback:")
        st.code(traceback.format_exc())
        logger.error(f"Streamlit App Error: {str(e)}")
        logger.error(traceback.format_exc())
    
    # Log backend URL for debugging
    logger.info(f"Using Backend URL: {BACKEND_URL}")
    
    # Constants used within this module or imported from a central place
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

    class constants: # Standard values
        ONBOARDING_STATUS_NEEDS_GOAL = "needs_goal"
        ONBOARDING_STATUS_NEEDS_CONTEXT = "needs_context"
        ONBOARDING_STATUS_COMPLETED = "completed"
        MIN_PASSWORD_LENGTH = 8

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

    # Initialize session state
    initialize_session_state()

    # Create fetch HTA state function
    def fetch_hta_state():
        """Fetch HTA state from the backend API"""
        try:
            # Check if authenticated
            if not st.session_state.get("authenticated") or not st.session_state.get("token"):
                log_once_per_session('warning', "Not authenticated, cannot fetch HTA state")
                return {}
                
            # Make API call
            response = call_forest_api(
                endpoint="/hta/state",
                method="GET",
                backend_url=BACKEND_URL,
                api_token=st.session_state.get("token")
            )
            
            # Handle response
            if response.get(KEY_ERROR):
                log_once_per_session('error', f"Failed to fetch HTA state: {response.get(KEY_ERROR)}")
                return {}
            elif response.get(KEY_STATUS_CODE) == 200 and isinstance(response.get(KEY_DATA), dict):
                log_once_per_session('info', "Successfully fetched HTA state")
                # Store the HTA state in session state
                st.session_state[KEY_HTA_STATE] = response.get(KEY_DATA, {})
                return response.get(KEY_DATA, {})
            else:
                log_once_per_session('error', f"Unexpected response fetching HTA state: {response.get(KEY_STATUS_CODE)}")
                return {}
        except Exception as e:
            log_detailed_error(e)
            return {}

    # Main application logic
    def main():
        # Diagnostic information in sidebar
        with st.sidebar:
            st.title("Forest OS")
            st.write(f"Backend URL: {BACKEND_URL}")
            
            # Display auth sidebar (login/registration or user info)
            auth_changed = display_auth_sidebar(backend_url=BACKEND_URL)
            if auth_changed:
                # If auth state changed, rerun the app
                st.rerun()
        
        # Main content area
        try:
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
                    st.title("Forest OS")
                    
                    # Display chat history
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
