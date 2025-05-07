# Deploying Debug API to Render.com

This guide explains how to deploy your debugging Flask API to Render.com. This will allow you to have your debug API accessible from a different domain than your main app.

## Steps to Deploy on Render.com

### 1. Create a Render Account

If you don't already have one, sign up at [render.com](https://render.com/).

### 2. Deploy the Debug API

#### Option A: Direct GitHub Integration

1. Log in to your Render dashboard
2. Click "New +" button and select "Web Service"
3. Connect your GitHub repository
4. Select the repository containing your Forest App
5. Configure the service:
   - **Name**: `forest-debug-api` (or any name you prefer)
   - **Root Directory**: `debug_suite/flask_api`
   - **Environment**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python flask_dashboard.py`
   - **Plan**: Free (or paid if you need more resources)
6. Click "Create Web Service"

#### Option B: Using render.yaml (Blueprint)

1. Commit and push the `render.yaml` file in the `debug_suite/flask_api` directory
2. Go to the Render dashboard
3. Click "New +" and select "Blueprint"
4. Connect your GitHub repository if needed
5. Render will detect the `render.yaml` configuration
6. Review the settings and click "Apply"

## Accessing Your Debug API

Once deployed, your debug API will be available at a URL like:
```
https://forest-debug-api.onrender.com
```

You can access the API endpoints with:
- `https://forest-debug-api.onrender.com/api/status`
- `https://forest-debug-api.onrender.com/api/errors`

## Updating the Configuration

1. In your `debug_suite/dashboard_config.py`, update:
```python
CLOUD_ERROR_LOGS_API = "https://forest-debug-api.onrender.com/api/errors"
```

2. Update `DEV_SUITE_URL` in your Streamlit app to point to your Streamlit debug dashboard.

## Redeploying After Changes

After you make changes to your repo:
1. Commit and push to GitHub
2. Render will automatically redeploy the service

## Advantages of Render.com

- Reliable free tier
- Automatic HTTPS
- Automatic deploys on git push
- Clean URLs without path prefixes
