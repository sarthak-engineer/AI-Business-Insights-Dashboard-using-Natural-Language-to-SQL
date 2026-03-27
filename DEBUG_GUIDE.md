# 🔧 Project Setup & Debugging Guide

## ✅ Current Status: ALL SYSTEMS OPERATIONAL

### Running Services
- ✅ **Backend:** http://localhost:5000 (Flask API)
- ✅ **Frontend:** http://localhost:5176 (React Vite)
- ✅ **Database:** Connected via Supabase

### API Endpoints Verified ✓
- GET http://localhost:5000/health → ✓ Backend Running
- GET http://localhost:5000/analytics/sales → ✓ Data Retrieved
- GET http://localhost:5000/analytics/customers → ✓ Data Retrieved
- GET http://localhost:5000/analytics/products → ✓ Data Retrieved

---

## 🚀 How to Access the Application

### Access the Dashboard
```
Open browser: http://localhost:5176
```

### Access Backend API Directly (for testing)
```
http://localhost:5000/health          → Check backend status
http://localhost:5000/analytics/sales → View sales analytics
```

---

## 🐛 If You See "404 Not Found"

### Cause 1: Accessing Wrong Port
❌ Wrong: `http://localhost:5000` (Backend API - no UI)  
✅ Correct: `http://localhost:5176` (Frontend with UI)

### Cause 2: Frontend Not Running
**Check if frontend is running:**
```bash
# In frontend directory
npm run dev
# Should show: ➜  Local:   http://localhost:5173 (or 5174, 5175, 5176...)
```

### Cause 3: Backend Not Running
**Check if backend is running:**
```bash
# In backend directory
python app.py
# Should show: * Running on http://127.0.0.1:5000
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "Connection Refused" Error
```
Error: Cannot connect to http://localhost:5000
```
**Solution:** Start the backend
```bash
cd backend
python app.py
```

### Issue 2: "Port Already in Use"
```
Port 5173 is in use, trying another one...
Port 5174 is in use, trying another one...
```
**Solution:** This is normal. Frontend will use next available port (5175, 5176, etc.)  
Just access whichever port is shown: `http://localhost:5176`

### Issue 3: API Requests Timing Out or Failing
**Check:**
1. Backend is running: `curl http://localhost:5000/health`
2. Check browser console (F12) for detailed error
3. Verify frontend can reach backend (check Network tab)

**Solution:**
- Restart backend: `python app.py`
- Clear browser cache: Ctrl+Shift+Delete
- Check firewall isn't blocking port 5000

---

## 📊 Services Architecture

```
User Browser (http://localhost:5176)
        ↓
   React Frontend
   (Vite Dev Server)
        ↓
   API Requests
   (via frontend/src/api.js)
        ↓
   Flask Backend
   (http://localhost:5000)
        ↓
   Supabase Database
```

---

## 🧪 Quick Test Procedure

### 1. Verify Backend
```bash
curl http://localhost:5000/health
# Expected: {"status":"Backend is running"}
```

### 2. Verify Frontend
Open: http://localhost:5176 in browser
Expected: Dashboard UI loads without errors

### 3. Test API Features
- **Query:** Enter a question in the search box
- **Analytics:** Click on analytics page tabs
- **Upload:** Try uploading a CSV file
- **Export:** Export results to CSV

### 4. Check Browser Console
Press F12 → Console tab
Should NOT see:
- Red errors
- Connection refused messages
- 404 errors for /query, /analytics, /upload endpoints

---

## 🔍 Debug Mode

### Enable Detailed Logging
```bash
# Terminal 1 - Backend with debug logging
cd backend
python app.py

# Terminal 2 - Frontend with verbose output
cd frontend
npm run dev
```

### Monitor API Requests
1. Open browser DevTools: F12
2. Go to Network tab
3. Perform an action (query, upload, etc.)
4. Check each request:
   - ✅ Status: 200 (OK)
   - ✅ Response type should be JSON
   - ❌ Avoid: 404, 500, CORS errors

---

## 📋 URL Quick Reference

| Function | URL |
|----------|-----|
| **Dashboard** | http://localhost:5176 |
| **Backend Health** | http://localhost:5000/health |
| **Sales Analytics** | http://localhost:5000/analytics/sales |
| **Customer Analytics** | http://localhost:5000/analytics/customers |
| **Product Analytics** | http://localhost:5000/analytics/products |

---

## ✨ Features Verification

### ✓ Features Working (Verified)
- Backend API responds correctly
- All analytics endpoints active
- CORS enabled for frontend access
- Error handling implemented
- Retry logic active

### ✓ To Test in Frontend
- Natural language queries
- Drill-down on data points
- File upload and schema detection
- Export to CSV
- Reset to demo data

---

## 🆘 Still Getting 404?

**Systematic Debug Steps:**

1. **Check Backend:**
   ```bash
   curl http://localhost:5000/health
   # If error → Backend not running, start it
   ```

2. **Check Frontend:**
   ```bash
   # Ensure you're accessing the correct port shown in terminal
   # Look for: ➜  Local:   http://localhost:XXXX/
   ```

3. **Check Browser Console:**
   - F12 → Console tab
   - Look for exact error message
   - Check Network tab for failed requests

4. **Check Environment:**
   - Frontend env var: `REACT_APP_API_URL`
   - Default is: `http://localhost:5000`

5. **Reset Everything:**
   ```bash
   # Kill backend (Ctrl+C)
   # Kill frontend (Ctrl+C)
   # Restart backend: python app.py
   # Restart frontend: npm run dev
   ```

---

## 📞 Support Info

- **Backend Port:** 5000
- **Frontend Port:** 5173+ (auto-increments if busy)
- **API Base:** http://localhost:5000
- **Frontend URL:** Check terminal output for exact port

**Remember:** Frontend and Backend are separate services and must BOTH be running!

---

**Last Updated:** 2026-03-26  
**Status:** ✅ All Systems Operational
