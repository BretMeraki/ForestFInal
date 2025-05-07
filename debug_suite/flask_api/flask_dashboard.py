"""
Standalone Flask Debug API for Forest App Debug Suite

This exposes error log and status endpoints for use by the debug dashboard or external tools.
"""
from flask import Flask, jsonify, request
import os
import json
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return """
    <h2>Forest Debug Suite API</h2>
    <ul>
        <li><a href=\"/api/status\">/api/status</a></li>
        <li><a href=\"/api/errors\">/api/errors</a></li>
        <li><a href=\"/api/errors/&lt;error_id&gt;/priority\">/api/errors/&lt;error_id&gt;/priority</a></li>
    </ul>
    """

ERROR_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../error.log'))
PRIORITY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'error_priorities.json'))
STATUS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'error_status.json'))

def load_priorities():
    if os.path.exists(PRIORITY_PATH):
        with open(PRIORITY_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def save_priorities(priorities):
    with open(PRIORITY_PATH, 'w', encoding='utf-8') as f:
        json.dump(priorities, f, indent=2)

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"})

@app.route("/api/errors", methods=["GET"])
def get_errors():
    """Return recent error logs as JSON array (for debug dashboard consumption)"""
    limit = int(request.args.get("limit", 100))
    level = request.args.get("level")
    logs = []
    priorities = load_priorities()
    statuses = load_statuses()
    if os.path.exists(ERROR_LOG_PATH):
        with open(ERROR_LOG_PATH, "r", encoding="utf-8") as f:
            for line in reversed(list(f)):
                try:
                    entry = json.loads(line)
                    error_id = str(entry.get("id", entry.get("timestamp", "")))
                    if level and entry.get("level") != level:
                        continue
                    entry["priority"] = priorities.get(error_id, "normal")
                    entry["status"] = statuses.get(error_id, "New")
                    logs.append(entry)
                    if len(logs) >= limit:
                        break
                except Exception:
                    continue
    return jsonify(list(reversed(logs)))

@app.route("/api/errors/<error_id>/priority", methods=["POST"])
def set_priority(error_id):
    """Set the priority for a given error (by id or timestamp)."""
    data = request.get_json(force=True)
    priority = data.get("priority")
    if not priority:
        return jsonify({"error": "Missing priority"}), 400
    priorities = load_priorities()
    priorities[str(error_id)] = priority
    save_priorities(priorities)
    return jsonify({"message": f"Priority for error {error_id} set to {priority}"})

@app.route("/api/errors/<error_id>/priority", methods=["GET"])
def get_priority(error_id):
    """Get the priority for a given error."""
    priorities = load_priorities()
    return jsonify({"error_id": error_id, "priority": priorities.get(str(error_id), "normal")})

@app.route("/api/errors/<error_id>/status", methods=["POST"])
def set_status(error_id):
    data = request.get_json(force=True)
    status = data.get("status")
    if not status:
        return jsonify({"error": "Missing status"}), 400
    statuses = load_statuses()
    statuses[str(error_id)] = status
    save_statuses(statuses)
    # Update error log entry
    update_error_log_status(error_id, status)
    # Trigger Windsurf/Cascade webhook if status is 'Fixed' or 'Complete'
    if status.lower() in ("fixed", "complete"):
        try:
            trigger_windsurf_webhook(error_id, status)
        except Exception as e:
            print(f"Failed to trigger Windsurf/Cascade webhook: {e}")
    return jsonify({"message": f"Status for error {error_id} set to {status}"})


def update_error_log_status(error_id, new_status):
    """Update the status field for a given error in the error.log file (if present)."""
    if not os.path.exists(ERROR_LOG_PATH):
        return
    updated_lines = []
    found = False
    with open(ERROR_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line)
                eid = str(entry.get("id", entry.get("timestamp", "")))
                if eid == str(error_id):
                    entry["status"] = new_status
                    found = True
                updated_lines.append(json.dumps(entry) + "\n")
            except Exception:
                updated_lines.append(line)
    if found:
        with open(ERROR_LOG_PATH, "w", encoding="utf-8") as f:
            f.writelines(updated_lines)


def trigger_windsurf_webhook(error_id, status):
    """Placeholder for Windsurf/Cascade webhook integration."""
    import requests
    WINDSURF_WEBHOOK_URL = os.environ.get("WINDSURF_WEBHOOK_URL", "https://your-windsurf-cascade-webhook-url")
    payload = {"error_id": error_id, "status": status}
    headers = {"Content-Type": "application/json"}
    response = requests.post(WINDSURF_WEBHOOK_URL, json=payload, headers=headers, timeout=5)
    response.raise_for_status()

@app.route("/api/errors/<error_id>/status", methods=["GET"])
def get_status(error_id):
    statuses = load_statuses()
    return jsonify({"error_id": error_id, "status": statuses.get(str(error_id), "New")})


def load_statuses():
    if os.path.exists(STATUS_PATH):
        with open(STATUS_PATH, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}

def save_statuses(statuses):
    with open(STATUS_PATH, 'w', encoding='utf-8') as f:
        json.dump(statuses, f, indent=2)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
