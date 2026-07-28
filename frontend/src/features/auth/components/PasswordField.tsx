import React, { useState } from 'react';
import { Lock, Eye, EyeOff, AlertTriangle } from 'lucide-react';

interface PasswordFieldProps {
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  disabled?: boolean;
}

export const PasswordField: React.FC<PasswordFieldProps> = ({
  value,
  onChange,
  placeholder = '••••••••••••',
  disabled = false,
}) => {
  const [showPassword, setShowPassword] = useState(false);
  const [capsLockOn, setCapsLockOn] = useState(false);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.getModifierState('CapsLock')) {
      setCapsLockOn(true);
    } else {
      setCapsLockOn(false);
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label className="block text-xs font-semibold text-slate-300">
          Password
        </label>
        <button
          type="button"
          tabIndex={-1}
          onClick={() => {}}
          className="text-xs text-indigo-400 hover:text-indigo-300 font-medium transition cursor-pointer"
        >
          Forgot password?
        </button>
      </div>

      <div className="relative w-full">
        <div className="absolute inset-y-0 left-0 w-12 flex items-center justify-center pointer-events-none z-10">
          <Lock className="h-5 w-5 text-slate-400" />
        </div>
        <input
          type={showPassword ? 'text' : 'password'}
          required
          disabled={disabled}
          value={value}
          onChange={onChange}
          onKeyDown={handleKeyDown}
          onKeyUp={handleKeyDown}
          placeholder={placeholder}
          className="w-full h-12 bg-slate-950 border border-slate-800 rounded-xl !pl-12 !pr-12 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/25 transition duration-200 disabled:opacity-50 font-medium shadow-inner"
        />
        <button
          type="button"
          tabIndex={-1}
          onClick={() => setShowPassword(!showPassword)}
          className="absolute inset-y-0 right-0 w-12 flex items-center justify-center text-slate-400 hover:text-slate-200 transition cursor-pointer z-10"
          aria-label={showPassword ? 'Hide password' : 'Show password'}
        >
          {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
        </button>
      </div>

      {capsLockOn && (
        <div className="flex items-center gap-1.5 text-xs text-amber-400 font-medium pt-0.5">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>Caps Lock is ON</span>
        </div>
      )}
    </div>
  );
};

export default PasswordField;
