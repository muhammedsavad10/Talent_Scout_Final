import React, { useEffect } from 'react';
import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/features/auth/store/useAuthStore';
import { ROUTES } from '@/shared/constants/routes';
import { ShieldCheck, Loader2 } from 'lucide-react';

interface ProtectedRouteProps {
  children?: React.ReactNode;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();
  const location = useLocation();

  useEffect(() => {
    // Only verify session on initial mount if not already authenticated
    if (!isAuthenticated) {
      checkAuth();
    }
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 flex flex-col items-center justify-center p-4 text-slate-100">
        <div className="relative flex items-center justify-center mb-6">
          <div className="w-16 h-16 rounded-2xl bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center backdrop-blur-md animate-pulse">
            <ShieldCheck className="w-8 h-8 text-indigo-400" />
          </div>
          <Loader2 className="w-20 h-20 text-indigo-500/50 animate-spin absolute" />
        </div>
        <h3 className="text-xl font-semibold tracking-tight text-white mb-2">TalentScout Enterprise</h3>
        <p className="text-sm text-slate-400 animate-pulse">Verifying secure recruiter session...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to={ROUTES.LOGIN} state={{ from: location }} replace />;
  }

  return children ? <>{children}</> : <Outlet />;
};

export default ProtectedRoute;
