# BACKEND CONNECTION FAILED - SOLUTION GUIDE

## Problem
You're seeing "Error: Backend connection failed" when you try to submit a query.

## Root Causes
1. Backend not running on expected port (5000)
2. Frontend trying to connect to wrong backend URL
3. CORS (Cross-Origin Resource Sharing) blocking the request from the browser
4. Network connectivity issues

## Solutions (Try in Order)

### SOLUTION 1: Verify Backend is Running (MANDATORY)

Open a terminal and run:
```bash
python http://127.0.0.1:5000/query -X POST -H "Content-Type: application/json" -d "{\"query\":\"test\"}"
```

Or from Python:
```python
import requests
r = requests.post('http://localhost:5000/query', json={'query': 'test'})
print(f"Backend Status: {r.status_code}")
```

**If this fails:** Backend is not running. Start it:
```bash
cd backend
python app.py
```

---

### SOLUTION 2: Check Frontend is on Correct Port

1. Look at the browser address bar - you should be at:
   - `http://localhost:5175`
   - OR `http://localhost:5174`
   - OR `http://localhost:5173`

2. If you're at a different port, that's the issue! 

3. Restart frontend:
   ```bash
   cd frontend
   npm run dev
   ```

---

### SOLUTION 3: Clear Browser Cache & Hard Refresh

This often fixes CORS issues:

**Windows/Linux:**
- Press `Ctrl+Shift+Delete` 
- Select "Cached images and files"
- Click "Clear now"
- Refresh the page: `Ctrl+F5` or `Ctrl+Shift+R`

**Mac:**
- Press `Cmd+Shift+Delete`
- Or: `Cmd+Option+E` if using Safari

---

### SOLUTION 4: Check Browser Console for Real Error

The "Backend connection failed" message is generic. The real error is in Console:

1. Open Developer Tools: `F12`
2. Go to "Console" tab
3. Try making a query
4. Look for error messages (usually in red)
5. Screenshot or note the exact error

Common errors:
- "CORS policy: No 'Access-Control-Allow-Origin' header"
- "NetworkError: A network error occurred"
- "ERR_CONNECTION_REFUSED"
- "Failed to fetch"

---

### SOLUTION 5: Check Network Tab

This shows the actual HTTP requests:

1. Open `Developer Tools` → `Network` tab
2. Try making a query
3. Look for a failed `POST` request to `/query`
4. Click on it and check:
   - **Status**: Should be 200
   - **Headers**: Look for `Access-Control-Allow-Origin`
   - **Response**: Should show JSON with data

---

## QUICKFIX: Restart Both Servers

Often the simplest solution works:

**Terminal 1 (Backend):**
```bash
cd backend
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Then in browser:
1. Clear cache (`Ctrl+Shift+Delete`)
2. Go to http://localhost:5175 (or whatever port shows in terminal)
3. Try a query

---

## BYPASS CORS (Temporary Development Fix)

If you're still having CORS issues, try this:

**Use a CORS proxy during development** - Run this in a NEW terminal:
```bash
pip install flask-cors
# Already installed, so just make sure it's configured
```

The backend already has manual CORS handling, but if it's still not working, the issue might be with the requests library not sending the Origin header.

---

## Permanent Solution: Environment Variables

Set this environment variable before starting the backend:
```bash
# Windows PowerShell
$env:FLASK_ENV = "development"
$env:CORS_ORIGINS = "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://127.0.0.1:5173"
python backend/app.py

# Linux/Mac
export FLASK_ENV=development
export CORS_ORIGINS="http://localhost:5173,http://localhost:5174,http://localhost:5175,http://127.0.0.1:5173"  
python backend/app.py
```

---

## Testing Backend Directly

If frontend isn't working, test the backend directly:

```python
import requests

# Test 1: Can we reach the backend?
try:
    r = requests.post('http://localhost:5000/query', json={'query': 'revenue'}, timeout=5)
    print(f"✅ Backend responds: {r.status_code}")
    print(f"   Response: {r.json()}")
except Exception as e:
    print(f"❌ Cannot reach backend: {e}")

# Test 2: Do we get proper response?
r = requests.post('http://localhost:5000/query', json={'query': 'total revenue by category'}, timeout=5)
if 'data' in r.json():
    print("✅ Backend returns data correctly")
else:
    print(f"❌ Unexpected response: {r.json()}")
```

---

## Final Troubleshooting Checklist

- [ ] Backend is running (`python backend/app.py`) 
- [ ] Frontend is running (`npm run dev`)
- [ ] Frontend is at http://localhost:5175 (or 5173/5174)
- [ ] Cannot reach backend on http://localhost:5000
- [ ] Browser console shows specific error (F12 → Console)
- [ ] Tried hard refresh (Ctrl+Shift+R)
- [ ] Tried clearing cache (Ctrl+Shift+Delete)
- [ ] Firewall not blocking port 5000
- [ ] No VPN/proxy interfering

---

## Still Not Working?

If none of these work, provide:
1. **Screenshot of the error** in browser console (F12 → Console tab)
2. **Network tab screenshot** showing the failed request
3. **Terminal output** from both backend and frontend
4. **URL** you're visiting in the browser
5. **What port** npm shows when you run `npm run dev`

This will help diagnose the exact issue.
