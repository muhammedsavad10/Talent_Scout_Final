import React from 'react';
import { useEvaluation } from '../context/EvaluationContext';
import { getDimensionLabel } from '../../../utils/dimensionLabels';

export default function DimensionScorePanel() {
  const { state } = useEvaluation();
  const { result } = state;

  if (!result || !result.dimensionScores || result.dimensionScores.length === 0) return null;

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4 animate-fadeIn">
      {result.dimensionScores.map(dim => (
        <div key={dim.key} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm text-center space-y-1 hover:border-indigo-300 transition-colors cursor-default" title={dim.evidence?.join('\n')}>
          <span className="text-[10px] sm:text-xs font-bold text-slate-400 uppercase tracking-wider block truncate">{getDimensionLabel(dim.key)}</span>
          <span className="text-2xl sm:text-3xl font-black text-indigo-600 font-sans">
            {dim.score}
          </span>
          <span className="text-[9px] text-slate-400 font-bold tracking-wider block">CONF: {dim.confidence}%</span>
        </div>
      ))}
    </div>
  );
}
