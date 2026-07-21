import React from 'react';
import { CheckCircle, AlertCircle, RefreshCw, Save, Edit2 } from 'lucide-react';
import { useEvaluation } from '../context/EvaluationContext';

export default function DecisionStep() {
  const { state, dispatch } = useEvaluation();
  const { 
    result, overrideDecision, notesEditable, editedNotes, isSubmittingScreening, screeningSuccess 
  } = state;

  if (!result) return null;

  const handleSubmitScreening = async () => {
    dispatch({ type: 'DECISION/SUBMIT_START' });
    setTimeout(() => {
      dispatch({ type: 'DECISION/SUBMIT_SUCCESS' });
      setTimeout(() => {
        dispatch({ type: 'DECISION/RESET_STATE' });
      }, 3000);
    }, 1000);
  };

  return (
    <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6 animate-fadeIn">
      <div className="flex items-center space-x-2">
        <div className="p-2 bg-indigo-50 dark:bg-indigo-950/40 rounded-lg text-indigo-600 dark:text-indigo-400">
          <CheckCircle className="w-5 h-5" />
        </div>
        <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">6. Finalize Screening Evaluation & Decisions</h2>
      </div>

      {/* Override Status Button matrix */}
      <div className="space-y-2">
        <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider font-sans">Override Decision Status</label>
        <div className="grid grid-cols-3 gap-4">
          {['Shortlist', 'Hold', 'Reject'].map((opt) => {
            const active = overrideDecision.toLowerCase().includes(opt.toLowerCase());
            
            return (
              <button
                key={opt}
                type="button"
                onClick={() => dispatch({ type: 'DECISION/UPDATE_DECISION', payload: opt })}
                className={`p-4 border rounded-xl text-sm font-bold shadow-sm transition flex flex-col items-center space-y-2 ${
                  active
                    ? opt === 'Shortlist' 
                      ? 'bg-emerald-50 border-emerald-500 text-emerald-800 font-extrabold ring-2 ring-emerald-500/20'
                      : opt === 'Hold'
                        ? 'bg-amber-50 border-amber-500 text-amber-800 font-extrabold ring-2 ring-amber-500/20'
                        : 'bg-rose-50 border-rose-500 text-rose-800 font-extrabold ring-2 ring-rose-500/20'
                    : 'bg-white dark:bg-surface-900 border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-surface-850 text-slate-600 dark:text-slate-400'
                }`}
              >
                <span>{opt}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Checklist Audits */}
      <div className="bg-slate-50 dark:bg-surface-950 border border-slate-100 dark:border-slate-850 rounded-xl p-4 text-xs space-y-3">
        <span className="font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block text-[10px] font-sans">Checklist Audits</span>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {result.recruiter?.resume_feedback?.map((fb, idx) => (
            <div key={idx} className="flex items-center space-x-2">
              {fb.status === 'pass' ? (
                <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
              ) : (
                <AlertCircle className="w-4 h-4 text-amber-500 flex-shrink-0" />
              )}
              <span className="text-slate-600 dark:text-slate-400 font-semibold">{fb.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Recruiter Notes Editor */}
      <div className="space-y-2 border-t border-slate-100 dark:border-slate-800 pt-5">
        <div className="flex items-center justify-between">
          <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider font-sans">Recruiter Notes</label>
          <button
            type="button"
            onClick={() => dispatch({ type: 'DECISION/SET_NOTES_EDITABLE', payload: !notesEditable })}
            className="text-xs font-bold text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 flex items-center space-x-1"
          >
            {notesEditable ? (
              <>
                <Save className="w-3 h-3" />
                <span>Lock Notes</span>
              </>
            ) : (
              <>
                <Edit2 className="w-3 h-3" />
                <span>Edit Notes</span>
              </>
            )}
          </button>
        </div>

        <textarea
          rows={5}
          readOnly={!notesEditable}
          value={editedNotes}
          onChange={(e) => dispatch({ type: 'DECISION/UPDATE_NOTES', payload: e.target.value })}
          className={`w-full p-3 border rounded-xl focus:outline-none transition text-xs font-medium text-slate-700 dark:text-slate-200 ${
            notesEditable 
              ? 'border-indigo-400 bg-white dark:bg-surface-900 ring-2 ring-indigo-500/10 focus:ring-2 focus:ring-indigo-500' 
              : 'border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-surface-950/50 cursor-not-allowed'
          }`}
          placeholder="Add recruiter notes and manual feedback details here..."
        />
      </div>

      <button
        onClick={handleSubmitScreening}
        disabled={isSubmittingScreening}
        className="w-full flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3.5 px-4 rounded-xl shadow-lg transition-all mt-4"
      >
        {isSubmittingScreening ? (
          <>
            <RefreshCw className="w-5 h-5 animate-spin" />
            <span>Logging Decision...</span>
          </>
        ) : (
          <span>Submit Final Screening Decision</span>
        )}
      </button>

      {screeningSuccess && (
        <div className="flex items-center justify-center space-x-2 p-3 bg-emerald-50 border border-emerald-100 rounded-xl text-emerald-800 text-xs font-bold animate-pulse text-center">
          <CheckCircle className="w-4 h-4 text-emerald-500" />
          <span>Screening logged successfully! Returning to Ingest screen...</span>
        </div>
      )}
    </div>
  );
}
