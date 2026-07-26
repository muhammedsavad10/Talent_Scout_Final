import React from 'react';
import { Card, Table, Heading, Text, Button } from '@/shared/ui';
import type { RankedCandidate } from '../hooks/useBatchPoll';
import { Link } from 'react-router-dom';
import { ROUTES } from '@/shared/constants/routes';
import { Eye, ShieldCheck, ShieldAlert } from 'lucide-react';

interface RankedCandidatesListProps {
  candidates: RankedCandidate[];
}

export const RankedCandidatesList: React.FC<RankedCandidatesListProps> = ({ candidates }) => {
  if (candidates.length === 0) return null;

  const columns = [
    {
      key: 'rank',
      header: 'Rank',
      render: (c: RankedCandidate) => <span style={{ fontWeight: 700, fontSize: '14px' }}>#{c.rank}</span>
    },
    {
      key: 'candidate_name',
      header: 'Candidate & Recruiter Summary',
      render: (c: RankedCandidate) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
          <span style={{ fontWeight: 600, fontSize: '14px' }}>{c.candidate_name}</span>
          {c.explanation_narrative ? (
            <span style={{ fontSize: '11px', color: 'hsl(var(--muted-foreground))', maxWidth: '340px', lineHeight: 1.3 }}>
              {c.explanation_narrative}
            </span>
          ) : (
            <span style={{ fontSize: '11px', color: 'hsl(var(--muted-foreground))' }}>
              {c.filename}
            </span>
          )}
        </div>
      )
    },
    {
      key: 'overall_score',
      header: 'Technical Match',
      render: (c: RankedCandidate) => (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
          <span style={{
            fontWeight: 700,
            fontSize: '14px',
            color: c.overall_score >= 80 ? 'hsl(var(--success))' : c.overall_score >= 60 ? 'hsl(var(--accent))' : 'inherit'
          }}>
            {c.overall_score.toFixed(1)}%
          </span>
          {c.hiring_priority_score !== undefined && (
            <span style={{ fontSize: '11px', color: 'hsl(var(--muted-foreground))' }}>
              Priority: {c.hiring_priority_score} pts
            </span>
          )}
        </div>
      )
    },
    {
      key: 'recommendation_tier',
      header: 'Priority Tier',
      render: (c: RankedCandidate) => {
        const tier = c.hiring_priority_tier || c.recommendation_tier;
        const isTop = tier.includes('Top') || tier === 'Tier 1';
        const isStrong = tier.includes('Strong');
        return (
          <span style={{
            padding: '3px 10px',
            borderRadius: '12px',
            fontSize: '11px',
            fontWeight: 600,
            background: isTop ? 'hsla(var(--success), 0.15)' : isStrong ? 'hsla(var(--accent), 0.15)' : 'hsla(var(--foreground), 0.06)',
            color: isTop ? 'hsl(var(--success))' : isStrong ? 'hsl(var(--accent))' : 'hsl(var(--muted-foreground))',
          }}>
            {tier}
          </span>
        );
      }
    },
    {
      key: 'policy_eligible',
      header: 'Policy Match',
      render: (c: RankedCandidate) => (
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 500 }}>
          {c.policy_eligible ? (
            <>
              <ShieldCheck size={16} style={{ color: 'hsl(var(--success))' }} />
              Eligible
            </>
          ) : (
            <>
              <ShieldAlert size={16} style={{ color: 'hsl(var(--destructive))' }} />
              Disqualified
            </>
          )}
        </span>
      )
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (c: RankedCandidate) => (
        <Link to={ROUTES.CANDIDATE.replace(':id', c.evaluation_id)}>
          <Button variant="ghost" size="sm" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Eye size={14} /> View Profile
          </Button>
        </Link>
      )
    }
  ];

  return (
    <Card style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ borderBottom: '1px solid hsl(var(--border))', paddingBottom: '12px' }}>
        <Heading level={3} style={{ fontSize: '18px', margin: 0 }}>Swarm Evaluation Rankings</Heading>
        <Text variant="muted" style={{ fontSize: '13px', marginTop: '4px' }}>
          Audit-ready candidate evaluations ranked by Stage 2 Hiring Priority and Stage 1 Match Scorer.
        </Text>
      </div>
      <Table
        data={candidates}
        columns={columns}
        keyExtractor={(c) => c.evaluation_id}
      />
    </Card>
  );
};
export default RankedCandidatesList;
