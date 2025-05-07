# Deploying the Flask Dashboard to Render

This guide explains how to deploy your Flask Debug Dashboard to Render.com so you can access it from anywhere.

## 1. Prepare Your Files
- Confirm you have these files in `debug_suite/`:
  - `flask_dashboard.py` (the dashboard app)
  - `Procfile` (with `web: python flask_dashboard.py`)
  - `requirements.txt` (with Flask, requests, jinja2)
  - `templates/` directory (with `dashboard.html`)

## 2. Push to GitHub
- Make sure your latest code is pushed to GitHub.

## 3. Deploy on Render
1. Go to https://dashboard.render.com/
2. Click **New +** → **Web Service**.
3. Connect your GitHub repo and pick the branch.
4. Set the root directory to `/debug_suite`.
5. Build command: `pip install -r requirements.txt`
6. Start command: `python flask_dashboard.py`
7. Click **Create Web Service**.

## 4. Access Your Dashboard
- Once deployed, Render will give you a public URL (e.g., `https://your-dashboard.onrender.com`).
- Visit that URL for your live dashboard UI!

---
If you need to use environment variables (like `DASHBOARD_SECRET_KEY`), add them in the Render dashboard under your service's settings.
