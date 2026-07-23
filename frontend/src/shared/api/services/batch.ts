import type { paths } from '../../../generated/api';
import { apiClient } from '../apiClient';

type SubmitBatchResponse = paths['/api/v1/evaluate/batch']['post']['responses']['200']['content']['application/json'];
type PollBatchResponse = paths['/api/v1/evaluate/batch/{batch_id}']['get']['responses']['200']['content']['application/json'];

export const batchService = {
  submitBatch: async (formData: FormData): Promise<SubmitBatchResponse> => {
    const res = await apiClient.post<SubmitBatchResponse>('/evaluate/batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  getBatchStatus: async (batchId: string): Promise<PollBatchResponse> => {
    const res = await apiClient.get<PollBatchResponse>(`/evaluate/batch/${batchId}`);
    return res.data;
  },
};
export default batchService;
