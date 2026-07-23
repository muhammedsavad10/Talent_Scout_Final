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
      render: (c: RankedCandidate) => <span style={{ fontWeight: 600 }}>#{c.rank}</span>
    },
    {
      key: 'candidate_name',
      header: 'Candidate Name',
      render: (c: RankedCandidate) => <span style={{ fontWeight: 500 }}>{c.candidate_name}</span>
    },
    {
      key: 'overall_score',
      header: 'Overall Score',
      render: (c: RankedCandidate) => (
        <span style={{
          fontWeight: 600,
          color: c.overall_score >= 80 ? 'hsl(var(--success))' : c.overall_score >= 60 ? 'hsl(var(--accent))' : 'inherit'
        }}>
          {c.overall_score}%
        </span>
      )
    },
    {
      key: 'recommendation_tier',
      header: 'Tier',
      render: (c: RankedCandidate) => (
        <span style={{
          padding: '2px 8px',
          borderRadius: '12px',
          fontSize: '11px',
          fontWeight: 600,
          background: c.recommendation_tier === 'Tier 1' ? 'hsla(var(--success), 0.12)' : 'hsla(var(--foreground), 0.04)',
          color: c.recommendation_tier === 'Tier 1' ? 'hsl(var(--success))' : 'hsl(var(--muted-foreground))',
        }}>
          {c.recommendation_tier}
        </span>
      )
    },
    {
      key: 'policy_eligible',
      header: 'Policy Match',
      render: (c: RankedCandidate) => (
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}>
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
          Compare parsed profiles evaluated through the comparator scoring layers.
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
