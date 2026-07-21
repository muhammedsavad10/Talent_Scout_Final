import { Users, CheckCircle, XCircle } from 'lucide-react';
import { useEvaluation } from '../context/EvaluationContext';

export default function EvidenceStep() {
  const { state } = useEvaluation();
  const { result } = state;

  if (!result) return null;

  const matched = result.evidenceStates?.matched || [];
  const missing = result.evidenceStates?.missing || [];

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Semantic Factual Evidence Logs */}
      <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
        <div className="flex items-center space-x-2">
          <div className="p-2 bg-indigo-50 dark:bg-indigo-950/40 rounded-lg text-indigo-600 dark:text-indigo-400">
            <Users className="w-5 h-5" />
          </div>
          <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">3. Factual Evidence Audit Logs</h2>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Identified/Matched Skills */}
          <div className="bg-slate-50 dark:bg-surface-950 border border-slate-200 dark:border-slate-850 rounded-xl p-5 space-y-3">
            <h3 className="text-xs font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider flex items-center">
              <CheckCircle className="w-4 h-4 mr-1.5" /> Identified / Matched Skills ({matched.length})
            </h3>
            <ul className="space-y-1.5">
              {matched.map((skill, idx) => (
                <li key={idx} className="text-xs font-bold text-slate-700 dark:text-slate-200 bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 flex items-center justify-between">
                  <span>{skill}</span>
                  <span className="text-[10px] font-bold text-emerald-600 uppercase">Verified</span>
                </li>
              ))}
              {matched.length === 0 && (
                <p className="text-xs text-slate-400 italic">No skills matched.</p>
              )}
            </ul>
          </div>

          {/* Missing Skills */}
          <div className="bg-slate-50 dark:bg-surface-950 border border-slate-200 dark:border-slate-850 rounded-xl p-5 space-y-3">
            <h3 className="text-xs font-bold text-rose-700 dark:text-rose-400 uppercase tracking-wider flex items-center">
              <XCircle className="w-4 h-4 mr-1.5" /> Missing Skills ({missing.length})
            </h3>
            <ul className="space-y-1.5">
              {missing.map((skill, idx) => (
                <li key={idx} className="text-xs font-bold text-slate-700 dark:text-slate-200 bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 flex items-center justify-between">
                  <span>{skill}</span>
                  <span className="text-[10px] font-bold text-rose-600 uppercase font-sans">Not Found</span>
                </li>
              ))}
              {missing.length === 0 && (
                <p className="text-xs text-slate-400 italic font-semibold">All required skills identified!</p>
              )}
            </ul>
          </div>
        </div>
      </div>

      {/* Business Impact Metrics */}
      <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
        <h3 className="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Extracted Business Impact & Quantifiable Outcomes</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {result.businessImpact.map((item, idx) => (
            <div key={idx} className="bg-indigo-50/30 dark:bg-indigo-950/10 border border-indigo-100 dark:border-indigo-900/30 rounded-xl p-4 flex items-start space-x-3 shadow-sm">
              <span className="w-2.5 h-2.5 bg-indigo-500 rounded-full flex-shrink-0 mt-1.5" />
              <div>
                <span className="text-[10px] font-black text-indigo-700 dark:text-indigo-300 uppercase tracking-wide bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded border border-indigo-150 dark:border-indigo-900/50">{item.category}</span>
                <p className="text-sm text-slate-700 dark:text-slate-300 mt-2 font-medium">{item.description}</p>
              </div>
            </div>
          ))}
          {(!result.businessImpact || result.businessImpact.length === 0) && (
            <p className="text-xs text-slate-400 italic col-span-2">No business impact outcomes extracted.</p>
          )}
        </div>
      </div>
    </div>
  );
}
