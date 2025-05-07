"""
Debug Dashboard - A standalone Streamlit app for monitoring errors in real-time.

This dashboard runs separately from your main app and monitors the error log,
providing a user-friendly interface to track, understand, and manage errors.
"""
import streamlit as st
import pandas as pd
import time
import os
import json
from datetime import datetime
from pathlib import Path

# Import local modules
from error_parser import parse_error_log, classify_error, get_human_explanation
from db_handler import ErrorDatabase
from log_watcher import LogWatcher

# Constants
ERROR_LOG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "error.log")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "error_db.json")
REFRESH_INTERVAL = 5  # seconds

# Page configuration
st.set_page_config(
    page_title="Forest App Debug Dashboard",
    page_icon="🐞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
db = ErrorDatabase(DB_PATH)

# Initialize session state
if 'filter_status' not in st.session_state:
    st.session_state.filter_status = "All"
if 'filter_severity' not in st.session_state:
    st.session_state.filter_severity = "All"
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = datetime.now()

# Dashboard Header
st.title("🐞 Forest App Debug Dashboard")
st.markdown("""
This dashboard provides real-time monitoring and analysis of errors and warnings 
from your Forest App. Track issues, get human-readable explanations, and mark them as fixed.
""")

# Sidebar filters
st.sidebar.header("Filters")

# Status filter
status_options = ["All", "New", "In Progress", "Fixed", "Ignored"]
selected_status = st.sidebar.selectbox("Status", status_options, key="status_filter")
st.session_state.filter_status = selected_status

# Severity filter
severity_options = ["All", "CRITICAL", "ERROR", "WARNING", "INFO"]
selected_severity = st.sidebar.selectbox("Severity", severity_options, key="severity_filter")
st.session_state.filter_severity = selected_severity

# Search box
search_query = st.sidebar.text_input("Search errors", key="search_box")
st.session_state.search_query = search_query

# Auto-refresh toggle
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=st.session_state.auto_refresh)
st.session_state.auto_refresh = auto_refresh

# Manual refresh button
if st.sidebar.button("Refresh Now"):
    st.session_state.last_refresh = datetime.now()
    st.experimental_rerun()

# Show last refresh time
st.sidebar.markdown(f"Last refresh: {st.session_state.last_refresh.strftime('%H:%M:%S')}")

# Stats section
st.sidebar.header("Stats")
stats = db.get_stats()
col1, col2 = st.sidebar.columns(2)
col1.metric("Total Errors", stats.get("total", 0))
col2.metric("Fixed", stats.get("fixed", 0))

col3, col4 = st.sidebar.columns(2)
col3.metric("New Today", stats.get("new_today", 0))
col4.metric("Critical", stats.get("critical", 0))

# Function to refresh the error data
def refresh_error_data():
    # Parse the error log file and get new entries
    new_errors = parse_error_log(ERROR_LOG_PATH, db.get_last_line_position())
    
    # Add new errors to the database
    for error in new_errors:
        # Classify the error and get explanations
        error_type = classify_error(error)
        explanation = get_human_explanation(error, error_type)
        
        # Add to database
        db.add_error(
            timestamp=error.get("timestamp"),
            level=error.get("level"),
            module=error.get("module"),
            message=error.get("message"),
            error_type=error_type,
            explanation=explanation,
            stack_trace=error.get("stack_trace", ""),
            file_path=error.get("file_path", ""),
            line_number=error.get("line_number", "")
        )
    
    # Return filtered errors based on current filters
    return db.get_filtered_errors(
        status=st.session_state.filter_status,
        severity=st.session_state.filter_severity,
        search_query=st.session_state.search_query
    )

# Get filtered errors
filtered_errors = refresh_error_data()

# Display data in tabs
tab1, tab2, tab3 = st.tabs(["Active Errors", "All Errors", "Error Trends"])

with tab1:
    if not filtered_errors:
        st.info("No errors matching your filters. 🎉")
    else:
        for error in filtered_errors:
            with st.expander(f"{error['level']} - {error['timestamp']}: {error['message'][:100]}..."):
                # Error details
                st.markdown(f"**Type:** {error['error_type']}")
                st.markdown(f"**Module:** {error['module']}")
                st.markdown(f"**Status:** {error['status']}")
                
                # Human explanation
                st.markdown("### What this means:")
                st.info(error['explanation'])
                
                # Stack trace
                if error['stack_trace']:
                    with st.expander("Stack Trace"):
                        st.code(error['stack_trace'])
                
                # Actions
                col1, col2, col3, col4 = st.columns(4)
                if col1.button("Mark Fixed", key=f"fix_{error['id']}"):
                    db.update_error_status(error['id'], "Fixed")
                    st.experimental_rerun()
                if col2.button("Mark In Progress", key=f"progress_{error['id']}"):
                    db.update_error_status(error['id'], "In Progress")
                    st.experimental_rerun()
                if col3.button("Ignore", key=f"ignore_{error['id']}"):
                    db.update_error_status(error['id'], "Ignored")
                    st.experimental_rerun()
                if col4.button("Delete", key=f"delete_{error['id']}"):
                    db.delete_error(error['id'])
                    st.experimental_rerun()

with tab2:
    # All errors in a DataFrame
    all_errors = db.get_all_errors()
    if all_errors:
        df = pd.DataFrame(all_errors)
        df = df[['timestamp', 'level', 'module', 'message', 'status', 'error_type']]
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No errors in the database.")

with tab3:
    # Simple error trends chart
    st.markdown("### Error Trends")
    trends_data = db.get_error_trends()
    if trends_data:
        df = pd.DataFrame(trends_data)
        st.line_chart(df)
    else:
        st.info("Not enough data to show trends.")

# Auto-refresh logic
if st.session_state.auto_refresh:
    time_since_refresh = (datetime.now() - st.session_state.last_refresh).total_seconds()
    if time_since_refresh > REFRESH_INTERVAL:
        st.session_state.last_refresh = datetime.now()
        time.sleep(0.5)  # Brief pause to avoid constant reruns
        st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("🐞 Forest App Debug Dashboard | Developed with 💚 to make debugging easier")
