import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { ROUTES } from '@/shared/constants/routes';
import { AnimatedBackground } from '../components/AnimatedBackground';
import { LoginCard } from '../components/LoginCard';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, isLoading, error, clearError } = useAuthStore();

  const from = (location.state as any)?.from?.pathname || ROUTES.DASHBOARD;

  const handleLoginSubmit = async (email: string, pass: string) => {
    await login({ email, password: pass });
    // Navigate immediately upon successful login resolution
    navigate(from, { replace: true });
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex items-center justify-center p-4 relative overflow-hidden font-sans">
      {/* Background Ambient FX */}
      <AnimatedBackground />

      {/* Centered Minimal Enterprise Login Container */}
      <div className="w-full flex items-center justify-center relative z-10 my-auto">
        <LoginCard
          onLoginSubmit={handleLoginSubmit}
          isLoading={isLoading}
          error={error}
          onClearError={clearError}
        />
      </div>
    </div>
  );
};

export default LoginPage;
