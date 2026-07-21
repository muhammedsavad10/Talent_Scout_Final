import React, { useState } from 'react';
import { 
  Users, CheckCircle, XCircle, AlertCircle, RefreshCw, ChevronRight, ChevronLeft, Mail, Clock, Save, Edit2
} from 'lucide-react';
import { useEvaluation } from '../context/EvaluationContext';
import DimensionScorePanel from './DimensionScorePanel';
import SkillAnalysisCard from './SkillAnalysisCard';
import { candidateService } from '../../../services/candidateService';

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

export default function EvaluationWizard() {
  const { state, dispatch } = useEvaluation();
  const { 
    result, activeStep, activeRole, batchResult, filterTier,
    emailTemplateType, emailDraft, isGeneratingEmail,
    notesEditable, editedNotes, overrideDecision, isSubmittingScreening, screeningSuccess
  } = state;

  // Local UI-only states
  const [selectedQuestionsTab, setSelectedQuestionsTab] = useState('easy');
  const [localDevPassword, setLocalDevPassword] = useState('');

  if (!result) return null;

  const displayStep = activeStep;
  const isInterviewer = activeRole === 'Interviewer';

  const isStepLocked = (stepNum) => {
    if (activeRole === 'Interviewer') return stepNum !== 4;
    if (activeRole === 'Hiring Manager') return stepNum > 4;
    return false;
  };

  const isStepVisible = (stepNum) => {
    if (activeRole === 'Interviewer') return stepNum === 4;
    return true;
  };

  const stepsList = [
    { num: 2, label: 'Profile Suitability' },
    { num: 3, label: 'Factual Evidence' },
    { num: 4, label: 'Technical Questions' },
    { num: 5, label: 'Draft Communication' },
    { num: 6, label: 'Screening Decision' }
  ];

  const handleBackToComparison = () => {
    dispatch({ type: 'BACK_TO_COMPARISON' });
  };

  const handleGenerateEmail = async () => {
    dispatch({ type: 'GENERATE_EMAIL_START' });
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
      dispatch({ type: 'GENERATE_EMAIL_SUCCESS', payload: data });
    } catch (err) {
      console.error(err);
      alert("Failed to generate communication draft.");
      dispatch({ type: 'STOP_LOADING' });
    }
  };

  const handleSubmitScreening = async () => {
    dispatch({ type: 'SUBMIT_SCREENING_START' });
    // Simulate database write
    setTimeout(() => {
      dispatch({ type: 'SUBMIT_SCREENING_SUCCESS' });
      setTimeout(() => {
        dispatch({ type: 'RESET_SCREENING_STATE' });
      }, 3000);
    }, 1000);
  };

  return (
    <div className="space-y-6">
      {/* Step Switcher Header */}
      {!isInterviewer && (
        <div className="sticky top-16 bg-white/95 dark:bg-surface-900/95 backdrop-blur border-b border-slate-200 dark:border-slate-800 z-40 py-3.5 mb-6 -mx-4 px-4 sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8">
          <div className="max-w-7xl mx-auto flex items-center justify-between overflow-x-auto scrollbar-none space-x-4">
            <div className="flex items-center space-x-1 sm:space-x-2">
              {stepsList.map((step) => {
                const isVisible = isStepVisible(step.num);
                if (!isVisible) return null;
                const locked = isStepLocked(step.num);
                const active = displayStep === step.num;
                const completed = displayStep > step.num;

                return (
                  <button
                    key={step.num}
                    disabled={locked}
                    onClick={() => dispatch({ type: 'SET_STEP', payload: step.num })}
                    className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
                      active 
                        ? 'bg-indigo-50 dark:bg-indigo-950/40 text-indigo-700 dark:text-indigo-300 ring-2 ring-indigo-600/20' 
                        : completed
                          ? 'text-indigo-600 dark:text-indigo-400 hover:bg-slate-50 dark:hover:bg-surface-850'
                          : locked
                            ? 'text-slate-300 dark:text-slate-700 cursor-not-allowed'
                            : 'text-slate-500 hover:text-indigo-600 hover:bg-slate-50 dark:hover:bg-surface-850'
                    }`}
                  >
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center border font-sans ${
                      completed 
                        ? 'bg-indigo-600 border-indigo-600 text-white' 
                        : active 
                          ? 'border-indigo-600 text-indigo-600 bg-white dark:bg-surface-900' 
                          : 'border-slate-300 text-slate-400'
                    }`}>
                      {completed ? <CheckCircle className="w-3 h-3 text-white" /> : step.num}
                    </span>
                    <span>{step.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Next / Back Step Controls */}
            <div className="flex space-x-2">
              <button
                disabled={displayStep === 2}
                onClick={() => {
                  let prevStep = displayStep - 1;
                  while (prevStep >= 2 && !isStepVisible(prevStep)) {
                    prevStep--;
                  }
                  dispatch({ type: 'SET_STEP', payload: prevStep });
                }}
                className="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-surface-850 rounded-lg disabled:opacity-30 disabled:pointer-events-none transition"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>

              <button
                disabled={displayStep === 6}
                onClick={() => {
                  let nextStep = displayStep + 1;
                  while (nextStep <= 6 && !isStepVisible(nextStep)) {
                    nextStep++;
                  }
                  dispatch({ type: 'SET_STEP', payload: nextStep });
                }}
                className="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-surface-850 rounded-lg disabled:opacity-30 disabled:pointer-events-none transition"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* STEP 2: UNDERSTAND CANDIDATE */}
      {displayStep === 2 && (
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
                <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">2. Profile Suitability Overview</h2>
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
      )}

      {/* STEP 3: FACTUAL EVIDENCE AUDIT */}
      {displayStep === 3 && (
        <div className="space-y-6 animate-fadeIn">
          <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
            <div className="flex items-center space-x-2">
              <div className="p-2 bg-indigo-50 dark:bg-indigo-950/40 rounded-lg text-indigo-600 dark:text-indigo-400">
                <Users className="w-5 h-5" />
              </div>
              <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">3. Factual Evidence Audit Logs</h2>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-slate-50 dark:bg-surface-950 border border-slate-200 dark:border-slate-850 rounded-xl p-5 space-y-3">
                <h3 className="text-xs font-bold text-emerald-700 dark:text-emerald-400 uppercase tracking-wider flex items-center">
                  <CheckCircle className="w-4 h-4 mr-1.5" /> Identified / Matched Skills ({result.evidenceStates?.matched?.length || 0})
                </h3>
                <ul className="space-y-1.5">
                  {(result.evidenceStates?.matched || []).map((skill, idx) => (
                    <li key={idx} className="text-xs font-bold text-slate-700 dark:text-slate-200 bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 flex items-center justify-between">
                      <span>{skill}</span>
                      <span className="text-[10px] font-bold text-emerald-600 uppercase">Verified</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div className="bg-slate-50 dark:bg-surface-950 border border-slate-200 dark:border-slate-850 rounded-xl p-5 space-y-3">
                <h3 className="text-xs font-bold text-rose-700 dark:text-rose-400 uppercase tracking-wider flex items-center">
                  <XCircle className="w-4 h-4 mr-1.5" /> Missing Skills ({result.evidenceStates?.missing?.length || 0})
                </h3>
                <ul className="space-y-1.5">
                  {(result.evidenceStates?.missing || []).map((skill, idx) => (
                    <li key={idx} className="text-xs font-bold text-slate-700 dark:text-slate-200 bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-lg px-3 py-2 flex items-center justify-between">
                      <span>{skill}</span>
                      <span className="text-[10px] font-bold text-rose-600 uppercase">Not Found</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
            <h3 className="text-sm font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Extracted Business Impact & Quantifiable Outcomes</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {result.businessImpact.map((item, idx) => (
                <div key={idx} className="bg-indigo-50/30 dark:bg-indigo-950/10 border border-indigo-100 dark:border-indigo-900/30 rounded-xl p-4 flex items-start space-x-3 shadow-sm">
                  <span className="w-2.5 h-2.5 bg-indigo-500 rounded-full flex-shrink-0 mt-1.5" />
                  <div>
                    <span className="text-[10px] font-black text-indigo-700 dark:text-indigo-300 uppercase tracking-wide bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded border border-indigo-150 dark:border-indigo-900/50">{item.category}</span>
                    <p className="text-sm text-slate-700 dark:text-slate-300 mt-2 font-medium">{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* STEP 4: DECIDE INTERVIEW QUESTIONS */}
      {displayStep === 4 && (
        <div className="space-y-6 animate-fadeIn">
          {!isInterviewer && (
            <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
              <div className="flex items-center space-x-2">
                <div className="p-2 bg-indigo-50 dark:bg-indigo-950/40 rounded-lg text-indigo-600 dark:text-indigo-400">
                  <Clock className="w-5 h-5" />
                </div>
                <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">4. Onboarding & Learning Strategy</h2>
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
                        <span className="text-indigo-600">✔</span>
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
      )}

      {/* STEP 5: GENERATE COMMUNICATIONS */}
      {displayStep === 5 && (
        <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6 animate-fadeIn">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-indigo-50 dark:bg-indigo-950/40 rounded-lg text-indigo-600 dark:text-indigo-400">
              <Mail className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">5. Candidate Communications Generator</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center pt-2">
            <div className="space-y-2 col-span-2">
              <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Select Template</label>
              <select
                value={emailTemplateType}
                onChange={(e) => dispatch({ type: 'SET_EMAIL_TEMPLATE', payload: e.target.value })}
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
                  onChange={(e) => dispatch({ type: 'GENERATE_EMAIL_SUCCESS', payload: { ...emailDraft, subject: e.target.value } })}
                  className="w-full p-2 border border-slate-200 dark:border-slate-800 rounded-lg text-xs font-semibold text-slate-700 dark:text-slate-300 bg-white dark:bg-surface-900"
                />
              </div>
              
              <div className="space-y-1">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block font-sans">Draft Body</span>
                <textarea
                  rows={12}
                  value={emailDraft.body}
                  onChange={(e) => dispatch({ type: 'GENERATE_EMAIL_SUCCESS', payload: { ...emailDraft, body: e.target.value } })}
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
      )}

      {/* STEP 6: COMPLETE SCREENING */}
      {displayStep === 6 && (
        <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6 animate-fadeIn">
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-indigo-50 dark:bg-indigo-950/40 rounded-lg text-indigo-600 dark:text-indigo-400">
              <CheckCircle className="w-5 h-5" />
            </div>
            <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">6. Finalize Screening Evaluation & Decisions</h2>
          </div>

          <div className="space-y-2">
            <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider font-sans">Override Decision Status</label>
            <div className="grid grid-cols-3 gap-4">
              {['Shortlist', 'Hold', 'Reject'].map((opt) => {
                const active = overrideDecision.toLowerCase().includes(opt.toLowerCase());
                
                return (
                  <button
                    key={opt}
                    type="button"
                    onClick={() => dispatch({ type: 'UPDATE_DECISION', payload: opt })}
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

          <div className="space-y-2 border-t border-slate-100 dark:border-slate-800 pt-5">
            <div className="flex items-center justify-between">
              <label className="block text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider font-sans">Recruiter Notes</label>
              <button
                type="button"
                onClick={() => dispatch({ type: 'SET_NOTES_EDITABLE', payload: !notesEditable })}
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
              onChange={(e) => dispatch({ type: 'UPDATE_NOTES', payload: e.target.value })}
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
      )}
    </div>
  );
}
