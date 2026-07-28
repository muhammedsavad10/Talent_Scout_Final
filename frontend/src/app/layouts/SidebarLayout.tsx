import React, { useState } from 'react';
import { NavLink, Outlet, useLocation } from 'react-router-dom';
import { ROUTES } from '@/shared/constants/routes';
import { Layout, Upload, Settings, BarChart2, Menu, X, Sun, Moon, LogOut } from 'lucide-react';
import { useTheme } from '@/app/providers/ThemeProvider';
import { useAuthStore } from '@/features/auth/store/useAuthStore';

export const SidebarLayout: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const menuItems = [
    { name: 'Dashboard', path: ROUTES.DASHBOARD, icon: BarChart2 },
    { name: 'Upload Resumes', path: ROUTES.UPLOAD, icon: Upload },
    { name: 'Settings', path: ROUTES.SETTINGS, icon: Settings },
  ];

  const handleLinkClick = () => {
    setMobileOpen(false);
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', width: '100vw', background: 'hsl(var(--background))' }}>
      
      {/* Sidebar - Desktop */}
      <aside style={{
        width: '260px',
        borderRight: '1px solid hsl(var(--border))',
        background: 'hsl(var(--card))',
        display: 'flex',
        flexDirection: 'column',
        position: 'fixed',
        top: 0,
        bottom: 0,
        left: 0,
        zIndex: 100,
      }} className="desktop-sidebar">
        <div style={{
          height: '64px',
          display: 'flex',
          alignItems: 'center',
          padding: '0 24px',
          borderBottom: '1px solid hsl(var(--border))',
          gap: '12px'
        }}>
          <Layout size={24} style={{ color: 'hsl(var(--accent))' }} />
          <h2 style={{ fontSize: '18px', fontWeight: 700, letterSpacing: '0.5px', margin: 0 }}>TalentScout</h2>
        </div>
        
        <nav style={{ flex: 1, padding: '24px 16px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={handleLinkClick}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '12px 16px',
                  borderRadius: 'var(--radius)',
                  color: isActive ? '#ffffff' : 'hsl(var(--muted-foreground))',
                  background: isActive ? 'linear-gradient(135deg, hsl(var(--primary)), #8b5cf6)' : 'transparent',
                  textDecoration: 'none',
                  fontSize: '14px',
                  fontWeight: 500,
                  transition: 'var(--transition)',
                }}
              >
                <Icon size={18} />
                {item.name}
              </NavLink>
            );
          })}
        </nav>
        
        {/* User Profile & Logout Section */}
        {user && (
          <div style={{ padding: '12px 16px', borderTop: '1px solid hsl(var(--border))', background: 'rgba(15, 23, 42, 0.4)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#fff',
                fontSize: '12px',
                fontWeight: 700
              }}>
                {user.full_name ? user.full_name.charAt(0) : 'R'}
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <p style={{ margin: 0, fontSize: '13px', fontWeight: 600, color: 'hsl(var(--foreground))', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {user.full_name}
                </p>
                <p style={{ margin: 0, fontSize: '11px', color: 'hsl(var(--muted-foreground))', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {user.email}
                </p>
              </div>
            </div>
            <button
              onClick={() => logout()}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '8px 12px',
                borderRadius: '6px',
                border: '1px solid rgba(239, 68, 68, 0.2)',
                background: 'rgba(239, 68, 68, 0.1)',
                color: '#f87171',
                fontSize: '12px',
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'var(--transition)'
              }}
            >
              <LogOut size={14} />
              Sign Out
            </button>
          </div>
        )}

        <div style={{ padding: '12px 16px', borderTop: '1px solid hsl(var(--border))', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span style={{ fontSize: '12px', color: 'hsl(var(--muted-foreground))' }}>System v1.0.0</span>
          <button
            onClick={toggleTheme}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'hsl(var(--muted-foreground))',
              cursor: 'pointer',
              display: 'flex',
              padding: '6px',
              borderRadius: '6px',
              transition: 'var(--transition)',
            }}
            aria-label="Toggle theme mode"
          >
            {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div style={{ flex: 1, paddingLeft: '260px', display: 'flex', flexDirection: 'column', minWidth: 0 }} className="main-viewport">
        {/* Mobile Header Top Navigation */}
        <header style={{
          height: '64px',
          borderBottom: '1px solid hsl(var(--border))',
          background: 'hsl(var(--card))',
          display: 'flex',
          alignItems: 'center',
          padding: '0 24px',
          justifyContent: 'space-between',
          position: 'sticky',
          top: 0,
          zIndex: 90,
        }} className="mobile-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'hsl(var(--foreground))',
                cursor: 'pointer',
                display: 'none',
              }}
              className="menu-toggle-btn"
              aria-label="Toggle menu drawer"
            >
              {mobileOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
            <h2 style={{ fontSize: '16px', fontWeight: 600, margin: 0 }} className="mobile-header-title">TalentScout Swarm</h2>
          </div>
          
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span style={{
              padding: '4px 10px',
              borderRadius: '12px',
              background: 'hsla(var(--success), 0.1)',
              color: 'hsl(var(--success))',
              fontSize: '11px',
              fontWeight: 500,
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'currentColor' }} />
              API Connected
            </span>
          </div>
        </header>
        
        {/* Router Viewport Outlet */}
        <main style={{ flex: 1, display: 'flex', width: '100%' }}>
          <Outlet />
        </main>
      </div>

      {/* Mobile Drawer Drawer Navigation Overlay */}
      {mobileOpen && (
        <div
          style={{
            position: 'fixed',
            top: '64px',
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0,0,0,0.6)',
            backdropFilter: 'blur(4px)',
            zIndex: 1000,
            display: 'flex',
          }}
          onClick={() => setMobileOpen(false)}
        >
          <div
            style={{
              width: '260px',
              background: 'hsl(var(--card))',
              height: '100%',
              padding: '24px 16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px',
              boxShadow: 'var(--shadow-lg)'
            }}
            onClick={(e) => e.stopPropagation()}
          >
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={handleLinkClick}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    padding: '12px 16px',
                    borderRadius: 'var(--radius)',
                    color: isActive ? '#ffffff' : 'hsl(var(--muted-foreground))',
                    background: isActive ? 'linear-gradient(135deg, hsl(var(--primary)), #8b5cf6)' : 'transparent',
                    textDecoration: 'none',
                    fontSize: '14px',
                    fontWeight: 500,
                  }}
                >
                  <Icon size={18} />
                  {item.name}
                </NavLink>
              );
            })}
          </div>
        </div>
      )}

      {/* Responsive Layout CSS Rules (embedded directly or inside index.css) */}
      <style>{`
        @media (max-width: 1024px) {
          .desktop-sidebar {
            display: none !important;
          }
          .main-viewport {
            padding-left: 0 !important;
          }
          .menu-toggle-btn {
            display: block !important;
          }
        }
      `}</style>
    </div>
  );
};
export default SidebarLayout;
