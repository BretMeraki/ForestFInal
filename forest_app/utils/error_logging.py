import logging
import os
from logging.handlers import RotatingFileHandler

LOG_FILE = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../error_rolling.log")
)


def get_error_logger():
    """
    Returns a logger configured to write error logs to a rolling file.
    Use this logger for all error-level logs across the application.
    """
    logger = logging.getLogger("forest_error_logger")
    logger.setLevel(logging.ERROR)
    if not logger.handlers:
        handler = RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
