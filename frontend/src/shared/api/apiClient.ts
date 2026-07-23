import axios from 'axios';
import { env } from '../config/env';

export const apiClient = axios.create({
  baseURL: env.API_BASE_URL,
  timeout: 15000,
  withCredentials: true,
});
