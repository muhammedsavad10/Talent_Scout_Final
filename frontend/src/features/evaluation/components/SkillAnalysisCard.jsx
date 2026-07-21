import React from 'react';
import { useEvaluation } from '../context/EvaluationContext';

export default function SkillAnalysisCard() {
  const { state } = useEvaluation();
  const { result } = state;

  if (!result) return null;

  const matched = result.evidenceStates?.matched || [];
  const missing = result.evidenceStates?.missing || [];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 animate-fadeIn">
      {/* Matched Skills */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
          Matched Skills ({matched.length})
        </h3>
        <div className="flex flex-wrap gap-2">
          {matched.map((skill, idx) => (
            <span key={idx} className="px-2.5 py-1 bg-emerald-50 border border-emerald-100 text-emerald-700 text-xs font-bold rounded-lg animate-fadeIn">
              {skill}
            </span>
          ))}
          {matched.length === 0 && (
            <p className="text-xs text-slate-400 italic">No skills matched.</p>
          )}
        </div>
      </div>

      {/* Missing Skills */}
      <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
        <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
          Missing Skills ({missing.length})
        </h3>
        <div className="flex flex-wrap gap-2">
          {missing.map((skill, idx) => (
            <span key={idx} className="px-2.5 py-1 bg-rose-50 border border-rose-100 text-rose-700 text-xs font-bold rounded-lg animate-fadeIn">
              {skill}
            </span>
          ))}
          {missing.length === 0 && (
            <p className="text-xs text-slate-400 italic font-semibold">All required skills identified!</p>
          )}
        </div>
      </div>
    </div>
  );
}
