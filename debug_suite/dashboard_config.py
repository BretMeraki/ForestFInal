# dashboard_config.py

# Default endpoints
LOCAL_ERROR_LOGS_API = "http://localhost:8000/error_logs"
CLOUD_ERROR_LOGS_API = "https://forestapp.koyeb.app/error_logs"  # Updated for your Forest app deployment

# Configuration for remote operation
REMOTE_MODE = True  # Set to True for remote debugging, False for local

# Path configurations
LOCAL_ERROR_LOG_PATH = "../error.log"  # Relative path from debug_suite dir to local log
REMOTE_ERROR_LOG_URL = "https://forestapp.koyeb.app/error_logs"  # URL to fetch error logs from cloud

# Authentication (if needed)
API_KEY = ""  # Add API key if your endpoints are protected

# You can override these via environment variables or UI
