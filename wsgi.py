"""
WSGI entry point for compatibility with the default gunicorn startup command.
"""
import os
from debug_suite.flask_api.flask_dashboard import app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
