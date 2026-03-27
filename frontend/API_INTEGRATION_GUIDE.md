# API Centralization & Retry Logic - Integration Guide

## 🎯 Overview
The application now has a centralized, production-grade API layer with automatic retry logic, exponential backoff, and comprehensive error handling. This replaces scattered `axios` calls throughout the codebase.

---

## ✅ What's Fixed

### **Issues Addressed:**
1. ❌ **Hardcoded URLs** → ✅ Single configuration point
2. ❌ **No retry logic** → ✅ Auto-retry with 3 attempts
3. ❌ **Poor error messages** → ✅ Clear, actionable messages
4. ❌ **No connection status** → ✅ Proper network error detection
5. ❌ **Analytics page crashes** → ✅ Graceful error handling

---

## 🚀 Quick Start

### **1. Verify Installation**
```bash
npm install  # Already have axios? Good!
```

### **2. ENV Configuration** (Optional)
Create `.env` in the `frontend` directory:
```
REACT_APP_API_URL=http://localhost:5000
```

If not provided, defaults to `http://localhost:5000`

### **3. Start the App**
```bash
npm run dev      # Frontend dev server
python app.py   # Backend server (separate terminal)
```

---

## 📋 API Reference

### **Centralized API Service** (`src/api.js`)

#### Configuration Options:
```javascript
const API_CONFIG = {
  BASE_URL: 'http://localhost:5000',  // Backend URL
  TIMEOUT: 30000,                      // Request timeout (ms)
  RETRY: {
    enabled: true,                     // Enable retries?
    attempts: 3,                       // Retry 3 times
    delay: 500,                        // Initial backoff (ms)
    statusCodes: [408, 500, 502, 503, 504]  // Retry these codes
  }
};
```

#### Available Endpoints:
```javascript
import { api, handleApiError } from './api';

// ✅ Query execution
api.query({ query: 'text', filters: {} })

// ✅ Drill-down queries
api.drillDown({ query: 'text' }, { field: 'x', value: 'y' })

// ✅ Analytics
api.analytics('top_spending_customers')

// ✅ File upload
api.upload(formData)

// ✅ Reset to demo
api.reset()

// ✅ Export data
api.export(dataArray)
```

#### Error Handling:
```javascript
try {
  const response = await api.query({ query: userInput });
  console.log(response.data);
} catch (err) {
  const errorInfo = handleApiError(err);
  // errorInfo = {
  //   success: false,
  //   error: "Clear error message",
  //   status: 500,
  //   isConnectionError: true/false,
  //   originalError: err
  // }
  alert(errorInfo.error);
}
```

---

## 🔄 How Retry Logic Works

**Automatic Retries for:**
- Network errors (no internet, backend down)
- 408 (Request Timeout)
- 500 (Internal Server Error)
- 502 (Bad Gateway)
- 503 (Service Unavailable)
- 504 (Gateway Timeout)

**Exponential Backoff:**
```
Attempt 1: 500ms delay
Attempt 2: 1000ms delay (500 × 2)
Attempt 3: 2000ms delay (500 × 4)
```

**Console Output:**
```
[API] Retry attempt 1/3 for POST /query (waiting 500ms)
[API] Retry attempt 2/3 for POST /query (waiting 1000ms)
```

---

## 🎯 Where It's Used

### **App.jsx** - Updated endpoints:
- `handleQuery()` - Main query execution
- `handleDrillDown()` - Nested data analysis
- `handleFileUpload()` - CSV import & reset
- `handleExportCSV()` - Download results
- Analytics pages - Data fetching

### **All API calls now:**
✅ Use centralized configuration  
✅ Automatically retry on failure  
✅ Have consistent error messages  
✅ Include proper timeouts  
✅ Log meaningful errors  

---

## 🛠️ Customization

### **Change Backend URL:**
```javascript
// Option 1: Environment variable
REACT_APP_API_URL=http://api.example.com npm run dev

// Option 2: Direct modification (not recommended)
// Edit frontend/src/api.js line 13:
const BASE_URL = 'http://api.example.com';
```

### **Disable Retries:**
```javascript
// In api.js line 30:
enabled: false
```

### **Increase Timeout:**
```javascript
// In api.js line 18:
TIMEOUT: 60000  // 60 seconds
```

### **Custom Error Messages:**
```javascript
// In api.js MESSAGES object
MESSAGES: {
  CONNECTION_FAILED: 'Your custom message...',
  // ...
}
```

---

## 📊 Error Message Reference

| Error | Cause | Solution |
|-------|-------|----------|
| "Unable to connect to server" | Backend not running | `python app.py` |
| "Request timeout" | Server slow/overloaded | Wait or increase TIMEOUT |
| "Server error occurred" | Backend bug | Check backend logs |
| "Network error" | Internet issue | Check connection |
| "Invalid request" | Bad query input | Verify input formatting |

---

## 🧪 Testing

### **Verify Retries Work:**
1. Start backend: `python app.py`
2. Make a query
3. Stop backend (Ctrl+C)
4. Make another query → Should show retries in console
5. Restart backend
6. Should auto-recover after a few retries

### **Console Debugging:**
```javascript
// Open browser DevTools (F12) → Console
// You'll see logs like:
// [API Error] { message: "...", status: 500, url: "..." }
// [API] Retry attempt 1/3 for POST /query (waiting 500ms)
```

---

## 📝 Files Modified

| File | Changes |
|------|---------|
| `frontend/src/api.js` | **NEW** - Centralized API layer |
| `frontend/src/App.jsx` | Updated all axios calls to use new API service |

---

## ✨ Benefits

✅ **Reliability** - Automatic retries on network failures  
✅ **Maintainability** - Single place to update all API calls  
✅ **User Experience** - Clear error messages  
✅ **Debugging** - Consistent logging  
✅ **Scalability** - Easy to add new endpoints  
✅ **Production-Ready** - Industry best practices  

---

## 🐛 Troubleshooting

### **"Cannot find module 'axios'"**
```bash
cd frontend && npm install axios
```

### **"Backend connection failed" even though backend is running**
- Check if backend is on `http://localhost:5000`
- Check browser console for full error details
- Ensure no firewall is blocking port 5000

### **Queries timing out**
- Increase TIMEOUT in `api.js`
- Check backend performance
- Reduce query complexity

### **Retries not working**
- Ensure `RETRY.enabled: true` in `api.js`
- Check browser console for retry logs

---

## 📚 Additional Resources

- [Axios Interceptors](https://axios-http.com/docs/interceptors)
- [Exponential Backoff](https://en.wikipedia.org/wiki/Exponential_backoff)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)

---

**Last Updated:** 2024  
**Status:** ✅ Production Ready
