import React from 'react';
import { Heading } from './Heading';

export interface PageLayoutProps {
  title: string;
  subtitle?: React.ReactNode;
  actions?: React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export const PageLayout: React.FC<PageLayoutProps> = ({
  title,
  subtitle,
  actions,
  children,
  className = '',
}) => {
  return (
    <div className={`page-layout fade-in ${className}`} style={{
      display: 'flex',
      flexDirection: 'column',
      gap: '24px',
      width: '100%',
      padding: '24px',
    }}>
      <div style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        flexWrap: 'wrap',
        gap: '16px',
        borderBottom: '1px solid hsl(var(--border))',
        paddingBottom: '20px',
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <Heading level={1} style={{ fontSize: '28px', margin: 0 }}>{title}</Heading>
          {subtitle && (
            <div style={{ fontSize: '14px', color: 'hsl(var(--muted-foreground))', marginTop: '4px' }}>
              {subtitle}
            </div>
          )}
        </div>
        {actions && <div className="page-actions" style={{ display: 'flex', gap: '12px' }}>{actions}</div>}
      </div>
      <div className="page-content" style={{ display: 'flex', flexDirection: 'column', gap: '20px', width: '100%' }}>
        {children}
      </div>
    </div>
  );
};
export default PageLayout;
