import logging
from forest_app.core.jsonl_error_logger import setup_jsonl_error_logging

# Setup JSONL error logging
setup_jsonl_error_logging('/Users/bretmeraki/Downloads/ForestFInal-main-16/error.jsonl')

# Configure root logger
logging.basicConfig(level=logging.ERROR)

def test_error_logging():
    try:
        # Intentionally raise an exception to test error logging
        x = 1 / 0
    except Exception as e:
        # Log the error
        logging.error("Test error logging", exc_info=True)

if __name__ == "__main__":
    test_error_logging()
    print("Error logging test completed. Check error.jsonl for details.")
