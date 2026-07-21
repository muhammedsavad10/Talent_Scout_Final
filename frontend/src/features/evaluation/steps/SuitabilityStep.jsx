import React from 'react';
import { Users, ChevronLeft, CheckCircle, AlertCircle, XCircle } from 'lucide-react';
import { useEvaluation } from '../context/EvaluationContext';
import DimensionScorePanel from '../components/DimensionScorePanel';
import SkillAnalysisCard from '../components/SkillAnalysisCard';

const getRecommendationStyle = (recTier) => {
  const tier = recTier?.toLowerCase() || '';
  if (tier.includes('shortlist') || tier.includes('interview')) {
    return { bg: 'bg-emerald-50 dark:bg-emerald-950/20 border-emerald-200 dark:border-emerald-900/40', text: 'text-emerald-700 dark:text-emerald-400' };
  }
  if (tier.includes('hold') || tier.includes('review')) {
    return { bg: 'bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-900/40', text: 'text-amber-700 dark:text-amber-400' };
  }
  return { bg: 'bg-rose-50 dark:bg-rose-950/20 border-rose-200 dark:border-rose-900/40', text: 'text-rose-700 dark:text-rose-400' };
};

export default function SuitabilityStep() {
  const { state, dispatch } = useEvaluation();
  const { result, batchResult } = state;

  if (!result) return null;

  const handleBackToComparison = () => {
    dispatch({ type: 'EVALUATION/BACK_TO_COMPARISON' });
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {batchResult && (
        <div className="flex items-center pb-2">
          <button 
            onClick={handleBackToComparison}
            className="flex items-center space-x-2 px-4 py-2 bg-slate-100 dark:bg-surface-850 hover:bg-slate-200 dark:hover:bg-surface-800 text-slate-700 dark:text-slate-300 text-sm font-bold rounded-xl transition"
          >
            <ChevronLeft className="w-4 h-4" />
            <span>Back to Batch Comparison</span>
          </button>
        </div>
      )}

      <DimensionScorePanel />
      <SkillAnalysisCard />

      <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-100 dark:border-slate-800 space-y-3 sm:space-y-0">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-indigo-50 dark:bg-indigo-950/40 rounded-lg text-indigo-600 dark:text-indigo-400">
              <Users className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100 font-sans">2. Profile Suitability Overview</h2>
          </div>
          
          <span className={`px-4 py-1.5 rounded-full text-xs font-black tracking-wide border uppercase shadow-sm ${
            getRecommendationStyle(result.recommendation?.tier).bg
          } ${
            getRecommendationStyle(result.recommendation?.tier).text
          }`}>
            {result.recommendation?.tier}
          </span>
        </div>

        <div className="space-y-6 pt-2">
          {result.recommendation?.reasoning && (
            <div className="bg-slate-50 dark:bg-surface-950 border border-slate-100 dark:border-slate-850 rounded-xl p-5 space-y-3">
              <h3 className="text-sm font-bold text-slate-800 dark:text-slate-200">Decision Reasoning</h3>
              <p className="text-sm text-slate-600 dark:text-slate-400 leading-relaxed">{result.recommendation.reasoning}</p>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Strengths */}
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-emerald-600 dark:text-emerald-400 uppercase tracking-wider flex items-center">
                <CheckCircle className="w-4 h-4 mr-1.5" /> Strengths
              </h3>
              <ul className="space-y-2">
                {(result.recommendation?.strengths || []).map((bullet, idx) => (
                  <li key={idx} className="flex items-start space-x-2.5 text-sm text-slate-600 dark:text-slate-400">
                    <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full flex-shrink-0 mt-2" />
                    <span>{bullet}</span>
                  </li>
                ))}
                {(result.recommendation?.strengths || []).length === 0 && (
                  <p className="text-xs text-slate-400 italic">None reported.</p>
                )}
              </ul>
            </div>

            {/* Weaknesses */}
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider flex items-center">
                <AlertCircle className="w-4 h-4 mr-1.5" /> Weaknesses / Policy Flags
              </h3>
              <ul className="space-y-2">
                {result.policyFlags.map((bullet, idx) => (
                  <li key={idx} className="flex items-start space-x-2.5 text-sm text-slate-600 dark:text-slate-400">
                    <span className="w-1.5 h-1.5 bg-amber-500 rounded-full flex-shrink-0 mt-2" />
                    <span>{bullet}</span>
                  </li>
                ))}
                {result.policyFlags.length === 0 && (
                  <p className="text-xs text-slate-400 italic">No policy flags triggered.</p>
                )}
              </ul>
            </div>

            {/* Critical Missing */}
            <div className="space-y-3">
              <h3 className="text-sm font-bold text-rose-600 dark:text-rose-400 uppercase tracking-wider flex items-center">
                <XCircle className="w-4 h-4 mr-1.5" /> Critical Missing
              </h3>
              <ul className="space-y-2">
                {(result.recommendation?.criticalMissingSkills || result.evidenceStates?.missing || []).map((skill, idx) => (
                  <li key={idx} className="flex items-start space-x-2.5 text-sm text-slate-600 dark:text-slate-400">
                    <span className="w-1.5 h-1.5 bg-rose-500 rounded-full flex-shrink-0 mt-2" />
                    <span>{skill}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Career Timeline */}
      <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
        <h3 className="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{result.evidence?.timeline_title || "Chronological Career Milestones"}</h3>
        <div className="relative border-l-2 border-slate-200 dark:border-slate-800 pl-6 space-y-8 ml-2">
          {result.careerTimeline.map((item, idx) => (
            <div key={idx} className="relative">
              <span className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-white dark:bg-surface-900 border-2 border-indigo-600 flex items-center justify-center">
                <span className="w-1.5 h-1.5 bg-indigo-600 rounded-full" />
              </span>
              {item.year && (
                <span className="text-xs font-bold text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-950/30 border border-indigo-100 dark:border-indigo-900/30 rounded-md px-2 py-0.5">{item.year}</span>
              )}
              <h4 className={`text-sm font-bold text-slate-800 dark:text-slate-100 ${item.year ? 'mt-2' : ''}`}>{item.role}</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 font-semibold">{item.company}</p>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">{item.details}</p>
            </div>
          ))}
        </div>
      </div>

      <p className="text-center text-[10px] text-slate-400 italic font-medium px-4">
        {result.recommendation?.disclaimer}
      </p>
    </div>
  );
}
