import React from 'react';
import { CheckCircle, ChevronRight, ChevronLeft } from 'lucide-react';
import { useEvaluation } from '../context/EvaluationContext';

// Import workflow steps
import SuitabilityStep from '../steps/SuitabilityStep';
import EvidenceStep from '../steps/EvidenceStep';
import LearningStep from '../steps/LearningStep';
import CommunicationStep from '../steps/CommunicationStep';
import DecisionStep from '../steps/DecisionStep';

const STEP_REGISTRY = {
  2: {
    label: 'Profile Suitability',
    component: SuitabilityStep
  },
  3: {
    label: 'Factual Evidence',
    component: EvidenceStep
  },
  4: {
    label: 'Technical Questions',
    component: LearningStep
  },
  5: {
    label: 'Draft Communication',
    component: CommunicationStep
  },
  6: {
    label: 'Screening Decision',
    component: DecisionStep
  }
};

export default function EvaluationWizard() {
  const { state, dispatch } = useEvaluation();
  const { result, activeStep, activeRole } = state;

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

  const stepsList = Object.entries(STEP_REGISTRY).map(([num, config]) => ({
    num: Number(num),
    label: config.label
  }));

  const ActiveStepComponent = STEP_REGISTRY[displayStep]?.component || null;

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
                    onClick={() => dispatch({ type: 'INGEST/SET_STEP', payload: step.num })}
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
                  dispatch({ type: 'INGEST/SET_STEP', payload: prevStep });
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
                  dispatch({ type: 'INGEST/SET_STEP', payload: nextStep });
                }}
                className="p-2 text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-surface-850 rounded-lg disabled:opacity-30 disabled:pointer-events-none transition"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {ActiveStepComponent && <ActiveStepComponent />}
    </div>
  );
}
