import { useQuery } from '@tanstack/react-query';
import { evaluationService, QUERY_KEYS } from '@/shared/api';
import type { CandidateEvaluationPayload } from '../types/candidate';

export function useCandidateDetail(evaluationId: string | undefined) {
  return useQuery<CandidateEvaluationPayload>({
    queryKey: [QUERY_KEYS.EVALUATION_STATUS, evaluationId],
    queryFn: async () => {
      if (!evaluationId) throw new Error('No candidate evaluation ID provided');
      const response = await evaluationService.getStatus(evaluationId);
      // Cast the response payload to the structured payload interface
      return response as unknown as CandidateEvaluationPayload;
    },
    enabled: !!evaluationId,
  });
}
export default useCandidateDetail;
