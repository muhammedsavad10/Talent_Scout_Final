import type { paths } from '../../../generated/api';
import { apiClient } from '../apiClient';

type EvaluateResponse = paths['/api/v1/evaluation/evaluate']['post']['responses']['200']['content']['application/json'];
type StatusResponse = paths['/api/v1/evaluation/status/{evaluation_id}']['get']['responses']['200']['content']['application/json'];
type EmailGenerateResponse = paths['/api/v1/evaluation/email/generate']['post']['responses']['200']['content']['application/json'];

export const evaluationService = {
  evaluate: async (formData: FormData): Promise<EvaluateResponse> => {
    const res = await apiClient.post<EvaluateResponse>('/evaluation/evaluate', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  getStatus: async (evaluationId: string): Promise<StatusResponse> => {
    const res = await apiClient.get<StatusResponse>(`/evaluation/status/${evaluationId}`);
    return res.data;
  },

  generateEmail: async (candidateId: string, templateType: string = 'interview_invitation'): Promise<EmailGenerateResponse> => {
    const res = await apiClient.post<EmailGenerateResponse>('/evaluation/email/generate', {
      candidate_id: candidateId,
      evaluation_id: candidateId,
      template_type: templateType,
    });
    return res.data;
  },
};
export default evaluationService;
