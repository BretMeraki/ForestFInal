"""
Error Parser Module

This module handles parsing the error log file, extracting structured information,
classifying error types, and providing human-readable explanations.
"""
import re
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Regular expressions for different log formats
STANDARD_LOG_PATTERN = re.compile(
    r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) (\w+) ([^:]+): (.*)'
)

TRACEBACK_START_PATTERN = re.compile(r'^Traceback \(most recent call last\):$')
FILE_LINE_PATTERN = re.compile(r'^  File "([^"]+)", line (\d+), in (.+)$')
EXCEPTION_PATTERN = re.compile(r'^([A-Za-z0-9_.]+): (.+)$')

# Error classification patterns
ERROR_PATTERNS = {
    "IndentationError": {
        "pattern": re.compile(r"IndentationError:"),
        "explanation": "Python detected incorrect indentation. Check spacing at the indicated line."
    },
    "ModuleNotFoundError": {
        "pattern": re.compile(r"ModuleNotFoundError: No module named '([^']+)'"),
        "explanation": "A required Python module is missing. Run 'pip install {0}' to add it."
    },
    "ImportError": {
        "pattern": re.compile(r"ImportError: cannot import name '([^']+)'"),
        "explanation": "Unable to import '{0}'. Check if the name is correct and the module is installed."
    },
    "RerunException": {
        "pattern": re.compile(r"RerunException"),
        "explanation": "Streamlit tried to rerun the app, possibly creating an infinite loop. Check for st.rerun() calls."
    },
    "SyntaxError": {
        "pattern": re.compile(r"SyntaxError: (.+)"),
        "explanation": "Python syntax error: {0}. Check for missing parentheses, quotes, etc."
    },
    "AttributeError": {
        "pattern": re.compile(r"AttributeError: '([^']+)' object has no attribute '([^']+)'"),
        "explanation": "The {0} object doesn't have a {1} attribute/method. Check object type and available attributes."
    },
    "TypeError": {
        "pattern": re.compile(r"TypeError: (.+)"),
        "explanation": "Type mismatch: {0}. Check that you're using compatible data types."
    },
    "KeyError": {
        "pattern": re.compile(r"KeyError: '([^']+)'"),
        "explanation": "Dictionary key '{0}' not found. Add a check for its existence before access."
    },
    "FileNotFoundError": {
        "pattern": re.compile(r"FileNotFoundError: (.+)"),
        "explanation": "File not found: {0}. Check the path and permissions."
    },
    "ValueError": {
        "pattern": re.compile(r"ValueError: (.+)"),
        "explanation": "Invalid value: {0}. Check the input parameters."
    },
    "RuntimeError": {
        "pattern": re.compile(r"RuntimeError: (.+)"),
        "explanation": "Runtime error: {0}. Check for issues with event loops or resource allocation."
    },
    "ConnectionError": {
        "pattern": re.compile(r"(Connection|ConnectionError|ConnectionRefused)"),
        "explanation": "Connection issue. Check network connectivity and service availability."
    },
    "Task not found in backlog": {
        "pattern": re.compile(r"Task ([^ ]+) not found in backlog"),
        "explanation": "Task '{0}' doesn't exist in the backlog. It may have been deleted or completed already."
    },
    "HTTP Error": {
        "pattern": re.compile(r"HTTP Error (\d+)"),
        "explanation": "HTTP error {0}. Check API credentials, parameters, and endpoint availability."
    },
    "Event loop is closed": {
        "pattern": re.compile(r"Event loop is closed"),
        "explanation": "The async event loop was closed while operations were still pending. Check async/await usage."
    },
    "SENTRY_DSN": {
        "pattern": re.compile(r"SENTRY_DSN environment variable not found"),
        "explanation": "Sentry error tracking is not configured. This is just informational, not a critical error."
    },
    "XP_MASTERY feature": {
        "pattern": re.compile(r"XP_MASTERY feature enabled but (\w+) (?:is|are) invalid or dummy"),
        "explanation": "The XP_MASTERY feature is enabled but {0} is not properly configured. Update backend config."
    },
    "Invalid response format": {
        "pattern": re.compile(r"Invalid response format"),
        "explanation": "API response validation failed. Check expected vs. actual API response structure."
    },
    "Mock object": {
        "pattern": re.compile(r"Mock object"),
        "explanation": "Using a mock object in production code. Replace with actual implementation."
    }
}

def parse_error_log(log_path: str, last_position: int = 0) -> List[Dict[str, Any]]:
    """
    Parse the error log file and extract new error entries.
    
    Args:
        log_path: Path to the error log file
        last_position: Last read position in the file
        
    Returns:
        List of parsed error dictionaries
    """
    if not os.path.exists(log_path):
        return []
        
    results = []
    current_error = None
    stack_trace_lines = []
    in_traceback = False
    
    with open(log_path, 'r') as f:
        # Skip to the last read position
        f.seek(last_position)
        
        for line in f:
            # Check if this is the start of a new log entry
            std_match = STANDARD_LOG_PATTERN.match(line)
            
            if std_match:
                # If we were collecting a traceback, finalize it for the previous error
                if in_traceback and current_error:
                    current_error['stack_trace'] = '\n'.join(stack_trace_lines)
                    stack_trace_lines = []
                    in_traceback = False
                
                # Start a new error entry
                timestamp_str, level, module, message = std_match.groups()
                try:
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                except ValueError:
                    timestamp = datetime.now()  # Fallback
                
                current_error = {
                    'timestamp': timestamp_str,
                    'level': level,
                    'module': module,
                    'message': message.strip(),
                    'stack_trace': '',
                    'file_path': '',
                    'line_number': ''
                }
                results.append(current_error)
            
            # Check for traceback start
            elif TRACEBACK_START_PATTERN.match(line):
                in_traceback = True
                stack_trace_lines = [line.strip()]
            
            # Continue collecting traceback lines
            elif in_traceback:
                stack_trace_lines.append(line.strip())
                
                # Extract file and line info if present
                file_match = FILE_LINE_PATTERN.match(line)
                if file_match and current_error:
                    file_path, line_number, function = file_match.groups()
                    # Only update if not already set (to catch the first occurrence)
                    if not current_error['file_path']:
                        current_error['file_path'] = file_path
                        current_error['line_number'] = line_number
                
                # Check for exception type
                exception_match = EXCEPTION_PATTERN.match(line)
                if exception_match and current_error:
                    exception_type, exception_msg = exception_match.groups()
                    # Add to message for better classification
                    current_error['message'] += f" - {exception_type}: {exception_msg}"
    
    # Handle any pending traceback
    if in_traceback and current_error:
        current_error['stack_trace'] = '\n'.join(stack_trace_lines)
    
    return results

def classify_error(error: Dict[str, Any]) -> str:
    """
    Determine the type of error based on patterns in the message.
    
    Args:
        error: Parsed error dictionary
        
    Returns:
        Error type classification
    """
    message = error.get('message', '') + '\n' + error.get('stack_trace', '')
    
    for error_type, pattern_info in ERROR_PATTERNS.items():
        match = pattern_info['pattern'].search(message)
        if match:
            return error_type
    
    # Default classification based on log level
    level = error.get('level', '').upper()
    if level == 'CRITICAL' or level == 'ERROR':
        return 'Unclassified Error'
    elif level == 'WARNING':
        return 'Unclassified Warning'
    else:
        return 'Informational'

def get_human_explanation(error: Dict[str, Any], error_type: str) -> str:
    """
    Generate a human-readable explanation for the error.
    
    Args:
        error: Parsed error dictionary
        error_type: Classified error type
        
    Returns:
        Human-readable explanation
    """
    message = error.get('message', '') + '\n' + error.get('stack_trace', '')
    
    if error_type in ERROR_PATTERNS:
        pattern_info = ERROR_PATTERNS[error_type]
        match = pattern_info['pattern'].search(message)
        
        if match:
            # Format explanation with captured groups
            try:
                return pattern_info['explanation'].format(*match.groups())
            except (IndexError, KeyError):
                return pattern_info['explanation']
    
    # Generate a generic explanation based on the error's module and level
    module = error.get('module', '')
    level = error.get('level', '').upper()
    
    if 'api_client' in module:
        return "API communication issue. Check the endpoint, credentials, and request data."
    elif 'processors' in module:
        return "Backend processing error. Check data format and processor configuration."
    elif 'hta_tree' in module:
        return "Error in the hierarchical task analysis tree. Check tree structure and node references."
    elif 'integrations' in module:
        return "Issue with external integration. Check API keys, endpoints, and service status."
    
    # Default explanations by level
    if level == 'CRITICAL':
        return "Critical error that prevents the application from functioning. Immediate attention required."
    elif level == 'ERROR':
        return "Error that affects functionality but doesn't crash the application. Should be fixed soon."
    elif level == 'WARNING':
        return "Potential issue that doesn't affect core functionality but should be reviewed."
    else:
        return "Informational message. No action required."
