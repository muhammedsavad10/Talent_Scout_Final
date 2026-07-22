import axios from 'axios';

// Point to the FastAPI backend
const API_BASE_URL = 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checkHealth = async () => {
  try {
    const response = await apiClient.get('/health/databases');
    return response.data;
  } catch (error) {
    console.error("Backend connection failed", error);
    throw error;
  }
};
