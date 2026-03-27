# Frontend API Configuration & Error Handling Analysis
## AI Business Insights Dashboard - App.jsx Review

---

## Executive Summary
The frontend uses **axios** for HTTP requests with **hardcoded backend URLs**. Error handling is basic with toast notifications and inline error messages. **No retry logic exists** and there's **no centralized API configuration**.

---

## 1. AXIOS/FETCH CALLS TO BACKEND

### **Location: All API calls use `http://localhost:5000/` hardcoded URLs**

#### Call 1: Query Endpoint - Main AI Query Interface
```javascript
// Line ~558: handleQuery() function
const response = await axios.post('http://localhost:5000/query', { 
  query: targetQuery, 
  filters: filters 
});
```
- **Method:** POST
- **Payload:** `{ query: string, filters: object }`
- **Expected Response:** Result object with data, chart_type, interpretation, insights, ml_insights

#### Call 2: Drill-Down Query
```javascript
// Line ~578: handleDrillDown() function
const response = await axios.post('http://localhost:5000/query', { 
  query: query,
  drill_down: { field, value: String(value).trim() }
});
```
- **Method:** POST
- **Payload:** `{ query: string, drill_down: {field, value} }`
- **Used for:** Deep diving into data segments

#### Call 3: File Upload / Schema Detection
```javascript
// Line ~600: handleFileUpload() function
const response = await axios.post('http://localhost:5000/upload', formData);
```
- **Method:** POST
- **Payload:** FormData with file
- **Expected Response:** `{ message: string }`

#### Call 4: Reset to Demo Dataset
```javascript
// Line ~594: handleFileUpload() with action='reset'
await axios.post('http://localhost:5000/reset');
```
- **Method:** POST
- **No payload**
- **Side Effect:** Clears uploaded data, returns to demo

#### Call 5: Analytics Endpoints
```javascript
// Line ~373: AnalyticsPage component
axios.get(`http://localhost:5000/analytics/${endpoint}`)
```
- **Method:** GET
- **Endpoints:** Hardcoded paths for `sales`, `customers`, `products`
- **Expected Response:** Array of data objects

#### Call 6: Export to CSV
```javascript
// Line ~629: handleExportCSV() function
const response = await axios.post('http://localhost:5000/export', 
  { data: dataToExport }, 
  { responseType: 'blob' }
);
```
- **Method:** POST
- **Payload:** `{ data: array }`
- **Response Type:** Blob (binary CSV file)

---

## 2. ERROR HANDLING IN handleQuery FUNCTION

### **Lines ~540-575: handleQuery Implementation**

#### Two-Phase Error Handling:

**Phase 1: Success Path**
```javascript
try {
  // 1. Set loading states and clear previous errors
  setLoading("🤖 Understanding your query...");
  setResult(null);
  setError(null);
  setPrevResult(null);
  setDrillDownPath([]);

  // 2. Simulate thinking with staged loading messages
  window.queryTimeouts.push(setTimeout(() => setLoading("🔍 Generating SQL..."), 800));
  window.queryTimeouts.push(setTimeout(() => setLoading("📊 Fetching insights..."), 1600));

  // 3. Make API request
  const response = await axios.post('http://localhost:5000/query', {
    query: targetQuery,
    filters: filters
  });

  // 4. Clear timeouts immediately on success
  window.queryTimeouts.forEach(t => clearTimeout(t));
  setResult(response.data);
  setLoading(null);
```

**Phase 2: Error Path**
```javascript
} catch (err) {
  // 1. Clear pending timeouts
  window.queryTimeouts.forEach(t => clearTimeout(t));
  
  // 2. Extract error message (cascading fallback)
  const msg = err.response?.data?.error || 
              err.response?.data?.message || 
              'Backend connection failed.';
  
  // 3. Set error state and show toast
  setError(msg);
  setToast(msg);
  setLoading(null);
}
```

### **Error Extraction Logic:**
```
Priority Order:
1. err.response?.data?.error       (Backend custom error)
2. err.response?.data?.message     (Backend standard message)
3. 'Backend connection failed.'    (Default fallback)
```

---

## 3. ERROR DISPLAY TO USER

### **Method 1: Inline Error Alert (AIQueryPage)**
```javascript
// Line ~386
{error && <div className="error-alert">❌ Error: {error}</div>}
```
- **Display:** Bold red alert box in query section
- **Content:** Error message from backend or fallback
- **Duration:** Persistent until next query or cleared manually

### **Method 2: Toast Notification**
```javascript
// Lines 57-67: Toast component
const Toast = ({ message, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(onClose, 5000);  // 5-second auto-dismiss
    return () => clearTimeout(timer);
  }, [onClose]);
  
  return (
    <div className="toast-notification">
      <div className="toast-content">
        <span className="toast-icon">⚠️</span>
        <p>{message}</p>
        <button onClick={onClose} className="toast-close">×</button>
      </div>
    </div>
  );
};
```
- **Trigger Points:**
  1. Query errors (handleQuery)
  2. Drill-down errors (handleDrillDown)
  3. File upload errors (handleFileUpload)
  4. Reset errors (handleFileUpload)
  5. Export errors (handleExportCSV)
  
- **Display:** Toast UI in corner
- **Auto-dismiss:** 5 seconds
- **Manual dismiss:** Click × button

### **Method 3: Console Logging**
```javascript
// Line ~578: handleDrillDown()
if (!value || String(value).trim() === "") {
  console.error("Invalid drill-down selection (Empty value).");
  setToast("Invalid selection. Please try again.");
  return;
}
```
- **Purpose:** Debug information for developers
- **Not visible to end users**

---

## 4. RETRY LOGIC ANALYSIS

### **❌ NO RETRY LOGIC FOUND**

#### Current Behavior on Failures:
1. **Query Fails:** User sees error message, must manually re-submit
2. **Upload Fails:** User must re-upload file
3. **Analytics Fails:** Loading state shows indefinitely or error in console
4. **Export Fails:** User gets toast with failure message

#### Issues with Current Approach:
- Network timeouts will leave user hanging
- Temporary backend interruptions cause permanent failure
- User must remember query and re-enter it
- No exponential backoff for rate limits
- No max retry attempts validation

#### Example: AnalyticsPage Component (No Retry)
```javascript
// Lines 369-379
useEffect(() => {
  setLoading(true);
  axios.get(`http://localhost:5000/analytics/${endpoint}`)
    .then(res => setData(res.data))
    .catch(err => console.error(err))  // ← Just logs, no retry
    .finally(() => setLoading(false));
}, [endpoint]);
```

---

## 5. CENTRALIZED API CONFIGURATION

### **❌ NO CENTRALIZED API CONFIGURATION**

#### Hard-coded URLs Found (10 locations):
1. Line 369: `http://localhost:5000/analytics/${endpoint}` - Analytics GET
2. Line 558: `http://localhost:5000/query` - Main query POST
3. Line 578: `http://localhost:5000/query` - Drill-down POST
4. Line 596: `http://localhost:5000/reset` - Reset POST
5. Line 610: `http://localhost:5000/upload` - Upload POST
6. Line 634: `http://localhost:5000/export` - Export POST
7-10. Implied in other component flows

#### Problems with Current Approach:
- **Not Environment-Aware:** Hardcoded localhost won't work in production
- **DRY Violation:** Base URL repeated across multiple files
- **Maintenance Risk:** Changing backend URL requires code edits
- **Type Safety:** No request/response type validation
- **Timeout Config:** No default timeouts set
- **Axios Instance:** No shared configuration

---

## 6. SUMMARY TABLE: All API Endpoints

| Endpoint | Method | Called From | Error Handling | Timeout | Retry |
|----------|--------|-------------|-----------------|---------|-------|
| `/query` | POST | handleQuery, handleDrillDown | Toast + Inline Error | ❌ None | ❌ |
| `/upload` | POST | handleFileUpload | Toast | ❌ None | ❌ |
| `/reset` | POST | handleFileUpload | Toast | ❌ None | ❌ |
| `/analytics/{endpoint}` | GET | AnalyticsPage | Console.error | ❌ None | ❌ |
| `/export` | POST | handleExportCSV | Toast | ❌ None | ❌ |

---

## 7. CODE STRUCTURE & DEPENDENCIES

### **Frontend Stack:**
- **React:** 19.2.4 - UI framework
- **Axios:** 1.13.6 - HTTP client
- **Recharts:** 3.8.0 - Data visualization
- **Vite:** 8.0.1 - Build tool

### **Configuration Locations:**
- frontend/vite.config.js - Build config (no API proxy)
- frontend/package.json - Dependencies (axios included)
- frontend/src/App.jsx - All API calls here (no api.js or config file)

### **Entry Point:**
- frontend/src/main.jsx → imports App.jsx

---

## 8. POTENTIAL IMPROVEMENTS (Preview)

### **Recommendations for Future Enhancement:**

1. **Create Centralized API Config**
   - File: `frontend/src/config/api.js` or `frontend/src/utils/api.ts`
   - Exports: Base URL, timeout, default headers

2. **Create Axios Instance**
   - File: `frontend/src/services/axiosInstance.js`
   - Handles: Base URL, timeout, interceptors

3. **Add Retry Logic**
   - Library: `axios-retry` or custom interceptor
   - Config: Max retries = 3, exponential backoff

4. **Add Request/Response Interceptors**
   - Centralize error handling
   - Add request headers (auth, content-type)
   - Transform responses

5. **Type Safety** (if adding TypeScript)
   - Define interfaces for all API responses
   - Validate backend responses

6. **Error Boundary**
   - Catch unexpected errors across components
   - Graceful degradation

---

## 9. DEPENDENCIES & EXTERNAL FACTORS

### **Backend Dependencies (Flask):**
- CORS configured at `http://localhost:5000` (hardcoded in backend/app.py)
- Allowed origins in backend: localhost:5173, 5174, 5175, 3000

### **Browser Console Observations:**
- No CORS errors expected in development
- Network timeouts not explicitly handled
- No service worker or offline support

---

## Current Flow Diagram

```
User Input (Query/Filter)
    ↓
handleQuery() / handleDrillDown()
    ↓
axios.post('http://localhost:5000/...')
    ↓
SUCCESS: setResult() + setLoading(null)
    ↗ ↘
    FAILURE: Extract error message
         ↓
    setError() + setToast()
    setLoading(null)
    ↓
Render: <div className="error-alert"> or <Toast>
```

---

## FILES ANALYZED
- [frontend/src/App.jsx](frontend/src/App.jsx) - Main component with all API calls
- [frontend/src/main.jsx](frontend/src/main.jsx) - App initialization
- [frontend/package.json](frontend/package.json) - Dependencies
- [frontend/vite.config.js](frontend/vite.config.js) - Build config
- [backend/app.py](backend/app.py) - Backend CORS configuration

---

**Analysis Date:** March 26, 2026
**Status:** Ready for improvement planning
