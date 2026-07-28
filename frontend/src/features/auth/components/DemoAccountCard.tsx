import React, { useState } from 'react';
import { Sparkles, Check, ArrowRight } from 'lucide-react';

interface DemoAccountCardProps {
  onFillCredentials: (email: string, pass: string) => void;
  disabled?: boolean;
}

export const DemoAccountCard: React.FC<DemoAccountCardProps> = ({
  onFillCredentials,
  disabled = false,
}) => {
  const [filled, setFilled] = useState(false);

  const handleAutoFill = () => {
    onFillCredentials('recruiter@talentscout.ai', 'Recruiter123!');
    setFilled(true);
    setTimeout(() => setFilled(false), 2500);
  };

  return (
    <div className="mt-6 pt-6 border-t border-slate-800/80">
      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800/90 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-inner">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-indigo-500/15 border border-indigo-500/30 flex items-center justify-center shrink-0">
            <Sparkles className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-200">
              Recruiter Sandbox
            </h4>
            <p className="text-[11px] text-slate-400">
              Experience TalentScout instantly
            </p>
          </div>
        </div>

        <button
          type="button"
          disabled={disabled}
          onClick={handleAutoFill}
          className="px-3.5 py-2 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/30 border border-indigo-500/30 text-xs text-indigo-300 font-semibold flex items-center justify-center gap-1.5 transition duration-200 cursor-pointer disabled:opacity-50 shrink-0"
        >
          {filled ? (
            <>
              <Check className="w-3.5 h-3.5 text-emerald-400" />
              <span>Auto Filled</span>
            </>
          ) : (
            <>
              <span>Auto Fill Credentials</span>
              <ArrowRight className="w-3.5 h-3.5 text-indigo-400" />
            </>
          )}
        </button>
      </div>
    </div>
  );
};

export default DemoAccountCard;
