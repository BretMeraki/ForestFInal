"""
Rotating error logger for the Forest stack (front end, back end, Flask API, Streamlit)
- Import and call setup_rotating_error_log() at the top of any entry point (Flask, Streamlit, FastAPI, etc)
- Ensures robust, unified error logging across all components
- Rotates log when it exceeds max_bytes (default 1MB), keeping up to backup_count logs
- Rate-limits repeated identical errors to prevent log spam
"""
import logging
from logging.handlers import RotatingFileHandler
import sys
import os
import threading
import time

# In-memory cache for error spam protection
_error_cache = {}
_cache_lock = threading.Lock()
_SPAM_INTERVAL = 10  # seconds; only log identical error once per interval


def setup_rotating_error_log(logfile: str = None, max_bytes: int = 1_000_000, backup_count: int = 5):
    if logfile is None:
        # Default: error.log at project root
        logfile = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../error.log'))
    root_logger = logging.getLogger()
    # Only add if not already present
    if not any(isinstance(h, RotatingFileHandler) and getattr(h, 'baseFilename', None) == logfile for h in root_logger.handlers):
        handler = RotatingFileHandler(logfile, maxBytes=max_bytes, backupCount=backup_count)
        handler.setLevel(logging.WARNING)
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
        root_logger.addHandler(handler)
    # Patch logger to rate-limit spammy errors
    _patch_logger_for_spam_protection(root_logger)
    # Ensure uncaught exceptions are logged
    def log_uncaught_exceptions(exctype, value, tb):
        root_logger.error("Uncaught exception", exc_info=(exctype, value, tb))
    sys.excepthook = log_uncaught_exceptions


def _patch_logger_for_spam_protection(logger):
    orig_error = logger.error
    def spam_protected_error(msg, *args, **kwargs):
        key = str(msg)
        now = time.time()
        with _cache_lock:
            last_logged = _error_cache.get(key, 0)
            if now - last_logged < _SPAM_INTERVAL:
                return  # Skip repeated error
            _error_cache[key] = now
        return orig_error(msg, *args, **kwargs)
    logger.error = spam_protected_error
