import type { paths } from '../../../generated/api';
import { apiClient } from '../apiClient';

type AskAssistantResponse = paths['/api/v1/evaluation/assistant/ask']['post']['responses']['200']['content']['application/json'];

export const assistantService = {
  askAssistant: async (query: string, candidateId: string): Promise<AskAssistantResponse> => {
    const res = await apiClient.post<AskAssistantResponse>('/evaluation/assistant/ask', {
      query,
      candidate_id: candidateId,
    });
    return res.data;
  },
};
export default assistantService;
