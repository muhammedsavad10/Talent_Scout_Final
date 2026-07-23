import React from 'react';
import { Card, Heading, Text } from '@/shared/ui';
import type { TimelineMilestone } from '../types/candidate';
import { Briefcase } from 'lucide-react';

interface EvidenceTimelineProps {
  timeline: TimelineMilestone[];
}

export const EvidenceTimeline: React.FC<EvidenceTimelineProps> = ({ timeline }) => {
  if (timeline.length === 0) {
    return (
      <Card>
        <Text variant="muted">No career chronological milestones extracted from this profile.</Text>
      </Card>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <Heading level={3} style={{ fontSize: '18px', margin: 0 }}>Career Milestones</Heading>
      
      <div style={{
        position: 'relative',
        paddingLeft: '28px',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px'
      }}>
        {/* Vertical Timeline bar */}
        <div style={{
          position: 'absolute',
          left: '9px',
          top: '4px',
          bottom: '4px',
          width: '2px',
          background: 'hsl(var(--border))'
        }} />

        {timeline.map((item, index) => (
          <div key={index} style={{ position: 'relative' }}>
            
            {/* Timeline dot icon */}
            <div style={{
              position: 'absolute',
              left: '-28px',
              top: '2px',
              width: '20px',
              height: '20px',
              borderRadius: '50%',
              background: 'hsl(var(--background))',
              border: '2px solid hsl(var(--primary))',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'hsl(var(--primary))',
            }}>
              <Briefcase size={10} />
            </div>

            {/* Content card */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px' }}>
                <Heading level={4} style={{ fontSize: '15px', fontWeight: 600, margin: 0, color: '#ffffff' }}>
                  {item.role || 'Professional Role'}
                </Heading>
                {item.year && (
                  <span style={{
                    fontSize: '11px',
                    fontWeight: 600,
                    color: 'hsl(var(--accent))',
                    background: 'hsla(var(--accent), 0.1)',
                    padding: '2px 8px',
                    borderRadius: '12px'
                  }}>
                    {item.year}
                  </span>
                )}
              </div>
              
              {item.company && (
                <Text style={{ fontSize: '13px', fontWeight: 500, color: 'hsl(var(--muted-foreground))' }}>
                  {item.company}
                </Text>
              )}
              
              {item.description && (
                <Text variant="muted" style={{ fontSize: '13px', marginTop: '6px', lineHeight: '1.5' }}>
                  {item.description}
                </Text>
              )}
            </div>

          </div>
        ))}
      </div>
    </div>
  );
};
export default EvidenceTimeline;
