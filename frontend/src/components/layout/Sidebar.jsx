import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Users, FileText, Settings, ChevronLeft, ChevronRight,
  Briefcase, Moon, Sun, Activity
} from 'lucide-react';
import { useTheme } from '../../providers/ThemeProvider';

const SIDEBAR_KEY = 'talentscout-sidebar-collapsed';

const navItems = [
  { path: '/',           icon: LayoutDashboard, label: 'Dashboard',     section: 'main' },
  { path: '/candidate',  icon: Users,           label: 'Candidate Portal', section: 'main' },
];

const bottomItems = [
  { path: '/settings',   icon: Settings,        label: 'Settings',      section: 'bottom' },
];

export default function Sidebar({ dbStatus = 'Checking...' }) {
  const location = useLocation();
  const { theme, toggleTheme, isDark } = useTheme();
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem(SIDEBAR_KEY) === 'true';
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(SIDEBAR_KEY, String(collapsed));
    } catch { /* storage unavailable */ }
  }, [collapsed]);

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  const NavLink = ({ item }) => {
    const active = isActive(item.path);
    const Icon = item.icon;
    return (
      <Link
        to={item.path}
        title={collapsed ? item.label : undefined}
        aria-label={item.label}
        className={`
          group flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium
          transition-all duration-150 relative
          ${active
            ? 'bg-brand-50 dark:bg-brand-950/40 text-brand-700 dark:text-brand-300'
            : 'text-surface-600 hover:text-surface-900 hover:bg-surface-100 dark:hover:bg-surface-200'
          }
          ${collapsed ? 'justify-center' : ''}
        `}
      >
        {active && (
          <span className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-brand-600 rounded-r-full" />
        )}
        <Icon className={`w-[18px] h-[18px] flex-shrink-0 ${active ? 'text-brand-600 dark:text-brand-400' : 'text-surface-400 group-hover:text-surface-600'}`} />
        {!collapsed && <span>{item.label}</span>}
      </Link>
    );
  };

  return (
    <aside
      className={`
        fixed top-0 left-0 h-screen z-50 flex flex-col
        border-r transition-all duration-200 ease-in-out
        ${collapsed ? 'w-[72px]' : 'w-[260px]'}
      `}
      style={{ background: 'var(--bg-sidebar)', borderColor: 'var(--border-primary)' }}
    >
      {/* Logo area */}
      <div className={`flex items-center h-14 px-4 border-b ${collapsed ? 'justify-center' : 'gap-3'}`}
           style={{ borderColor: 'var(--border-primary)' }}>
        <div className="w-8 h-8 rounded-lg bg-brand-600 flex items-center justify-center flex-shrink-0">
          <Briefcase className="w-4 h-4 text-white" />
        </div>
        {!collapsed && (
          <div className="flex flex-col min-w-0">
            <span className="text-sm font-bold text-heading tracking-tight truncate">TalentScout</span>
            <span className="text-2xs text-muted">Enterprise</span>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto scrollbar-none">
        <div className={`mb-3 ${collapsed ? 'text-center' : ''}`}>
          {!collapsed && (
            <span className="text-2xs font-semibold text-muted uppercase tracking-widest px-3">Navigation</span>
          )}
        </div>
        {navItems.map(item => (
          <NavLink key={item.path} item={item} />
        ))}
      </nav>

      {/* Bottom section */}
      <div className="px-3 pb-4 space-y-2 border-t pt-3" style={{ borderColor: 'var(--border-subtle)' }}>
        {/* API Status */}
        <div className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs ${collapsed ? 'justify-center' : ''}`}>
          <Activity className={`w-3.5 h-3.5 flex-shrink-0 ${dbStatus === 'Online' ? 'text-emerald-500' : dbStatus === 'Offline' ? 'text-red-500' : 'text-amber-500'}`} />
          {!collapsed && (
            <span className="text-muted font-medium">API: {dbStatus}</span>
          )}
        </div>

        {/* Theme toggle */}
        <button
          onClick={toggleTheme}
          title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
          className={`
            flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium w-full
            text-surface-600 hover:text-surface-900 hover:bg-surface-100 dark:hover:bg-surface-200
            transition-all duration-150
            ${collapsed ? 'justify-center' : ''}
          `}
        >
          {isDark ? <Sun className="w-[18px] h-[18px] text-amber-500" /> : <Moon className="w-[18px] h-[18px] text-surface-400" />}
          {!collapsed && <span>{isDark ? 'Light Mode' : 'Dark Mode'}</span>}
        </button>

        {/* Settings */}
        {bottomItems.map(item => (
          <NavLink key={item.path} item={item} />
        ))}

        {/* Collapse toggle */}
        <button
          onClick={() => setCollapsed(prev => !prev)}
          title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          className={`
            flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium w-full
            text-surface-400 hover:text-surface-600 hover:bg-surface-100 dark:hover:bg-surface-200
            transition-all duration-150
            ${collapsed ? 'justify-center' : ''}
          `}
        >
          {collapsed ? <ChevronRight className="w-[18px] h-[18px]" /> : <ChevronLeft className="w-[18px] h-[18px]" />}
          {!collapsed && <span className="text-muted">Collapse</span>}
        </button>
      </div>
    </aside>
  );
}
