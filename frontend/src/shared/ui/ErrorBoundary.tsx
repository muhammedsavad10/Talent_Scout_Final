import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';
import { Card, Heading, Text, Button } from '@/shared/ui';
import { AlertCircle } from 'lucide-react';
import { logger } from '@/shared/utils';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public override state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public override componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    logger.error('React component tree crash caught by ErrorBoundary:', error, errorInfo);
  }

  private handleReset = () => {
    this.setState({ hasError: false, error: null });
    window.location.reload();
  };

  private handleReturnHome = () => {
    this.setState({ hasError: false, error: null });
    window.location.href = '/';
  };

  public override render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          width: '100vw',
          padding: '24px',
          background: 'hsl(var(--background))',
        }}>
          <Card style={{ maxWidth: '500px', width: '100%', padding: '32px', textAlign: 'center', display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'center' }}>
              <div style={{
                width: '56px',
                height: '56px',
                borderRadius: '50%',
                background: 'hsla(var(--destructive), 0.1)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'hsl(var(--destructive))',
              }}>
                <AlertCircle size={28} />
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <Heading level={2} style={{ fontSize: '20px', margin: 0 }}>Something went wrong</Heading>
              <Text variant="muted">
                The application encountered an unexpected runtime failure. The error has been captured.
              </Text>
            </div>

            {this.state.error && (
              <div style={{
                padding: '12px',
                background: 'hsl(var(--secondary))',
                borderRadius: 'var(--radius)',
                border: '1px solid hsl(var(--border))',
                fontSize: '12px',
                color: 'hsl(var(--destructive))',
                textAlign: 'left',
                fontFamily: 'monospace',
                wordBreak: 'break-all',
                maxHeight: '120px',
                overflowY: 'auto',
              }}>
                {this.state.error.toString()}
              </div>
            )}

            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '8px' }}>
              <Button variant="primary" onClick={this.handleReset}>
                Reload Application
              </Button>
              <Button variant="secondary" onClick={this.handleReturnHome}>
                Go to Dashboard
              </Button>
            </div>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}
export default ErrorBoundary;
