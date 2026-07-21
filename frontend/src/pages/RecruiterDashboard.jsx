import React, { useState, useEffect } from 'react';
import { 
  Users, UploadCloud, FileText, CheckCircle, XCircle, AlertCircle, 
  RefreshCw, Mail, MessageSquare, Send, Terminal, 
  ArrowUpRight, Save, Edit2
} from 'lucide-react';
import { mapEvaluationResponse } from '../services/evaluationMapper';
import { evaluationService } from '../services/evaluationService';
import { batchService } from '../services/batchService';
import { chatService } from '../services/chatService';
import { useEvaluation } from '../features/evaluation/context/EvaluationContext';
import UploadWizard from '../features/batch/components/UploadWizard';
import BatchProgress from '../features/batch/components/BatchProgress';
import BatchCompleteCard from '../features/batch/components/BatchCompleteCard';
import EvaluationWizard from '../features/evaluation/components/EvaluationWizard';
import ComparisonFeature from '../features/comparison/ComparisonFeature';
import AssistantFeature from '../features/assistant/AssistantFeature';
import DeveloperConsole from '../features/developer/DeveloperConsole';

const RecruiterDashboard = ({ activeRole = 'Recruiter' }) => {
  const { state, dispatch } = useEvaluation();
  const {
    isLoading, error, activeStep, result, batchResult, activeBatchId,
    batchStatus, selectedCandidates, showSideBySide, filterTier, sortConfig,
    chatMessages, isChatLoading
  } = state;

  // Handle access restrictions for Candidate role on Recruiter Dashboard
  if (activeRole === 'Candidate') {
    return (
      <div className="max-w-4xl mx-auto p-8 text-center space-y-6">
        <div className="p-4 bg-rose-50 border border-rose-100 rounded-2xl text-rose-800 shadow-sm inline-block">
          <XCircle className="w-12 h-12 text-rose-500 mx-auto mb-2" />
          <h2 className="text-xl font-bold">Access Denied</h2>
          <p className="text-sm mt-1">Candidates do not have access to the internal Recruiter Command Center.</p>
        </div>
        <div>
          <a 
            href="/candidate" 
            className="inline-flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition-all"
          >
            <span>Go to Candidate Portal</span>
            <ArrowUpRight className="w-4 h-4" />
          </a>
        </div>
      </div>
    );
  }

  // Handle Interviewer layout locks (Lock to Step 4: Decide Interview)
  const isInterviewer = activeRole === 'Interviewer';
  const displayStep = isInterviewer ? 4 : activeStep;

  // --- Local UI-only states ---
  const [devPassword, setDevPassword] = useState('');
  const [isDevUnlocked, setIsDevUnlocked] = useState(false);
  const [devError, setDevError] = useState('');
  const [isDevDrawerOpen, setIsDevDrawerOpen] = useState(false);

  // Poll batch status if activeBatchId changes
  useEffect(() => {
    if (!activeBatchId) return;

    const startTime = Date.now();
    const pollInterval = setInterval(async () => {
      try {
        if (Date.now() - startTime > 30 * 60 * 1000) { // 30 mins max timeout
          clearInterval(pollInterval);
          dispatch({ type: 'INGEST/SET_ERROR', payload: "Batch Evaluation Timeout." });
          return;
        }
        
        const data = await batchService.getBatchStatus(activeBatchId);
        dispatch({ type: 'BATCH/POLL_TICK', payload: data });

        if (import.meta.env.DEV) {
          console.group(`🔄 [Polling Response] Batch ID: ${activeBatchId}`);
          console.log("Status:", data.status, `(${data.completed}/${data.total} completed)`);
          if (data.results?.ranked_candidates) {
            console.table(data.results.ranked_candidates);
          }
          console.groupEnd();
        }
        
        if (data.status === 'COMPLETED' || data.status === 'COMPLETED_WITH_ERRORS' || data.status === 'FAILED') {
          clearInterval(pollInterval);
          
          if (data.status === 'FAILED') {
            dispatch({ type: 'INGEST/SET_ERROR', payload: data.error || "Batch processing failed." });
            return;
          }
          
          dispatch({ type: 'BATCH/POLL_SUCCESS', payload: data.results });
          if (data.status === 'COMPLETED_WITH_ERRORS') {
            dispatch({ type: 'INGEST/SET_ERROR', payload: "Batch completed but some post-processing errors occurred." });
          } else if (data.failed > 0 && data.completed === 0) {
            dispatch({ type: 'INGEST/SET_ERROR', payload: "All evaluations failed in the batch." });
          } else if (data.results?.ranked_candidates?.length >= 1) {
            // Auto-load top candidate result
            handleViewResult(data.results.ranked_candidates[0]);
          }
        }
      } catch (err) {
        if (err.response && err.response.status === 404) {
          clearInterval(pollInterval);
          dispatch({ type: 'INGEST/SET_ERROR', payload: "Batch not found." });
        }
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [activeBatchId]);

  const handleViewResult = async (candRow) => {
    dispatch({ type: 'INGEST/START_LOADING' });
    dispatch({ type: 'INGEST/CLEAR_ERROR' });
    try {
      if (import.meta.env.DEV) {
        console.group(`📋 [Evaluation Response] GET /api/v1/evaluation/status/${candRow.evaluation_id}`);
        console.log("Candidate Row:", candRow);
      }

      const data = await evaluationService.getEvaluationStatus(candRow.evaluation_id);
      
      if (import.meta.env.DEV) {
        console.log("Raw GET /status Response:", data);
        console.groupEnd();
      }

      const mapped = mapEvaluationResponse(data);

      if (mapped) {
        if (!mapped.filename && candRow.filename) {
          mapped.filename = candRow.filename;
        }

        if (import.meta.env.DEV) {
          console.group("💡 [Normalized Evaluation Model - 1-to-1 Mapping]");
          console.log("Overall Score:", mapped.overallScore);
          console.log("Recommendation Tier:", mapped.recommendation.tier);
          console.log("Matched Skills:", mapped.evidenceStates.matched);
          console.log("Missing Skills:", mapped.evidenceStates.missing);
          console.log("Dimension Scores:", mapped.dimensionScores);
          console.log("Policy Flags:", mapped.policyFlags);
          console.groupEnd();
        }

        dispatch({ type: 'EVALUATION/LOAD_SUCCESS', payload: { mapped, evaluationId: candRow.evaluation_id } });
        localStorage.setItem('lastEvaluation', JSON.stringify(mapped));
      } else {
        dispatch({ type: 'INGEST/SET_ERROR', payload: `Cannot view result: evaluation status is ${data?.status} or result is missing` });
      }
    } catch (err) {
      dispatch({ type: 'INGEST/SET_ERROR', payload: "Failed to fetch full evaluation payload." });
      console.error("❌ Evaluation Fetch Error:", err);
    }
  };

  const handleUnlockDevMode = async (e) => {
    e.preventDefault();
    setDevError('');
    try {
      const data = await evaluationService.verifyDevMode(devPassword);
      if (data.success) {
        setIsDevUnlocked(true);
        setDevPassword('');
      }
    } catch (err) {
      setDevError(err.message || "Verification failed. Try again.");
    }
  };

  return (
    <div className="relative space-y-6">
      
      {/* Page Title Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-100">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Recruiter Command Center</h1>
          <p className="text-xs text-slate-500 font-semibold">Ingest candidates and view semantic match decision insights</p>
        </div>
      </div>
      
      {/* Main Workspace Layout (Workflow Left, Assistant Chat Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        
        {/* Left Workflow Area */}
        <div className="lg:col-span-8 space-y-6">
          
          {/* SKELETON LOADER (Vercel-style skeleton) */}
          {isLoading && (
            <div className="bg-white border border-slate-200 rounded-2xl p-8 space-y-6 shadow-sm min-h-[500px] flex flex-col justify-center animate-pulse">
              <div className="w-12 h-12 bg-slate-200 rounded-xl mx-auto mb-4" />
              <div className="h-6 bg-slate-200 rounded max-w-sm mx-auto w-4/5" />
              <div className="h-4 bg-slate-100 rounded max-w-xs mx-auto w-3/5" />
              <div className="text-center space-y-1 py-2">
                <p className="font-bold text-slate-600 text-sm">Processing LangGraph Swarm...</p>
                <p className="text-xs text-slate-400 font-semibold">LangGraph Swarm Running</p>
              </div>
              <div className="space-y-3 pt-6 max-w-md mx-auto w-full">
                <div className="h-3 bg-slate-100 rounded w-full" />
                <div className="h-3 bg-slate-100 rounded w-5/6" />
                <div className="h-3 bg-slate-100 rounded w-4/5" />
              </div>
              <div className="w-full max-w-xs mx-auto bg-slate-100 rounded-full h-1 overflow-hidden mt-6">
                <div className="bg-indigo-600 h-1 rounded-full w-2/3 animate-infinite-loading animate-slide" />
              </div>
            </div>
          )}

          {/* WORKFLOW SCREEN SWITCHER */}
          {!isLoading && (
            <>
              {/* STEP 1: INGEST RESUME */}
              {displayStep === 1 && (
                <div className="space-y-6">
                  <UploadWizard />
                  <BatchProgress />
                  <BatchCompleteCard onViewComparison={() => dispatch({ type: 'INGEST/SET_STEP', payload: 1.5 })} />
                </div>
              )}

              {/* STEP 1.5: CANDIDATE COMPARISON */}
              {displayStep === 1.5 && batchResult && (
                <ComparisonFeature onViewResult={handleViewResult} />
              )}

              {/* STEPS 2-6: EVALUATION SUITE */}
              {displayStep >= 2 && result && (
                <EvaluationWizard />
              )}
            </>
          )}

        </div>

        {/* Right Sidebar: Stateful Conversational Assistant OR empty placeholder */}
        <div className="lg:col-span-4">
          {result && displayStep > 1 ? (
            <AssistantFeature />
          ) : (
            <div className="bg-slate-50 dark:bg-surface-950 border border-slate-200 dark:border-slate-800 border-dashed rounded-2xl p-8 text-center flex flex-col justify-center items-center h-[400px] text-slate-400 space-y-3">
              <FileText className="w-12 h-12 text-slate-350 dark:text-slate-500" />
              <span className="text-sm font-bold text-slate-500 dark:text-slate-450">No Assessment Loaded</span>
              <p className="text-xs text-slate-400 dark:text-slate-500 max-w-[200px] mx-auto leading-relaxed">Provide a Job Description and upload a candidate resume to trigger the evaluation pipeline.</p>
            </div>
          )}
        </div>

      </div>

      <DeveloperConsole activeRole={activeRole} />

    </div>
  );
};

export default RecruiterDashboard;
