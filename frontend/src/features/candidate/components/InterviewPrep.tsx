import React, { useState, useMemo } from 'react';
import { Card, Heading, Text, Button } from '@/shared/ui';
import { evaluationService } from '@/shared/api';
import { HelpCircle, Mail, Copy, Check } from 'lucide-react';
import { logger } from '@/shared/utils';

interface InterviewPrepProps {
  evaluationId: string;
  questions: any;
}

export const InterviewPrep: React.FC<InterviewPrepProps> = ({
  evaluationId,
  questions,
}) => {
  const [emailSubject, setEmailSubject] = useState('');
  const [emailBody, setEmailBody] = useState('');
  const [loadingEmail, setLoadingEmail] = useState(false);
  const [copied, setCopied] = useState(false);

  // Safely normalize raw questions response structure (supports Record<string, string[]>, string[], and undefined)
  const normalizedQuestions = useMemo(() => {
    if (!questions) return [];
    
    if (Array.isArray(questions)) {
      return questions.map((q, idx) => {
        if (typeof q === 'string') {
          return { id: `q-${idx}`, category: 'General', text: q };
        }
        return {
          id: `q-${idx}`,
          category: (q as any).category || (q as any).difficulty || 'General',
          text: (q as any).question || (q as any).text || JSON.stringify(q),
        };
      });
    }

    if (typeof questions === 'object') {
      const list: { id: string; category: string; text: string }[] = [];
      let index = 0;
      Object.entries(questions).forEach(([category, qList]) => {
        if (Array.isArray(qList)) {
          qList.forEach((qText) => {
            if (typeof qText === 'string') {
              list.push({
                id: `q-${index++}`,
                category: category.toUpperCase(),
                text: qText,
              });
            }
          });
        }
      });
      return list;
    }

    return [];
  }, [questions]);

  const handleGenerateEmail = async () => {
    setLoadingEmail(true);
    try {
      logger.info('Requesting recruiter email draft generation...');
      const response = await evaluationService.generateEmail(evaluationId);
      const data = response as { subject: string; body: string };
      setEmailSubject(data.subject);
      setEmailBody(data.body);
    } catch (err) {
      logger.error('Failed to generate email:', err);
    } finally {
      setLoadingEmail(false);
    }
  };

  const handleCopyEmail = () => {
    const textToCopy = `Subject: ${emailSubject}\n\n${emailBody}`;
    navigator.clipboard.writeText(textToCopy).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Interview Prep Questions Section */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <Heading level={3} style={{ fontSize: '18px', margin: 0 }}>Recruiter Technical Screener Questions</Heading>
        <Text variant="muted">
          Swarm-generated questions highlighting specific knowledge areas or anomalies discovered in the resume parsing stage.
        </Text>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {normalizedQuestions.length === 0 ? (
            <Card>
              <Text variant="muted">No custom interview questions generated for this candidate.</Text>
            </Card>
          ) : (
            normalizedQuestions.map((q) => (
              <Card key={q.id} style={{ borderLeft: '4px solid hsl(var(--primary))' }}>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                  <HelpCircle size={20} style={{ color: 'hsl(var(--primary))', flexShrink: 0, marginTop: '2px' }} />
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Heading level={4} style={{ fontSize: '14px', fontWeight: 600, margin: 0, color: '#ffffff' }}>
                        {q.text}
                      </Heading>
                      <span style={{
                        fontSize: '9px',
                        fontWeight: 700,
                        letterSpacing: '0.5px',
                        background: q.category === 'ADVANCED' ? 'hsla(var(--destructive), 0.12)' : q.category === 'MEDIUM' ? 'hsla(var(--accent), 0.12)' : 'hsla(var(--success), 0.12)',
                        color: q.category === 'ADVANCED' ? 'hsl(var(--destructive))' : q.category === 'MEDIUM' ? 'hsl(var(--accent))' : 'hsl(var(--success))',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        textTransform: 'uppercase',
                      }}>
                        {q.category}
                      </span>
                    </div>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>
      </div>

      {/* Recruiter invitation email template drafter */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <Heading level={3} style={{ fontSize: '18px', margin: 0 }}>Outreach & Schedulers Drafts</Heading>
        <Text variant="muted">
          Draft candidate outreach correspondence matching evaluated alignment metrics.
        </Text>

        {!emailBody ? (
          <Button
            variant="secondary"
            onClick={handleGenerateEmail}
            loading={loadingEmail}
            style={{ alignSelf: 'flex-start', display: 'flex', alignItems: 'center', gap: '8px' }}
          >
            <Mail size={16} /> Generate Outreach Email Draft
          </Button>
        ) : (
          <Card style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid hsl(var(--border))', paddingBottom: '12px' }}>
              <span style={{ fontSize: '13px', fontWeight: 600 }}>Draft: Interview Invitation</span>
              <div style={{ display: 'flex', gap: '8px' }}>
                <Button variant="ghost" size="sm" onClick={handleCopyEmail} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {copied ? <Check size={14} style={{ color: 'hsl(var(--success))' }} /> : <Copy size={14} />}
                  {copied ? 'Copied!' : 'Copy to Clipboard'}
                </Button>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <span style={{ fontSize: '12px', color: 'hsl(var(--muted-foreground))' }}>Subject line:</span>
              <div style={{ padding: '10px 12px', background: 'hsl(var(--secondary))', border: '1px solid hsl(var(--border))', borderRadius: 'var(--radius)', fontSize: '13px', color: '#ffffff', fontWeight: 500 }}>
                {emailSubject}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <span style={{ fontSize: '12px', color: 'hsl(var(--muted-foreground))' }}>Message context:</span>
              <textarea
                readOnly
                value={emailBody}
                style={{
                  width: '100%',
                  minHeight: '160px',
                  padding: '12px',
                  background: 'hsl(var(--secondary))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: 'var(--radius)',
                  fontSize: '13px',
                  color: '#ffffff',
                  outline: 'none',
                  resize: 'vertical',
                  fontFamily: 'inherit',
                  lineHeight: '1.5',
                }}
              />
            </div>
          </Card>
        )}
      </div>

    </div>
  );
};
export default InterviewPrep;
