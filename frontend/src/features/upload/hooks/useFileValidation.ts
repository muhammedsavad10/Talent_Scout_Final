import { useState, useCallback } from 'react';
import { ERROR_MESSAGES } from '@/shared/constants/errors';
import { env } from '@/shared/config/env';

export interface FileValidationError {
  filename: string;
  reason: string;
}

export function useFileValidation() {
  const [validationErrors, setValidationErrors] = useState<FileValidationError[]>([]);

  const validateFiles = useCallback((files: File[]): File[] => {
    const errors: FileValidationError[] = [];
    const validFiles: File[] = [];

    files.forEach((file) => {
      // 1. Mime/extension check
      const isPdf = file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf');
      if (!isPdf) {
        errors.push({
          filename: file.name,
          reason: ERROR_MESSAGES.INVALID_FILE_TYPE,
        });
        return;
      }

      // 2. Size check
      if (file.size > env.DEFAULT_MAX_FILE_SIZE_BYTES) {
        errors.push({
          filename: file.name,
          reason: ERROR_MESSAGES.FILE_TOO_LARGE,
        });
        return;
      }

      validFiles.push(file);
    });

    setValidationErrors(errors);
    return validFiles;
  }, []);

  const clearErrors = useCallback(() => {
    setValidationErrors([]);
  }, []);

  return {
    validateFiles,
    validationErrors,
    clearErrors,
  };
}
