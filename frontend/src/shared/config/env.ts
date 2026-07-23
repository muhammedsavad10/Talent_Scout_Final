export const env = {
  API_BASE_URL: (import.meta.env.VITE_API_URL as string) || 'http://localhost:8000/api/v1',
  POLLING_INTERVAL_MS: Number(import.meta.env.VITE_POLLING_INTERVAL) || 1500,
  DEFAULT_MAX_FILE_SIZE_BYTES: 5 * 1024 * 1024, // 5MB
};
