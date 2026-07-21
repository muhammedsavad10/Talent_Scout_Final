import React from 'react';
import { Users, XCircle } from 'lucide-react';
import { useEvaluation } from '../evaluation/context/EvaluationContext';
import ComparisonTable from './components/ComparisonTable';
import CandidateCard from './components/CandidateCard';

export default function ComparisonFeature({ onViewResult }) {
  const { state, dispatch } = useEvaluation();
  const { 
    batchResult, filterTier, selectedCandidates, showSideBySide 
  } = state;

  if (!batchResult || !batchResult.ranked_candidates) return null;

  const getSortedFilteredCandidates = () => {
    let filtered = [...batchResult.ranked_candidates];
    
    if (filterTier !== 'All') {
      filtered = filtered.filter(c => c.recommendation_tier === filterTier);
    }
    
    if (state.sortConfig.key !== 'rank') {
      filtered.sort((a, b) => {
        let aVal = a[state.sortConfig.key];
        let bVal = b[state.sortConfig.key];
        
        if (state.sortConfig.key === 'policy_eligible') {
          aVal = a.policy_eligible ? 1 : 0;
          bVal = b.policy_eligible ? 1 : 0;
        }

        if (aVal < bVal) return state.sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return state.sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    
    return filtered;
  };

  const filteredCandidates = getSortedFilteredCandidates();

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-slate-800 dark:text-slate-200 font-sans">Candidate Comparison</h2>
        <div className="flex space-x-3">
          <select 
            value={filterTier}
            onChange={(e) => dispatch({ type: 'BATCH/SET_FILTER_TIER', payload: e.target.value })}
            className="px-3 py-1.5 border border-slate-200 dark:border-slate-800 rounded-lg text-sm text-slate-700 dark:text-slate-300 font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white dark:bg-surface-900"
          >
            <option value="All">All Tiers</option>
            <option value="Recommended">Recommended</option>
            <option value="Review Before Interview">Review</option>
            <option value="Keep as Backup">Backup</option>
            <option value="Not Suitable for this Role">Not Suitable</option>
          </select>
          
          <button 
            onClick={() => dispatch({ type: 'BATCH/TOGGLE_SIDE_BY_SIDE', payload: true })}
            disabled={selectedCandidates.length < 2 || selectedCandidates.length > 4}
            className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-350 text-white text-sm font-bold rounded-lg transition"
          >
            Compare Selected ({selectedCandidates.length})
          </button>
        </div>
      </div>

      <ComparisonTable candidates={filteredCandidates} onViewResult={onViewResult} />
      
      {/* Side-by-side Modal */}
      {showSideBySide && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="bg-white dark:bg-surface-900 rounded-2xl shadow-xl w-full max-w-6xl max-h-[90vh] flex flex-col overflow-hidden">
            <div className="p-4 border-b border-slate-100 dark:border-slate-800 flex justify-between items-center bg-slate-50 dark:bg-surface-955">
              <h2 className="text-lg font-bold text-slate-800 dark:text-slate-200 flex items-center"><Users className="w-5 h-5 mr-2 text-indigo-600" /> Side-by-Side Comparison</h2>
              <button onClick={() => dispatch({ type: 'BATCH/TOGGLE_SIDE_BY_SIDE', payload: false })} className="p-2 hover:bg-slate-250 dark:hover:bg-surface-850 rounded-lg"><XCircle className="w-5 h-5 text-slate-500" /></button>
            </div>
            
            <div className="p-6 overflow-auto flex-1 bg-slate-50/50 dark:bg-surface-950/20">
              <div className="flex space-x-4 min-w-max pb-2">
                {selectedCandidates.map(evalId => {
                  const cand = batchResult.ranked_candidates.find(c => c.evaluation_id === evalId);
                  return (
                    <CandidateCard 
                      key={evalId} 
                      candidate={cand} 
                      onViewResult={(selectedCand) => {
                        dispatch({ type: 'BATCH/TOGGLE_SIDE_BY_SIDE', payload: false });
                        onViewResult(selectedCand);
                      }} 
                    />
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
