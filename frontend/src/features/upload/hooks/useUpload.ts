import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { batchService } from '@/shared/api';
import { ROUTES } from '@/shared/constants/routes';
import { logger } from '@/shared/utils';
import type { paths } from '@/generated/api';
import type { AppError } from '@/shared/api/interceptors';
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
      
      const result = await batchService.submitBatch(formData);

      console.log("========== UPLOAD RESPONSE ==========");
      console.log(result);
      console.log("Batch ID:", result?.batch_id);
      console.log("Status:", result?.status);
      console.log("====================================");

      return result;
    },
    onSuccess: (data) => {
    console.log("===== onSuccess =====");
    console.log(data);

    const result = data as { batch_id: string };

    console.log("Batch ID:", result.batch_id);

    setLastBatchId(result.batch_id);

   console.log("Navigating to:",
    ROUTES.BATCH.replace(':id', result.batch_id)
  );

  navigate(ROUTES.BATCH.replace(':id', result.batch_id));

  console.log("Navigation called");
},
    onError: (err) => {
  console.error("UPLOAD ERROR:", err);
},
  });
}
export default useUpload;
