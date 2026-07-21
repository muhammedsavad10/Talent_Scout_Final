import React, { useState } from 'react';
import { Clock } from 'lucide-react';
import { useEvaluation } from '../context/EvaluationContext';

export default function LearningStep() {
  const { state } = useEvaluation();
  const { result, activeRole } = state;
  const [selectedQuestionsTab, setSelectedQuestionsTab] = useState('easy');

  if (!result) return null;

  const isInterviewer = activeRole === 'Interviewer';

  return (
    <div className="space-y-6 animate-fadeIn">
      {!isInterviewer && (
        <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-indigo-50 dark:bg-indigo-950/40 rounded-lg text-indigo-600 dark:text-indigo-400">
              <Clock className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100 font-sans">4. Onboarding & Learning Strategy</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
            <div className="bg-indigo-950 text-white rounded-xl p-5 shadow flex flex-col justify-between md:col-span-1">
              <div>
                <span className="text-[10px] font-bold text-indigo-200 uppercase tracking-wider">Estimated Ramp-Up</span>
                <h3 className="text-3xl font-black mt-2 text-white">{result.onboarding?.estimated_ramp_up}</h3>
              </div>
              <p className="text-[10px] text-indigo-300/80 leading-snug mt-6">Timeline to achieve standalone contribution eligibility.</p>
            </div>
            
            <div className="md:col-span-2 space-y-3">
              <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">Upskilling Justification Factors</span>
              <ul className="space-y-2">
                {result.onboarding?.rationale_factors?.map((factor, idx) => (
                  <li key={idx} className="flex items-start space-x-2 text-xs text-slate-600 dark:text-slate-400 font-semibold bg-slate-50 dark:bg-surface-950 border border-slate-100 dark:border-slate-850 rounded-lg p-2.5">
                    <span className="text-indigo-600 font-sans">✔</span>
                    <span>{factor}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
        <h3 className="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Learnability Transition Matrix (Adjacent Technology Mappings)</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-xs text-left text-slate-500 border-collapse">
            <thead>
              <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-400 font-bold uppercase text-[10px] bg-slate-50/50 dark:bg-surface-950/50">
                <th className="py-3 px-4">Requirement</th>
                <th className="py-3 px-4">Estimated Difficulty</th>
                <th className="py-3 px-4">Transition Path / Rationale</th>
              </tr>
            </thead>
            <tbody>
              {result.onboarding?.learning_curve?.map((item, idx) => (
                <tr key={idx} className="border-b border-slate-100 dark:border-slate-850 hover:bg-slate-50/30 dark:hover:bg-surface-950/20">
                  <td className="py-3 px-4 font-bold text-slate-700 dark:text-slate-300">{item.skill}</td>
                  <td className="py-3 px-4">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      item.difficulty.toLowerCase().includes('easy') 
                        ? 'bg-emerald-50 text-emerald-700 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-900/40' 
                        : 'bg-amber-50 text-amber-700 dark:text-amber-400 border border-amber-100 dark:border-amber-900/40'
                    }`}>
                      {item.difficulty}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-slate-600 dark:text-slate-400">{item.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
        <div className="flex items-center justify-between pb-4 border-b border-slate-150 dark:border-slate-800">
          <h3 className="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Difficulty-Graded Technical Question Checklist</h3>
          
          <div className="flex space-x-1 bg-slate-100 dark:bg-surface-950 rounded-lg p-1 border border-slate-200 dark:border-slate-800">
            {['easy', 'medium', 'advanced'].map((tab) => (
              <button
                key={tab}
                onClick={() => setSelectedQuestionsTab(tab)}
                className={`px-3 py-1 text-xs font-bold rounded-md capitalize transition ${
                  selectedQuestionsTab === tab 
                    ? 'bg-white dark:bg-surface-900 text-indigo-700 dark:text-indigo-400 shadow-sm' 
                    : 'text-slate-500 hover:text-slate-800 dark:hover:text-slate-300'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-slate-50 dark:bg-surface-950 border border-slate-100 dark:border-slate-850 rounded-xl p-4 text-xs space-y-2">
          <span className="font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block text-[10px]">Verification Target Focus Areas</span>
          <ul className="list-disc pl-4 space-y-1.5 text-slate-600 dark:text-slate-400 font-semibold">
            {result.interview?.verify_during_interview?.map((area, idx) => (
              <li key={idx}>{area}</li>
            ))}
          </ul>
        </div>

        <div className="space-y-3 pt-2">
          {result.interview?.interview_questions?.[selectedQuestionsTab]?.map((q, idx) => (
            <div key={idx} className="flex items-start space-x-3 p-3 bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-850 rounded-xl shadow-sm">
              <input
                type="checkbox"
                id={`q-${selectedQuestionsTab}-${idx}`}
                className="w-4 h-4 text-indigo-600 dark:text-indigo-400 border-slate-300 dark:border-slate-700 rounded focus:ring-indigo-500 mt-0.5"
              />
              <label htmlFor={`q-${selectedQuestionsTab}-${idx}`} className="text-xs font-medium text-slate-700 dark:text-slate-300 cursor-pointer">
                {q}
              </label>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
