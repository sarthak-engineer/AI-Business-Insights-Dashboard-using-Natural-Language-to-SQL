/**
 * API Configuration & Service Layer
 * Centralized backend communication with retry logic and error handling
 */

import axios from 'axios';

// ===== CONFIGURATION =====
const API_CONFIG = {
  // Backend URL - Update based on environment
  BASE_URL: import.meta.env.VITE_API_URL || "https://ai-business-insights-dashboard-using.onrender.com",
  
  // Timeout settings (ms)
  TIMEOUT: 30000,
  
  // Retry configuration
  RETRY: {
    enabled: true,
    attempts: 3,
    delay: 500, // ms, increases exponentially
    statusCodes: [408, 502, 503, 504] // Only retry transient errors
  },
  
  // Error messages
  MESSAGES: {
    CONNECTION_FAILED: 'Unable to connect to server. Please check the backend configuration.',
    TIMEOUT: 'Request timeout. Server took too long to respond.',
    SERVER_ERROR: 'Server error occurred. Please try again.',
    NETWORK_ERROR: 'Network error. Check your internet connection.',
    UNKNOWN_ERROR: 'An unexpected error occurred.'
  }
};

// Log active API URL (useful for troubleshooting deployment)
console.info(`[API] Service initialized with BASE_URL: ${API_CONFIG.BASE_URL}`);

// ===== AXIOS INSTANCE =====
const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  }
});

// ===== RETRY INTERCEPTOR =====
let retryCount = 0;

apiClient.interceptors.response.use(
  response => response, // Success - pass through
  async error => {
    const config = error.config;

    // Skip retry if already attempted max times or retry disabled
    if (!config || !API_CONFIG.RETRY.enabled || !config.retryCount) {
      config.retryCount = 0;
    }

    if (config.retryCount < API_CONFIG.RETRY.attempts) {
      config.retryCount += 1;
      
      // Only retry on specific status codes or network errors
      const shouldRetry = 
        !error.response || // Network error
        API_CONFIG.RETRY.statusCodes.includes(error.response.status);

      if (shouldRetry) {
        // Exponential backoff: delay = baseDelay * (2 ^ (attempt - 1))
        const delay = API_CONFIG.RETRY.delay * Math.pow(2, config.retryCount - 1);
        
        console.warn(
          `[API] Retry attempt ${config.retryCount}/${API_CONFIG.RETRY.attempts} ` +
          `for ${config.method.toUpperCase()} ${config.url} (waiting ${delay}ms)`
        );
        
        await new Promise(resolve => setTimeout(resolve, delay));
        return apiClient(config);
      }
    }

    // All retries exhausted or non-retryable error
    return Promise.reject(error);
  }
);

// ===== ERROR HANDLER =====
export const handleApiError = (error) => {
  console.error('[API Error]', {
    message: error.message,
    status: error.response?.status,
    data: error.response?.data,
    url: error.config?.url
  });

  let userMessage = API_CONFIG.MESSAGES.UNKNOWN_ERROR;

  if (error.code === 'ECONNABORTED') {
    userMessage = API_CONFIG.MESSAGES.TIMEOUT;
  } else if (error.code === 'ERR_NETWORK' || !error.response) {
    userMessage = API_CONFIG.MESSAGES.CONNECTION_FAILED;
  } else if (error.response?.status >= 500) {
    userMessage = error.response?.data?.message || API_CONFIG.MESSAGES.SERVER_ERROR;
  } else if (error.response?.status === 400 || error.response?.status === 422) {
    userMessage = error.response?.data?.message || 'Invalid request. Please check your input.';
  } else if (error.response?.data?.message) {
    userMessage = error.response.data.message;
  }

  return {
    success: false,
    error: userMessage,
    status: error.response?.status,
    isConnectionError: !error.response,
    originalError: error
  };
};

// ===== API ENDPOINTS =====
export const api = {
  // Query execution
  query: (queryData) => 
    apiClient.post('/query', queryData),

  // Drill-down queries
  drillDown: (queryData, drillData) =>
    apiClient.post('/query', { ...queryData, drill_down: drillData }),

  // Analytics endpoints
  analytics: (endpoint) =>
    apiClient.get(`/analytics/${endpoint}`),

  // File upload
  upload: (formData) =>
    apiClient.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),

  // Reset to demo
  reset: () =>
    apiClient.post('/reset'),

  // Export data
  export: (data) =>
    apiClient.post('/export', { data }, { responseType: 'blob' })
};

// ===== UTILITY FUNCTION =====
export const getBackendUrl = () => API_CONFIG.BASE_URL;

export default apiClient;
