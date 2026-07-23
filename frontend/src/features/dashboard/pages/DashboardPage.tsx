import React, { useState, useMemo } from 'react';
import { PageLayout, Card, Heading, Text, Table, Button, EmptyState, Loader } from '@/shared/ui';
import { Link } from 'react-router-dom';
import { ROUTES } from '@/shared/constants/routes';
import { useAppStore } from '@/shared/store/useAppStore';
import { useBatchPoll } from '@/features/batch/hooks/useBatchPoll';
import type { RankedCandidate } from '@/features/batch/hooks/useBatchPoll';
import { Search, Filter, ShieldCheck, ShieldAlert, Users, Award, AlertCircle, TrendingUp, ArrowUpDown, Eye } from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const lastBatchId = useAppStore((state) => state.lastBatchId);
  const { data, isLoading, isError, error } = useBatchPoll(lastBatchId ?? undefined);

  // Search & Filtering State
  const [searchTerm, setSearchTerm] = useState('');
  const [tierFilter, setTierFilter] = useState<string>('ALL');
  const [policyFilter, setPolicyFilter] = useState<string>('ALL');
  
  // Sorting State
  const [sortKey, setSortKey] = useState<'rank' | 'overall_score'>('rank');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');

  const candidates = useMemo(() => {
    return data?.results?.ranked_candidates ?? [];
  }, [data]);

  // Compute metrics/KPIs
  const metrics = useMemo(() => {
    if (candidates.length === 0) return { total: 0, avgScore: 0, recommended: 0, disqualified: 0 };
    const total = candidates.length;
    const avgScore = Math.round(candidates.reduce((sum, c) => sum + c.overall_score, 0) / total);
    const recommended = candidates.filter(c => c.recommendation_tier === 'Tier 1' || c.recommendation_tier === 'Hire').length;
    const disqualified = candidates.filter(c => !c.policy_eligible).length;
    return { total, avgScore, recommended, disqualified };
  }, [candidates]);

  // Filter & Sort candidates
  const processedCandidates = useMemo(() => {
    let result = [...candidates];

    // Search filter
    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase();
      result = result.filter(c => 
        c.candidate_name.toLowerCase().includes(term) ||
        c.filename.toLowerCase().includes(term)
      );
    }

    // Tier filter
    if (tierFilter !== 'ALL') {
      result = result.filter(c => c.recommendation_tier === tierFilter);
    }

    // Policy filter
    if (policyFilter !== 'ALL') {
      const isEligible = policyFilter === 'ELIGIBLE';
      result = result.filter(c => c.policy_eligible === isEligible);
    }

    // Sorting logic
    result.sort((a, b) => {
      let valA = a[sortKey];
      let valB = b[sortKey];

      if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
      if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return result;
  }, [candidates, searchTerm, tierFilter, policyFilter, sortKey, sortOrder]);

  const toggleSort = (key: 'rank' | 'overall_score') => {
    if (sortKey === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortOrder('asc');
    }
  };

  if (!lastBatchId) {
    return (
      <PageLayout title="Recruit Comparison Dashboard" subtitle="Compare evaluated resume swarms against job requirements.">
        <EmptyState
          title="No Active Evaluation Found"
          description="Upload job description details and multiple resume PDFs to kickstart the multi-agent ranking pipeline."
          action={
            <Link to={ROUTES.UPLOAD}>
              <Button variant="primary">Start New Evaluation</Button>
            </Link>
          }
        />
      </PageLayout>
    );
  }

  const columns = [
    {
      key: 'rank',
      header: 'Rank',
      render: (c: RankedCandidate) => <span style={{ fontWeight: 600 }}>#{c.rank}</span>
    },
    {
      key: 'candidate_name',
      header: 'Candidate Name',
      render: (c: RankedCandidate) => (
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <span style={{ fontWeight: 500, color: '#ffffff' }}>{c.candidate_name}</span>
          <span style={{ fontSize: '11px', color: 'hsl(var(--muted-foreground))' }}>{c.filename}</span>
        </div>
      )
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
      header: 'Recommendation Tier',
      render: (c: RankedCandidate) => (
        <span style={{
          padding: '4px 10px',
          borderRadius: '12px',
          fontSize: '11px',
          fontWeight: 600,
          background: c.recommendation_tier === 'Tier 1' || c.recommendation_tier === 'Hire' ? 'hsla(var(--success), 0.12)' : 'hsla(var(--foreground), 0.04)',
          color: c.recommendation_tier === 'Tier 1' || c.recommendation_tier === 'Hire' ? 'hsl(var(--success))' : 'hsl(var(--muted-foreground))',
        }}>
          {c.recommendation_tier}
        </span>
      )
    },
    {
      key: 'policy_eligible',
      header: 'Gate Eligibility',
      render: (c: RankedCandidate) => (
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '13px' }}>
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
      header: 'Action',
      render: (c: RankedCandidate) => (
        <Link to={ROUTES.CANDIDATE.replace(':id', c.evaluation_id)}>
          <Button variant="ghost" size="sm" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Eye size={14} /> View Details
          </Button>
        </Link>
      )
    }
  ];

  return (
    <PageLayout
      title="Recruit Comparison Dashboard"
      subtitle="Compare evaluated candidate resumes using multi-agent metrics."
      actions={
        <div style={{ display: 'flex', gap: '12px' }}>
          <Link to={ROUTES.BATCH.replace(':id', lastBatchId)}>
            <Button variant="secondary">Watch Process</Button>
          </Link>
          <Link to={ROUTES.UPLOAD}>
            <Button variant="primary">New Upload</Button>
          </Link>
        </div>
      }
    >
      {isLoading && (
        <Card style={{ padding: '32px', textAlign: 'center' }}>
          <Loader size="md" />
          <Text style={{ marginTop: '16px' }}>Fetching latest evaluation data...</Text>
        </Card>
      )}

      {isError && (
        <Card style={{ padding: '24px', border: '1px solid hsl(var(--destructive))', background: 'hsla(var(--destructive), 0.08)' }}>
          <Heading level={3} style={{ color: 'hsl(var(--destructive))' }}>Retrieval Error</Heading>
          <Text style={{ marginTop: '8px' }}>{error instanceof Error ? error.message : 'Unable to query batch evaluations.'}</Text>
        </Card>
      )}

      {data && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '28px', width: '100%' }}>
          
          {/* KPI Dashboard Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', width: '100%' }}>
            <Card hoverable>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text variant="muted">Evaluated Candidates</Text>
                <Users size={20} style={{ color: 'hsl(var(--primary))' }} />
              </div>
              <Heading level={2} style={{ fontSize: '32px', marginTop: '12px', marginBottom: 0 }}>{metrics.total}</Heading>
            </Card>

            <Card hoverable>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text variant="muted">Average Score</Text>
                <TrendingUp size={20} style={{ color: 'hsl(var(--accent))' }} />
              </div>
              <Heading level={2} style={{ fontSize: '32px', marginTop: '12px', marginBottom: 0 }}>{metrics.avgScore}%</Heading>
            </Card>

            <Card hoverable>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text variant="muted">Recommended (Tier 1)</Text>
                <Award size={20} style={{ color: 'hsl(var(--success))' }} />
              </div>
              <Heading level={2} style={{ fontSize: '32px', marginTop: '12px', marginBottom: 0, color: 'hsl(var(--success))' }}>{metrics.recommended}</Heading>
            </Card>

            <Card hoverable>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text variant="muted">Disqualified</Text>
                <AlertCircle size={20} style={{ color: 'hsl(var(--destructive))' }} />
              </div>
              <Heading level={2} style={{ fontSize: '32px', marginTop: '12px', marginBottom: 0, color: 'hsl(var(--destructive))' }}>{metrics.disqualified}</Heading>
            </Card>
          </div>

          {/* Filters controls bar */}
          <Card style={{ padding: '16px 20px' }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '16px', alignItems: 'center', justifyContent: 'space-between' }}>
              
              {/* Search */}
              <div style={{ position: 'relative', flex: 1, minWidth: '240px' }}>
                <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'hsl(var(--muted-foreground))' }} />
                <input
                  type="text"
                  placeholder="Search candidates or files..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 12px 10px 38px',
                    background: 'hsl(var(--secondary))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: 'var(--radius)',
                    color: '#ffffff',
                    fontSize: '13px',
                    outline: 'none',
                  }}
                />
              </div>

              {/* Filters dropdowns */}
              <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Filter size={14} style={{ color: 'hsl(var(--muted-foreground))' }} />
                  <select
                    value={tierFilter}
                    onChange={(e) => setTierFilter(e.target.value)}
                    style={{
                      padding: '8px 12px',
                      background: 'hsl(var(--secondary))',
                      border: '1px solid hsl(var(--border))',
                      borderRadius: 'var(--radius)',
                      color: '#ffffff',
                      fontSize: '13px',
                      outline: 'none',
                    }}
                  >
                    <option value="ALL">All Tiers</option>
                    <option value="Tier 1">Tier 1</option>
                    <option value="Tier 2">Tier 2</option>
                    <option value="Tier 3">Tier 3</option>
                  </select>
                </div>

                <select
                  value={policyFilter}
                  onChange={(e) => setPolicyFilter(e.target.value)}
                  style={{
                    padding: '8px 12px',
                    background: 'hsl(var(--secondary))',
                    border: '1px solid hsl(var(--border))',
                    borderRadius: 'var(--radius)',
                    color: '#ffffff',
                    fontSize: '13px',
                    outline: 'none',
                  }}
                >
                  <option value="ALL">All Eligibility</option>
                  <option value="ELIGIBLE">Eligible Only</option>
                  <option value="DISQUALIFIED">Disqualified Only</option>
                </select>

                {/* Sort Toggle Buttons */}
                <div style={{ display: 'flex', gap: '6px' }}>
                  <Button
                    variant={sortKey === 'rank' ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => toggleSort('rank')}
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}
                  >
                    Rank <ArrowUpDown size={12} />
                  </Button>
                  <Button
                    variant={sortKey === 'overall_score' ? 'primary' : 'ghost'}
                    size="sm"
                    onClick={() => toggleSort('overall_score')}
                    style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px' }}
                  >
                    Score <ArrowUpDown size={12} />
                  </Button>
                </div>
              </div>

            </div>
          </Card>

          {/* Sticky header ranked list grid */}
          <div style={{ position: 'relative', width: '100%' }}>
            <Table
              data={processedCandidates}
              columns={columns}
              keyExtractor={(c) => c.evaluation_id}
            />
          </div>

        </div>
      )}
    </PageLayout>
  );
};
export default DashboardPage;
