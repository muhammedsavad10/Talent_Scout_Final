import { useMutation } from '@tanstack/react-query';
import { assistantService } from '@/shared/api';
import { logger } from '@/shared/utils';
import { AppError } from '@/shared/api/interceptors';

export interface AssistantAskResponse {
  answer: string;
  citations: string[];
  confidence?: string;
  match_type?: string;
  interview_verification?: string;
}

export interface AssistantAskPayload {
  query: string;
  candidateId: string;
}

export function useAssistantAsk() {
  return useMutation<AssistantAskResponse, AppError, AssistantAskPayload>({
    mutationFn: async (payload: AssistantAskPayload) => {
      logger.info('Querying LangGraph Copilot Assistant Swarm. Query:', payload.query);
      const res = await assistantService.askAssistant(payload.query, payload.candidateId);
      return res as unknown as AssistantAskResponse;
    },
    onError: (err) => {
      logger.error('Failed to get answer from Copilot Swarm:', err);
    },
  });
}
export default useAssistantAsk;
