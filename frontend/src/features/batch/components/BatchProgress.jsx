import React from 'react';
import { Activity } from 'lucide-react';
import { useEvaluation } from '../../evaluation/context/EvaluationContext';

export default function BatchProgress() {
  const { state } = useEvaluation();
  const { batchStatus } = state;

  if (!batchStatus) return null;

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200 flex items-center space-x-2">
        <Activity className="w-4 h-4 text-indigo-500" />
        <span>Batch Evaluation Progress</span>
      </h3>
      <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-xl p-6 shadow-sm">
        <div className="flex justify-between items-center mb-4">
          <span className="text-slate-500 dark:text-slate-400 font-bold text-sm">Total Candidates: {batchStatus.total}</span>
          <span className="text-indigo-600 dark:text-indigo-400 font-bold text-sm">Batch ID: {batchStatus.batch_id.substring(0, 8)}...</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
          <div className="p-3 bg-emerald-50 dark:bg-emerald-950/20 rounded-lg border border-emerald-100 dark:border-emerald-900/30">
            <div className="text-2xl font-black text-emerald-600 dark:text-emerald-400">{batchStatus.completed}</div>
            <div className="text-xs font-bold text-emerald-800 dark:text-emerald-300 uppercase">Completed</div>
          </div>
          <div className="p-3 bg-indigo-50 dark:bg-indigo-950/20 rounded-lg border border-indigo-100 dark:border-indigo-900/30">
            <div className="text-2xl font-black text-indigo-600 dark:text-indigo-400">{batchStatus.processing}</div>
            <div className="text-xs font-bold text-indigo-800 dark:text-indigo-300 uppercase">Processing</div>
          </div>
          <div className="p-3 bg-slate-50 dark:bg-slate-850/40 rounded-lg border border-slate-100 dark:border-slate-800/40">
            <div className="text-2xl font-black text-slate-600 dark:text-slate-400">{batchStatus.pending}</div>
            <div className="text-xs font-bold text-slate-800 dark:text-slate-300 uppercase">Pending</div>
          </div>
          <div className="p-3 bg-rose-50 dark:bg-rose-950/20 rounded-lg border border-rose-100 dark:border-rose-900/30">
            <div className="text-2xl font-black text-rose-600 dark:text-rose-400">{batchStatus.failed}</div>
            <div className="text-xs font-bold text-rose-800 dark:text-rose-300 uppercase">Failed</div>
          </div>
        </div>
        
        {batchStatus.status === 'PROCESSING' && (
          <div className="mt-6 w-full bg-slate-100 dark:bg-slate-850 rounded-full h-2 overflow-hidden">
            <div 
              className="bg-indigo-600 h-2 rounded-full transition-all duration-500" 
              style={{ width: `${((batchStatus.completed + batchStatus.failed) / batchStatus.total) * 100}%` }}
            />
          </div>
        )}
      </div>
    </div>
  );
}
