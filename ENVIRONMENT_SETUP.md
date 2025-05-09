# ForestApp Environment Setup Guide

## Environment Configuration

ForestApp uses environment variables to configure its behavior in different deployment contexts. 
The key configuration toggle is `USE_CLOUD_MODE`, which controls whether the app uses cloud resources or local resources.

## Quick Setup

1. Copy `.env.example` to `.env` for local development
2. Fill in the required variables based on your environment
3. For cloud deployment, set these variables in your platform dashboard (Koyeb, Render, etc.)

## Required Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `USE_CLOUD_MODE` | Toggle between cloud and local modes | `False` | Yes |
| `DB_CONNECTION_STRING` | PostgreSQL connection string | Local test DB | Yes |
| `GOOGLE_API_KEY` | Google Generative AI API key | None | Yes |
| `SECRET_KEY` | App secret for security | Random in dev | Yes |

## Cloud-Only Variables 
(Required when `USE_CLOUD_MODE=True`)

| Variable | Description | Default | Required for Cloud |
|----------|-------------|---------|----------|
| `GCP_SA_KEY` | Base64-encoded GCP service account key | None | Yes |
| `SENTRY_DSN` | Sentry error tracking | None | No |

## Local Development (without Docker)

ForestApp can run directly on your localhost with a local PostgreSQL database:

1. Make sure PostgreSQL is installed and running on your local machine
2. Run the setup script to create your environment:
   ```powershell
   # Windows
   .\setup_localhost.ps1
   ```
3. Edit the `.env` file with your PostgreSQL credentials and API keys
4. Start the application:
   ```powershell
   # Windows
   .\run_localhost.ps1
   ```

Your `.env` file should contain:
```
USE_CLOUD_MODE=False
DB_CONNECTION_STRING=postgresql://postgres:your_password@localhost:5432/postgres
GOOGLE_API_KEY=your_test_key_or_actual_key
SECRET_KEY=your_dev_secret_key
```

## Cloud Deployment

For cloud deployment on platforms like Koyeb, Render, Railway, or Google Cloud Run:
```
USE_CLOUD_MODE=True
DB_CONNECTION_STRING=your_cloud_sql_connection_string
GOOGLE_API_KEY=your_production_api_key
SECRET_KEY=your_production_secret_key
GCP_SA_KEY=your_base64_encoded_service_account_key
SENTRY_DSN=your_sentry_project_dsn
```

## Platform-Specific Configuration

### Koyeb

In your Koyeb dashboard:
1. Go to your app > Settings > Environment Variables
2. Add each required variable
3. Redeploy your service

### Render

In your Render dashboard:
1. Go to your service > Environment
2. Add each required variable
3. Apply changes

### Google Cloud Run

Use the Cloud Console or gcloud CLI:
```bash
gcloud run services update YOUR_SERVICE_NAME \
  --update-env-vars USE_CLOUD_MODE=True,DB_CONNECTION_STRING=YOUR_CONNECTION_STRING
```

## Testing Your Configuration

Run the following command to verify your environment is correctly configured:
```bash
./entrypoint.sh
```

This script will check for required variables and report any missing configurations.
