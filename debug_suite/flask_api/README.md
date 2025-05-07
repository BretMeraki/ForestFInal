# Debug Suite Flask API

This is a standalone Flask API for the Forest App Debug Suite. It exposes endpoints to access error logs and other debugging utilities, independently from the Streamlit dashboard.

## How to Deploy

1. Deploy this folder (`debug_suite/flask_api/`) to a platform that supports Python web servers (Koyeb, Render, Heroku, etc).
2. Make sure you set the entrypoint to `flask_dashboard.py` (see the `Procfile`).
3. Install dependencies from `requirements.txt`.

## Example Endpoints

- `/api/errors` — Get error logs (JSON)
- `/api/status` — Health/status check

## Usage

- The Streamlit debug dashboard can be configured to fetch data from this API.
- You (or your team) can call these endpoints directly for debugging/monitoring.

---

**Security Note:**
Add authentication if you want to restrict access to the debug API.
