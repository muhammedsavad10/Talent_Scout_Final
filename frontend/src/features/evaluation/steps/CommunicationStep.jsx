import React from 'react';
import { Mail, RefreshCw } from 'lucide-react';
import { useEvaluation } from '../context/EvaluationContext';
import { candidateService } from '../../../services/candidateService';

export default function CommunicationStep() {
  const { state, dispatch } = useEvaluation();
  const { 
    result, emailTemplateType, emailDraft, isGeneratingEmail, editedNotes 
  } = state;

  if (!result) return null;

  const handleGenerateEmail = async () => {
    dispatch({ type: 'DECISION/GENERATE_EMAIL_START' });
    try {
      const payload = {
        filename: result.filename,
        template_type: emailTemplateType,
        hiring_recommendation: result.recommendation?.tier || 'Review Before Interview',
        candidate_summary: result.recommendation?.strengths || [],
        strengths: result.recommendation?.strengths || [],
        missing_skills: result.evidenceStates?.missing || [],
        custom_recruiter_notes: editedNotes
      };
      
      const data = await candidateService.generateCommunicationEmail(payload);
      dispatch({ type: 'DECISION/GENERATE_EMAIL_SUCCESS', payload: data });
    } catch (err) {
      console.error(err);
      alert("Failed to generate communication draft.");
      dispatch({ type: 'INGEST/STOP_LOADING' });
    }
  };

  return (
    <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6 animate-fadeIn">
      <div className="flex items-center space-x-2">
        <div className="p-2 bg-indigo-50 dark:bg-indigo-950/40 rounded-lg text-indigo-600 dark:text-indigo-400">
          <Mail className="w-5 h-5" />
        </div>
        <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100 font-sans">5. Candidate Communications Generator</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center pt-2">
        <div className="space-y-2 col-span-2">
          <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Select Template</label>
          <select
            value={emailTemplateType}
            onChange={(e) => dispatch({ type: 'DECISION/SET_EMAIL_TEMPLATE', payload: e.target.value })}
            className="w-full p-3 border border-slate-200 dark:border-slate-850 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none transition text-slate-700 dark:text-slate-200 bg-slate-50/50 dark:bg-surface-950 text-sm font-semibold"
          >
            <option value="interview_invite">Interview Invitation Email</option>
            <option value="shortlisted">Shortlist Notification Email</option>
            <option value="rejection">Polite & Encouraging Rejection Email</option>
            <option value="candidate_feedback">Comprehensive Upskilling Growth Plan</option>
          </select>
        </div>

        <div className="pt-6 col-span-1">
          <button
            onClick={handleGenerateEmail}
            disabled={isGeneratingEmail}
            className="w-full flex items-center justify-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3.5 px-4 rounded-xl shadow-lg transition-all text-xs"
          >
            {isGeneratingEmail ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin" />
                <span>Drafting...</span>
              </>
            ) : (
              <span>Generate Communication</span>
            )}
          </button>
        </div>
      </div>

      {emailDraft && (
        <div className="border border-slate-200 dark:border-slate-850 rounded-2xl p-5 space-y-4 bg-slate-50/40 dark:bg-surface-950/40 shadow-inner mt-6 animate-fadeIn">
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block font-sans">Subject</span>
            <input
              type="text"
              value={emailDraft.subject}
              onChange={(e) => dispatch({ type: 'DECISION/GENERATE_EMAIL_SUCCESS', payload: { ...emailDraft, subject: e.target.value } })}
              className="w-full p-2 border border-slate-200 dark:border-slate-800 rounded-lg text-xs font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-surface-900"
            />
          </div>
          
          <div className="space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block font-sans">Draft Body</span>
            <textarea
              rows={12}
              value={emailDraft.body}
              onChange={(e) => dispatch({ type: 'DECISION/GENERATE_EMAIL_SUCCESS', payload: { ...emailDraft, body: e.target.value } })}
              className="w-full p-3 border border-slate-200 dark:border-slate-800 rounded-lg text-xs font-medium text-slate-700 dark:text-slate-300 bg-white dark:bg-surface-900"
            />
          </div>
          
          <div className="flex justify-end pt-2">
            <button
              onClick={() => {
                navigator.clipboard.writeText(`Subject: ${emailDraft.subject}\n\n${emailDraft.body}`);
                alert("Copied to clipboard!");
              }}
              className="px-4 py-2 border border-slate-200 dark:border-slate-850 hover:bg-slate-50 dark:hover:bg-surface-850 rounded-lg text-xs font-bold text-slate-600 dark:text-slate-400 transition"
            >
              Copy Complete Message
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
