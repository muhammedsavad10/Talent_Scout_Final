import { apiClient } from '@/shared/api/apiClient';
import type { LoginCredentials, AuthResponse, User } from '../types/auth';

export const loginApi = async (credentials: LoginCredentials): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
  return response.data;
};

export const fetchCurrentUserApi = async (token?: string): Promise<User> => {
  const options = token ? { headers: { Authorization: `Bearer ${token}` } } : {};
  const response = await apiClient.get<User>('/auth/me', options);
  return response.data;
};

export const refreshTokenApi = async (refreshToken: string): Promise<AuthResponse> => {
  const response = await apiClient.post<AuthResponse>('/auth/refresh', { refresh_token: refreshToken });
  return response.data;
};

export const logoutApi = async (refreshToken?: string): Promise<void> => {
  await apiClient.post('/auth/logout', refreshToken ? { refresh_token: refreshToken } : {});
};
