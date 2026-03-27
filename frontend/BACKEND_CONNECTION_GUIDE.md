# Backend Connection Issues - Troubleshooting & Solutions

## 🎯 This document addresses the root causes of connection failures identified during the security audit.

---

## 📋 Issues Fixed

### **1. Hardcoded Backend URLs (Critical)**

**Problem:** 10+ hardcoded `http://localhost:5000` URLs scattered across the code
- If backend runs on different port → breaks
- Environment-specific configurations impossible
- Maintenance nightmare

**Solution:** ✅ Centralized `frontend/src/api.js`
```javascript
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
```

**Usage:**
```bash
# Development (default)
npm run dev  # Uses http://localhost:5000

# Custom backend
REACT_APP_API_URL=http://api.example.com npm run dev

# Docker environment
REACT_APP_API_URL=http://backend:5000 npm run dev
```

---

### **2. No Retry Logic (Major)**

**Problem:** Single connection failure = immediate error to user
- Network hiccup → fails
- Temporary DNS issue → fails  
- Backend restarting → fails

**Solution:** ✅ Automatic retry with exponential backoff
```javascript
// Retries: 500ms → 1s → 2s delays
// Applies to: network errors, timeouts, 5xx errors
```

**Console Output:**
```
[API] Retry attempt 1/3 for POST /query (waiting 500ms)
[API] Retry attempt 2/3 for POST /query (waiting 1000ms)
[API] Request succeeded on retry 2
```

---

### **3. Poor Error Messages (Major)**

**Problem:** Generic error messages confuse users

| Old Message | New Message |
|---|---|
| "Backend connection failed." | "Unable to connect to server. Please ensure the backend is running on http://localhost:5000" |
| HTTP 500 error | "Server error occurred. Please try again." |
| Connection timeout | "Request timeout. Server took too long to respond." |
| No backend | "Unable to connect to server. Check if backend is running." |

---

### **4. Analytics Page Crashes (Critical)**

**Problem:** No error handling on `/analytics/{endpoint}`
```javascript
// OLD CODE - NO ERROR HANDLING
axios.get(`http://localhost:5000/analytics/${endpoint}`)
  .then(res => setData(res.data))
  .catch(err => console.error(err))  // <- Silently fails!
  .finally(() => setLoading(false));
```

**Solution:** ✅ Proper error handling
```javascript
api.analytics(endpoint)
  .then(res => setData(res.data))
  .catch(err => {
    const errorInfo = handleApiError(err);
    setError(errorInfo.error);  // Shows to user!
  })
  .finally(() => setLoading(false));
```

---

## 🚀 Setup Instructions

### **Step 1: Install Dependencies**
```bash
cd frontend
npm install
```
Already have axios? ✅ No action needed.

### **Step 2: Configure Backend URL** (Optional)

**Option A: Use Default** (Recommended for local development)
```bash
npm run dev  # Automatically uses http://localhost:5000
```

**Option B: Custom Backend**

Create `frontend/.env`:
```
REACT_APP_API_URL=http://your-backend-url.com
```

Then run:
```bash
npm run dev
```

**Option C: Docker**

In docker-compose.yml or Kubernetes values:
```yaml
environment:
  REACT_APP_API_URL: http://backend-service:5000
```

### **Step 3: Start Services**

**Terminal 1 - Backend:**
```bash
python app.py
# Backend should show: Running on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Frontend should show: http://localhost:5173 (or similar)
```

**Terminal 3 - Browser:**
```
Open http://localhost:5173
```

---

## 🧪 Verification Checklist

- [ ] Backend runs: `python app.py` → "Running on..."
- [ ] Frontend runs: `npm run dev` → Shows URL
- [ ] Browser opens frontend URL
- [ ] Can make a query
- [ ] No "connection failed" errors
- [ ] Console shows successful API calls

---

## 🐛 Common Issues & Solutions

### **Issue 1: "Unable to connect to server"**

**Causes:**
1. Backend not running
2. Backend on wrong port
3. Firewall blocking port 5000
4. CORS issue

**Solutions:**
```bash
# Check backend is running
python app.py

# Check port 5000 is open
# Windows:
netstat -ano | findstr :5000

# Linux/Mac:
lsof -i :5000

# Check CORS in backend (should be configured)
# File: backend/app.py
# Should have: @app.after_request or flask_cors setup
```

### **Issue 2: Queries timeout**

**Causes:**
- Backend is slow/overloaded
- Query is complex
- Network is slow

**Solutions:**
```javascript
// Edit frontend/src/api.js line 18:
// Increase timeout from 30s to 60s:
TIMEOUT: 60000

// Or reduce backend load:
# Stop other processes
# Reduce dataset size
# Optimize queries
```

### **Issue 3: "Connection failed" but backend is running**

**Causes:**
- Wrong backend URL configured
- Backend port changed
- CORS issues
- Browser cache

**Solutions:**
```bash
# Check configured URL
# Frontend: http://localhost:5173
# Open DevTools (F12) → Console → Type:
// JavaScript console
fetch('http://localhost:5000/').then(r => r.json())

# Should return something, if error → connection issue

# Clear cache:
# Ctrl+Shift+Delete (Windows)
# Cmd+Shift+Delete (Mac)
```

### **Issue 4: Retries not working**

**Causes:**
- Retry disabled in config
- Wrong error codes

**Solutions:**
```javascript
// Verify in frontend/src/api.js:
RETRY: {
  enabled: true,           // <- Must be true
  attempts: 3,
  delay: 500,
  statusCodes: [408, 500, 502, 503, 504]
}

// Monitor retries:
// Open DevTools → Network tab
// Make failed query
// Should see multiple attempts
```

---

## 📊 Network Flow Diagram

```
Browser
   ↓
Frontend (React)
   ↓
api.js (Centralized Config + Retry Logic)
   ↓
Axios HTTP Client
   ↓
http://localhost:5000 (or REACT_APP_API_URL)
   ↓
Backend (Flask)
   ↓
Database
```

---

## 🔑 Key Files

| File | Purpose | Changes |
|------|---------|---------|
| `frontend/src/api.js` | ✅ NEW - API centralization & retry logic | Central config, retry interceptor |
| `frontend/src/App.jsx` | ✅ UPDATED - Uses new API service | Removed hardcoded URLs |
| `frontend/.env` | Optional - Backend URL override | Add if custom backend |

---

## 📝 Configuration Reference

### **Timeout Settings**
```javascript
TIMEOUT: 30000  // 30 seconds

// When exceeded: "Request timeout" error
// Increase for slow networks/servers
```

### **Retry Settings**
```javascript
RETRY: {
  enabled: true,              // Enable/disable retries
  attempts: 3,                // Max retry attempts
  delay: 500,                 // Initial delay (ms)
  statusCodes: [408, 500, 502, 503, 504]  // Retry these codes
}

// Retry delays: 500ms, 1000ms, 2000ms
// Only retries on: network errors + 408/5xx status codes
// 4xx errors (bad input) don't retry
```

### **Error Messages**
```javascript
MESSAGES: {
  CONNECTION_FAILED: '...',  // Network down
  TIMEOUT: '...',            // Slow server
  SERVER_ERROR: '...',       // 5xx errors
  NETWORK_ERROR: '...',      // Internet down
  UNKNOWN_ERROR: '...'       // Catch-all
}
```

---

## 🚀 Production Deployment

### **Docker**
```yaml
services:
  frontend:
    environment:
      REACT_APP_API_URL: http://backend:5000

  backend:
    ports:
      - "5000:5000"
```

### **Kubernetes**
```yaml
env:
  - name: REACT_APP_API_URL
    value: http://backend-service:5000
```

### **Vercel/Netlify**
```bash
# Set environment variable in dashboard:
REACT_APP_API_URL=https://your-api.com
```

---

## ✅ Validation

After setup, verify with:

```bash
# Check API connectivity
curl http://localhost:5000/

# Check frontend loads
curl http://localhost:5173

# Check API calls work
# Make a query in UI → Check browser DevTools Network tab
# Should see request to /query endpoint
```

---

## 📞 Support Flowchart

```
Connection Issue?
├─ Backend not running → python app.py
├─ Wrong port → Check REACT_APP_API_URL
├─ Firewall blocked → Allow port 5000
├─ Timeout → Increase TIMEOUT in api.js
└─ Other → Check browser console (F12)
```

---

**Last Updated:** 2024  
**Version:** 1.0  
**Status:** ✅ Production Ready
