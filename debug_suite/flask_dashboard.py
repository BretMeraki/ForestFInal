"""
Flask Debug Dashboard for Forest App

Runs independently from your main app. No login required.
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import os
import requests
from datetime import datetime
from dashboard_config import LOCAL_ERROR_LOGS_API, CLOUD_ERROR_LOGS_API

app = Flask(__name__)
app.secret_key = os.environ.get('DASHBOARD_SECRET_KEY', 'forest-debug-dashboard')  # Needed for session

# Endpoint options
ENDPOINTS = {
    'Local': LOCAL_ERROR_LOGS_API,
    'Cloud': CLOUD_ERROR_LOGS_API,
}

def fetch_errors_from_api(endpoint, params=None):
    try:
        resp = requests.get(endpoint, params=params, timeout=5)
        if resp.status_code == 200:
            # Each line is a JSON object
            return [json.loads(line) for line in resp.text.strip().split('\n') if line.strip()]
        else:
            return []
    except Exception as e:
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    # Endpoint selection UI
    if request.method == "POST":
        selected_endpoint = request.form.get("endpoint_select")
        if selected_endpoint in ENDPOINTS:
            session['selected_endpoint'] = selected_endpoint
        return redirect(url_for('index'))
    selected_endpoint = session.get('selected_endpoint', 'Local')
    endpoint_url = ENDPOINTS.get(selected_endpoint, LOCAL_ERROR_LOGS_API)

    # Filtering
    status = request.args.get('status', 'All')
    severity = request.args.get('severity', 'All')
    search = request.args.get('search', '')
    params = {}
    if severity != 'All':
        params['level'] = severity
    if search:
        params['search'] = search
    errors = fetch_errors_from_api(endpoint_url, params=params)
    # Fake stats for now (could be improved)
    stats = {
        'total': len(errors),
        'fixed': 0,
        'new_today': 0,
        'critical': sum(1 for e in errors if e.get('level') == 'CRITICAL')
    }
    return render_template("dashboard.html", errors=errors, stats=stats, status=status, severity=severity, search=search, critical_tab=False, endpoint_options=ENDPOINTS.keys(), selected_endpoint=selected_endpoint)

@app.route("/critical")
def critical():
    # Only show critical errors
    errors = db.get_filtered_errors(status='All', severity='CRITICAL', search_query='')
    stats = db.get_stats()
    return render_template("dashboard.html", errors=errors, stats=stats, status='All', severity='CRITICAL', search='', critical_tab=True)

@app.route("/error/<error_id>/status", methods=["POST"])
def update_status(error_id):
    status = request.form.get("status")
    db.update_error_status(error_id, status)
    # Log the action to error.log
    error = next((e for e in db.get_all_errors() if e['id'] == error_id), None)
    if error:
        log_dashboard_action(f"User marked error {error_id} as {status}: '{error['message']}'")
    else:
        log_dashboard_action(f"User marked error {error_id} as {status} (error not found in DB)")
    return redirect(url_for('index'))

@app.route("/error/<error_id>/delete", methods=["POST"])
def delete_error(error_id):
    # Log the action to error.log before deleting
    error = next((e for e in db.get_all_errors() if e['id'] == error_id), None)
    if error:
        log_dashboard_action(f"User deleted error {error_id}: '{error['message']}'")
    else:
        log_dashboard_action(f"User deleted error {error_id} (error not found in DB)")
    db.delete_error(error_id)
    return redirect(url_for('index'))

@app.route("/api/errors")
def api_errors():
    # For AJAX polling
    status = request.args.get('status', 'All')
    severity = request.args.get('severity', 'All')
    search = request.args.get('search', '')
    errors = db.get_filtered_errors(status=status, severity=severity, search_query=search)
    return jsonify(errors)

@app.route("/api/stats")
def api_stats():
    stats = db.get_stats()
    return jsonify(stats)

def log_dashboard_action(message: str):
    """Append a dashboard action to the error log."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
    log_line = f"{now} INFO dashboard_action: {message}\n"
    with open(ERROR_LOG_PATH, "a") as f:
        f.write(log_line)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8600, debug=True)

