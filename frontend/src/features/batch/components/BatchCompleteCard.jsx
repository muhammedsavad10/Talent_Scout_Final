import React from 'react';
import { CheckCircle } from 'lucide-react';
import { useEvaluation } from '../../evaluation/context/EvaluationContext';

export default function BatchCompleteCard({ onViewComparison }) {
  const { state } = useEvaluation();
  const { batchResult } = state;

  if (!batchResult) return null;

  return (
    <div className="bg-emerald-50 dark:bg-emerald-950/10 border border-emerald-200 dark:border-emerald-900/30 rounded-xl p-6 shadow-sm text-center space-y-4">
      <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto" />
      <div>
        <h3 className="text-lg font-bold text-emerald-800 dark:text-emerald-300">Batch Evaluation Complete</h3>
        <p className="text-emerald-600 dark:text-emerald-400 text-sm mt-1">{batchResult.successfully_evaluated} candidates evaluated successfully.</p>
      </div>
      <button
        onClick={onViewComparison}
        className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg shadow transition"
      >
        View Candidate Comparison
      </button>
    </div>
  );
}
