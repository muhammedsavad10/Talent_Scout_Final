import React, { useState, useEffect } from 'react';
import { 
  Users, UploadCloud, Briefcase, FileText, CheckCircle, XCircle, AlertCircle, 
  RefreshCw, ChevronRight, ChevronLeft, Mail, MessageSquare, Send, Terminal, 
  Lock, Unlock, Clock, ArrowUpRight, BookOpen, Award, Check, Save, Edit2, Info, Activity
} from 'lucide-react';
import { mapEvaluationResponse } from '../services/evaluationMapper';
import { getDimensionLabel } from '../utils/dimensionLabels';
import { evaluationService } from '../services/evaluationService';
import { batchService } from '../services/batchService';
import { candidateService } from '../services/candidateService';
import { chatService } from '../services/chatService';

const RecruiterDashboard = ({ activeRole = 'Recruiter' }) => {
  // --- Authentication / Authorization State (RBAC) ---
  // Handled via activeRole prop passed from App.jsx

  // --- Evaluation State ---
  const [files, setFiles] = useState([]); // Support multiple files
  const [batchJobs, setBatchJobs] = useState([]); // Track batch upload queue
  const [jdText, setJdText] = useState('');
  const [jdSkills, setJdSkills] = useState('');
  const [evaluationId, setEvaluationId] = useState(null); // Active viewed eval ID
  const [activeStep, setActiveStep] = useState(1); // 1: Ingest, 1.5: Batch Compare, 2: Suitability, 3: Evidence, 4: Onboarding/Interview, 5: Comm, 6: Finalize
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  // Drag & Drop / File selection handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFiles = Array.from(e.dataTransfer.files).filter(f => f.name.endsWith('.pdf'));
      if (droppedFiles.length > 0) {
        setFiles(prev => [...prev, ...droppedFiles]);
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files).filter(f => f.name.endsWith('.pdf'));
      setFiles(prev => [...prev, ...selected]);
    }
  };

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  // --- Batch Evaluation State ---
  const [activeBatchId, setActiveBatchId] = useState(null);
  const [batchStatus, setBatchStatus] = useState(null);
  const [batchResult, setBatchResult] = useState(null);
  const [selectedCandidates, setSelectedCandidates] = useState([]);
  const [showSideBySide, setShowSideBySide] = useState(false);
  const [filterTier, setFilterTier] = useState('All');
  const [sortConfig, setSortConfig] = useState({ key: 'rank', direction: 'asc' });

  // --- Candidate Screening Decision State ---
  const [selectedQuestionsTab, setSelectedQuestionsTab] = useState('easy');
  const [emailTemplateType, setEmailTemplateType] = useState('interview_invite');
  const [emailDraft, setEmailDraft] = useState(null);
  const [isGeneratingEmail, setIsGeneratingEmail] = useState(false);
  const [notesEditable, setNotesEditable] = useState(false);
  const [editedNotes, setEditedNotes] = useState('');
  const [overrideDecision, setOverrideDecision] = useState('');
  const [isSubmittingScreening, setIsSubmittingScreening] = useState(false);
  const [screeningSuccess, setScreeningSuccess] = useState(false);

  // Accordion toggle state (Skill index to boolean)
  const [expandedAccordions, setExpandedAccordions] = useState({});

  // --- Stateful Recruiter Assistant State ---
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [isChatLoading, setIsChatLoading] = useState(false);

  // --- Developer Mode State ---
  const [devPassword, setDevPassword] = useState('');
  const [isDevUnlocked, setIsDevUnlocked] = useState(false);
  const [devError, setDevError] = useState('');
  const [isDevDrawerOpen, setIsDevDrawerOpen] = useState(false);

  // Reset local state if result changes
  useEffect(() => {
    if (result) {
      setEditedNotes(result.rawPayload?.recruiter?.recruiter_notes || '');
      setOverrideDecision(result.recommendation?.tier || 'Review Before Interview');
      setEmailDraft(null);
      setChatMessages([
        {
          role: 'assistant',
          content: `Hello! I have loaded the evaluation for **${result.filename || 'Candidate'}**. You can ask me questions about their technical skills, projects, or work history, and I will cite evidence directly from their resume.`,
          citations: []
        }
      ]);
    }
  }, [result]);

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

  // Submit Handler for asynchronous processing
  const handleSubmitEvaluation = async (e) => {
    e.preventDefault();
    if (files.length === 0) {
      setError("Please upload at least one candidate PDF resume.");
      return;
    }
    if (!jdText.trim()) {
      setError("Please provide a Job Description.");
      return;
    }

    setIsLoading(true);
    setError(null);
    setResult(null);
    setBatchResult(null);
    setActiveBatchId(null);
    setBatchStatus(null);
    setScreeningSuccess(false);
    setSelectedCandidates([]);
    setShowSideBySide(false);
    setFilterTier('All');
    setSortConfig({ key: 'rank', direction: 'asc' });

    const formData = new FormData();
    files.forEach(f => formData.append('files', f));
    formData.append('job_description', jdText);
    if (jdSkills.trim()) {
      formData.append('jd_skills', jdSkills);
    }

    try {
      if (import.meta.env.DEV) {
        console.group("🚀 [Upload Request] POST /api/v1/evaluate/batch");
        console.log("Files:", files.map(f => f.name));
        console.log("Job Description:", jdText);
        console.log("JD Skills Overrides:", jdSkills);
        console.groupEnd();
      }

      const data = await batchService.batchEvaluate(formData);

      if (import.meta.env.DEV) {
        console.group("✅ [Upload Response]");
        console.log(data);
        console.groupEnd();
      }

      const bId = data.batch_id;
      if (bId) {
        setActiveBatchId(bId);
        setBatchStatus(data);
        pollBatchJob(bId);
      }
    } catch (err) {
      console.error("❌ Upload Error:", err);
      const detail = err.response?.data?.detail || "Batch upload failed.";
      const errMsg = typeof detail === 'object' ? JSON.stringify(detail) : detail;
      setError(errMsg);
    } finally {
      setIsLoading(false);
      setFiles([]); // clear input
    }
  };

  const pollBatchJob = (bId) => {
    const startTime = Date.now();
    const pollInterval = setInterval(async () => {
      try {
        if (Date.now() - startTime > 30 * 60 * 1000) { // 30 mins max timeout
          clearInterval(pollInterval);
          setError("Batch Evaluation Timeout.");
          return;
        }
        
        const data = await batchService.getBatchStatus(bId);
        setBatchStatus(data);

        if (import.meta.env.DEV) {
          console.group(`🔄 [Polling Response] Batch ID: ${bId}`);
          console.log("Status:", data.status, `(${data.completed}/${data.total} completed)`);
          if (data.results?.ranked_candidates) {
            console.table(data.results.ranked_candidates);
          }
          console.groupEnd();
        }
        
        if (data.status === 'COMPLETED' || data.status === 'COMPLETED_WITH_ERRORS' || data.status === 'FAILED') {
          clearInterval(pollInterval);
          
          if (data.status === 'FAILED') {
            setError(data.error || "Batch processing failed.");
            return;
          }
          
          setBatchResult(data.results);
          if (data.status === 'COMPLETED_WITH_ERRORS') {
            setError("Batch completed but some post-processing errors occurred.");
          } else if (data.failed > 0 && data.completed === 0) {
            setError("All evaluations failed in the batch.");
          } else if (data.results?.ranked_candidates?.length >= 1) {
            // Auto-load top candidate result
            handleViewResult(data.results.ranked_candidates[0]);
          }
        }
      } catch (err) {
        if (err.response && err.response.status === 404) {
          clearInterval(pollInterval);
          setError("Batch not found.");
        }
      }
    }, 2000);
  };

  const handleViewResult = async (candRow) => {
    setIsLoading(true);
    setError(null);
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

        setResult(mapped);
        setEvaluationId(candRow.evaluation_id);
        localStorage.setItem('lastEvaluation', JSON.stringify(mapped));
        setActiveStep(2);
      } else {
        setError(`Cannot view result: evaluation status is ${data?.status} or result is missing`);
      }
    } catch (err) {
      setError("Failed to fetch full evaluation payload.");
      console.error("❌ Evaluation Fetch Error:", err);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleBackToComparison = () => {
    setResult(null);
    setEvaluationId(null);
    setActiveStep(1.5);
  };

  // On-demand Email Generator trigger
  const handleGenerateEmail = async () => {
    if (!result) return;
    setIsGeneratingEmail(true);
    try {
      const payload = {
        filename: result.filename,
        template_type: emailTemplateType,
        hiring_recommendation: result.recommendation?.hiring_recommendation || 'Review Before Interview',
        candidate_summary: result.recommendation?.candidate_summary || [],
        strengths: result.recommendation?.candidate_highlights || [],
        missing_skills: result.evidence?.skills_evidence?.filter(s => s.status.toLowerCase().includes("not")).map(s => s.skill) || [],
        custom_recruiter_notes: editedNotes
      };
      
      const data = await candidateService.generateCommunicationEmail(payload);
      setEmailDraft(data);
    } catch (err) {
      console.error(err);
      alert("Failed to generate communication draft.");
    } finally {
      setIsGeneratingEmail(false);
    }
  };

  // Conversational Assistant submission
  const handleAskAssistant = async (e) => {
    e.preventDefault();
    if (!chatInput.trim() || !result) return;

    const userQuestion = chatInput.trim();
    setChatInput('');
    
    // Add user message to state
    const updatedHistory = [...chatMessages, { role: 'user', content: userQuestion }];
    setChatMessages(updatedHistory);
    setIsChatLoading(true);

    try {
      const historyPayload = updatedHistory.slice(1, -1).map(msg => ({
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
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: data.answer,
        citations: data.citations || []
      }]);
    } catch (err) {
      console.error(err);
      setChatMessages(prev => [...prev, {
        role: 'assistant',
        content: "I'm sorry, I couldn't reach the backend to answer your question.",
        citations: []
      }]);
    } finally {
      setIsChatLoading(false);
    }
  };

  // Developer Mode password unlock
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

  // Submit Final Screening Decision (Step 6)
  const handleSubmitScreening = async () => {
    setIsSubmittingScreening(true);
    // Simulate database write
    setTimeout(() => {
      setIsSubmittingScreening(false);
      setScreeningSuccess(true);
      // Reset result and return to Step 1
      setTimeout(() => {
        setResult(null);
        setEvaluationId(null);
        setFile(null);
        setActiveStep(1);
        setScreeningSuccess(false);
      }, 3000);
    }, 1500);
  };

  // Helper to toggle accordions
  const toggleAccordion = (index) => {
    setExpandedAccordions(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  // Safe color maps for hiring recommendations
  const getRecommendationStyle = (rec) => {
    const r = (rec || '').toLowerCase();
    if (r.includes('recommended')) return { bg: 'bg-emerald-50 border-emerald-200', text: 'text-emerald-700', badge: 'bg-emerald-500 text-white' };
    if (r.includes('review') || r.includes('backup')) return { bg: 'bg-amber-50 border-amber-200', text: 'text-amber-700', badge: 'bg-amber-500 text-white' };
    return { bg: 'bg-rose-50 border-rose-200', text: 'text-rose-700', badge: 'bg-rose-500 text-white' };
  };

  // Check step lock status (Steps 2-6 require an evaluation payload)
  const isStepLocked = (stepNum) => {
    return !result && stepNum > 1;
  };

  // Filter Steps based on role limits
  // Hiring Manager hides Ingest (1) and Comms (5)
  // Interviewer hides all except Decide (4)
  const isStepVisible = (stepNum) => {
    if (isInterviewer) return stepNum === 4;
    if (activeRole === 'Hiring Manager') return stepNum !== 1 && stepNum !== 5;
    return true;
  };

  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });
  };

  const toggleCandidateSelection = (evalId) => {
    setSelectedCandidates(prev => 
      prev.includes(evalId) 
        ? prev.filter(id => id !== evalId)
        : prev.length < 4 ? [...prev, evalId] : prev
    );
  };

  const getSortedFilteredCandidates = () => {
    if (!batchResult || !batchResult.ranked_candidates) return [];
    
    let filtered = [...batchResult.ranked_candidates];
    
    // Filter
    if (filterTier !== 'All') {
      filtered = filtered.filter(c => c.recommendation_tier === filterTier);
    }
    
    // Sort
    if (sortConfig.key !== 'rank') { // Default 'rank' is just the array order from backend
      filtered.sort((a, b) => {
        let aVal = a[sortConfig.key];
        let bVal = b[sortConfig.key];
        
        // Handle policy eligibility string sorting visually
        if (sortConfig.key === 'policy_eligible') {
          aVal = a.policy_eligible ? 1 : 0;
          bVal = b.policy_eligible ? 1 : 0;
        }

        if (aVal < bVal) return sortConfig.direction === 'asc' ? -1 : 1;
        if (aVal > bVal) return sortConfig.direction === 'asc' ? 1 : -1;
        return 0;
      });
    }
    
    return filtered;
  };

  const stepsList = [
    { num: 1, label: 'Ingest Resume' },
    { num: 2, label: 'Understand Profile' },
    { num: 3, label: 'Verify Evidence' },
    { num: 4, label: 'Decide Interview' },
    { num: 5, label: 'Generate Comms' },
    { num: 6, label: 'Complete Screening' }
  ];

  return (
    <div className="relative space-y-6">
      
      {/* Page Title Header */}
      <div className="flex items-center justify-between pb-2 border-b border-slate-100">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Recruiter Command Center</h1>
          <p className="text-xs text-slate-500 font-semibold">Ingest candidates and view semantic match decision insights</p>
        </div>
      </div>
      
      {/* 6-Step Progressive Workflow Sticky Navigation */}
      {!isInterviewer && (
        <div className="sticky top-16 bg-white/95 backdrop-blur border-b border-slate-200 z-40 py-3.5 mb-6 -mx-4 px-4 sm:-mx-6 sm:px-6 lg:-mx-8 lg:px-8">
          <div className="max-w-7xl mx-auto flex items-center justify-between overflow-x-auto scrollbar-none space-x-4">
            <div className="flex items-center space-x-1 sm:space-x-2">
              {stepsList.map((step) => {
                const isVisible = isStepVisible(step.num);
                if (!isVisible) return null;
                const locked = isStepLocked(step.num);
                const active = displayStep === step.num;
                const completed = result && displayStep > step.num;

                return (
                  <button
                    key={step.num}
                    disabled={locked}
                    onClick={() => setActiveStep(step.num)}
                    className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
                      active 
                        ? 'bg-indigo-50 text-indigo-700 ring-2 ring-indigo-600/20' 
                        : completed
                          ? 'text-indigo-600 hover:bg-slate-50'
                          : locked
                            ? 'text-slate-300 cursor-not-allowed'
                            : 'text-slate-500 hover:text-indigo-600 hover:bg-slate-50'
                    }`}
                  >
                    <span className={`w-5 h-5 rounded-full flex items-center justify-center border font-sans ${
                      completed 
                        ? 'bg-indigo-600 border-indigo-600 text-white' 
                        : active 
                          ? 'border-indigo-600 text-indigo-600 bg-white' 
                          : 'border-slate-300 text-slate-400'
                    }`}>
                      {completed ? <Check className="w-3 h-3" /> : step.num}
                    </span>
                    <span className="hidden lg:inline">{step.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Next / Back Step Controls */}
            {result && (
              <div className="flex space-x-2">
                <button
                  disabled={displayStep === 1 || (activeRole === 'Hiring Manager' && displayStep === 2)}
                  onClick={() => {
                    let prevStep = displayStep - 1;
                    while (prevStep >= 1 && !isStepVisible(prevStep)) {
                      prevStep--;
                    }
                    setActiveStep(prevStep);
                  }}
                  className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg disabled:opacity-30 disabled:pointer-events-none transition"
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
                    setActiveStep(nextStep);
                  }}
                  className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-100 rounded-lg disabled:opacity-30 disabled:pointer-events-none transition"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            )}
          </div>
        </div>
      )}

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
                <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
                  <div className="flex items-center space-x-2">
                    <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
                      <UploadCloud className="w-5 h-5" />
                    </div>
                    <h2 className="text-lg font-bold text-slate-800">1. Ingest Resume & Job Parameters</h2>
                  </div>

                  <form onSubmit={handleSubmitEvaluation} className="space-y-6">
                    <div className="space-y-2">
                      <label htmlFor="jd-text-area" className="block text-sm font-semibold text-slate-700">Job Description *</label>
                      <textarea
                        id="jd-text-area"
                        className="w-full h-48 p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none transition text-slate-700 bg-slate-50/30 text-sm font-medium"
                        placeholder="Paste core Job Description text here..."
                        value={jdText}
                        onChange={(e) => setJdText(e.target.value)}
                      />
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="jd-skills-input" className="block text-sm font-semibold text-slate-700">
                        Skills Overrides <span className="text-slate-400 font-normal">(Optional, comma-separated)</span>
                      </label>
                      <input
                        id="jd-skills-input"
                        type="text"
                        className="w-full p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none transition text-slate-700 bg-slate-50/30 text-sm"
                        placeholder="e.g. AWS, Python, Kubernetes"
                        value={jdSkills}
                        onChange={(e) => setJdSkills(e.target.value)}
                      />
                    </div>

                    <div className="space-y-2">
                      <label htmlFor="resume-file-input" className="block text-sm font-semibold text-slate-700">Resume PDF *</label>
                      <div
                        onDragEnter={handleDrag}
                        onDragOver={handleDrag}
                        onDragLeave={handleDrag}
                        onDrop={handleDrop}
                        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition ${
                          dragActive ? 'border-indigo-600 bg-indigo-50/50' : 'border-slate-200 hover:bg-slate-50/80 bg-slate-50/10'
                        }`}
                      >
                        <input
                          type="file"
                          id="resume-file-input"
                          accept="application/pdf"
                          multiple
                          className="hidden"
                          onChange={handleFileChange}
                        />
                        <label htmlFor="resume-file-input" className="cursor-pointer space-y-3 block">
                          <UploadCloud className="w-10 h-10 text-slate-400 mx-auto" />
                          {files.length > 0 ? (
                            <div className="space-y-2">
                              <p className="text-sm font-bold text-slate-700">{files.length} file(s) selected</p>
                              <div className="flex flex-wrap gap-2 justify-center">
                                {files.map((f, idx) => (
                                  <div key={idx} className="flex items-center space-x-1.5 bg-indigo-50 px-2 py-1 rounded-lg border border-indigo-100">
                                    <FileText className="w-3.5 h-3.5 text-indigo-600" />
                                    <span className="text-xs font-bold text-indigo-800 max-w-[120px] truncate">{f.name}</span>
                                    <button 
                                      type="button" 
                                      onClick={(e) => { e.preventDefault(); e.stopPropagation(); removeFile(idx); }}
                                      className="text-indigo-400 hover:text-indigo-600 ml-1"
                                    >
                                      &times;
                                    </button>
                                  </div>
                                ))}
                              </div>
                            </div>
                          ) : (
                            <div>
                              <p className="text-sm font-medium text-slate-700">Drag and drop PDF resumes here, or click to browse</p>
                              <p className="text-xs text-slate-400 mt-1">Supports multiple standard PDFs up to 10MB each</p>
                            </div>
                          )}
                        </label>
                      </div>
                    </div>

                    <button
                      type="submit"
                      disabled={isLoading || files.length === 0 || !jdText.trim()}
                      className={`w-full flex items-center justify-center space-x-2 font-bold py-3.5 px-4 rounded-xl shadow-lg transition-all ${
                        isLoading || files.length === 0 || !jdText.trim()
                          ? 'bg-slate-300 text-slate-500 cursor-not-allowed'
                          : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                      }`}
                    >
                      <span>{files.length > 1 ? `Evaluate ${files.length} Candidates` : 'Evaluate Candidate'}</span>
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </form>

                  {error && (
                    <div className="flex items-start space-x-3 p-4 bg-rose-50 border border-rose-100 rounded-xl text-rose-800 text-xs shadow-sm">
                      <AlertCircle className="w-4 h-4 text-rose-500 flex-shrink-0 mt-0.5" />
                      <span>{error}</span>
                    </div>
                  )}

                  {/* Batch Upload Queue Progress */}
                  {batchStatus && !batchResult && (
                    <div className="mt-8 space-y-4">
                      <h3 className="text-sm font-bold text-slate-800 flex items-center space-x-2">
                        <Activity className="w-4 h-4 text-indigo-500" />
                        <span>Batch Evaluation Progress</span>
                      </h3>
                      <div className="bg-white border border-slate-200 rounded-xl p-6 shadow-sm">
                        <div className="flex justify-between items-center mb-4">
                          <span className="text-slate-500 font-bold text-sm">Total Candidates: {batchStatus.total}</span>
                          <span className="text-indigo-600 font-bold text-sm">Batch ID: {batchStatus.batch_id.substring(0, 8)}...</span>
                        </div>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                          <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-100">
                            <div className="text-2xl font-black text-emerald-600">{batchStatus.completed}</div>
                            <div className="text-xs font-bold text-emerald-800 uppercase">Completed</div>
                          </div>
                          <div className="p-3 bg-indigo-50 rounded-lg border border-indigo-100">
                            <div className="text-2xl font-black text-indigo-600">{batchStatus.processing}</div>
                            <div className="text-xs font-bold text-indigo-800 uppercase">Processing</div>
                          </div>
                          <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
                            <div className="text-2xl font-black text-slate-600">{batchStatus.queued}</div>
                            <div className="text-xs font-bold text-slate-800 uppercase">Queued</div>
                          </div>
                          <div className="p-3 bg-rose-50 rounded-lg border border-rose-100">
                            <div className="text-2xl font-black text-rose-600">{batchStatus.failed}</div>
                            <div className="text-xs font-bold text-rose-800 uppercase">Failed</div>
                          </div>
                        </div>
                        
                        {batchStatus.status === 'PROCESSING' && (
                          <div className="mt-6 w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                            <div 
                              className="bg-indigo-600 h-2 rounded-full transition-all duration-500" 
                              style={{ width: `${((batchStatus.completed + batchStatus.failed) / batchStatus.total) * 100}%` }}
                            />
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Batch Completion Action */}
                  {batchResult && (
                    <div className="mt-8">
                      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6 shadow-sm text-center space-y-4">
                        <CheckCircle className="w-12 h-12 text-emerald-500 mx-auto" />
                        <div>
                          <h3 className="text-lg font-bold text-emerald-800">Batch Evaluation Complete</h3>
                          <p className="text-emerald-600 text-sm mt-1">{batchResult.successfully_evaluated} candidates evaluated successfully.</p>
                        </div>
                        <button
                          onClick={() => setActiveStep(1.5)} // Magic step for Candidate Comparison Table
                          className="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-lg shadow transition"
                        >
                          View Candidate Comparison
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* STEP 1.5: CANDIDATE COMPARISON */}
              {displayStep === 1.5 && batchResult && (
                <div className="space-y-6">
                  <div className="flex items-center justify-between">
                    <h2 className="text-xl font-bold text-slate-800">Candidate Comparison</h2>
                    <div className="flex space-x-3">
                      <select 
                        value={filterTier}
                        onChange={(e) => setFilterTier(e.target.value)}
                        className="px-3 py-1.5 border border-slate-200 rounded-lg text-sm text-slate-700 font-semibold focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      >
                        <option value="All">All Tiers</option>
                        <option value="Recommended">Recommended</option>
                        <option value="Review Before Interview">Review</option>
                        <option value="Keep as Backup">Backup</option>
                        <option value="Not Suitable for this Role">Not Suitable</option>
                      </select>
                      
                      <button 
                        onClick={() => setShowSideBySide(true)}
                        disabled={selectedCandidates.length < 2 || selectedCandidates.length > 4}
                        className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-300 text-white text-sm font-bold rounded-lg transition"
                      >
                        Compare Selected ({selectedCandidates.length})
                      </button>
                    </div>
                  </div>

                  <div className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm">
                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="bg-slate-50 border-b border-slate-200">
                            <th className="p-4"><input type="checkbox" disabled className="rounded text-indigo-600" /></th>
                            <th className="p-4 text-xs font-bold text-slate-500 uppercase cursor-pointer" onClick={() => handleSort('rank')}>
                              Rank {sortConfig.key === 'rank' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                            </th>
                            <th className="p-4 text-xs font-bold text-slate-500 uppercase cursor-pointer" onClick={() => handleSort('filename')}>
                              Candidate {sortConfig.key === 'filename' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                            </th>
                            <th className="p-4 text-xs font-bold text-slate-500 uppercase cursor-pointer" onClick={() => handleSort('recommendation_tier')}>
                              Policy Tier {sortConfig.key === 'recommendation_tier' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                            </th>
                            <th className="p-4 text-xs font-bold text-slate-500 uppercase cursor-pointer" onClick={() => handleSort('policy_eligible')}>
                              Eligibility {sortConfig.key === 'policy_eligible' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                            </th>
                            <th className="p-4 text-xs font-bold text-slate-500 uppercase cursor-pointer" onClick={() => handleSort('overall_score')}>
                              Score {sortConfig.key === 'overall_score' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                            </th>
                            <th className="p-4 text-xs font-bold text-slate-500 uppercase cursor-pointer" onClick={() => handleSort('skill_match')}>
                              Skill Match {sortConfig.key === 'skill_match' && (sortConfig.direction === 'asc' ? '↑' : '↓')}
                            </th>
                            <th className="p-4 text-xs font-bold text-slate-500 uppercase">Missing Critical</th>
                            <th className="p-4 text-xs font-bold text-slate-500 uppercase">Action</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-100">
                          {getSortedFilteredCandidates().map(cand => (
                            <tr key={cand.evaluation_id} className={`hover:bg-slate-50 transition ${!cand.policy_eligible ? 'bg-slate-50/50' : ''}`}>
                              <td className="p-4">
                                <input 
                                  type="checkbox" 
                                  checked={selectedCandidates.includes(cand.evaluation_id)}
                                  onChange={() => toggleCandidateSelection(cand.evaluation_id)}
                                  disabled={!selectedCandidates.includes(cand.evaluation_id) && selectedCandidates.length >= 4}
                                  className="rounded text-indigo-600 focus:ring-indigo-500"
                                />
                              </td>
                              <td className="p-4">
                                <span className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${cand.rank === 1 ? 'bg-amber-100 text-amber-700' : 'bg-slate-100 text-slate-600'}`}>
                                  {cand.rank}
                                </span>
                              </td>
                              <td className="p-4 font-bold text-slate-800 text-sm">{cand.filename.replace('.pdf', '')}</td>
                              <td className="p-4">
                                <span className={`px-2.5 py-1 text-[10px] font-bold uppercase rounded-md border ${getRecommendationStyle(cand.recommendation_tier).bg} ${getRecommendationStyle(cand.recommendation_tier).text}`}>
                                  {cand.recommendation_tier}
                                </span>
                              </td>
                              <td className="p-4">
                                {cand.policy_eligible ? (
                                  <span className="flex items-center space-x-1 text-emerald-600 text-xs font-bold"><CheckCircle className="w-3.5 h-3.5" /> <span>Eligible</span></span>
                                ) : (
                                  <span className="flex items-center space-x-1 text-rose-600 text-xs font-bold"><XCircle className="w-3.5 h-3.5" /> <span>Not Suitable</span></span>
                                )}
                              </td>
                              <td className="p-4 font-black text-indigo-600">{cand.overall_score}</td>
                              <td className="p-4 font-semibold text-slate-700">{cand.skill_match}</td>
                              <td className="p-4">
                                {cand.critical_missing.length > 0 ? (
                                  <span className="text-rose-600 text-xs font-bold">{cand.critical_missing.length} skills</span>
                                ) : (
                                  <span className="text-slate-400 text-xs font-bold">-</span>
                                )}
                              </td>
                              <td className="p-4">
                                <button 
                                  onClick={() => handleViewResult(cand)}
                                  className="text-xs font-bold text-indigo-600 hover:text-indigo-800"
                                >
                                  View Full
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                  
                  {/* Side-by-side Modal */}
                  {showSideBySide && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
                      <div className="bg-white rounded-2xl shadow-xl w-full max-w-6xl max-h-[90vh] flex flex-col overflow-hidden">
                        <div className="p-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                          <h2 className="text-lg font-bold text-slate-800 flex items-center"><Users className="w-5 h-5 mr-2 text-indigo-600" /> Side-by-Side Comparison</h2>
                          <button onClick={() => setShowSideBySide(false)} className="p-2 hover:bg-slate-200 rounded-lg"><XCircle className="w-5 h-5 text-slate-500" /></button>
                        </div>
                        
                        <div className="p-6 overflow-auto flex-1">
                          <div className="flex space-x-4 min-w-max">
                            {selectedCandidates.map(evalId => {
                              const cand = batchResult.ranked_candidates.find(c => c.evaluation_id === evalId);
                              if (!cand) return null;
                              return (
                                <div key={evalId} className="w-80 border border-slate-200 rounded-xl overflow-hidden flex-shrink-0">
                                  <div className="p-4 bg-slate-50 border-b border-slate-200">
                                    <h3 className="font-bold text-slate-800 truncate" title={cand.filename}>{cand.filename}</h3>
                                    <div className="flex items-center space-x-2 mt-2">
                                      <span className="text-xl font-black text-indigo-600">{cand.overall_score}</span>
                                      <span className={`text-[10px] uppercase font-bold px-2 py-0.5 rounded-full ${cand.policy_eligible ? 'bg-emerald-100 text-emerald-700' : 'bg-rose-100 text-rose-700'}`}>
                                        {cand.policy_eligible ? 'Eligible' : 'Failed'}
                                      </span>
                                    </div>
                                  </div>
                                  <div className="p-4 space-y-4 text-sm">
                                    <div>
                                      <p className="text-xs font-bold text-slate-500 uppercase mb-1">Tier</p>
                                      <p className={`font-semibold ${getRecommendationStyle(cand.recommendation_tier).text}`}>{cand.recommendation_tier}</p>
                                    </div>
                                    <div className="grid grid-cols-2 gap-2">
                                      <div>
                                        <p className="text-xs font-bold text-slate-500 uppercase mb-1">Skill</p>
                                        <p className="font-bold text-slate-700">{cand.skill_match}</p>
                                      </div>
                                      <div>
                                        <p className="text-xs font-bold text-slate-500 uppercase mb-1">Relevance</p>
                                        <p className="font-bold text-slate-700">{cand.experience_relevance}</p>
                                      </div>
                                    </div>
                                    <div>
                                      <p className="text-xs font-bold text-emerald-600 uppercase mb-1">Strengths ({cand.strengths.length})</p>
                                      <ul className="list-disc pl-4 space-y-1 text-slate-600 text-xs">
                                        {cand.strengths.slice(0, 3).map((s, i) => <li key={i}>{s}</li>)}
                                        {cand.strengths.length > 3 && <li>+{cand.strengths.length - 3} more</li>}
                                      </ul>
                                    </div>
                                    <div>
                                      <p className="text-xs font-bold text-rose-600 uppercase mb-1">Missing Critical</p>
                                      {cand.critical_missing.length > 0 ? (
                                        <div className="flex flex-wrap gap-1">
                                          {cand.critical_missing.map((s, i) => <span key={i} className="px-1.5 py-0.5 bg-rose-50 border border-rose-100 text-rose-700 rounded text-[10px] font-bold">{s}</span>)}
                                        </div>
                                      ) : <p className="text-slate-400 italic text-xs">None</p>}
                                    </div>
                                    <div className="pt-4 border-t border-slate-100 text-center">
                                      <button 
                                        onClick={() => { setShowSideBySide(false); handleViewResult(cand); }}
                                        className="text-xs font-bold text-indigo-600 hover:text-indigo-800"
                                      >
                                        View Full Evaluation
                                      </button>
                                    </div>
                                  </div>
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* STEP 2: UNDERSTAND CANDIDATE */}
              {displayStep === 2 && result && (
                <div className="space-y-6">
                  
                  {batchResult && (
                    <div className="flex items-center pb-2">
                      <button 
                        onClick={() => handleBackToComparison()}
                        className="flex items-center space-x-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 text-sm font-bold rounded-xl transition"
                      >
                        <ChevronLeft className="w-4 h-4" />
                        <span>Back to Batch Comparison</span>
                      </button>
                    </div>
                  )}

                  {/* Decision Engine Dimension Scores */}
                  {result.dimensionScores && result.dimensionScores.length > 0 ? (
                    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
                      {result.dimensionScores.map(dim => (
                        <div key={dim.key} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm text-center space-y-1 hover:border-indigo-300 transition-colors cursor-default" title={dim.evidence?.join('\n')}>
                          <span className="text-[10px] sm:text-xs font-bold text-slate-400 uppercase tracking-wider block truncate">{getDimensionLabel(dim.key)}</span>
                          <span className="text-2xl sm:text-3xl font-black text-indigo-600 font-sans">
                            {dim.score}
                          </span>
                          <span className="text-[9px] text-slate-400 font-bold tracking-wider block">CONF: {dim.confidence}%</span>
                        </div>
                      ))}
                    </div>
                  ) : null}

                  {/* Skills Alignment Badges */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
                      <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                        Matched Skills ({(result.evidenceStates?.matched || []).length})
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {(result.evidenceStates?.matched || []).map((skill, idx) => (
                          <span key={idx} className="px-2.5 py-1 bg-emerald-50 border border-emerald-100 text-emerald-700 text-xs font-bold rounded-lg">
                            {skill}
                          </span>
                        ))}
                        {(result.evidenceStates?.matched || []).length === 0 && (
                          <p className="text-xs text-slate-400 italic">No skills matched.</p>
                        )}
                      </div>
                    </div>
                    <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm space-y-3">
                      <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">
                        Missing Skills ({(result.evidenceStates?.missing || []).length})
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {(result.evidenceStates?.missing || []).map((skill, idx) => (
                          <span key={idx} className="px-2.5 py-1 bg-rose-50 border border-rose-100 text-rose-700 text-xs font-bold rounded-lg">
                            {skill}
                          </span>
                        ))}
                        {(result.evidenceStates?.missing || []).length === 0 && (
                          <p className="text-xs text-slate-400 italic font-semibold">All required skills identified!</p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Structured Recommendation Basis & Executive Summary */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-4 border-b border-slate-100 space-y-3 sm:space-y-0">
                      <div className="flex items-center space-x-2">
                        <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
                          <Users className="w-5 h-5" />
                        </div>
                        <h2 className="text-lg font-bold text-slate-800">2. Profile Suitability Overview</h2>
                      </div>
                      
                      {/* Classification Badge */}
                      <span className={`px-4 py-1.5 rounded-full text-xs font-black tracking-wide border uppercase shadow-sm ${
                        getRecommendationStyle(result.recommendation?.tier).bg
                      } ${
                        getRecommendationStyle(result.recommendation?.tier).text
                      }`}>
                        {result.recommendation?.tier}
                      </span>
                    </div>

                    {/* Recommendation Basis (Direct from Decision Engine) */}
                    <div className="space-y-6 pt-2">
                      {result.recommendation?.reasoning && (
                        <div className="bg-slate-50 border border-slate-100 rounded-xl p-5 space-y-3">
                          <h3 className="text-sm font-bold text-slate-800">Decision Reasoning</h3>
                          <p className="text-sm text-slate-600 leading-relaxed">{result.recommendation.reasoning}</p>
                        </div>
                      )}

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Strengths */}
                        <div className="space-y-3">
                          <h3 className="text-sm font-bold text-emerald-600 uppercase tracking-wider flex items-center"><CheckCircle className="w-4 h-4 mr-1.5" /> Strengths</h3>
                          <ul className="space-y-2">
                            {(result.recommendation?.strengths || []).map((bullet, idx) => (
                              <li key={idx} className="flex items-start space-x-2.5 text-sm text-slate-600">
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
                          <h3 className="text-sm font-bold text-amber-600 uppercase tracking-wider flex items-center"><AlertCircle className="w-4 h-4 mr-1.5" /> Weaknesses / Policy Flags</h3>
                          <ul className="space-y-2">
                            {(result.recommendation?.weaknesses?.length > 0 ? result.recommendation.weaknesses : result.policyFlags || []).map((bullet, idx) => (
                              <li key={idx} className="flex items-start space-x-2.5 text-sm text-slate-600">
                                <span className="w-1.5 h-1.5 bg-amber-500 rounded-full flex-shrink-0 mt-2" />
                                <span>{bullet}</span>
                              </li>
                            ))}
                            {(result.recommendation?.weaknesses?.length === 0 && (result.policyFlags || []).length === 0) && (
                              <p className="text-xs text-slate-400 italic">No policy flags triggered.</p>
                            )}
                          </ul>
                        </div>

                        {/* Critical Missing */}
                        <div className="space-y-3">
                          <h3 className="text-sm font-bold text-rose-600 uppercase tracking-wider flex items-center"><XCircle className="w-4 h-4 mr-1.5" /> Critical Missing</h3>
                          <ul className="space-y-2">
                            {(result.recommendation?.criticalMissingSkills?.length > 0 ? result.recommendation.criticalMissingSkills : result.evidenceStates?.missing || []).map((skill, idx) => (
                              <li key={idx} className="flex items-start space-x-2.5 text-sm text-slate-600">
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
                  <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
                    <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">{result.evidence?.timeline_title || "Chronological Career Milestones"}</h3>
                    <div className="relative border-l-2 border-slate-200 pl-6 space-y-8 ml-2">
                      {result.evidence?.career_timeline?.map((item, idx) => (
                        <div key={idx} className="relative">
                          <span className="absolute -left-[31px] top-1.5 w-4 h-4 rounded-full bg-white border-2 border-indigo-600 flex items-center justify-center">
                            <span className="w-1.5 h-1.5 bg-indigo-600 rounded-full" />
                          </span>
                          {item.year && (
                            <span className="text-xs font-bold text-indigo-600 bg-indigo-50 border border-indigo-100 rounded-md px-2 py-0.5">{item.year}</span>
                          )}
                          <h4 className={`text-sm font-bold text-slate-800 ${item.year ? 'mt-2' : ''}`}>{item.role}</h4>
                          <p className="text-xs text-slate-500 font-semibold">{item.company}</p>
                          <p className="text-xs text-slate-600 mt-1">{item.details}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Disclaimer */}
                  <p className="text-center text-[10px] text-slate-400 italic font-medium px-4">
                    {result.recommendation?.disclaimer}
                  </p>
                </div>
              )}

              {/* STEP 3: VERIFY EVIDENCE */}
              {displayStep === 3 && result && (
                <div className="space-y-6">
                  
                  {/* Factual Evidence Audit */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
                    <div className="flex items-center space-x-2">
                      <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
                        <FileText className="w-5 h-5" />
                      </div>
                      <h2 className="text-lg font-bold text-slate-800">3. Factual Evidence Audit</h2>
                    </div>

                    {result.skillsEvidence && result.skillsEvidence.length > 0 ? (
                      <div className="space-y-3">
                        {result.skillsEvidence.map((item, idx) => {
                          const isIdentified = item.status?.toLowerCase().includes("identified") && !item.status?.toLowerCase().includes("not");
                          const isOpen = !!expandedAccordions[idx];

                          return (
                            <div key={idx} className="border border-slate-200 rounded-xl overflow-hidden shadow-sm bg-white">
                              <button
                                onClick={() => toggleAccordion(idx)}
                                className="w-full flex items-center justify-between p-4 hover:bg-slate-50 transition text-left"
                              >
                                <div className="flex items-center space-x-3">
                                  <span className="text-sm font-bold text-slate-800">{item.skill}</span>
                                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                                    isIdentified ? 'bg-emerald-50 border border-emerald-200 text-emerald-700' : 'bg-rose-50 border border-rose-200 text-rose-700'
                                  }`}>
                                    {isIdentified ? 'Identified' : 'Not identified'}
                                  </span>
                                </div>
                                <span className="text-xs font-bold text-slate-400 hover:text-slate-600">
                                  {isOpen ? 'Collapse' : 'Expand'}
                                </span>
                              </button>

                              {isOpen && (
                                <div className="p-4 bg-slate-50/50 border-t border-slate-100 text-xs text-slate-600 space-y-3">
                                  {item.evidence_snippet && (
                                    <div className="bg-white border border-slate-200 rounded-lg p-3 italic text-slate-700">
                                      "{item.evidence_snippet}"
                                    </div>
                                  )}
                                </div>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      /* Direct evidenceStates display from backend (NO synthetic text) */
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                          <h3 className="text-xs font-bold text-emerald-700 uppercase tracking-wider flex items-center">
                            <CheckCircle className="w-4 h-4 mr-1.5" /> Identified / Matched Skills ({result.evidenceStates?.matched?.length || 0})
                          </h3>
                          <ul className="space-y-1.5">
                            {(result.evidenceStates?.matched || []).map((skill, idx) => (
                              <li key={idx} className="text-xs font-bold text-slate-700 bg-white border border-slate-200 rounded-lg px-3 py-2 flex items-center justify-between">
                                <span>{skill}</span>
                                <span className="text-[10px] font-bold text-emerald-600 uppercase">Verified</span>
                              </li>
                            ))}
                            {(result.evidenceStates?.matched || []).length === 0 && (
                              <p className="text-xs text-slate-400 italic">No skills matched.</p>
                            )}
                          </ul>
                        </div>
                        <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 space-y-3">
                          <h3 className="text-xs font-bold text-rose-700 uppercase tracking-wider flex items-center">
                            <XCircle className="w-4 h-4 mr-1.5" /> Missing Skills ({result.evidenceStates?.missing?.length || 0})
                          </h3>
                          <ul className="space-y-1.5">
                            {(result.evidenceStates?.missing || []).map((skill, idx) => (
                              <li key={idx} className="text-xs font-bold text-slate-700 bg-white border border-slate-200 rounded-lg px-3 py-2 flex items-center justify-between">
                                <span>{skill}</span>
                                <span className="text-[10px] font-bold text-rose-600 uppercase">Not Found</span>
                              </li>
                            ))}
                            {(result.evidenceStates?.missing || []).length === 0 && (
                              <p className="text-xs text-slate-400 italic font-semibold">All required skills identified!</p>
                            )}
                          </ul>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Business Impact Metrics */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
                    <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">Extracted Business Impact & Quantifiable Outcomes</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {result.evidence?.business_impact?.map((item, idx) => (
                        <div key={idx} className="bg-indigo-50/30 border border-indigo-100 rounded-xl p-4 flex items-start space-x-3 shadow-sm">
                          <span className="w-2.5 h-2.5 bg-indigo-500 rounded-full flex-shrink-0 mt-1.5" />
                          <div>
                            <span className="text-[10px] font-black text-indigo-700 uppercase tracking-wide bg-indigo-50 px-2 py-0.5 rounded border border-indigo-150">{item.category}</span>
                            <p className="text-sm text-slate-700 mt-2 font-medium">{item.description}</p>
                          </div>
                        </div>
                      ))}
                      {(!result.evidence?.business_impact || result.evidence.business_impact.length === 0) && (
                        <p className="text-xs text-slate-400 italic col-span-2">No business impact or quantitative achievements could be extracted from the resume.</p>
                      )}
                    </div>
                  </div>

                </div>
              )}

              {/* STEP 4: DECIDE INTERVIEW */}
              {displayStep === 4 && result && (
                <div className="space-y-6">
                  
                  {/* Onboarding & Ramp-up (Hides for Interviewer role) */}
                  {!isInterviewer && (
                    <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
                      <div className="flex items-center space-x-2">
                        <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
                          <Clock className="w-5 h-5" />
                        </div>
                        <h2 className="text-lg font-bold text-slate-800">4. Onboarding & Learning Strategy</h2>
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
                              <li key={idx} className="flex items-start space-x-2 text-xs text-slate-600 font-semibold bg-slate-50 border border-slate-100 rounded-lg p-2.5">
                                <span className="text-indigo-600 font-black">✔</span>
                                <span>{factor}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Learnability Curves / Transition Matrix */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
                    <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">Learnability Transition Matrix (Adjacent Technology Mappings)</h3>
                    <div className="overflow-x-auto">
                      <table className="w-full text-xs text-left text-slate-500 border-collapse">
                        <thead>
                          <tr className="border-b border-slate-200 text-slate-400 font-bold uppercase text-[10px] bg-slate-50/50">
                            <th className="py-3 px-4">Requirement</th>
                            <th className="py-3 px-4">Estimated Difficulty</th>
                            <th className="py-3 px-4">Transition Path / Rationale</th>
                          </tr>
                        </thead>
                        <tbody>
                          {result.onboarding?.learning_curve?.map((item, idx) => (
                            <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50/30">
                              <td className="py-3 px-4 font-bold text-slate-700">{item.skill}</td>
                              <td className="py-3 px-4">
                                <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                  item.difficulty.toLowerCase().includes('easy') 
                                    ? 'bg-emerald-50 text-emerald-700 border border-emerald-100' 
                                    : 'bg-amber-50 text-amber-700 border border-amber-100'
                                }`}>
                                  {item.difficulty}
                                </span>
                              </td>
                              <td className="py-3 px-4 text-slate-600">{item.reason}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Graded Interview prep questions checklist */}
                  <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
                    <div className="flex items-center justify-between pb-4 border-b border-slate-150">
                      <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">Difficulty-Graded Technical Question Checklist</h3>
                      
                      {/* Tabs */}
                      <div className="flex space-x-1 bg-slate-100 rounded-lg p-1 border border-slate-200">
                        {['easy', 'medium', 'advanced'].map((tab) => (
                          <button
                            key={tab}
                            onClick={() => setSelectedQuestionsTab(tab)}
                            className={`px-3 py-1 text-xs font-bold rounded-md capitalize transition ${
                              selectedQuestionsTab === tab 
                                ? 'bg-white text-indigo-700 shadow-sm' 
                                : 'text-slate-500 hover:text-slate-800'
                            }`}
                          >
                            {tab}
                          </button>
                        ))}
                      </div>
                    </div>

                    {/* Interview Verification prep focus areas */}
                    <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 text-xs space-y-2">
                      <span className="font-bold text-slate-500 uppercase tracking-wider block text-[10px]">Verification Target Focus Areas</span>
                      <ul className="list-disc pl-4 space-y-1.5 text-slate-600 font-semibold">
                        {result.interview?.verify_during_interview?.map((area, idx) => (
                          <li key={idx}>{area}</li>
                        ))}
                      </ul>
                    </div>

                    {/* Graded Question lists */}
                    <div className="space-y-3 pt-2">
                      {result.interview?.interview_questions?.[selectedQuestionsTab]?.map((q, idx) => (
                        <div key={idx} className="flex items-start space-x-3 p-3 bg-white border border-slate-200 rounded-xl shadow-sm">
                          <input
                            type="checkbox"
                            id={`q-${selectedQuestionsTab}-${idx}`}
                            className="w-4 h-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500 mt-0.5"
                          />
                          <label htmlFor={`q-${selectedQuestionsTab}-${idx}`} className="text-xs font-medium text-slate-700 cursor-pointer">
                            {q}
                          </label>
                        </div>
                      ))}
                      {(!result.interview?.interview_questions?.[selectedQuestionsTab] || result.interview.interview_questions[selectedQuestionsTab].length === 0) && (
                        <p className="text-xs text-slate-400 italic">No questions generated for this difficulty category.</p>
                      )}
                    </div>
                  </div>

                </div>
              )}

              {/* STEP 5: GENERATE COMMUNICATIONS */}
              {displayStep === 5 && result && (
                <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
                  <div className="flex items-center space-x-2">
                    <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
                      <Mail className="w-5 h-5" />
                    </div>
                    <h2 className="text-lg font-bold text-slate-800">5. On-Demand Candidate Communications Generator</h2>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center pt-2">
                    <div className="space-y-2 col-span-2">
                      <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider">Select Communication Template</label>
                      <select
                        value={emailTemplateType}
                        onChange={(e) => setEmailTemplateType(e.target.value)}
                        className="w-full p-3 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none transition text-slate-700 bg-slate-50/50 text-sm font-semibold"
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

                  {/* Generated Email Editor */}
                  {emailDraft && (
                    <div className="border border-slate-200 rounded-2xl p-5 space-y-4 bg-slate-50/40 shadow-inner mt-6 animate-fadeIn">
                      <div className="space-y-1">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Subject</span>
                        <input
                          type="text"
                          value={emailDraft.subject}
                          onChange={(e) => setEmailDraft({ ...emailDraft, subject: e.target.value })}
                          className="w-full p-2 border border-slate-200 rounded-lg text-xs font-semibold text-slate-700 bg-white"
                        />
                      </div>
                      
                      <div className="space-y-1">
                        <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Draft Body</span>
                        <textarea
                          rows={12}
                          value={emailDraft.body}
                          onChange={(e) => setEmailDraft({ ...emailDraft, body: e.target.value })}
                          className="w-full p-3 border border-slate-200 rounded-lg text-xs font-medium text-slate-700 bg-white"
                        />
                      </div>
                      
                      <div className="flex justify-end pt-2">
                        <button
                          onClick={() => {
                            navigator.clipboard.writeText(`Subject: ${emailDraft.subject}\n\n${emailDraft.body}`);
                            alert("Copied to clipboard!");
                          }}
                          className="px-4 py-2 border border-slate-200 hover:bg-slate-50 rounded-lg text-xs font-bold text-slate-600 transition"
                        >
                          Copy Complete Message
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* STEP 6: COMPLETE SCREENING */}
              {displayStep === 6 && result && (
                <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
                  <div className="flex items-center space-x-2">
                    <div className="p-2 bg-indigo-50 rounded-lg text-indigo-600">
                      <CheckCircle className="w-5 h-5" />
                    </div>
                    <h2 className="text-lg font-bold text-slate-800">6. Finalize Screening Evaluation & Decisions</h2>
                  </div>

                  {/* Override Status Button matrix */}
                  <div className="space-y-2">
                    <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider">Hiring Status Override Decision</label>
                    <div className="grid grid-cols-3 gap-4">
                      {['Shortlist', 'Hold', 'Reject'].map((opt) => {
                        const active = overrideDecision.toLowerCase().includes(opt.toLowerCase());
                        
                        return (
                          <button
                            key={opt}
                            type="button"
                            onClick={() => setOverrideDecision(opt)}
                            className={`p-4 border rounded-xl text-sm font-bold shadow-sm transition flex flex-col items-center space-y-2 ${
                              active
                                ? opt === 'Shortlist' 
                                  ? 'bg-emerald-50 border-emerald-500 text-emerald-800 font-extrabold ring-2 ring-emerald-500/20'
                                  : opt === 'Hold'
                                    ? 'bg-amber-50 border-amber-500 text-amber-800 font-extrabold ring-2 ring-amber-500/20'
                                    : 'bg-rose-50 border-rose-500 text-rose-800 font-extrabold ring-2 ring-rose-500/20'
                                : 'bg-white border-slate-200 hover:bg-slate-50 text-slate-600'
                            }`}
                          >
                            <span>{opt}</span>
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  {/* Actionable Resume Improvement list */}
                  <div className="bg-slate-50 border border-slate-100 rounded-xl p-4 text-xs space-y-3">
                    <span className="font-bold text-slate-500 uppercase tracking-wider block text-[10px]">Resume Checklist Audits</span>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {result.recruiter?.resume_feedback?.map((fb, idx) => (
                        <div key={idx} className="flex items-center space-x-2">
                          {fb.status === 'pass' ? (
                            <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-amber-500 flex-shrink-0" />
                          )}
                          <span className="text-slate-600 font-semibold">{fb.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recruiter Notes Editor */}
                  <div className="space-y-2 border-t border-slate-100 pt-5">
                    <div className="flex items-center justify-between">
                      <label className="block text-xs font-bold text-slate-500 uppercase tracking-wider">Recruiter Notes</label>
                      <button
                        type="button"
                        onClick={() => setNotesEditable(!notesEditable)}
                        className="text-xs font-bold text-indigo-600 hover:text-indigo-800 flex items-center space-x-1"
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
                      onChange={(e) => setEditedNotes(e.target.value)}
                      className={`w-full p-3 border rounded-xl focus:outline-none transition text-xs font-medium text-slate-700 ${
                        notesEditable 
                          ? 'border-indigo-400 bg-white ring-2 ring-indigo-500/10 focus:ring-2 focus:ring-indigo-500' 
                          : 'border-slate-200 bg-slate-50/50 cursor-not-allowed'
                      }`}
                      placeholder="Add recruiter notes and manual feedback details here..."
                    />
                  </div>

                  {/* Submit decision */}
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
