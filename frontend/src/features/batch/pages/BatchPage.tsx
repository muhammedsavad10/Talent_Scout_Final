import React, { useEffect, useState } from 'react';
import { PageLayout, Loader, Heading, Text, Card, Button } from '@/shared/ui';
import { useParams, useNavigate } from 'react-router-dom';
import { useBatchPoll } from '../hooks/useBatchPoll';
import { BatchStatusCard } from '../components/BatchStatusCard';
import { RankedCandidatesList } from '../components/RankedCandidatesList';
import { ROUTES } from '@/shared/constants/routes';

export const BatchPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { data, isLoading, isError, error } = useBatchPoll(id);
  const [countdown, setCountdown] = useState<number | null>(null);

  useEffect(() => {
    if (data && ['COMPLETED', 'COMPLETED_WITH_ERRORS'].includes(data.status)) {
      setCountdown(2);
    }
  }, [data?.status]);

  useEffect(() => {
    if (countdown === null) return;
    if (countdown <= 0) {
      navigate(ROUTES.DASHBOARD);
      return;
    }
    const timer = setTimeout(() => {
      setCountdown(countdown - 1);
    }, 1000);
    return () => clearTimeout(timer);
  }, [countdown, navigate]);

  const getSub = () => {
    if (!data) return 'Polling batch details...';
    if (['QUEUED', 'PROCESSING'].includes(data.status)) return 'Evaluation in progress. Polling status...';
    return 'Evaluation complete. Review ranked profiles below.';
  };

  return (
    <PageLayout
      title={`Batch Tracker`}
      subtitle={getSub()}
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', width: '100%' }}>
        {countdown !== null && (
          <div style={{
            padding: '16px 20px',
            background: 'linear-gradient(135deg, hsla(var(--success), 0.1) 0%, hsla(var(--primary), 0.1) 100%)',
            border: '1px solid hsl(var(--success))',
            borderRadius: 'var(--radius)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            animation: 'fadeIn 0.5s ease-out'
          }}>
            <div>
              <span style={{ fontWeight: 600, color: 'hsl(var(--success))', display: 'block', fontSize: '15px' }}>
                All resumes analyzed!
              </span>
              <span style={{ fontSize: '13px', color: 'hsl(var(--muted-foreground))' }}>
                Redirecting to Comparison Dashboard in {countdown}s...
              </span>
            </div>
            <Button variant="primary" size="sm" onClick={() => navigate(ROUTES.DASHBOARD)}>
              View Dashboard Now
            </Button>
          </div>
        )}

        {isLoading && (
          <Card style={{ padding: '32px', textAlign: 'center' }}>
            <Loader size="md" />
            <Text style={{ marginTop: '16px' }}>Initializing parser pipeline instance...</Text>
          </Card>
        )}

        {isError && (
          <Card style={{ padding: '24px', border: '1px solid hsl(var(--destructive))', background: 'hsla(var(--destructive), 0.08)' }}>
            <Heading level={3} style={{ color: 'hsl(var(--destructive))' }}>Network Connection Error</Heading>
            <Text style={{ marginTop: '8px' }}>
              {error instanceof Error ? error.message : 'Unable to reach evaluation parser servers.'}
            </Text>
          </Card>
        )}

        {data && (
          <>
            <BatchStatusCard batch={data} />
            
            {/* Show rankings if completed */}
            {['COMPLETED', 'COMPLETED_WITH_ERRORS'].includes(data.status) && data.results?.ranked_candidates && (
              <RankedCandidatesList candidates={data.results.ranked_candidates} />
            )}
          </>
        )}
      </div>
    </PageLayout>
  );
};
export default BatchPage;
