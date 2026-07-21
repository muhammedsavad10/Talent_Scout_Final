import React from 'react';

/**
 * ErrorBoundary - Catches rendering errors in child components.
 * Prevents a crash in one section from bringing down the entire application.
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('[ErrorBoundary] Caught error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center min-h-[300px] p-8">
          <div className="card p-8 max-w-md text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-red-50 dark:bg-red-950/50 flex items-center justify-center mx-auto">
              <span className="text-red-500 text-xl font-bold">!</span>
            </div>
            <h2 className="text-heading text-lg">Something went wrong</h2>
            <p className="text-muted text-sm">
              An unexpected error occurred in this section. The rest of the application is still working.
            </p>
            <button
              onClick={() => this.setState({ hasError: false, error: null })}
              className="btn-secondary"
            >
              Try Again
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
