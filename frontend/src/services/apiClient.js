import axios from 'axios';

// Point to the FastAPI backend
const API_BASE_URL = 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Developer Logging Interceptors
apiClient.interceptors.request.use((config) => {
  if (import.meta.env.DEV) {
    console.group(`🚀 [API Request] ${config.method?.toUpperCase()} ${config.url}`);
    if (config.data) {
      if (config.data instanceof FormData) {
        console.log("FormData Keys:", Array.from(config.data.keys()));
      } else {
        console.log("Payload:", config.data);
      }
    }
    console.groupEnd();
  }
  return config;
}, (error) => {
  console.error("❌ [API Request Error]", error);
  return Promise.reject(error);
});

apiClient.interceptors.response.use((response) => {
  if (import.meta.env.DEV) {
    console.group(`✅ [API Response] ${response.status} ${response.config.url}`);
    console.log("Data:", response.data);
    console.groupEnd();
  }
  return response;
}, (error) => {
  console.group(`❌ [API Error] ${error.response?.status || 'Network Error'} ${error.config?.url}`);
  console.error("Detail:", error.response?.data || error.message);
  console.groupEnd();
  return Promise.reject(error);
});
