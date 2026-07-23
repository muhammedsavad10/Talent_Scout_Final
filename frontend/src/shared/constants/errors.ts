export const ERROR_MESSAGES = {
  INVALID_FILE_TYPE: 'Unsupported file format. Please upload a valid PDF.',
  FILE_TOO_LARGE: 'File exceeds maximum limit of 5MB.',
  GENERIC_ERROR: 'Pipeline evaluation failed. Please try again later.',
  RATE_LIMIT_EXCEEDED: 'AI services are currently busy. Retrying transaction...',
} as const;
