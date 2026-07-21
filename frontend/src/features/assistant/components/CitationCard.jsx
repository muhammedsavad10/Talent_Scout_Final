import React from 'react';

export default function CitationCard({ citation }) {
  if (!citation) return null;
  return (
    <div className="bg-slate-50 dark:bg-surface-950 border border-slate-200 dark:border-slate-850 rounded-lg p-2 text-[10px] text-slate-500 dark:text-slate-400 space-y-1">
      <div className="flex items-center justify-between font-bold text-slate-600 dark:text-slate-350 border-b border-slate-100 dark:border-slate-800 pb-1">
        <span>Evidence: {citation.section}</span>
        <span>{citation.source}</span>
      </div>
      <p className="italic text-slate-600 dark:text-slate-400 font-medium">"{citation.context}"</p>
    </div>
  );
}
