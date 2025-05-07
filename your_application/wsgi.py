import os
from debug_suite.flask_api.flask_dashboard import app as application

if __name__ == "__main__":
    application.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
