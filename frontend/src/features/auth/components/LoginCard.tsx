import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Mail, LogIn, AlertCircle, Layout, Check } from 'lucide-react';
import { PasswordField } from './PasswordField';

interface LoginCardProps {
  onLoginSubmit: (email: string, pass: string) => Promise<void>;
  isLoading: boolean;
  error: string | null;
  onClearError: () => void;
}

export const LoginCard: React.FC<LoginCardProps> = ({
  onLoginSubmit,
  isLoading,
  error,
  onClearError,
}) => {
  const [email, setEmail] = useState('recruiter@talentscout.ai');
  const [password, setPassword] = useState('Recruiter123!');
  const [rememberMe, setRememberMe] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [successState, setSuccessState] = useState(false);

  const emailInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    emailInputRef.current?.focus();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isSubmitting || isLoading) return;

    onClearError();
    setIsSubmitting(true);
    try {
      await onLoginSubmit(email, password);
      setSuccessState(true);
    } catch {
      setSuccessState(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  const busy = isLoading || isSubmitting || successState;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98, y: 12 }}
      animate={{ opacity: 1, scale: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="w-full max-w-[420px] bg-slate-900/90 backdrop-blur-xl border border-slate-800 rounded-2xl p-8 sm:p-9 shadow-[0_20px_50px_rgba(0,0,0,0.6)] relative z-10 space-y-6"
    >
      {/* Brand Header */}
      <div className="flex flex-col items-center text-center space-y-3">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 p-0.5 shadow-lg shadow-indigo-500/20">
          <div className="w-full h-full bg-slate-950 rounded-[14px] flex items-center justify-center">
            <Layout className="w-6 h-6 text-indigo-400" />
          </div>
        </div>
        <div>
          <h1 className="text-xl font-extrabold text-white tracking-tight">
            TalentScout Enterprise
          </h1>
          <p className="text-xs text-slate-400 font-medium mt-0.5">
            Enterprise Recruitment Intelligence Platform
          </p>
        </div>
      </div>

      <div className="text-center border-t border-slate-800/80 pt-5">
        <h2 className="text-lg font-bold text-white tracking-tight">
          Welcome Back
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Enter your recruiter credentials to access the portal
        </p>
      </div>

      {/* Error Alert */}
      <AnimatePresence mode="wait">
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -10, height: 0 }}
            animate={{ opacity: 1, y: 0, height: 'auto' }}
            exit={{ opacity: 0, y: -10, height: 0 }}
            className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/25 text-rose-300 text-xs flex items-start gap-2.5"
          >
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <span className="font-bold block uppercase tracking-wider text-[11px] text-rose-300">
                Authentication Failure
              </span>
              <p className="text-rose-200 mt-0.5">{error}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Login Form */}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-1.5">
          <label className="block text-xs font-semibold text-slate-300">
            Recruiter Email
          </label>
          <div className="relative w-full">
            <div className="absolute inset-y-0 left-0 w-12 flex items-center justify-center pointer-events-none z-10">
              <Mail className="h-5 w-5 text-slate-400" />
            </div>
            <input
              ref={emailInputRef}
              type="email"
              required
              disabled={busy}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="recruiter@talentscout.ai"
              className="w-full h-12 bg-slate-950 border border-slate-800 rounded-xl !pl-12 pr-4 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/25 transition duration-200 disabled:opacity-50 font-medium shadow-inner"
            />
          </div>
        </div>

        <PasswordField
          value={password}
          disabled={busy}
          onChange={(e) => setPassword(e.target.value)}
        />

        <div className="flex items-center justify-between pt-0.5">
          <label className="flex items-center gap-2 cursor-pointer select-none text-xs text-slate-400 font-medium">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="w-4 h-4 rounded border-slate-800 bg-slate-950 text-indigo-600 focus:ring-indigo-500 focus:ring-offset-slate-900 cursor-pointer"
            />
            <span>Remember this device</span>
          </label>
        </div>

        <motion.button
          whileHover={{ scale: 1.01 }}
          whileTap={{ scale: 0.99 }}
          type="submit"
          disabled={busy}
          className="w-full h-12 bg-gradient-to-r from-indigo-600 via-indigo-500 to-purple-600 hover:from-indigo-500 hover:to-purple-500 active:from-indigo-700 active:to-purple-700 disabled:opacity-50 text-white font-semibold rounded-xl text-sm flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/25 transition duration-200 cursor-pointer mt-3"
        >
          {successState ? (
            <span className="flex items-center gap-2 text-emerald-300 font-bold">
              <Check className="w-4 h-4 text-emerald-400" />
              Authenticated! Redirecting...
            </span>
          ) : busy ? (
            <span className="flex items-center gap-2">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Signing In...
            </span>
          ) : (
            <>
              <LogIn className="w-4 h-4" />
              Sign In
            </>
          )}
        </motion.button>
      </form>
    </motion.div>
  );
};

export default LoginCard;
