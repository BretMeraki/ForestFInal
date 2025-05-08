import logging
import json
from logging import Handler, LogRecord
from datetime import datetime
import os

class JSONLErrorHandler(Handler):
    def __init__(self, filename='error.jsonl', level=logging.ERROR):
        super().__init__(level)
        self.filename = os.path.abspath(filename)
        # Ensure the directory exists
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

    def emit(self, record: LogRecord):
        try:
            # Build the log entry
            log_entry = {
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'pathname': record.pathname,
                'lineno': record.lineno,
                'exc_info': self.formatException(record.exc_info) if record.exc_info else None,
            }
            # If extra structured info is present, add it
            if hasattr(record, 'explanation'):
                log_entry['explanation'] = record.explanation
            if hasattr(record, 'actionable_steps'):
                log_entry['actionable_steps'] = record.actionable_steps
            if hasattr(record, 'path'):
                log_entry['path'] = record.path
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception:
            self.handleError(record)

def setup_jsonl_error_logging(filename='error.jsonl'):
    handler = JSONLErrorHandler(filename=filename)
    handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(handler)
