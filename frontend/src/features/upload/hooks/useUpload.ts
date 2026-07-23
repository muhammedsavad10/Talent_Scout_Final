import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { batchService } from '@/shared/api';
import { ROUTES } from '@/shared/constants/routes';
import { logger } from '@/shared/utils';
import type { paths } from '@/generated/api';
import { AppError } from '@/shared/api/interceptors';
import { useAppStore } from '@/shared/store/useAppStore';

type SubmitBatchResponse = paths['/api/v1/evaluate/batch']['post']['responses']['200']['content']['application/json'];

export function useUpload() {
  const navigate = useNavigate();
  const setLastBatchId = useAppStore((state) => state.setLastBatchId);

  return useMutation<SubmitBatchResponse, AppError, { files: File[]; jobDescription: string; jdSkills: string[] }>({
    mutationFn: async (payload: { files: File[]; jobDescription: string; jdSkills: string[] }) => {
      logger.info('Submitting resume batch files for multi-agent swarm evaluation...');
      const formData = new FormData();
      payload.files.forEach((file) => formData.append('files', file));
      formData.append('job_description', payload.jobDescription);
      formData.append('jd_skills', payload.jdSkills.join(', '));
      
      return batchService.submitBatch(formData);
    },
    onSuccess: (data) => {
      const result = data as { batch_id: string };
      logger.info('Batch successfully submitted and queued. Batch ID:', result.batch_id);
      setLastBatchId(result.batch_id);
      navigate(ROUTES.BATCH.replace(':id', result.batch_id));
    },
    onError: (err) => {
      logger.error('Failed to submit resume batch:', err);
    },
  });
}
export default useUpload;
