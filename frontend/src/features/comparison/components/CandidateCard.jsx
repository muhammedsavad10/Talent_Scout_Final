import React from 'react';

const getRecommendationStyle = (rec) => {
  const r = (rec || '').toLowerCase();
  if (r.includes('recommended')) return { bg: 'bg-emerald-50 dark:bg-emerald-950/20 border-emerald-250 dark:border-emerald-900/40', text: 'text-emerald-700 dark:text-emerald-400' };
  if (r.includes('review') || r.includes('backup')) return { bg: 'bg-amber-50 dark:bg-amber-950/20 border-amber-250 dark:border-amber-900/40', text: 'text-amber-700 dark:text-amber-400' };
  return { bg: 'bg-rose-50 dark:bg-rose-950/20 border-rose-250 dark:border-rose-900/40', text: 'text-rose-700 dark:text-rose-400' };
};

export default function CandidateCard({ candidate, onViewResult }) {
  if (!candidate) return null;

  return (
    <div className="w-80 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden flex-shrink-0 bg-white dark:bg-surface-900 shadow-sm">
      <div className="p-4 bg-slate-50 dark:bg-surface-955 border-b border-slate-200 dark:border-slate-800">
        <h3 className="font-bold text-slate-800 dark:text-slate-200 truncate" title={candidate.filename}>{candidate.filename}</h3>
        <div className="flex items-center space-x-2 mt-2">
          <span className="text-xl font-black text-indigo-600 dark:text-indigo-400">{candidate.overall_score}</span>
          <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${candidate.policy_eligible ? 'bg-emerald-100 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300' : 'bg-rose-100 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300'}`}>
            {candidate.policy_eligible ? 'Eligible' : 'Failed'}
          </span>
        </div>
      </div>
      <div className="p-4 space-y-4 text-sm">
        <div>
          <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase mb-1">Tier</p>
          <p className={`font-semibold ${getRecommendationStyle(candidate.recommendation_tier).text}`}>{candidate.recommendation_tier}</p>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase mb-1">Skill</p>
            <p className="font-bold text-slate-700 dark:text-slate-200">{candidate.skill_match}</p>
          </div>
          <div>
            <p className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase mb-1">Relevance</p>
            <p className="font-bold text-slate-700 dark:text-slate-200">{candidate.experience_relevance}</p>
          </div>
        </div>
        <div>
          <p className="text-xs font-bold text-emerald-600 dark:text-emerald-400 uppercase mb-1">Strengths ({candidate.strengths.length})</p>
          <ul className="list-disc pl-4 space-y-1 text-slate-600 dark:text-slate-400 text-xs font-medium">
            {candidate.strengths.slice(0, 3).map((s, i) => <li key={i}>{s}</li>)}
            {candidate.strengths.length > 3 && <li>+{candidate.strengths.length - 3} more</li>}
          </ul>
        </div>
        <div>
          <p className="text-xs font-bold text-rose-600 dark:text-rose-455 uppercase mb-1">Missing Critical</p>
          {candidate.critical_missing.length > 0 ? (
            <div className="flex flex-wrap gap-1">
              {candidate.critical_missing.map((s, i) => <span key={i} className="px-1.5 py-0.5 bg-rose-50 dark:bg-rose-955 border border-rose-100 dark:border-rose-900 text-rose-700 dark:text-rose-350 rounded text-[10px] font-bold">{s}</span>)}
            </div>
          ) : <p className="text-slate-400 italic text-xs">None</p>}
        </div>
        <div className="pt-4 border-t border-slate-100 dark:border-slate-800 text-center">
          <button 
            onClick={() => onViewResult(candidate)}
            className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-350"
          >
            View Full Evaluation
          </button>
        </div>
      </div>
    </div>
  );
}
