"""
Root level redirector for Streamlit app deployment
This file simply imports the actual app from forest_app/front_end/streamlit_app.py
"""
# --- Robust Rotating Error Log Setup (MUST BE FIRST) ---
from forest_app.core.rotating_error_log import setup_rotating_error_log
setup_rotating_error_log()

# Import the actual Streamlit app
from forest_app.front_end.streamlit_app import *

# The imported app will run when this file is executed by Streamlit
