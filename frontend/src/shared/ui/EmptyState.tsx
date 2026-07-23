import React from 'react';

export interface EmptyStateProps {
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title = 'No records found',
  description = 'Try adjusting your filters or upload a new resume to get started.',
  icon,
  action,
}) => {
  return (
    <div className="empty-state fade-in">
      {icon ? (
        <div style={{ color: 'hsl(var(--muted-foreground))' }}>{icon}</div>
      ) : (
        <div style={{
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          background: 'hsla(var(--foreground), 0.03)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'hsl(var(--muted-foreground))',
          fontSize: '24px'
        }}>
          ?
        </div>
      )}
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-desc">{description}</p>
      {action && <div style={{ marginTop: '20px' }}>{action}</div>}
    </div>
  );
};
