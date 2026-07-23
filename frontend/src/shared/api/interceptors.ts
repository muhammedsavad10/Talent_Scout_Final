import { AxiosError } from 'axios';
import type { InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { apiClient } from './apiClient';
import { ERROR_MESSAGES } from '../constants/errors';
import { sentry } from '@/shared/utils';

export class AppError extends Error {
  public readonly title: string;
  public readonly statusCode: number | null;
  public readonly retryable: boolean;

  constructor(title: string, message: string, statusCode: number | null = null, retryable = false) {
    super(message);
    this.name = 'AppError';
    this.title = title;
    this.statusCode = statusCode;
    this.retryable = retryable;
    Object.setPrototypeOf(this, AppError.prototype);
  }
}

const extractErrorMessage = (data: any): string => {
  if (!data) return ERROR_MESSAGES.GENERIC_ERROR;
  if (typeof data === 'string') return data;
  
  // 1. If detail exists
  if (data.detail !== undefined && data.detail !== null) {
    if (typeof data.detail === 'string') return data.detail;
    if (Array.isArray(data.detail)) {
      const first = data.detail[0];
      if (first && typeof first === 'object') {
        return (first as any).msg || JSON.stringify(first);
      }
      return JSON.stringify(data.detail);
    }
    if (typeof data.detail === 'object') {
      return (data.detail as any).description || (data.detail as any).message || JSON.stringify(data.detail);
    }
  }

  // 2. If description exists
  if (typeof data.description === 'string') return data.description;
  
  // 3. If message exists
  if (typeof data.message === 'string') return data.message;
  if (typeof data.message === 'object' && data.message !== null) {
    return (data.message as any).description || (data.message as any).message || JSON.stringify(data.message);
  }

  // 4. If error object exists
  if (typeof data.error === 'string') return data.error;
  if (typeof data.error === 'object' && data.error !== null) {
    return (data.error as any).description || (data.error as any).message || JSON.stringify(data.error);
  }

  // 5. Direct properties check
  if (typeof data.description === 'object' && data.description !== null) {
    return JSON.stringify(data.description);
  }

  const rawDesc = data.description || data.message || data.error;
  if (typeof rawDesc === 'string') return rawDesc;

  return JSON.stringify(data);
};

const mapAxiosErrorToAppError = (error: AxiosError): AppError => {
  const status = error.response?.status ?? null;
  const errorData = error.response?.data;
  
  let title = 'Connection Failure';
  let message: string = ERROR_MESSAGES.GENERIC_ERROR;
  let retryable = false;

  if (status === 400) {
    title = 'Bad Request';
    message = extractErrorMessage(errorData);
  } else if (status === 413) {
    title = 'Payload Too Large';
    message = ERROR_MESSAGES.FILE_TOO_LARGE;
  } else if (status === 415) {
    title = 'Unsupported Type';
    message = extractErrorMessage(errorData);
  } else if (status === 422) {
    title = 'Validation Schema Error';
    message = extractErrorMessage(errorData);
  } else if (status === 429) {
    title = 'Rate Limit Exceeded';
    message = ERROR_MESSAGES.RATE_LIMIT_EXCEEDED;
    retryable = true;
  } else if (status && status >= 500) {
    title = 'Server Error';
    message = extractErrorMessage(errorData) || 'Third-party parser nodes failed. Please re-upload.';
    retryable = true;
  }

  const appErr = new AppError(title, message, status, retryable);
  
  // Track backend and network gateway crashes through Sentry
  sentry.captureException(appErr, {
    axiosMessage: error.message,
    url: error.config?.url,
    method: error.config?.method,
  });

  return appErr;
};

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
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
  (error: AxiosError) => {
    return Promise.reject(mapAxiosErrorToAppError(error));
  }
);
export default apiClient;
