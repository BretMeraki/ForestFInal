# Deploying the Debug Suite Separately from the Main App

## Overview
This repository is structured to allow you to deploy your main user-facing Streamlit app and the developer debug dashboard as two **separate Streamlit Community Cloud apps**. The backend API (FastAPI) is deployed independently (e.g., on Koyeb). This ensures the debug suite is always available for maintainers, but never exposed to end users.

---

## Structure

- `/main_app.py` — Main Streamlit app for users (deployed to Streamlit Cloud)
- `/forest_app/` — FastAPI backend (deployed to Koyeb)
- `/debug_suite/debug_dashboard.py` — Debug dashboard (deployed to Streamlit Cloud, separate from main app)

---

## Deployment Instructions

### 1. Deploy the Main App (for users)
- Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
- Connect this GitHub repo
- Set the main file to `main_app.py`
- Deploy

### 2. Deploy the Debug Suite (for maintainers)
- Go to [Streamlit Community Cloud](https://streamlit.io/cloud)
- Add a **new app** from the same repo
- Set the main file to `debug_suite/debug_dashboard.py`
- Deploy
- (Optional) Restrict access via Streamlit Cloud settings if desired

### 3. Deploy the Backend
- Deploy `/forest_app` to Koyeb (or your chosen backend platform)

---

## Access

- **Main App (users):**  
  `https://<your-main-app-name>-<your-username>.streamlit.app`
- **Debug Suite (devs):**  
  `https://<your-debug-suite-name>-<your-username>.streamlit.app`
- **Backend API:**  
  `https://forestapp.koyeb.app`

---

## Optional: Add a Developer Tools Link
You can add a link to the debug suite in your main app (visible only to admins/developers) for quick access.

---

## Why?
- **Security:** Debug suite is never visible to users.
- **Separation of Concerns:** Each app is deployed and updated independently.
- **Flexibility:** You can monitor and debug your backend from anywhere, anytime.

---

## Example Directory Tree

```
/forest_app/
/debug_suite/
    debug_dashboard.py
    ...
main_app.py
README.md
```

---

## Questions?
Contact the repo maintainer for further deployment support.
