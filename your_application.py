"""
WSGI application for Render deployment.
File name matches exactly what Render expects by default.
"""
import os
from debug_suite.flask_api.flask_dashboard import app

# This is for direct Python execution
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
