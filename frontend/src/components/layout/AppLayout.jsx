import React, { useState, useEffect } from 'react';
import Sidebar from './Sidebar';
import TopNav from './TopNav';
import ErrorBoundary from '../common/ErrorBoundary';

const SIDEBAR_KEY = 'talentscout-sidebar-collapsed';

/**
 * AppLayout — The main application shell.
 *
 * Wraps every page with the sidebar, top nav, and error boundary.
 * The sidebar collapsed state is read from localStorage to sync
 * the main content margin with the sidebar width.
 */
export default function AppLayout({ children, activeRole, onRoleChange, dbStatus }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
    try {
      return localStorage.getItem(SIDEBAR_KEY) === 'true';
    } catch {
      return false;
    }
  });

  // Listen for sidebar state changes via localStorage
  useEffect(() => {
    const handler = () => {
      try {
        setSidebarCollapsed(localStorage.getItem(SIDEBAR_KEY) === 'true');
      } catch { /* ignore */ }
    };
    // Poll on a short interval since storage events only fire cross-tab
    const interval = setInterval(handler, 300);
    window.addEventListener('storage', handler);
    return () => {
      clearInterval(interval);
      window.removeEventListener('storage', handler);
    };
  }, []);

  const mainMargin = sidebarCollapsed ? '72px' : '260px';

  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-app)' }}>
      {/* Sidebar */}
      <Sidebar dbStatus={dbStatus} />

      {/* Main content area */}
      <div
        className="transition-all duration-200 ease-in-out min-h-screen flex flex-col"
        style={{ marginLeft: mainMargin }}
      >
        <TopNav activeRole={activeRole} onRoleChange={onRoleChange} />

        <main className="flex-1 px-6 py-6 lg:px-8">
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </main>
      </div>
    </div>
  );
}
