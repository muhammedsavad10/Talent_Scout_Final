import { apiClient } from './apiClient';

/**
 * Common request helper.
 * Standardizes API calls, manages timeout/errors, normalization, and developer logging.
 */
export async function request({ method = 'GET', url, data, params, headers, timeout = 30000 }) {
  try {
    const config = {
      method,
      url,
      data,
      params,
      headers,
      timeout
    };

    const response = await apiClient(config);
    return response.data;
  } catch (error) {
    // Normalize errors
    const errorDetails = error.response?.data || {};
    const normalizedError = new Error(
      errorDetails.detail || 
      errorDetails.message || 
      error.message || 
      "An unexpected API error occurred."
    );
    normalizedError.status = error.response?.status || 500;
    normalizedError.raw = error;
    
    throw normalizedError;
  }
}
