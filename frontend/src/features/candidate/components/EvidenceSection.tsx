import React from 'react';
import { Card, Heading, Text } from '@/shared/ui';
import type { SkillEvidence } from '../types/candidate';
import { CheckCircle2, AlertTriangle, Zap } from 'lucide-react';

interface EvidenceSectionProps {
  matchedSkills: string[];
  inferredSkills?: string[];
  missingSkills: string[];
  skillsEvidence?: Record<string, SkillEvidence>;
}

export const EvidenceSection: React.FC<EvidenceSectionProps> = ({
  matchedSkills,
  inferredSkills = [],
  missingSkills,
  skillsEvidence = {},
}) => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Matched Skills Evidence Block */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <CheckCircle2 size={20} style={{ color: 'hsl(var(--success))' }} />
          <Heading level={3} style={{ fontSize: '18px', margin: 0 }}>Validated Core Capabilities ({matchedSkills.length})</Heading>
        </div>
        <Text variant="muted">
          Skills explicitly found in the resume matching requirements. Proof sentences are extracted from candidate work logs.
        </Text>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {matchedSkills.length === 0 ? (
            <Card>
              <Text variant="muted">No matching required skills validated for this profile.</Text>
            </Card>
          ) : (
            matchedSkills.map((skill) => {
              const evidence = skillsEvidence[skill];
              return (
                <Card key={skill} style={{ borderLeft: '3px solid hsl(var(--success))' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
                    <span style={{ fontWeight: 600, color: '#ffffff', fontSize: '14px' }}>{skill}</span>
                    {evidence?.confidence && (
                      <span style={{
                        fontSize: '11px',
                        fontWeight: 600,
                        color: 'hsl(var(--success))',
                        background: 'hsla(var(--success), 0.1)',
                        padding: '2px 8px',
                        borderRadius: '12px'
                      }}>
                        Confidence: {evidence.confidence}
                      </span>
                    )}
                  </div>
                  {evidence?.context ? (
                    <Text variant="muted" style={{ fontSize: '13px', marginTop: '6px', fontStyle: 'italic', lineHeight: '1.4' }}>
                      &ldquo;{evidence.context}&rdquo;
                    </Text>
                  ) : (
                    <Text variant="muted" style={{ fontSize: '12px', marginTop: '4px' }}>
                      Skill parsed and matches requested JD target.
                    </Text>
                  )}
                </Card>
              );
            })
          )}
        </div>
      </div>

      {/* Inferred Foundational Skills Block */}
      {inferredSkills.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Zap size={20} style={{ color: '#60a5fa' }} />
            <Heading level={3} style={{ fontSize: '18px', margin: 0 }}>Logically Inferred Foundational Skills ({inferredSkills.length})</Heading>
          </div>
          <Text variant="muted">
            Foundational skills logically inferred based on advanced technology prerequisites in the candidate&apos;s background (85% credit applied).
          </Text>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {inferredSkills.map((skill) => {
              const evidence = skillsEvidence[skill];
              return (
                <Card key={skill} style={{ borderLeft: '3px solid #3b82f6', background: 'rgba(59, 130, 246, 0.03)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
                    <span style={{ fontWeight: 600, color: '#60a5fa', fontSize: '14px' }}>⚡ {skill} (Inferred Foundation)</span>
                    <span style={{
                      fontSize: '11px',
                      fontWeight: 600,
                      color: '#60a5fa',
                      background: 'rgba(59, 130, 246, 0.15)',
                      padding: '2px 8px',
                      borderRadius: '12px'
                    }}>
                      Credit: 85%
                    </span>
                  </div>
                  {evidence?.context && (
                    <Text variant="muted" style={{ fontSize: '13px', marginTop: '6px', fontStyle: 'italic', lineHeight: '1.4' }}>
                      &ldquo;{evidence.context}&rdquo;
                    </Text>
                  )}
                </Card>
              );
            })}
          </div>
        </div>
      )}

      {/* Missing Skills Warning Block */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <AlertTriangle size={20} style={{ color: 'hsl(var(--destructive))' }} />
          <Heading level={3} style={{ fontSize: '18px', margin: 0 }}>Missing Target Requirements ({missingSkills.length})</Heading>
        </div>
        <Text variant="muted">
          Required job profile details that could not be validated or inferred from the resume context.
        </Text>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {missingSkills.length === 0 ? (
            <Card style={{ width: '100%' }}>
              <Text variant="muted">All mandatory and target job skills were successfully validated.</Text>
            </Card>
          ) : (
            missingSkills.map((skill) => (
              <span
                key={skill}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  padding: '6px 12px',
                  borderRadius: '16px',
                  background: 'hsla(var(--destructive), 0.08)',
                  border: '1px solid hsla(var(--destructive), 0.2)',
                  color: 'hsl(var(--destructive))',
                  fontSize: '13px',
                  fontWeight: 500
                }}
              >
                {skill}
              </span>
            ))
          )}
        </div>
      </div>

    </div>
  );
};
export default EvidenceSection;
