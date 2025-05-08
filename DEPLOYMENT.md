# Forest App Deployment Guide

This guide explains how to deploy both your main FastAPI app and the debugging suite to Koyeb in a single deployment process.

## Deployment Architecture

The deployment consists of:

1. **Main FastAPI App** - Your core application API
   - Deployed on Koyeb at `/` path
   - Runs on port 8000
   - Entrypoint: `uvicorn forest_app.core.main:app`

2. **Debug Flask API** - Debug utilities and error log access
   - Deployed on Koyeb at `/debug` path
   - Runs on port 8080
   - Entrypoint: `python debug_suite/flask_api/flask_dashboard.py`

3. **Streamlit Front-end** - User interface
   - Deployed on Streamlit Community Cloud (separate from Koyeb)
   - Connects to your FastAPI backend

## How to Deploy

### 1. Deploy Backend to Koyeb

#### First-time Setup

1. Create a Koyeb account if you don't have one
2. Install the Koyeb CLI:
   ```bash
   # macOS
   brew install koyeb/tap/cli
   # or for other platforms
   curl -fsSL https://cli.koyeb.com/install.sh | bash
   ```
3. Login to Koyeb CLI:
   ```bash
   koyeb login
   ```

#### Deploy With One Command

```bash
# From your repository root
koyeb app init --name forestapp --git github.com/BretMeraki/ForestFInal --git-branch main --ports 8000:http,8080:http --routes /:8000,/debug:8080 --env PORT=8000 --builder buildpacks --command "koyeb app services init"
```

OR

```bash
# Using the koyeb.yaml config
koyeb app create --config koyeb.yaml
```

#### Redeploy After Changes

```bash
git add .
git commit -m "Update app and debug suite"
git push

# Koyeb will automatically redeploy when you push to GitHub
```

### 2. Deploy Streamlit Front-end

1. Visit [Streamlit Community Cloud](https://streamlit.io/cloud)
2. Connect your GitHub repo
3. Set the main file to your Streamlit app entry point
4. Deploy

## Accessing Your Deployment

- **Main API**: `https://forestapp-xxxx.koyeb.app/`
- **Debug API**: `https://forestapp-xxxx.koyeb.app/debug/`
- **Streamlit Front-end**: The URL provided by Streamlit Community Cloud

## Configuration

The `koyeb.yaml` file contains the complete configuration for both services. You can:

- Modify environment variables
- Change scaling parameters
- Update entrypoint commands

## Troubleshooting

- Check Koyeb logs for both services
- Use the debug API to view error logs remotely
- Make sure your Streamlit app is configured to connect to the correct API URL

---

Questions? Contact the repo maintainer.
