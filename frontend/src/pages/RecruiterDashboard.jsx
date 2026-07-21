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
  const [chatInput, setChatInput] = useState('');
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

  const handleAskAssistant = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || !result) return;

    const userQuestion = chatInput.trim();
    setChatInput('');
    
    // Add user message to state
    dispatch({ type: 'CHAT/ADD_MESSAGE', payload: { role: 'user', content: userQuestion } });
    dispatch({ type: 'CHAT/START_LOADING' });

    try {
      // Build history payload for assistant context
      const historyPayload = [...chatMessages].map(msg => ({
        role: msg.role,
        content: msg.content
      }));

      const payload = {
        filename: result.filename,
        history: historyPayload,
        question: userQuestion,
        skills_evidence: result.evidence?.skills_evidence || []
      };

      const data = await chatService.askAssistant(payload);
      dispatch({ type: 'CHAT/ADD_MESSAGE', payload: {
        role: 'assistant',
        content: data.answer,
        citations: data.citations || []
      }});
    } catch (err) {
      console.error(err);
      dispatch({ type: 'CHAT/ADD_MESSAGE', payload: {
        role: 'assistant',
        content: "I'm sorry, I couldn't reach the backend to answer your question.",
        citations: []
      }});
    } finally {
      dispatch({ type: 'CHAT/STOP_LOADING' });
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
            <div className="bg-white border border-slate-200 rounded-2xl shadow-sm flex flex-col h-[600px] overflow-hidden">
              
              {/* Assistant Header */}
              <div className="p-4 border-b border-slate-200 bg-slate-50/50 flex items-center space-x-2">
                <MessageSquare className="w-4 h-4 text-indigo-600 animate-pulse" />
                <span className="text-sm font-bold text-slate-800">Recruiter AI Assistant</span>
              </div>

              {/* Chat Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin">
                {chatMessages.map((msg, idx) => (
                  <div 
                    key={idx} 
                    className={`flex flex-col max-w-[85%] ${
                      msg.role === 'user' ? 'ml-auto items-end' : 'items-start'
                    }`}
                  >
                    <div className={`p-3 rounded-2xl text-xs leading-relaxed ${
                      msg.role === 'user' 
                        ? 'bg-indigo-600 text-white rounded-br-none font-semibold' 
                        : 'bg-slate-100 text-slate-800 rounded-bl-none font-medium'
                    }`}>
                      {msg.content}
                    </div>
                    
                    {/* Citations list for assistant answers */}
                    {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
                      <div className="mt-1 space-y-1 w-full">
                        {msg.citations.map((cite, cIdx) => (
                          <div key={cIdx} className="bg-slate-50 border border-slate-200 rounded-lg p-2 text-[10px] text-slate-500 space-y-1">
                            <div className="flex items-center justify-between font-bold text-slate-600 border-b border-slate-100 pb-1">
                              <span>Evidence: {cite.section}</span>
                              <span>{cite.source}</span>
                            </div>
                            <p className="italic text-slate-600 font-medium">"{cite.context}"</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
                {isChatLoading && (
                  <div className="flex items-center space-x-2 bg-slate-100 text-slate-600 rounded-2xl rounded-bl-none p-3 max-w-[70%] text-xs font-semibold animate-pulse">
                    <RefreshCw className="w-3.5 h-3.5 animate-spin text-indigo-600" />
                    <span>Assistant is thinking...</span>
                  </div>
                )}
              </div>

              {/* Chat input form */}
              <form onSubmit={handleAskAssistant} className="p-3 border-t border-slate-200 bg-white flex space-x-2">
                <input
                  type="text"
                  placeholder="Ask about candidate experience/skills..."
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  disabled={isChatLoading}
                  className="flex-1 px-3 py-2 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:outline-none transition text-xs font-medium bg-slate-50/50"
                />
                <button
                  type="submit"
                  disabled={isChatLoading || !chatInput.trim()}
                  className="p-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl shadow transition disabled:opacity-50 flex items-center justify-center"
                >
                  <Send className="w-3.5 h-3.5" />
                </button>
              </form>
            </div>
          ) : (
            <div className="bg-slate-50 border border-slate-200 border-dashed rounded-2xl p-8 text-center flex flex-col justify-center items-center h-[400px] text-slate-400 space-y-3">
              <FileText className="w-12 h-12 text-slate-350" />
              <span className="text-sm font-bold text-slate-500">No Assessment Loaded</span>
              <p className="text-xs text-slate-400 max-w-[200px] mx-auto leading-relaxed">Provide a Job Description and upload a candidate resume to trigger the evaluation pipeline.</p>
            </div>
          )}
        </div>

      </div>

      {/* ADMIN OR PASSWORD-GATED DEVELOPER MODE BOX */}
      {activeRole !== 'Candidate' && activeRole !== 'Interviewer' && (
        <div className="mt-8 border-t border-slate-200 pt-6">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-white shadow-2xl relative overflow-hidden">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0 pb-4 border-b border-slate-800">
              <div className="flex items-center space-x-3">
                <Terminal className="w-6 h-6 text-indigo-500" />
                <div>
                  <h3 className="text-sm font-extrabold tracking-wide uppercase text-indigo-400">Developer Dashboard Console</h3>
                  <p className="text-[10px] text-slate-400 font-semibold">Audit LangGraph pipeline node states, latency, and LLM reasoning payloads</p>
                </div>
              </div>

              {/* Toggle Developer Console */}
              {isDevUnlocked ? (
                <button
                  onClick={() => setIsDevDrawerOpen(!isDevDrawerOpen)}
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg text-xs transition"
                >
                  {isDevDrawerOpen ? 'Close Developer Console' : 'Open Developer Console'}
                </button>
              ) : (
                <form onSubmit={handleUnlockDevMode} className="flex items-center space-x-2">
                  <input
                    type="password"
                    placeholder="Enter Developer Password"
                    value={devPassword}
                    onChange={(e) => setDevPassword(e.target.value)}
                    className="px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-950 text-xs text-white focus:outline-none focus:ring-1 focus:ring-indigo-500 font-semibold"
                  />
                  <button
                    type="submit"
                    className="px-4 py-1.5 bg-slate-800 hover:bg-slate-700 text-white font-bold rounded-lg text-xs transition"
                  >
                    Unlock
                  </button>
                </form>
              )}
            </div>

            {devError && (
              <p className="text-xs text-rose-500 font-bold mt-2">{devError}</p>
            )}

            {/* Console Content */}
            {isDevUnlocked && isDevDrawerOpen && (
              <div className="space-y-6 pt-6 animate-fadeIn font-mono">
                {isLoading && (
                  <div className="flex items-center space-x-2 text-xs text-indigo-400">
                    <RefreshCw className="w-3 h-3 animate-spin" />
                    <span>Evaluation in progress... loading results</span>
                  </div>
                )}
                {result ? (
                  <>
                    {isLoading && (
                      <div className="flex items-center space-x-2 text-xs text-indigo-400">
                        <RefreshCw className="w-3 h-3 animate-spin" />
                        <span>Refreshing evaluation data...</span>
                      </div>
                    )}
                    {/* Performance metrics & scores */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
                      <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                        <span className="text-[9px] text-slate-500 font-bold block uppercase tracking-wider">Processing Latency</span>
                        <span className="text-indigo-400 font-extrabold">{result.debug?.processing_ms?.toFixed(1) || 0} ms</span>
                      </div>
                      <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                        <span className="text-[9px] text-slate-500 font-bold block uppercase tracking-wider">Weighted Score</span>
                        <span className="text-indigo-400 font-extrabold">{result.debug?.raw_weighted_score?.toFixed(4) || 0.0}</span>
                      </div>
                      <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                        <span className="text-[9px] text-slate-500 font-bold block uppercase tracking-wider">Containment Score</span>
                        <span className="text-indigo-400 font-extrabold">{result.debug?.raw_containment_score?.toFixed(4) || 0.0}</span>
                      </div>
                      <div className="bg-slate-950/80 p-3 rounded-xl border border-slate-800">
                        <span className="text-[9px] text-slate-500 font-bold block uppercase tracking-wider">Semantic Match</span>
                        <span className="text-indigo-400 font-extrabold">{result.debug?.raw_semantic_similarity?.toFixed(4) || 0.0}</span>
                      </div>
                    </div>

                    {/* Node Transitions */}
                    <div className="space-y-2">
                      <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">LangGraph Execution Nodes</span>
                      <div className="flex items-center flex-wrap gap-2 text-xs">
                        {result.debug?.pipeline_node_transitions?.map((node, nIdx) => (
                          <div key={nIdx} className="flex items-center space-x-1 bg-slate-950 rounded-lg p-2 border border-slate-800 text-[10px] text-slate-300 font-bold">
                            <span>{node}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Agent execution trace logs */}
                    <div className="space-y-2 bg-slate-950/90 rounded-xl p-4 border border-slate-800 h-48 overflow-y-auto text-[10px] text-slate-300 leading-relaxed scrollbar-thin">
                      <span className="text-[9px] text-slate-500 font-bold block uppercase tracking-wider border-b border-slate-800 pb-1 mb-2">Agent Swarm Execution Logs</span>
                      {result.debug?.agent_logs?.map((log, lIdx) => (
                        <p key={lIdx} className="flex items-center space-x-2">
                          <span className="text-indigo-500">[INFO]</span>
                          <span>{log}</span>
                        </p>
                      ))}
                    </div>

                    {/* Raw JSON evaluations payload */}
                    <div className="space-y-2">
                      <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Raw Evaluation payload (JSON)</span>
                      <pre className="bg-slate-950/90 rounded-xl p-4 border border-slate-800 text-[10px] overflow-x-auto text-indigo-400/90 h-60 scrollbar-thin">
                        {JSON.stringify(result, null, 2)}
                      </pre>
                    </div>
                  </>
                ) : !isLoading && (
                  <p className="text-xs text-slate-400 italic">No evaluation loaded yet. Ingest a candidate resume to inspect execution outputs.</p>
                )}
              </div>
            )}
          </div>
        </div>
      )}

    </div>
  );
};

export default RecruiterDashboard;
