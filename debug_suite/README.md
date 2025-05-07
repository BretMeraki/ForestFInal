# Forest App Debug Suite

A comprehensive debugging dashboard that runs separately from your main Forest App, providing real-time monitoring, analysis, and management of errors.

## Features

- **Real-time Error Monitoring**: Watches your error log file for new entries
- **Error Classification**: Automatically categorizes errors by type and severity
- **Human-Readable Explanations**: Translates cryptic error messages into plain English
- **Interactive Dashboard**: Filter, search, and manage errors through a user-friendly interface
- **Error Trends**: Visualize error patterns over time

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Streamlit (installed automatically if missing)
- pandas (for data visualization)

### Running the Debug Dashboard

```bash
# From the debug_suite directory
./run_dashboard.py

# Or alternatively
python run_dashboard.py

# Or directly with Streamlit
streamlit run debug_dashboard.py --server.port 8502
```

The dashboard will launch in your browser and start monitoring the error log at `../error.log`.

## Using the Dashboard

### Main Features

1. **Active Errors Tab**: Lists current errors with explanations and actions
2. **All Errors Tab**: Shows all errors in a table format
3. **Error Trends Tab**: Visualizes error patterns over time

### Sidebar Options

- **Filter by Status**: All, New, In Progress, Fixed, Ignored
- **Filter by Severity**: All, CRITICAL, ERROR, WARNING, INFO
- **Search**: Find specific errors by keywords
- **Auto-refresh**: Toggle automatic dashboard updates

### Actions for Each Error

- **Mark Fixed**: Set error status as fixed
- **Mark In Progress**: Set error status as being worked on
- **Ignore**: Hide non-critical errors you don't want to address
- **Delete**: Remove the error from the database

## Customization

You can modify the error patterns and explanations in `error_parser.py` to better match your specific application's error messages.

## Troubleshooting

- If the dashboard doesn't pick up new errors, check if the path to your error log is correct
- Make sure the user running the dashboard has permission to read the error log file
- If you're not seeing any errors at all, ensure that errors are being written to the log file
