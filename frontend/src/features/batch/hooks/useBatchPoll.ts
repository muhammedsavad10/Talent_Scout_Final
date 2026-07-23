import { useQuery } from '@tanstack/react-query';
import { batchService, QUERY_KEYS } from '@/shared/api';
import { env } from '@/shared/config/env';

export interface RankedCandidate {
  rank: number;
  candidate_name: string;
  filename: string;
  recommendation_tier: string;
  policy_eligible: boolean;
  overall_score: number;
  skill_match: number;
  experience_quantity: number;
  experience_relevance: number;
  experience_quality: number;
  project_complexity: number;
  critical_missing: string[];
  required_missing: string[];
  strengths: string[];
  weaknesses: string[];
  evaluation_id: string;
}

export interface BatchEvaluationStatus {
  batch_id: string;
  status: 'QUEUED' | 'PROCESSING' | 'COMPLETED' | 'COMPLETED_WITH_ERRORS' | 'FAILED';
  total: number;
  queued: number;
  processing: number;
  completed: number;
  failed: number;
  results: {
    ranked_candidates?: RankedCandidate[];
  } | null;
}

export function useBatchPoll(batchId: string | undefined) {
  return useQuery<BatchEvaluationStatus>({
    queryKey: [QUERY_KEYS.BATCH_STATUS, batchId],
    queryFn: async () => {
      if (!batchId) throw new Error('No Batch ID provided');
      const response = await batchService.getBatchStatus(batchId);
      // Cast the untyped OpenAPI schema response into the structured interface
      return response as BatchEvaluationStatus;
    },
    enabled: !!batchId,
    // Poll dynamically based on active status
    refetchInterval: (query) => {
      const data = query.state.data;
      if (!data) return env.POLLING_INTERVAL_MS;
      return ['QUEUED', 'PROCESSING'].includes(data.status) ? env.POLLING_INTERVAL_MS : false;
    },
    refetchIntervalInBackground: false,
  });
}
export default useBatchPoll;
