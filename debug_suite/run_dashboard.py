#!/usr/bin/env python
"""
Run Script for Debug Dashboard

This script launches the debug dashboard as a standalone Streamlit app.
"""
import os
import sys
import subprocess
from pathlib import Path

# Get the absolute path of the debug_suite directory
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = SCRIPT_DIR.parent

def run_dashboard():
    """Run the Streamlit debug dashboard."""
    # Make sure streamlit is available
    try:
        import streamlit
    except ImportError:
        print("Streamlit not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])
    
    # Add the project root to the Python path to ensure imports work
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    
    # Launch the dashboard
    dashboard_path = SCRIPT_DIR / "debug_dashboard.py"
    print(f"Launching debug dashboard from {dashboard_path}")
    subprocess.run([
        "streamlit", "run", 
        str(dashboard_path),
        "--server.port", "8502",  # Use a different port than the main app
        "--server.headless", "true",
        "--browser.serverAddress", "localhost",
        "--browser.gatherUsageStats", "false"
    ])

if __name__ == "__main__":
    run_dashboard()
