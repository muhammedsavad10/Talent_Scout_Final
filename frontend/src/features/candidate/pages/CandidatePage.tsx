import React, { useState } from 'react';
import { PageLayout, Card, Heading, Text, Loader, Button } from '@/shared/ui';
import { useParams, Link } from 'react-router-dom';
import { useCandidateDetail } from '../hooks/useCandidateDetail';
import { EvidenceSection } from '../components/EvidenceSection';
import { EvidenceTimeline } from '../components/EvidenceTimeline';
import { InterviewPrep } from '../components/InterviewPrep';
import { AssistantDrawer } from '@/features/assistant/components/AssistantDrawer';
import { ROUTES } from '@/shared/constants/routes';
import {
  ArrowLeft,
  ShieldCheck,
  ShieldAlert,
  Mail,
  Phone,
  ExternalLink,
  MessageSquare
} from 'lucide-react';

export const CandidatePage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data, isLoading, isError, error } = useCandidateDetail(id);
  const [activeTab, setActiveTab] = useState<'overview' | 'skills' | 'evidence' | 'interview' | 'insights' | 'timeline' | 'breakdown'>('overview');
  const [assistantOpen, setAssistantOpen] = useState(false);

  // Recruiter Decision Panel Local Storage State
  const [recruiterDecision, setRecruiterDecision] = useState<'Hire' | 'Interview' | 'Hold' | 'Reject' | ''>(() => {
    return id ? (localStorage.getItem(`decision-${id}`) as any) || '' : '';
  });
  const [overrideReason] = useState<string>(() => {
    return id ? localStorage.getItem(`reason-${id}`) || 'Strong Technical Fit' : 'Strong Technical Fit';
  });
  const [recruiterNotes, setRecruiterNotes] = useState(() => {
    return id ? localStorage.getItem(`notes-${id}`) || '' : '';
  });
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSaveDecision = () => {
    if (!id) return;
    localStorage.setItem(`decision-${id}`, recruiterDecision);
    localStorage.setItem(`reason-${id}`, overrideReason);
    localStorage.setItem(`notes-${id}`, recruiterNotes);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const handleCitationClick = (citationText: string) => {
    setActiveTab('evidence');
    setAssistantOpen(false);
    
    setTimeout(() => {
      const elements = Array.from(document.querySelectorAll('span'));
      const matchingElement = elements.find(el => {
        const text = el.textContent || '';
        return text && text.length > 2 && citationText.toLowerCase().includes(text.toLowerCase());
      }) as HTMLElement | undefined;
      
      if (matchingElement) {
        matchingElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        const cardElement = (matchingElement.closest('.card-primitive') || matchingElement.parentElement) as HTMLElement | null;
        if (cardElement) {
          const originalShadow = cardElement.style.boxShadow;
          cardElement.style.boxShadow = '0 0 16px hsl(var(--primary))';
          cardElement.style.transition = 'box-shadow 0.3s ease';
          setTimeout(() => {
            cardElement.style.boxShadow = originalShadow;
          }, 2500);
        }
      }
    }, 150);
  };

  // Loading and Error States
  if (isLoading) {
    return (
      <PageLayout title="Evaluating Candidate Profile..." subtitle="Retrieving candidate metrics and evidence trace.">
        <Card style={{ padding: '40px', textAlign: 'center' }}>
          <Loader size="md" />
          <Text style={{ marginTop: '16px' }}>Querying candidate evaluation index...</Text>
        </Card>
      </PageLayout>
    );
  }

  if (isError || !data) {
    return (
      <PageLayout title="Evaluation Detail Error" subtitle="Unable to load the candidate profile.">
        <Card style={{ padding: '24px', border: '1px solid hsl(var(--destructive))', background: 'hsla(var(--destructive), 0.08)' }}>
          <Heading level={3} style={{ color: 'hsl(var(--destructive))' }}>Evaluation Profile Not Found</Heading>
          <Text style={{ marginTop: '8px' }}>
            {error instanceof Error ? error.message : 'Record may have expired or been deleted.'}
          </Text>
          <Link to={ROUTES.DASHBOARD} style={{ marginTop: '16px', display: 'inline-block' }}>
            <Button variant="secondary">Back to Dashboard</Button>
          </Link>
        </Card>
      </PageLayout>
    );
  }

  const { result } = data;
  const name = result.personal_info?.name || 'Unknown Candidate';
  const targetRole = (result as any).job_profile || (result.decision_engine as any)?.target_role || 'Software Engineer';
  const overallScore = result.overall_score || (result.decision_engine as any)?.overall_score || 0;
  const hiringRecommendation = result.recommendation?.hiring_recommendation || 'Interview';
  const meetsPolicy = result.decision_engine?.policy_eligible ?? false;
  const filename = (data as any).filename || (result as any).filename || 'resume.pdf';

  const career = result.evidence?.career_timeline || [];
  const candidateFacts = result.candidate_facts || {};
  const currentPosition = candidateFacts.current_employer || (career[0] ? `${career[0].role || 'Engineer'} at ${career[0].company || 'Company'}` : 'Not Specified');

  // Contacts
  const email = result.contacts?.email || result.personal_info?.email;
  const phone = result.contacts?.phone || result.personal_info?.phone;
  const links = (result.personal_info as any)?.links || [];

  // Core Deterministic Backend Scoring Metrics (Explicit Keyword Match 40%, Semantic Similarity 60%)
  const dimensionScores = result.decision_engine?.dimension_scores || {};
  const explicitKeywordMatchScore = dimensionScores.explicit_keyword_match?.score ?? dimensionScores.skill_match?.score ?? 0;
  const semanticSimilarityScore = dimensionScores.semantic_similarity?.score ?? dimensionScores.role_fit?.score ?? 0;

  // Skills
  const matchedSkills = result.matched_skills || [];
  const inferredSkills = (result as any).evidence_states?.INFERRED || (result.decision_engine as any)?.evidence_states?.INFERRED || [];
  const missingSkills = result.missing_skills || [];
  const criticalMissing = result.recommendation_basis?.critical_missing_skills || [];
  const allParsedSkills = ((result as any).parsed_resume)?.hard_skills || [];
  const additionalSkills = allParsedSkills.filter((s: string) => !matchedSkills.includes(s) && !inferredSkills.includes(s));

  // Strengths & Weaknesses
  const strengths = result.recommendation_basis?.strengths || result.recommendation?.candidate_highlights || [];
  const weaknesses = result.recommendation_basis?.weaknesses || [];
  const decisionReasoning = result.recommendation_basis?.decision_reasoning || ((result.decision_engine as any)?.decision_trace ? (result.decision_engine as any).decision_trace.join(' ') : '');

  // Insights & Onboarding
  const certClassifications = result.certification_suitability?.classifications || [];
  const rampUpEstimate = result.onboarding?.estimated_ramp_up || '2-4 weeks';
  const learningCurve = result.onboarding?.learning_curve || [];

  // Interview Questions
  const interviewQuestions = result.interview?.interview_questions || { easy: [], medium: [], advanced: [] };

  // Map skill_evidence list to record mapping
  const skillsEvidence = result.evidence?.skills_evidence || [];
  const skillsEvidenceRecord: Record<string, any> = {
    ...Object.fromEntries(
      (Array.isArray(skillsEvidence) ? skillsEvidence : []).map((item: any) => [
        item.skill,
        {
          context: item.evidence_snippet,
          confidence: item.match_confidence ? `${item.match_confidence}%` : '100%',
          sentence: item.evidence_snippet
        }
      ])
    ),
    ...(typeof skillsEvidence === 'object' && !Array.isArray(skillsEvidence) ? skillsEvidence : {})
  };

  // Timeline milestones mapping
  const timelineMilestones = career.map((c: any) => ({
    year: c.period || c.dates || c.year || '2022 – Present',
    role: c.role || 'Software Engineer',
    company: c.company || 'Company',
    details: c.details || c.description || 'Professional work history entry.'
  }));

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* 2 Core Scoring Metric Cards */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
              <Card hoverable style={{ borderTop: '4px solid #3b82f6' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text variant="muted" style={{ fontSize: '13px', fontWeight: 600 }}>Explicit Keyword Match</Text>
                  <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: 'hsla(var(--primary), 0.15)', color: 'hsl(var(--primary))', fontWeight: 700 }}>
                    Weight: 40%
                  </span>
                </div>
                <Heading level={2} style={{ fontSize: '36px', color: '#3b82f6', marginTop: '10px', marginBottom: '4px' }}>
                  {explicitKeywordMatchScore}%
                </Heading>
                <Text variant="muted" style={{ fontSize: '12px', fontStyle: 'italic' }}>
                  {dimensionScores.explicit_keyword_match?.evidence?.[0] || `Matched ${matchedSkills.length} required JD skills.`}
                </Text>
              </Card>

              <Card hoverable style={{ borderTop: '4px solid #a78bfa' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Text variant="muted" style={{ fontSize: '13px', fontWeight: 600 }}>Semantic Similarity</Text>
                  <span style={{ fontSize: '11px', padding: '2px 8px', borderRadius: '4px', background: 'hsla(var(--accent), 0.15)', color: '#a78bfa', fontWeight: 700 }}>
                    Weight: 60%
                  </span>
                </div>
                <Heading level={2} style={{ fontSize: '36px', color: '#a78bfa', marginTop: '10px', marginBottom: '4px' }}>
                  {semanticSimilarityScore}%
                </Heading>
                <Text variant="muted" style={{ fontSize: '12px', fontStyle: 'italic' }}>
                  {dimensionScores.semantic_similarity?.evidence?.[0] || 'Semantic similarity between candidate career experience and job target requirements.'}
                </Text>
              </Card>
            </div>

            {/* Executive Recommendation Box */}
            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <Heading level={3} style={{ fontSize: '16px' }}>Executive Recommendation Rationale</Heading>
                <span style={{
                  padding: '4px 12px',
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontWeight: 600,
                  background: 'hsla(var(--primary), 0.12)',
                  color: 'hsl(var(--primary))'
                }}>
                  {hiringRecommendation}
                </span>
              </div>
              <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px', margin: 0 }}>
                {(result.recommendation?.rationale_bullets || result.recommendation?.candidate_summary || []).map((bullet: string, idx: number) => (
                  <li key={idx} style={{ fontSize: '13px', color: 'hsl(var(--foreground))' }}>{bullet}</li>
                ))}
              </ul>
            </Card>

            {/* Strengths & Weaknesses */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' }}>
              <Card style={{ borderLeft: '4px solid hsl(var(--success))' }}>
                <Heading level={4} style={{ fontSize: '14px', color: 'hsl(var(--success))', marginBottom: '12px' }}>
                  Top Candidate Strengths
                </Heading>
                {strengths.length > 0 ? (
                  <ul style={{ paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '6px', margin: 0 }}>
                    {strengths.map((str: string, idx: number) => (
                      <li key={idx} style={{ fontSize: '12px' }}>{str}</li>
                    ))}
                  </ul>
                ) : (
                  <Text variant="muted" style={{ fontSize: '12px' }}>No explicit strength markers cataloged.</Text>
                )}
              </Card>

              <Card style={{ borderLeft: '4px solid hsl(var(--destructive))' }}>
                <Heading level={4} style={{ fontSize: '14px', color: 'hsl(var(--destructive))', marginBottom: '12px' }}>
                  Primary Weaknesses & Gaps
                </Heading>
                {weaknesses.length > 0 ? (
                  <ul style={{ paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '6px', margin: 0 }}>
                    {weaknesses.map((w: string, idx: number) => (
                      <li key={idx} style={{ fontSize: '12px' }}>{w}</li>
                    ))}
                  </ul>
                ) : (
                  <Text variant="muted" style={{ fontSize: '12px' }}>No major weaknesses identified.</Text>
                )}
              </Card>
            </div>
          </div>
        );

      case 'skills':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <Heading level={3} style={{ fontSize: '16px' }}>Technical Skill Inventory & Gap Analysis</Heading>
                <span style={{ fontSize: '13px', fontWeight: 600, color: 'hsl(var(--primary))' }}>
                  Explicit Keyword Match: {explicitKeywordMatchScore}%
                </span>
              </div>

              {criticalMissing.length > 0 && (
                <div style={{ padding: '12px 16px', background: 'hsla(var(--destructive), 0.1)', border: '1px solid hsl(var(--destructive))', borderRadius: '8px', marginBottom: '20px' }}>
                  <span style={{ fontWeight: 600, color: 'hsl(var(--destructive))', fontSize: '13px' }}>Skill Gap (Critical Missing Requirements): </span>
                  <span style={{ fontSize: '13px', color: 'hsl(var(--foreground))' }}>{criticalMissing.join(', ')}</span>
                </div>
              )}

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px' }}>
                <div>
                  <Heading level={4} style={{ fontSize: '13px', color: 'hsl(var(--success))', marginBottom: '10px' }}>
                    Matched Skills ({matchedSkills.length})
                  </Heading>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {matchedSkills.map((s: string) => (
                      <span key={s} style={{ padding: '4px 10px', background: 'hsla(var(--success), 0.12)', color: 'hsl(var(--success))', borderRadius: '6px', fontSize: '12px', fontWeight: 500 }}>
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                {inferredSkills.length > 0 && (
                  <div>
                    <Heading level={4} style={{ fontSize: '13px', color: '#60a5fa', marginBottom: '10px' }}>
                      Inferred Foundational Skills ({inferredSkills.length})
                    </Heading>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {inferredSkills.map((s: string) => (
                        <span key={s} title="Inferred from advanced technology prerequisite on resume" style={{ padding: '4px 10px', background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '6px', fontSize: '12px', fontWeight: 500 }}>
                          ⚡ {s} (Inferred)
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <Heading level={4} style={{ fontSize: '13px', color: 'hsl(var(--destructive))', marginBottom: '10px' }}>
                    Missing Skills ({missingSkills.length})
                  </Heading>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {missingSkills.map((s: string) => (
                      <span key={s} style={{ padding: '4px 10px', background: 'hsla(var(--destructive), 0.12)', color: 'hsl(var(--destructive))', borderRadius: '6px', fontSize: '12px', fontWeight: 500 }}>
                        {s}
                      </span>
                    ))}
                  </div>
                </div>

                {additionalSkills.length > 0 && (
                  <div>
                    <Heading level={4} style={{ fontSize: '13px', color: 'hsl(var(--muted-foreground))', marginBottom: '10px' }}>
                      Additional Candidate Skills ({additionalSkills.length})
                    </Heading>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                      {additionalSkills.map((s: string) => (
                        <span key={s} style={{ padding: '4px 10px', background: 'hsl(var(--secondary))', color: 'hsl(var(--foreground))', borderRadius: '6px', fontSize: '12px', fontWeight: 500 }}>
                          {s}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </Card>
          </div>
        );

      case 'evidence':
        return <EvidenceSection matchedSkills={matchedSkills} inferredSkills={inferredSkills} missingSkills={missingSkills} skillsEvidence={skillsEvidenceRecord} />;

      case 'interview':
        return <InterviewPrep evaluationId={id || ''} questions={interviewQuestions} />;

      case 'insights':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Certification Authority Tiers */}
            <Card>
              <Heading level={3} style={{ fontSize: '16px', marginBottom: '12px' }}>Certification Authority Classification</Heading>
              {certClassifications.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  {certClassifications.map((cert: any, idx: number) => (
                    <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 12px', background: 'hsl(var(--secondary))', borderRadius: '6px' }}>
                      <span style={{ fontSize: '13px', fontWeight: 500 }}>{cert.title}</span>
                      <span style={{
                        fontSize: '11px',
                        fontWeight: 600,
                        padding: '2px 8px',
                        borderRadius: '4px',
                        background: cert.tier === 'Industry-Standard' ? 'hsla(var(--success), 0.2)' : 'hsla(var(--muted-foreground), 0.2)',
                        color: cert.tier === 'Industry-Standard' ? 'hsl(var(--success))' : 'hsl(var(--muted-foreground))'
                      }}>
                        {cert.tier}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <Text variant="muted" style={{ fontSize: '12px' }}>No formal certifications cataloged on profile.</Text>
              )}
            </Card>

            {/* Learning Curve & Onboarding */}
            <Card>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                <Heading level={3} style={{ fontSize: '16px' }}>Learning Curve & Estimated Ramp-Up</Heading>
                <span style={{ fontSize: '12px', fontWeight: 600, color: 'hsl(var(--primary))' }}>Ramp-up: {rampUpEstimate}</span>
              </div>
              {learningCurve.length > 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {learningCurve.map((lc: any, idx: number) => (
                    <div key={idx} style={{ padding: '10px 14px', border: '1px solid hsl(var(--border))', borderRadius: '6px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 600 }}>
                        <span>Skill: {lc.skill}</span>
                        <span style={{ color: 'hsl(var(--accent))' }}>Difficulty: {lc.difficulty}</span>
                      </div>
                      <Text variant="muted" style={{ fontSize: '11px', marginTop: '4px' }}>{lc.reason}</Text>
                    </div>
                  ))}
                </div>
              ) : (
                <Text variant="muted" style={{ fontSize: '12px' }}>No steep learning curve transitions required.</Text>
              )}
            </Card>

            {/* Recruiter Notes & Decision Override */}
            <Card>
              <Heading level={3} style={{ fontSize: '16px', marginBottom: '12px' }}>Recruiter Decision & Assessment Notes</Heading>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <Text variant="muted" style={{ fontSize: '12px', marginBottom: '4px' }}>Recruiter Decision Action:</Text>
                  <select
                    value={recruiterDecision}
                    onChange={(e) => setRecruiterDecision(e.target.value as any)}
                    style={{ width: '100%', padding: '8px 12px', borderRadius: '6px', background: 'hsl(var(--background))', color: 'hsl(var(--foreground))', border: '1px solid hsl(var(--border))' }}
                  >
                    <option value="">-- Select Decision --</option>
                    <option value="Hire">Recommend Hire</option>
                    <option value="Interview">Schedule Interview</option>
                    <option value="Hold">Keep on Hold</option>
                    <option value="Reject">Reject Candidate</option>
                  </select>
                </div>

                <div>
                  <Text variant="muted" style={{ fontSize: '12px', marginBottom: '4px' }}>Recruiter Assessment Notes:</Text>
                  <textarea
                    rows={4}
                    value={recruiterNotes}
                    onChange={(e) => setRecruiterNotes(e.target.value)}
                    placeholder="Enter private recruiter assessment notes..."
                    style={{ width: '100%', padding: '10px', borderRadius: '6px', background: 'hsl(var(--background))', color: 'hsl(var(--foreground))', border: '1px solid hsl(var(--border))' }}
                  />
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Button variant="primary" onClick={handleSaveDecision}>Save Recruiter Assessment</Button>
                  {saveSuccess && <span style={{ color: 'hsl(var(--success))', fontSize: '12px', fontWeight: 600 }}>Assessment saved successfully!</span>}
                </div>
              </div>
            </Card>
          </div>
        );

      case 'timeline':
        return <EvidenceTimeline timeline={timelineMilestones} />;

      case 'breakdown':
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <Card>
              <Heading level={3} style={{ fontSize: '16px', marginBottom: '12px', color: 'hsl(var(--primary))' }}>
                Core Mathematical Scoring Breakdown
              </Heading>
              
              <div style={{ padding: '16px', background: 'hsla(var(--primary), 0.08)', border: '1px solid hsl(var(--primary))', borderRadius: '8px', marginBottom: '20px' }}>
                <span style={{ fontSize: '14px', fontWeight: 700, color: 'hsl(var(--primary))' }}>
                  Overall Score Formula:
                </span>
                <div style={{ fontSize: '13px', marginTop: '6px', fontFamily: 'monospace' }}>
                  Overall Match Score = (Explicit Keyword Match × 0.40) + (Semantic Similarity × 0.60)
                </div>
                <div style={{ fontSize: '13px', marginTop: '4px', color: 'hsl(var(--foreground))', fontWeight: 600 }}>
                  = ({explicitKeywordMatchScore} × 0.40) + ({semanticSimilarityScore} × 0.60) = {overallScore}%
                </div>
              </div>

              <Text style={{ fontSize: '13px', marginBottom: '16px' }}>{decisionReasoning}</Text>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div style={{ padding: '12px', background: 'hsl(var(--secondary))', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: 600 }}>
                    <span>Explicit Keyword Match</span>
                    <span>Score: {explicitKeywordMatchScore}% (Weight: 40%)</span>
                  </div>
                  <Text variant="muted" style={{ fontSize: '11px', marginTop: '4px' }}>
                    Evidence: {dimensionScores.explicit_keyword_match?.evidence?.[0] || 'Direct ratio of required skills found.'}
                  </Text>
                </div>

                <div style={{ padding: '12px', background: 'hsl(var(--secondary))', borderRadius: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: 600 }}>
                    <span>Semantic Similarity</span>
                    <span>Score: {semanticSimilarityScore}% (Weight: 60%)</span>
                  </div>
                  <Text variant="muted" style={{ fontSize: '11px', marginTop: '4px' }}>
                    Evidence: {dimensionScores.semantic_similarity?.evidence?.[0] || 'Semantic similarity between work history and target role.'}
                  </Text>
                </div>
              </div>
            </Card>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <PageLayout
      title={name}
      subtitle={`Applied Role: ${targetRole} • File: ${filename}`}
      actions={
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <Link to={ROUTES.DASHBOARD}>
            <Button variant="secondary" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <ArrowLeft size={16} /> Back to Dashboard
            </Button>
          </Link>
          <Button variant="primary" onClick={() => setAssistantOpen(true)} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MessageSquare size={16} /> Ask AI Copilot
          </Button>
        </div>
      }
    >
      <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
        
        {/* Candidate Summary Header Bar */}
        <Card style={{ padding: '20px 24px' }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center', gap: '16px' }}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Heading level={2} style={{ fontSize: '24px', margin: 0 }}>{name}</Heading>
                <span style={{
                  padding: '4px 12px',
                  borderRadius: '12px',
                  fontSize: '12px',
                  fontWeight: 600,
                  background: meetsPolicy ? 'hsla(var(--success), 0.15)' : 'hsla(var(--destructive), 0.15)',
                  color: meetsPolicy ? 'hsl(var(--success))' : 'hsl(var(--destructive))',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}>
                  {meetsPolicy ? <ShieldCheck size={14} /> : <ShieldAlert size={14} />}
                  {meetsPolicy ? 'Meets Hiring Policy' : 'Policy Gap / Disqualified'}
                </span>
              </div>
              <Text variant="muted" style={{ fontSize: '13px' }}>
                Current Position: <strong style={{ color: 'hsl(var(--foreground))' }}>{currentPosition}</strong>
              </Text>
            </div>

            <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
              <div style={{ textAlign: 'right' }}>
                <Text variant="muted" style={{ fontSize: '11px' }}>Overall Match Score</Text>
                <Heading level={2} style={{ fontSize: '32px', margin: 0, color: overallScore >= 80 ? 'hsl(var(--success))' : 'hsl(var(--accent))' }}>
                  {overallScore}%
                </Heading>
              </div>

              <div style={{ textAlign: 'right' }}>
                <Text variant="muted" style={{ fontSize: '11px' }}>Recommendation</Text>
                <span style={{ fontSize: '14px', fontWeight: 700, color: 'hsl(var(--primary))' }}>
                  {hiringRecommendation}
                </span>
              </div>
            </div>
          </div>

          {/* Contact Details Line */}
          {(email || phone || links.length > 0) && (
            <div style={{ marginTop: '16px', paddingTop: '16px', borderTop: '1px solid hsl(var(--border))', display: 'flex', flexWrap: 'wrap', gap: '20px', fontSize: '12px' }}>
              {email && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Mail size={14} style={{ color: 'hsl(var(--muted-foreground))' }} />
                  <span>{email}</span>
                </div>
              )}
              {phone && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Phone size={14} style={{ color: 'hsl(var(--muted-foreground))' }} />
                  <span>{phone}</span>
                </div>
              )}
              {links
                .map((rawLink: string) => {
                  if (!rawLink || typeof rawLink !== 'string') return null;
                  const trimmed = rawLink.trim();
                  if (!trimmed) return null;
                  const href = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;
                  try {
                    const parsed = new URL(href);
                    const host = parsed.hostname.toLowerCase();
                    let label = 'Website';
                    if (host.includes('github.com')) label = 'GitHub';
                    else if (host.includes('linkedin.com')) label = 'LinkedIn';
                    else if (host.includes('portfolio') || host.includes('vercel.app') || host.includes('netlify.app')) label = 'Portfolio';
                    return { href, label };
                  } catch {
                    return null;
                  }
                })
                .filter((item: any): item is { href: string; label: string } => item !== null)
                .map((item: any, idx: number) => (
                  <a key={idx} href={item.href} target="_blank" rel="noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '4px', color: 'hsl(var(--primary))', textDecoration: 'none', fontWeight: 500 }}>
                    <ExternalLink size={14} /> {item.label}
                  </a>
                ))}
            </div>
          )}
        </Card>

        {/* 7 Recruiter Layout Tabs Navigation */}
        <div style={{ borderBottom: '1px solid hsl(var(--border))', display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '2px' }}>
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'skills', label: 'Skills' },
            { id: 'evidence', label: 'Evidence' },
            { id: 'interview', label: 'Interview' },
            { id: 'insights', label: 'Recruiter' },
            { id: 'timeline', label: 'Timeline' },
            { id: 'breakdown', label: 'Decision Breakdown' }
          ].map((t) => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              style={{
                padding: '10px 16px',
                fontSize: '13px',
                fontWeight: activeTab === t.id ? 600 : 400,
                color: activeTab === t.id ? 'hsl(var(--primary))' : 'hsl(var(--muted-foreground))',
                borderBottom: activeTab === t.id ? '2px solid hsl(var(--primary))' : '2px solid transparent',
                background: 'none',
                borderTop: 'none',
                borderLeft: 'none',
                borderRight: 'none',
                cursor: 'pointer',
                whiteSpace: 'nowrap'
              }}
            >
              {t.label}
            </button>
          ))}
        </div>

        {/* Tab Panel Render */}
        {renderTabContent()}

        {/* AI Copilot Drawer */}
        {assistantOpen && (
          <AssistantDrawer
            isOpen={assistantOpen}
            onClose={() => setAssistantOpen(false)}
            candidateName={name}
            candidateId={id || ''}
            onCitationClick={handleCitationClick}
          />
        )}
      </div>
    </PageLayout>
  );
};
