import { apiClient } from './apiClient';
import type { InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';

export interface AppError {
  message: string;
  statusCode?: number | undefined;
  code?: string | undefined;
  raw?: unknown;
}

export const mapAxiosErrorToAppError = (error: AxiosError): AppError => {
  const statusCode = error.response?.status;
  const data = error.response?.data as { detail?: string; message?: string } | undefined;
  
  let message = 'An unexpected error occurred. Please try again.';
  
  if (data?.detail) {
    message = data.detail;
  } else if (data?.message) {
    message = data.message;
  } else if (error.message) {
    message = error.message;
  }

  return {
    message,
    statusCode,
    code: error.code,
    raw: error,
  };
};

let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string) => void; reject: (error: any) => void }> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((promise) => {
    if (error) {
      promise.reject(error);
    } else {
      promise.resolve(token!);
    }
  });
  failedQueue = [];
};

const isAuthEndpoint = (url: string = ''): boolean => {
  return (
    url.includes('/auth/login') ||
    url.includes('/auth/token') ||
    url.includes('/auth/refresh') ||
    url.includes('/auth/logout')
  );
};

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const url = config.url || '';
    // Do NOT attach Authorization header to authentication endpoints to prevent credential leakage or loops
    if (!isAuthEndpoint(url)) {
      const token = localStorage.getItem('talentscout_access_token');
      if (token && config.headers) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(mapAxiosErrorToAppError(error));
  }
);

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };
    const status = error.response?.status;
    const url = originalRequest?.url || '';

    // NEVER attempt token refresh for authentication endpoints (/auth/login, /auth/token, /auth/refresh, /auth/logout)
    if (status === 401 && !originalRequest._retry && !isAuthEndpoint(url)) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token: string) => {
              if (originalRequest.headers) {
                originalRequest.headers.Authorization = `Bearer ${token}`;
              }
              resolve(apiClient(originalRequest));
            },
            reject: (err: any) => {
              reject(err);
            },
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const { useAuthStore } = await import('@/features/auth/store/useAuthStore');
        const refreshed = await useAuthStore.getState().refreshSession();
        if (refreshed) {
          const newToken = localStorage.getItem('talentscout_access_token');
          if (newToken && originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
          }
          processQueue(null, newToken);
          return apiClient(originalRequest);
        } else {
          processQueue(new Error('Refresh session expired'), null);
        }
      } catch (refreshErr) {
        processQueue(refreshErr, null);
        const { useAuthStore } = await import('@/features/auth/store/useAuthStore');
        await useAuthStore.getState().logout();
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(mapAxiosErrorToAppError(error));
  }
);

export default apiClient;
