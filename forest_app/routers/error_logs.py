# forest_app/routers/error_logs.py
"""
API endpoint to stream/query structured error logs (JSONL) for debugging dashboard.
"""
import os
import json
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from datetime import datetime

router = APIRouter()

ERROR_LOG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../error.jsonl'))


def parse_jsonl_line(line):
    try:
        return json.loads(line)
    except Exception:
        return None

@router.get("/error_logs", tags=["Debugging"], summary="Stream or query recent error logs.")
def get_error_logs(
    level: Optional[str] = Query(None, description="Filter by log level (e.g. ERROR, WARNING)"),
    path: Optional[str] = Query(None, description="Filter by request path"),
    since: Optional[str] = Query(None, description="ISO timestamp to filter logs after this time (UTC)"),
    limit: int = Query(100, ge=1, le=1000, description="Max number of log entries to return"),
):
    """
    Returns recent error logs as structured JSON objects, supports filtering.
    """
    if not os.path.exists(ERROR_LOG_PATH):
        raise HTTPException(status_code=404, detail="No error logs found.")

    def log_stream():
        count = 0
        with open(ERROR_LOG_PATH, 'r', encoding='utf-8') as f:
            for line in reversed(list(f)):
                entry = parse_jsonl_line(line)
                if not entry:
                    continue
                if level and entry.get('level') != level:
                    continue
                if path and entry.get('path') != path:
                    continue
                if since:
                    try:
                        entry_time = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                        since_time = datetime.fromisoformat(since)
                        if entry_time < since_time:
                            continue
                    except Exception:
                        continue
                yield json.dumps(entry) + '\n'
                count += 1
                if count >= limit:
                    break
    return StreamingResponse(log_stream(), media_type="application/jsonl")
