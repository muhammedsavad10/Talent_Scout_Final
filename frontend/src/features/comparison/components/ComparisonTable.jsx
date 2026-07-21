import React from 'react';
import { CheckCircle, XCircle } from 'lucide-react';
import { useEvaluation } from '../../evaluation/context/EvaluationContext';

const getRecommendationStyle = (rec) => {
  const r = (rec || '').toLowerCase();
  if (r.includes('recommended')) return { bg: 'bg-emerald-50 dark:bg-emerald-950/20 border-emerald-250 dark:border-emerald-900/40', text: 'text-emerald-700 dark:text-emerald-400' };
  if (r.includes('review') || r.includes('backup')) return { bg: 'bg-amber-50 dark:bg-amber-950/20 border-amber-250 dark:border-amber-900/40', text: 'text-amber-700 dark:text-amber-400' };
  return { bg: 'bg-rose-50 dark:bg-rose-950/20 border-rose-250 dark:border-rose-900/40', text: 'text-rose-700 dark:text-rose-400' };
};

export default function ComparisonTable({ candidates, onViewResult }) {
  const { state, dispatch } = useEvaluation();
  const { selectedCandidates, sortConfig } = state;

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    dispatch({ type: 'BATCH/SET_SORT_CONFIG', payload: { key, direction } });
  };

  const toggleCandidateSelection = (evalId) => {
    dispatch({ type: 'BATCH/SELECT_CANDIDATE', payload: evalId });
  };

  return (
    <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-xl overflow-hidden shadow-sm">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50 dark:bg-surface-955 border-b border-slate-200 dark:border-slate-800">
              <th className="p-4"><input type="checkbox" disabled className="rounded text-indigo-600 dark:bg-surface-950" /></th>
              <th className="p-4 text-xs font-bold text-slate-500 uppercase cursor-pointer select-none" onClick={() => handleSort('rank')}>
                Rank {sortConfig.key === 'rank' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th className="p-4 text-xs font-bold text-slate-500 uppercase cursor-pointer select-none" onClick={() => handleSort('filename')}>
                Candidate {sortConfig.key === 'filename' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th className="p-4 text-xs font-bold text-slate-500 uppercase cursor-pointer select-none" onClick={() => handleSort('recommendation_tier')}>
                Policy Tier {sortConfig.key === 'recommendation_tier' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th className="p-4 text-xs font-bold text-slate-500 uppercase cursor-pointer select-none" onClick={() => handleSort('policy_eligible')}>
                Eligibility {sortConfig.key === 'policy_eligible' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th className="p-4 text-xs font-bold text-slate-500 uppercase cursor-pointer select-none" onClick={() => handleSort('overall_score')}>
                Score {sortConfig.key === 'overall_score' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th className="p-4 text-xs font-bold text-slate-500 uppercase cursor-pointer select-none" onClick={() => handleSort('skill_match')}>
                Skill Match {sortConfig.key === 'skill_match' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
              </th>
              <th className="p-4 text-xs font-bold text-slate-500 uppercase">Missing Critical</th>
              <th className="p-4 text-xs font-bold text-slate-500 uppercase">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
            {candidates.map(cand => (
              <tr key={cand.evaluation_id} className={`hover:bg-slate-50 dark:hover:bg-surface-950 transition ${!cand.policy_eligible ? 'bg-slate-50/50 dark:bg-surface-950/20' : ''}`}>
                <td className="p-4">
                  <input 
                    type="checkbox" 
                    checked={selectedCandidates.includes(cand.evaluation_id)}
                    onChange={() => toggleCandidateSelection(cand.evaluation_id)}
                    disabled={!selectedCandidates.includes(cand.evaluation_id) && selectedCandidates.length >= 4}
                    className="rounded text-indigo-600 focus:ring-indigo-500 dark:bg-surface-950"
                  />
                </td>
                <td className="p-4">
                  <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${cand.rank === 1 ? 'bg-amber-100 text-amber-700 dark:bg-amber-950/50 dark:text-amber-300' : 'bg-slate-100 text-slate-600 dark:bg-surface-850 dark:text-slate-400'}`}>
                    {cand.rank}
                  </span>
                </td>
                <td className="p-4 font-bold text-slate-800 dark:text-slate-200 text-sm truncate max-w-[200px]" title={cand.filename}>
                  {cand.filename.replace('.pdf', '')}
                </td>
                <td className="p-4">
                  <span className={`px-2.5 py-1 text-[10px] font-bold uppercase rounded-md border ${getRecommendationStyle(cand.recommendation_tier).bg} ${getRecommendationStyle(cand.recommendation_tier).text}`}>
                    {cand.recommendation_tier}
                  </span>
                </td>
                <td className="p-4">
                  {cand.policy_eligible ? (
                    <span className="flex items-center space-x-1 text-emerald-600 dark:text-emerald-400 text-xs font-bold"><CheckCircle className="w-3.5 h-3.5" /> <span>Eligible</span></span>
                  ) : (
                    <span className="flex items-center space-x-1 text-rose-600 dark:text-rose-400 text-xs font-bold"><XCircle className="w-3.5 h-3.5" /> <span>Not Suitable</span></span>
                  )}
                </td>
                <td className="p-4 font-black text-indigo-600 dark:text-indigo-400">{cand.overall_score}</td>
                <td className="p-4 font-semibold text-slate-700 dark:text-slate-350">{cand.skill_match}</td>
                <td className="p-4">
                  {cand.critical_missing.length > 0 ? (
                    <span className="text-rose-600 dark:text-rose-400 text-xs font-bold">{cand.critical_missing.length} skills</span>
                  ) : (
                    <span className="text-slate-400 dark:text-slate-600 text-xs font-bold">-</span>
                  )}
                </td>
                <td className="p-4">
                  <button 
                    onClick={() => onViewResult(cand)}
                    className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-350"
                  >
                    View Full Evaluation
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
