"""
Standalone Flask Debug API for Forest App Debug Suite

This exposes error log and status endpoints for use by the debug dashboard or external tools.
"""
from flask import Flask, jsonify, request
import os
import json
from datetime import datetime

app = Flask(__name__)

ERROR_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../error.log'))

@app.route("/api/status", methods=["GET"])
def status():
    return jsonify({"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z"})

@app.route("/api/errors", methods=["GET"])
def get_errors():
    """Return recent error logs as JSON array (for debug dashboard consumption)"""
    limit = int(request.args.get("limit", 100))
    level = request.args.get("level")
    logs = []
    if os.path.exists(ERROR_LOG_PATH):
        with open(ERROR_LOG_PATH, "r", encoding="utf-8") as f:
            for line in reversed(list(f)):
                try:
                    entry = json.loads(line)
                    if level and entry.get("level") != level:
                        continue
                    logs.append(entry)
                    if len(logs) >= limit:
                        break
                except Exception:
                    continue
    return jsonify(list(reversed(logs)))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
