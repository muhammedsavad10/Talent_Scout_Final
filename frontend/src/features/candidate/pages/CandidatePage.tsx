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
  MessageSquare,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  Briefcase,
  Award,
  Cpu,
  Users
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

  // Two-Phase Recruitment Intelligence Scoring Metrics
  const dimensionScores = result.decision_engine?.dimension_scores || {};
  const explicitKeywordMatchScore = dimensionScores.explicit_keyword_match?.score ?? dimensionScores.skill_match?.score ?? 0;
  const semanticSimilarityScore = dimensionScores.semantic_similarity?.score ?? dimensionScores.role_fit?.score ?? 0;
  const stage1MatchScore = (result as any).stage1_match_score ?? (result as any).technical_score ?? Math.round((explicitKeywordMatchScore * 0.40) + (semanticSimilarityScore * 0.60));
  
  const hiringPriority = (result as any).hiring_priority || {};
  const hiringPriorityScore = (result as any).hiring_priority_score ?? hiringPriority.hiring_priority_score ?? overallScore;
  const hiringPriorityTier = (result as any).hiring_priority_tier ?? hiringPriority.hiring_priority_tier ?? 'Standard Review';

  // Candidate-Specific Recruiter Evidence Signals (Ground Truth Data Extraction)
  const priorityFactors = hiringPriority.priority_factors || {};
  const profProfile = hiringPriority.professional_profile || {};
  const totalYearsExp = profProfile.total_professional_years 
    ?? profProfile.years_experience 
    ?? profProfile.total_years_experience 
    ?? (result as any).evidence?.years_of_experience 
    ?? (candidateFacts as any).years_experience 
    ?? 0;
  const profExpCount = profProfile.professional_experience_count ?? (career.length || 0);
  const seniorityLevel = profProfile.seniority_level || (
    totalYearsExp >= 3 || profExpCount >= 2 ? 'Senior / Lead' :
    totalYearsExp >= 1 || profExpCount >= 1 ? 'Mid-Level' : 'Entry-Level'
  );
  const prodIndicators = hiringPriority.production_indicators || (result as any).evidence?.production_engineering || [];
  const projectComplexityScore = hiringPriority.project_complexity ?? 0;
  const certsList = hiringPriority.certifications || (result as any).certifications || (result as any).evidence?.certifications || [];
  const leadIndicators = (result as any).evidence?.leadership_mentorship || [];
  const seniorityPts = priorityFactors.seniority_alignment_pts ?? 0;

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
        {
          const rawRank = (result as any).rank ?? (result as any).candidate_rank;
          const hasRankContext = typeof rawRank === 'number' && rawRank > 0;
          const rankLabel = hasRankContext ? `Ranked #${rawRank}` : 'Standalone Evaluation';

          const confidenceLevel = (result as any).recommendation?.confidence || (result as any).confidence || 'Very High';
          const confidenceReasoning = (result as any).recommendation?.confidence_reasoning || 'Based on deterministic evidence coverage, resume completeness, and semantic alignment.';

          const dynamicRationaleParts = [];
          if (hasRankContext) {
            dynamicRationaleParts.push(`Ranked #${rawRank} for ${targetRole}`);
          } else {
            dynamicRationaleParts.push(`Evaluated for ${targetRole}`);
          }
          dynamicRationaleParts.push(`demonstrating ${stage1MatchScore}% Stage 1 Technical Match`);
          if (totalYearsExp > 0 || profExpCount > 0) {
            dynamicRationaleParts.push(`supported by ${totalYearsExp > 0 ? `${totalYearsExp.toFixed(1)} years` : `${profExpCount} positions`} verified industry experience`);
          }
          if (seniorityLevel) dynamicRationaleParts.push(`${seniorityLevel} career progression`);
          if (prodIndicators.length > 0) dynamicRationaleParts.push(`and ${prodIndicators.length} production engineering indicators (${prodIndicators.slice(0, 3).join(', ')})`);

          const evidenceGroundedRationale = (decisionReasoning && !decisionReasoning.includes('evaluated with overall match score'))
            ? decisionReasoning
            : (dynamicRationaleParts.join(', ') + '.');

          return (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              {/* 1. Candidate Evaluation Decision Summary Hero Card */}
              <Card style={{ padding: '20px', border: '1px solid hsl(var(--border))', borderRadius: '12px', background: 'hsl(var(--secondary))', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid hsl(var(--border))', paddingBottom: '12px' }}>
                  <Heading level={3} style={{ fontSize: '18px', margin: 0, color: '#ffffff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <ShieldCheck size={20} style={{ color: 'hsl(var(--primary))' }} /> Candidate Evaluation Decision Summary
                  </Heading>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '2px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 700, padding: '4px 10px', borderRadius: '12px', background: 'hsla(var(--primary), 0.15)', color: 'hsl(var(--primary))', border: '1px solid hsl(var(--primary))' }}>
                      Confidence: {confidenceLevel}
                    </span>
                    <span style={{ fontSize: '10px', color: 'hsl(var(--muted-foreground))' }}>
                      {confidenceReasoning}
                    </span>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '12px' }}>
                  {/* Metric 1: Stage 1 Technical Match */}
                  <div style={{ padding: '12px', background: 'hsla(var(--primary), 0.08)', border: '1px solid hsl(var(--primary))', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--primary))', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Technical Match
                    </span>
                    <span style={{ fontSize: '24px', fontWeight: 800, color: 'hsl(var(--primary))' }}>
                      {stage1MatchScore}%
                    </span>
                    <span style={{ fontSize: '10px', color: 'hsl(var(--muted-foreground))' }}>
                      Stage 1 ATS + Semantic
                    </span>
                  </div>

                  {/* Metric 2: Recruiter Priority Score */}
                  <div style={{ padding: '12px', background: 'hsla(var(--accent), 0.08)', border: '1px solid #a78bfa', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: '#a78bfa', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Recruiter Priority
                    </span>
                    <span style={{ fontSize: '24px', fontWeight: 800, color: '#a78bfa' }}>
                      {hiringPriorityScore} pts
                    </span>
                    <span style={{ fontSize: '10px', color: '#a78bfa' }}>
                      Phase 2 Experience Score
                    </span>
                  </div>

                  {/* Metric 3: Candidate Hiring Score & Rank */}
                  <div style={{ padding: '12px', background: 'hsla(var(--success), 0.08)', border: '1px solid hsl(var(--success))', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--success))', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Final Hiring Score
                    </span>
                    <span style={{ fontSize: '24px', fontWeight: 800, color: 'hsl(var(--success))' }}>
                      {overallScore}%
                    </span>
                    <span style={{ fontSize: '10px', fontWeight: 700, color: 'hsl(var(--success))' }}>
                      {rankLabel}
                    </span>
                  </div>

                  {/* Metric 4: Recommendation Tier */}
                  <div style={{ padding: '12px', background: 'hsla(var(--foreground), 0.04)', border: '1px solid hsl(var(--border))', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--muted-foreground))', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Recommendation Tier
                    </span>
                    <span style={{ fontSize: '14px', fontWeight: 700, color: '#ffffff' }}>
                      {hiringRecommendation}
                    </span>
                    <span style={{ fontSize: '10px', color: 'hsl(var(--muted-foreground))' }}>
                      {hiringPriorityTier}
                    </span>
                  </div>
                </div>

                <div style={{ padding: '12px 14px', background: 'hsla(var(--foreground), 0.03)', borderLeft: '3px solid hsl(var(--primary))', borderRadius: '4px', fontSize: '12px', lineHeight: 1.5, color: 'hsl(var(--foreground))' }}>
                  <strong>Primary Decision Rationale:</strong> {evidenceGroundedRationale}
                </div>
              </Card>

              {/* 2. Transparent Two-Phase Decision Flow Box (NO FAKE ARITHMETIC) */}
              <Card style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <Heading level={4} style={{ fontSize: '15px', margin: 0, display: 'flex', alignItems: 'center', gap: '8px', color: '#ffffff' }}>
                  <TrendingUp size={16} style={{ color: 'hsl(var(--primary))' }} /> Two-Phase Decision Flow & Recruiter Signals
                </Heading>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px', alignItems: 'center' }}>
                  {/* Phase 1: Technical Match */}
                  <div style={{ padding: '14px', background: 'hsla(var(--primary), 0.08)', border: '1px solid hsl(var(--primary))', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--primary))', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Phase 1: Technical Match
                    </span>
                    <span style={{ fontSize: '28px', fontWeight: 800, color: 'hsl(var(--primary))' }}>
                      {stage1MatchScore}%
                    </span>
                    <span style={{ fontSize: '11px', color: 'hsl(var(--muted-foreground))' }}>
                      Explicit Skills ({explicitKeywordMatchScore}%) + Semantic ({semanticSimilarityScore}%)
                    </span>
                  </div>

                  {/* Recruiter Evaluation Factors */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', padding: '12px', background: 'hsla(var(--foreground), 0.03)', borderRadius: '8px', border: '1px solid hsl(var(--border))' }}>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: '#a78bfa', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Primary Decision Signals
                    </span>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '11px' }}>
                      {totalYearsExp > 0 || profExpCount > 0 ? (
                        <span style={{ color: 'hsl(var(--success))', fontWeight: 600 }}>
                          ✔ Verified {totalYearsExp > 0 ? `${totalYearsExp.toFixed(1)} years` : `${profExpCount} positions`} industry employment
                        </span>
                      ) : (
                        <span style={{ color: 'hsl(var(--destructive))', fontWeight: 500 }}>
                          ✖ No verified industry employment history
                        </span>
                      )}

                      {seniorityPts > 0 || seniorityLevel !== 'Entry-Level' ? (
                        <span style={{ color: 'hsl(var(--success))', fontWeight: 600 }}>✔ {seniorityLevel} career alignment</span>
                      ) : (
                        <span style={{ color: 'hsl(var(--muted-foreground))' }}>⚠ Entry-level career profile</span>
                      )}

                      {prodIndicators.length > 0 ? (
                        <span style={{ color: 'hsl(var(--success))', fontWeight: 600 }}>✔ {prodIndicators.length} production tech indicators ({prodIndicators.slice(0, 3).join(', ')})</span>
                      ) : (
                        <span style={{ color: 'hsl(var(--muted-foreground))' }}>✖ No production deployment history</span>
                      )}
                    </div>
                  </div>

                  {/* Phase 2: Final Decision */}
                  <div style={{ padding: '14px', background: 'hsla(var(--accent), 0.12)', border: '1px solid #a78bfa', borderRadius: '8px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    <span style={{ fontSize: '11px', fontWeight: 700, color: '#a78bfa', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                      Phase 2: Final Decision
                    </span>
                    <span style={{ fontSize: '28px', fontWeight: 800, color: '#a78bfa' }}>
                      {overallScore}%
                    </span>
                    <span style={{ fontSize: '11px', fontWeight: 600, color: '#a78bfa' }}>
                      {hasRankContext ? `Ranked #${rawRank} (${hiringPriorityTier})` : hiringPriorityTier}
                    </span>
                  </div>
                </div>
              </Card>

              {/* 3. Grouped Candidate Evidence Signal Matrix (4 Recruiter Domains) */}
              <Card style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <Heading level={4} style={{ fontSize: '15px', margin: 0, color: '#ffffff' }}>
                  Detected Candidate Evidence (Grouped Recruiter Domains)
                </Heading>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
                  {/* Domain 1: Professional Profile */}
                  <div style={{ padding: '16px', background: 'hsl(var(--secondary))', border: '1px solid hsl(var(--border))', borderRadius: '10px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <span style={{ fontSize: '13px', fontWeight: 700, color: 'hsl(var(--primary))', display: 'flex', alignItems: 'center', gap: '6px', borderBottom: '1px solid hsl(var(--border))', paddingBottom: '6px' }}>
                      <Briefcase size={16} /> Professional Profile
                    </span>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>Industry Experience</span>
                        {totalYearsExp > 0 || profExpCount > 0 ? (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--success))', background: 'hsla(var(--success), 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✔ {totalYearsExp > 0 ? `${totalYearsExp.toFixed(1)} yrs` : `${profExpCount} Positions`}
                          </span>
                        ) : (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--destructive))', background: 'hsla(var(--destructive), 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✖ Not detected
                          </span>
                        )}
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>Seniority Level</span>
                        <span style={{ fontSize: '11px', fontWeight: 700, color: seniorityPts > 10 ? 'hsl(var(--success))' : 'hsl(var(--accent))', background: 'hsla(var(--foreground), 0.06)', padding: '2px 8px', borderRadius: '4px' }}>
                          {seniorityLevel}
                        </span>
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>Employment History</span>
                        {career.length > 0 ? (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--success))', background: 'hsla(var(--success), 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✔ {career.length} Positions
                          </span>
                        ) : (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--muted-foreground))', background: 'hsla(var(--foreground), 0.06)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✖ Not detected
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Domain 2: Engineering Profile */}
                  <div style={{ padding: '16px', background: 'hsl(var(--secondary))', border: '1px solid hsl(var(--border))', borderRadius: '10px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <span style={{ fontSize: '13px', fontWeight: 700, color: '#3b82f6', display: 'flex', alignItems: 'center', gap: '6px', borderBottom: '1px solid hsl(var(--border))', paddingBottom: '6px' }}>
                      <Cpu size={16} /> Engineering Profile
                    </span>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>Production Engineering</span>
                        {prodIndicators.length > 0 ? (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--success))', background: 'hsla(var(--success), 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✔ {prodIndicators.length} Tech Signals
                          </span>
                        ) : (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--muted-foreground))', background: 'hsla(var(--foreground), 0.06)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✖ Not detected
                          </span>
                        )}
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>Project Complexity</span>
                        {projectComplexityScore >= 50 ? (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--success))', background: 'hsla(var(--success), 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✔ Enterprise Scale
                          </span>
                        ) : (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--accent))', background: 'hsla(var(--accent), 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                            ⚠ Portfolio / Personal
                          </span>
                        )}
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>System Architecture</span>
                        {matchedSkills.some((s: string) => ['Microservices', 'Distributed Systems', 'Docker', 'Kubernetes', 'AWS'].includes(s)) ? (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--success))', background: 'hsla(var(--success), 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✔ Distributed / Cloud
                          </span>
                        ) : (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--muted-foreground))', background: 'hsla(var(--foreground), 0.06)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✖ Standard Scope
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Domain 3: Leadership & Impact */}
                  <div style={{ padding: '16px', background: 'hsl(var(--secondary))', border: '1px solid hsl(var(--border))', borderRadius: '10px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <span style={{ fontSize: '13px', fontWeight: 700, color: '#f59e0b', display: 'flex', alignItems: 'center', gap: '6px', borderBottom: '1px solid hsl(var(--border))', paddingBottom: '6px' }}>
                      <Users size={16} /> Leadership & Impact
                    </span>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>Team Leadership</span>
                        {leadIndicators.length > 0 ? (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--success))', background: 'hsla(var(--success), 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✔ {leadIndicators.length} Signals
                          </span>
                        ) : (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--muted-foreground))', background: 'hsla(var(--foreground), 0.06)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✖ Not detected
                          </span>
                        )}
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>Mentorship & Training</span>
                        {(result as any).evidence?.mentorship ? (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--success))', background: 'hsla(var(--success), 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✔ Verified
                          </span>
                        ) : (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--muted-foreground))', background: 'hsla(var(--foreground), 0.06)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✖ Not detected
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Domain 4: Credentials & Education */}
                  <div style={{ padding: '16px', background: 'hsl(var(--secondary))', border: '1px solid hsl(var(--border))', borderRadius: '10px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <span style={{ fontSize: '13px', fontWeight: 700, color: '#10b981', display: 'flex', alignItems: 'center', gap: '6px', borderBottom: '1px solid hsl(var(--border))', paddingBottom: '6px' }}>
                      <Award size={16} /> Credentials & Education
                    </span>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>Certifications</span>
                        {certsList.length > 0 ? (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--success))', background: 'hsla(var(--success), 0.15)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✔ {certsList.length} Certified
                          </span>
                        ) : (
                          <span style={{ fontSize: '11px', fontWeight: 700, color: 'hsl(var(--muted-foreground))', background: 'hsla(var(--foreground), 0.06)', padding: '2px 8px', borderRadius: '4px' }}>
                            ✖ Not detected
                          </span>
                        )}
                      </div>

                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span>Academic Field</span>
                        <span style={{ fontSize: '11px', fontWeight: 600, color: 'hsl(var(--foreground))' }}>
                          {(result as any).parsed_resume?.education?.[0]?.degree || 'Computer Science / Engineering'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>

              {/* 4. Primary Strengths vs Primary Risk Factors Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '16px' }}>
                {/* Primary Strengths Box */}
                <div style={{ padding: '16px', background: 'hsla(var(--success), 0.06)', border: '1px solid hsl(var(--success))', borderRadius: '10px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <span style={{ fontSize: '14px', fontWeight: 700, color: 'hsl(var(--success))', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <CheckCircle2 size={16} /> Primary Positive Decision Factors
                  </span>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', color: 'hsl(var(--foreground))' }}>
                    {strengths.length > 0 ? (
                      strengths.map((strItem: string, idx: number) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                          <span style={{ color: 'hsl(var(--success))', fontWeight: 700 }}>✔</span>
                          <span>{strItem}</span>
                        </div>
                      ))
                    ) : (
                      <Text variant="muted" style={{ fontSize: '12px' }}>No specific strengths highlighted.</Text>
                    )}
                  </div>
                </div>

                {/* Primary Risk Factors Box */}
                <div style={{ padding: '16px', background: 'hsla(var(--destructive), 0.06)', border: '1px solid hsl(var(--destructive))', borderRadius: '10px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  <span style={{ fontSize: '14px', fontWeight: 700, color: 'hsl(var(--destructive))', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <AlertTriangle size={16} /> Primary Limiting Factors & Risk Areas
                  </span>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px', color: 'hsl(var(--foreground))' }}>
                    {weaknesses.length > 0 ? (
                      weaknesses.map((weakItem: string, idx: number) => (
                        <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                          <span style={{ color: 'hsl(var(--destructive))', fontWeight: 700 }}>✖</span>
                          <span>{weakItem}</span>
                        </div>
                      ))
                    ) : (
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                        <span style={{ color: 'hsl(var(--success))', fontWeight: 700 }}>✔</span>
                        <span>No critical risk factors or missing mandatory skills flagged.</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* 5. Phase 1 Technical Screening Math Details */}
              <Card style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <Heading level={4} style={{ fontSize: '14px', margin: 0, color: 'hsl(var(--primary))' }}>
                  Phase 1 Technical Match Breakdown Details
                </Heading>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
                  <div style={{ padding: '12px 16px', background: 'hsl(var(--secondary))', borderRadius: '8px', borderLeft: '4px solid #3b82f6' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: 600 }}>
                      <span>Explicit ATS Keyword Match</span>
                      <span style={{ color: '#3b82f6' }}>Score: {explicitKeywordMatchScore}% (Weight: 40%)</span>
                    </div>
                    <Text variant="muted" style={{ fontSize: '11px', marginTop: '4px' }}>
                      Evidence: {dimensionScores.explicit_keyword_match?.evidence?.[0] || `Matched ${matchedSkills.length} required JD skills.`}
                    </Text>
                  </div>

                  <div style={{ padding: '12px 16px', background: 'hsl(var(--secondary))', borderRadius: '8px', borderLeft: '4px solid #a78bfa' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', fontWeight: 600 }}>
                      <span>Semantic AI Similarity Alignment</span>
                      <span style={{ color: '#a78bfa' }}>Score: {semanticSimilarityScore}% (Weight: 60%)</span>
                    </div>
                    <Text variant="muted" style={{ fontSize: '11px', marginTop: '4px' }}>
                      Evidence: {dimensionScores.semantic_similarity?.evidence?.[0] || 'Semantic similarity between candidate career experience and job target requirements.'}
                    </Text>
                  </div>
                </div>
              </Card>
            </div>
          );
        }

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
