import React from 'react';
import { Card, Heading, Text, Button, Loader } from '@/shared/ui';
import type { BatchEvaluationStatus } from '../hooks/useBatchPoll';
import { CheckCircle2, AlertTriangle, XCircle, Clock } from 'lucide-react';
import { Link } from 'react-router-dom';
import { ROUTES } from '@/shared/constants/routes';

interface BatchStatusCardProps {
  batch: BatchEvaluationStatus;
}

export const BatchStatusCard: React.FC<BatchStatusCardProps> = ({ batch }) => {
  const { status, total, completed, failed } = batch;

  // Calculate percentage progress
  const progressPercent = total > 0 ? Math.round((completed / total) * 100) : 0;

  const renderStatusDetails = () => {
    switch (status) {
      case 'QUEUED':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', padding: '24px 0' }}>
            <Clock size={48} style={{ color: 'hsl(var(--warning))', animation: 'pulse 2s infinite' }} />
            <div style={{ textAlign: 'center' }}>
              <Heading level={2} style={{ fontSize: '20px' }}>Swarm Ingestion Queued</Heading>
              <Text variant="muted" style={{ marginTop: '8px' }}>
                Waiting to lock parser instances and downstream vector collections...
              </Text>
            </div>
            <Loader size="sm" />
          </div>
        );

      case 'PROCESSING':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', padding: '12px 0' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Loader size="sm" />
                <Heading level={3} style={{ fontSize: '16px', margin: 0 }}>Evaluating Resumes...</Heading>
              </div>
              <Text style={{ fontWeight: 600 }}>{progressPercent}%</Text>
            </div>
            
            {/* Progress Bar container */}
            <div style={{ width: '100%', height: '8px', background: 'hsl(var(--secondary))', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{
                width: `${progressPercent}%`,
                height: '100%',
                background: 'linear-gradient(90deg, hsl(var(--primary)) 0%, hsl(var(--accent)) 100%)',
                transition: 'width 0.4s ease-out',
                borderRadius: '4px',
              }} />
            </div>
            
            <Text variant="muted" style={{ textAlign: 'center', fontSize: '13px' }}>
              Analyzing resume {completed + 1} of {total} candidates against target job descriptions.
            </Text>
          </div>
        );

      case 'COMPLETED':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', padding: '16px 0' }}>
            <CheckCircle2 size={48} style={{ color: 'hsl(var(--success))' }} />
            <div style={{ textAlign: 'center' }}>
              <Heading level={2} style={{ fontSize: '20px' }}>Evaluation Complete</Heading>
              <Text variant="muted" style={{ marginTop: '6px' }}>
                All {total} candidate profiles processed and saved successfully.
              </Text>
            </div>
            <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
              <Link to={ROUTES.DASHBOARD}>
                <Button variant="primary">View Candidate Rankings</Button>
              </Link>
            </div>
          </div>
        );

      case 'COMPLETED_WITH_ERRORS':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', padding: '16px 0' }}>
            <AlertTriangle size={48} style={{ color: 'hsl(var(--warning))' }} />
            <div style={{ textAlign: 'center' }}>
              <Heading level={2} style={{ fontSize: '20px' }}>Completed with Warnings</Heading>
              <Text variant="muted" style={{ marginTop: '6px' }}>
                Processed {completed} of {total} resumes successfully ({failed} files failed validation or extraction).
              </Text>
            </div>
            <div style={{ display: 'flex', gap: '12px', marginTop: '12px' }}>
              <Link to={ROUTES.DASHBOARD}>
                <Button variant="primary">View Successful Rankings</Button>
              </Link>
              <Link to={ROUTES.UPLOAD}>
                <Button variant="secondary">Re-upload Failures</Button>
              </Link>
            </div>
          </div>
        );

      case 'FAILED':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '16px', padding: '16px 0' }}>
            <XCircle size={48} style={{ color: 'hsl(var(--destructive))' }} />
            <div style={{ textAlign: 'center' }}>
              <Heading level={2} style={{ fontSize: '20px' }}>Evaluation Pipeline Failed</Heading>
              <Text variant="muted" style={{ marginTop: '6px' }}>
                Fatal error: Downstream AI completions or Qdrant index servers are offline.
              </Text>
            </div>
            <Link to={ROUTES.UPLOAD} style={{ marginTop: '12px' }}>
              <Button variant="secondary">Try Again</Button>
            </Link>
          </div>
        );
    }
  };

  return (
    <Card style={{ padding: '32px' }}>
      {renderStatusDetails()}
      
      {/* Sub metrics layout */}
      <div style={{
        display: 'flex',
        justifyContent: 'space-around',
        borderTop: '1px solid hsl(var(--border))',
        paddingTop: '24px',
        marginTop: '8px',
        textAlign: 'center',
      }}>
        <div>
          <Text variant="muted" style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Total Resumes</Text>
          <Heading level={3} style={{ fontSize: '18px', marginTop: '4px' }}>{total}</Heading>
        </div>
        <div>
          <Text variant="muted" style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Completed</Text>
          <Heading level={3} style={{ fontSize: '18px', marginTop: '4px', color: 'hsl(var(--success))' }}>{completed}</Heading>
        </div>
        <div>
          <Text variant="muted" style={{ fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Failed</Text>
          <Heading level={3} style={{ fontSize: '18px', marginTop: '4px', color: failed > 0 ? 'hsl(var(--destructive))' : 'inherit' }}>{failed}</Heading>
        </div>
      </div>
    </Card>
  );
};
export default BatchStatusCard;
