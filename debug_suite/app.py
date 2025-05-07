"""
Unified Forest Debug Suite Flask App
- Combines API endpoints and dashboard UI
- Deploy this as a single service on Render
"""
import os
import json
from datetime import datetime
from flask import Flask, jsonify, request, render_template, redirect, url_for, session

# --- Config ---
ERROR_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../error.log'))
PRIORITY_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'flask_api/error_priorities.json'))
STATUS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'flask_api/error_status.json'))

app = Flask(__name__)
app.secret_key = os.environ.get('DASHBOARD_SECRET_KEY', 'forest-debug-dashboard')

# --- API ENDPOINTS ---
@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"})

@app.route("/api/errors", methods=["GET"])
def get_errors():
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
    update_error_log_status(error_id, status)
    log_action_entry(error_id, status)
    return jsonify({"message": f"Status for error {error_id} set to {status}"})

@app.route("/api/errors/<error_id>/status", methods=["GET"])
def get_status(error_id):
    statuses = load_statuses()
    return jsonify({"error_id": error_id, "status": statuses.get(str(error_id), "New")})

# --- Dashboard UI ENDPOINTS ---
@app.route("/", methods=["GET", "POST"])
def dashboard_index():
    # Filtering (simple, local only)
    status = request.args.get('status', 'All')
    severity = request.args.get('severity', 'All')
    search = request.args.get('search', '')
    errors = fetch_errors()
    # Filter in Python for demo
    if status != 'All':
        errors = [e for e in errors if e.get('status', 'New') == status]
    if severity != 'All':
        errors = [e for e in errors if e.get('level', '') == severity]
    if search:
        errors = [e for e in errors if search.lower() in str(e).lower()]
    stats = {
        'total': len(errors),
        'fixed': sum(1 for e in errors if e.get('status') == 'Fixed'),
        'new_today': 0,  # You can improve this
        'critical': sum(1 for e in errors if e.get('level') == 'CRITICAL')
    }
    return render_template("dashboard.html", errors=errors, stats=stats, status=status, severity=severity, search=search, critical_tab=False, endpoint_options=['Local'], selected_endpoint='Local')

@app.route("/critical")
def critical():
    errors = [e for e in fetch_errors() if e.get('level') == 'CRITICAL']
    stats = {
        'total': len(errors),
        'fixed': sum(1 for e in errors if e.get('status') == 'Fixed'),
        'new_today': 0,
        'critical': len(errors)
    }
    return render_template("dashboard.html", errors=errors, stats=stats, status='All', severity='CRITICAL', search='', critical_tab=True, endpoint_options=['Local'], selected_endpoint='Local')

@app.route("/error/<error_id>/status", methods=["POST"])
def update_status(error_id):
    status = request.form.get("status")
    if not status:
        return redirect(url_for('dashboard_index'))
    update_error_log_status(error_id, status)
    log_action_entry(error_id, status)
    return redirect(url_for('dashboard_index'))

@app.route("/error/<error_id>/delete", methods=["POST"])
def delete_error(error_id):
    # Just log the action for now
    log_action_entry(error_id, "deleted")
    # (Optional: actually remove from log)
    return redirect(url_for('dashboard_index'))

# --- Helpers ---
def fetch_errors():
    errors = []
    statuses = load_statuses()
    priorities = load_priorities()
    if os.path.exists(ERROR_LOG_PATH):
        with open(ERROR_LOG_PATH, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    if isinstance(entry, dict):
                        # Ensure all entries have an ID
                        if not entry.get('id'):
                            entry['id'] = entry.get('timestamp', '')
                        # Add status and priority if missing
                        error_id = str(entry.get('id'))
                        entry['status'] = statuses.get(error_id, 'New')
                        entry['priority'] = priorities.get(error_id, 'normal')
                        # Ensure expected fields exist for the template
                        for field in ['explanation', 'fix_suggestion', 'stack_trace', 'file_path', 'line_number', 'error_type']:
                            if field not in entry:
                                entry[field] = None
                        errors.append(entry)
                except Exception:
                    continue
    return errors

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

def update_error_log_status(error_id, new_status):
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

def log_action_entry(error_id, status):
    action_entry = {
        "action": "status_update",
        "error_id": error_id,
        "new_status": status,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    with open(ERROR_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(action_entry) + "\n")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8600))
    app.run(host="0.0.0.0", port=port, debug=True)
