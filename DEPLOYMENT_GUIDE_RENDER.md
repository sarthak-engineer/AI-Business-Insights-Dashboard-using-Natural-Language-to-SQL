# 🚀 Deployment Guide: AI Business Insights Dashboard

This guide outlines how to deploy your **React/Vite Frontend** and **Flask API Backend** using **Render**.

### 🔹 1. Quick Deployment: Render Blueprint (Recommended)
I have created a `render.yaml` file in the root of your project. This is a "Blueprint" that automatically sets up both services with the correct connections in one go.

1.  Push your code to a GitHub/GitLab repository.
2.  Go to the [Render Dashboard](https://dashboard.render.com/).
3.  Click **New +** and select **Blueprint**.
4.  Connect your repository.
5.  Render will detect `render.yaml` and offer to create:
    -   `ai-business-insights-api` (Flask Web Service)
    -   `ai-business-insights-ui` (React Static Site)

### 🔹 2. Manual Deployment Steps

If you prefer to set them up manually:

#### **Backend (Flask API Web Service)**
1.  **Project Type**: Flask / Python
2.  **Build Command**: `pip install -r backend/requirements.txt`
3.  **Start Command**: `gunicorn --chdir backend app:app`
4.  **Add Environment Variables**:
    -   `GROQ_API_KEY`: *(Your Grok API Key)*
    -   `SUPABASE_URL`: *(Your Supabase Project URL)*
    -   `SUPABASE_KEY`: *(Your Supabase Anon Key)*
    -   `FRONTEND_URL`: `https://[your-frontend-url].onrender.com`

#### **Frontend (React Static Site)**
1.  **Project Type**: Static Site
2.  **Build Command**: `cd frontend && npm install && npm run build`
3.  **Publish Directory**: `frontend/dist`
4.  **Add Environment Variables**:
    -   `VITE_API_URL`: `https://[your-backend-api-url].onrender.com`

---

### 🔹 3. Connecting the Services
-   The **Frontend** needs to know where the **Backend** is via `VITE_API_URL`.
-   The **Backend** needs to allow access from the **Frontend** via `FRONTEND_URL` for CORS security.

### 🔹 4. Project Files Added/Updated
| File | Purpose |
| :--- | :--- |
| [`backend/requirements.txt`](file:///c:/Users/sarth/Desktop/AI-Business-Insights-Dashboard-using-Natural-Language-to-SQL/backend/requirements.txt) | Python dependencies for the production API. |
| [`backend/app.py`](file:///c:/Users/sarth/Desktop/AI-Business-Insights-Dashboard-using-Natural-Language-to-SQL/backend/app.py) | Production-ready CORS and server startup logic. |
| [`render.yaml`](file:///c:/Users/sarth/Desktop/AI-Business-Insights-Dashboard-using-Natural-Language-to-SQL/render.yaml) | Render Blueprint for automated deployment. |
| [`backend/Procfile`](file:///c:/Users/sarth/Desktop/AI-Business-Insights-Dashboard-using-Natural-Language-to-SQL/backend/Procfile) | Standard process definition for web services. |
| [`.env.example`](file:///c:/Users/sarth/Desktop/AI-Business-Insights-Dashboard-using-Natural-Language-to-SQL/backend/.env.example) | Environment variable templates. |

> [!TIP]
> Ensure you have your **Grok/Groq API Key** and **Supabase Credentials** ready to paste into the Render Environment Variables tab.
