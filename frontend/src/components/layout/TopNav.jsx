import React from 'react';
import { useLocation } from 'react-router-dom';
import { Shield } from 'lucide-react';

const DEMO_MODE = import.meta.env.VITE_DEMO_MODE !== 'false';

/**
 * Breadcrumb mapping from pathname to labels.
 */
function getBreadcrumbs(pathname) {
  const crumbs = [{ label: 'Dashboard', path: '/' }];

  if (pathname.startsWith('/batch/') && pathname.includes('/compare')) {
    crumbs.push({ label: 'Batch Processing', path: pathname.replace('/compare', '') });
    crumbs.push({ label: 'Candidate Comparison', path: pathname });
  } else if (pathname.startsWith('/batch/')) {
    crumbs.push({ label: 'Batch Processing', path: pathname });
  } else if (pathname.startsWith('/evaluation/')) {
    crumbs.push({ label: 'Full Evaluation', path: pathname });
  } else if (pathname === '/candidate') {
    crumbs.push({ label: 'Candidate Portal', path: pathname });
  } else if (pathname === '/settings') {
    crumbs.push({ label: 'Settings', path: pathname });
  }

  return crumbs;
}

export default function TopNav({ activeRole, onRoleChange }) {
  const location = useLocation();
  const breadcrumbs = getBreadcrumbs(location.pathname);

  return (
    <header
      className="sticky top-0 z-40 flex items-center justify-between h-14 px-6 border-b"
      style={{ background: 'var(--bg-card)', borderColor: 'var(--border-primary)' }}
    >
      {/* Breadcrumbs */}
      <nav aria-label="Breadcrumb" className="flex items-center gap-1.5 text-sm">
        {breadcrumbs.map((crumb, idx) => (
          <React.Fragment key={crumb.path}>
            {idx > 0 && <span className="text-surface-300 select-none">/</span>}
            {idx === breadcrumbs.length - 1 ? (
              <span className="font-semibold text-heading">{crumb.label}</span>
            ) : (
              <span className="text-muted hover:text-surface-700 cursor-default transition-colors">
                {crumb.label}
              </span>
            )}
          </React.Fragment>
        ))}
      </nav>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* RBAC Role Switcher (Demo Mode Only) */}
        {DEMO_MODE && (
          <div className="flex items-center gap-2 bg-surface-100 dark:bg-surface-200 rounded-lg px-3 py-1.5 border"
               style={{ borderColor: 'var(--border-primary)' }}>
            <Shield className="w-3.5 h-3.5 text-brand-600" />
            <span className="text-2xs font-semibold text-muted uppercase tracking-wider hidden sm:inline">Role:</span>
            <select
              value={activeRole}
              onChange={onRoleChange}
              className="bg-transparent text-xs font-bold text-heading focus:outline-none cursor-pointer pr-1"
              aria-label="Select active role"
            >
              <option value="Admin">Admin</option>
              <option value="Recruiter">Recruiter</option>
              <option value="Hiring Manager">Hiring Manager</option>
              <option value="Interviewer">Interviewer</option>
              <option value="Candidate">Candidate</option>
            </select>
          </div>
        )}
      </div>
    </header>
  );
}
