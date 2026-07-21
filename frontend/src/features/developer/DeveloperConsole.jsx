import React, { useState } from 'react';
import { Terminal, RefreshCw } from 'lucide-react';
import { useEvaluation } from '../evaluation/context/EvaluationContext';
import { evaluationService } from '../../services/evaluationService';

export default function DeveloperConsole({ activeRole }) {
  const { state } = useEvaluation();
  const { result, isLoading } = state;

  const [devPassword, setDevPassword] = useState('');
  const [isDevUnlocked, setIsDevUnlocked] = useState(false);
  const [devError, setDevError] = useState('');
  const [isDevDrawerOpen, setIsDevDrawerOpen] = useState(false);

  if (activeRole === 'Candidate' || activeRole === 'Interviewer') return null;

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
    <div className="mt-8 border-t border-slate-200 dark:border-slate-800 pt-6">
      <div className="bg-slate-900 border border-slate-850 rounded-2xl p-6 text-white shadow-2xl relative overflow-hidden">
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
                  <div className="bg-slate-955 p-3 rounded-xl border border-slate-800">
                    <span className="text-[9px] text-slate-550 font-bold block uppercase tracking-wider">Processing Latency</span>
                    <span className="text-indigo-400 font-extrabold">{result.debug?.processing_ms?.toFixed(1) || 0} ms</span>
                  </div>
                  <div className="bg-slate-955 p-3 rounded-xl border border-slate-800">
                    <span className="text-[9px] text-slate-555 font-bold block uppercase tracking-wider">Weighted Score</span>
                    <span className="text-indigo-400 font-extrabold">{result.debug?.raw_weighted_score?.toFixed(4) || 0.0}</span>
                  </div>
                  <div className="bg-slate-955 p-3 rounded-xl border border-slate-800">
                    <span className="text-[9px] text-slate-555 font-bold block uppercase tracking-wider">Containment Score</span>
                    <span className="text-indigo-400 font-extrabold">{result.debug?.raw_containment_score?.toFixed(4) || 0.0}</span>
                  </div>
                  <div className="bg-slate-955 p-3 rounded-xl border border-slate-800">
                    <span className="text-[9px] text-slate-555 font-bold block uppercase tracking-wider">Semantic Match</span>
                    <span className="text-indigo-400 font-extrabold">{result.debug?.raw_semantic_similarity?.toFixed(4) || 0.0}</span>
                  </div>
                </div>

                {/* Node Transitions */}
                <div className="space-y-2">
                  <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">LangGraph Execution Nodes</span>
                  <div className="flex items-center flex-wrap gap-2 text-xs">
                    {result.debug?.pipeline_node_transitions?.map((node, nIdx) => (
                      <div key={nIdx} className="flex items-center space-x-1 bg-slate-950 rounded-lg p-2 border border-slate-800 text-[10px] text-slate-350 font-bold">
                        <span>{node}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Agent execution trace logs */}
                <div className="space-y-2 bg-slate-950/90 rounded-xl p-4 border border-slate-800 h-48 overflow-y-auto text-[10px] text-slate-350 leading-relaxed scrollbar-thin">
                  <span className="text-[9px] text-slate-555 font-bold block uppercase tracking-wider border-b border-slate-800 pb-1 mb-2">Agent Swarm Execution Logs</span>
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
  );
}
