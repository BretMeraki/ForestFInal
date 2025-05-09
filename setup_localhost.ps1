# Setup script for localhost development without Docker
# Run this script to configure your local environment

# Create a .env file from example if it doesn't exist
if (-not (Test-Path .\.env)) {
    Write-Host "Creating .env file from example..."
    Copy-Item .\.env.example .\.env
    Write-Host "Created .env file. Please edit it with your actual values."
}

# Install dependencies
Write-Host "Installing Python dependencies..."
pip install -r requirements.txt

# Check for PostgreSQL
try {
    & psql --version
    Write-Host "PostgreSQL client found."
} catch {
    Write-Host "PostgreSQL client not found. Please install PostgreSQL and make sure 'psql' is in your PATH."
    Write-Host "Download: https://www.postgresql.org/download/windows/"
    exit 1
}

# Run database migrations (if configured)
$env:PYTHONPATH = "$PSScriptRoot;$PSScriptRoot\forest_app"
Write-Host "Running database migrations..."
try {
    & alembic upgrade head
    Write-Host "Database migrations completed."
} catch {
    Write-Host "Database migration failed. Please make sure PostgreSQL is running"
    Write-Host "and your DB_CONNECTION_STRING in .env is correct."
}

Write-Host ""
Write-Host "Local setup complete! To run the application:"
Write-Host "1. Make sure your PostgreSQL server is running"
Write-Host "2. Set environment variable: `$env:PYTHONPATH = '$PSScriptRoot;$PSScriptRoot\forest_app'"
Write-Host "3. Run: uvicorn forest_app.core.main:app --reload"
Write-Host ""
