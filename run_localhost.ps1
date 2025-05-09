# Run ForestApp on localhost
# This script sets the necessary environment variables and starts the application

# Set Python path
$env:PYTHONPATH = "$PSScriptRoot;$PSScriptRoot\forest_app"

# Ensure USE_CLOUD_MODE is set to False for localhost
$env:USE_CLOUD_MODE = "False"

# Load .env file if it exists
if (Test-Path .\.env) {
    Get-Content .\.env | ForEach-Object {
        if ($_ -match '^([^#=]+)=(.+)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            # Don't override USE_CLOUD_MODE
            if ($key -ne "USE_CLOUD_MODE") {
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
            }
        }
    }
    Write-Host "Loaded environment variables from .env file"
} else {
    Write-Host "No .env file found. Please run setup_localhost.ps1 first."
    exit 1
}

# Run the application
Write-Host "Starting ForestApp on localhost with USE_CLOUD_MODE=False..."
Write-Host "API will be available at: http://localhost:8000"
Write-Host "Press Ctrl+C to stop the application"
uvicorn forest_app.core.main:app --reload --host 0.0.0.0 --port 8000
