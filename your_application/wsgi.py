"""
WSGI application for Render deployment.
This structure matches exactly what Render expects by default.
"""
import os
from debug_suite.flask_api.flask_dashboard import app as application

# This makes the variable 'application' available to WSGI servers
# which is what Render's default gunicorn command expects

# This is for direct Python execution
if __name__ == "__main__":
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
