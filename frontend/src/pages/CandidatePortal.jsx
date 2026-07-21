import React, { useEffect, useState } from 'react';
import { 
  Target, Award, BookOpen, CheckCircle, ArrowRight, FileText, Sparkles, HelpCircle, AlertCircle, Play
} from 'lucide-react';
import { mapEvaluationResponse } from '../services/evaluationMapper';

const mockEvaluationData = {
  status: "success",
  filename: "muhammed_savad_ds_resume.pdf",
  overall_score: 82,
  decision_engine: {
    overall_score: 82,
    evidence_states: {
      MATCHED: [
        "Python", "Machine Learning", "SQL", "Docker", "AWS", "PyTorch", 
        "TensorFlow", "FastAPI", "Pandas", "NumPy", "Git"
      ],
      MISSING: ["Qdrant", "Flask", "Agile"],
      INFERRED: [],
      CONTRADICTED: []
    },
    recommendation: {
      hiring_recommendation: "Interview Candidate",
      recommendation_basis: {
        strengths: ["Strong ML & Deep Learning experience", "FastAPI microservices background"],
        weaknesses: ["Missing Qdrant vector database experience"],
        critical_missing_skills: ["Qdrant"]
      }
    }
  },
  onboarding: {
    learning_curve: [
      { skill: "Qdrant", difficulty: "Moderate", reason: "Transition path: extend FAISS experience to vector indexes." },
      { skill: "Flask", difficulty: "Easy", reason: "Transition path: pick up application factories from FastAPI routing concepts." }
    ]
  },
  recruiter: {
    resume_feedback: [
      { label: "Quantify business impact statistics", status: "warning" },
      { label: "Add live deployment links to projects", status: "warning" },
      { label: "Skills organization is clear and parsing-friendly", status: "pass" }
    ]
  },
  feedback_report: `# Career Coaching & Development Roadmap

Hello! Your technical profile matches **81.5%** of the target Data Scientist requirements. You have a very strong foundation in Machine Learning, Deep Learning, and Python-based backend APIs.

## Key Strengths
- **ML & DL Foundations:** Strong expertise with PyTorch and TensorFlow, mapping cleanly to modern Machine Learning requirements.
- **Core API Development:** Proficiency in FastAPI for high-performance microservices.
- **Data Operations & Engineering:** Native competence in NumPy and Pandas for data manipulation, and Git for version control.

## Recommended Upskilling Areas (Gap Analysis)
You missed: **Qdrant**, **Flask**, and **Agile**.

## Actionable 2-Step Roadmap

### Step 1: Vector Search Engines (Qdrant)
* **Action:** Study vector indexing, similarity measurements, and semantic retrieval operations.
* **Context:** Since you already have Pinecone and FAISS experience, extending your database knowledge to Qdrant will be direct because the underlying vector embedding math is identical.

### Step 2: Alternative Microservice Frameworks (Flask)
* **Action:** Build a simple REST API using Flask to understand its routing and extensions.
* **Context:** You have deep FastAPI expertise. Flask shares similar routing/request concepts, so picking it up will be a straightforward transition focusing on its application factories rather than starting backend development from scratch.`
};

const CandidatePortal = ({ evaluationData = null, activeRole = 'Candidate' }) => {
  const [data, setData] = useState(mockEvaluationData);
  const [isUsingLive, setIsUsingLive] = useState(false);

  useEffect(() => {
    if (evaluationData) {
      setData(evaluationData);
      setIsUsingLive(true);
    } else {
      const stored = localStorage.getItem('lastEvaluation');
      if (stored) {
        try {
          const parsed = JSON.parse(stored);
          setData(parsed);
          setIsUsingLive(true);
        } catch (e) {
          console.error("Failed to parse cached evaluation from localStorage", e);
        }
      }
    }
  }, [evaluationData]);

  const handleClearCache = () => {
    localStorage.removeItem('lastEvaluation');
    setData(mockEvaluationData);
    setIsUsingLive(false);
  };

  // Centralized Evaluation Mapping
  const mapped = mapEvaluationResponse(data) || {};
  const filename = mapped.filename || "resume.pdf";
  const overallScorePercent = mapped.overallScore ?? 0;
  const matchedSkills = mapped.evidenceStates?.matched || [];
  const missingSkills = mapped.evidenceStates?.missing || [];
  const learningCurve = mapped.onboarding?.learning_curve || mapped.recommendation?.weaknesses?.map(w => ({ skill: w, difficulty: "Moderate", reason: w })) || [];
  const resumeFeedback = data.recruiter?.resume_feedback || [];

  // Simple Markdown formatting helper for the AI feedback report
  const parseBold = (text) => {
    const parts = text.split(/\*\*(.*?)\*\*/g);
    return parts.map((part, i) => i % 2 === 1 ? <strong key={i} className="font-semibold text-slate-900">{part}</strong> : part);
  };

  const renderMarkdown = (text) => {
    if (!text) return null;
    return text.split('\n').map((line, idx) => {
      let cleanLine = line.trim();
      if (cleanLine.startsWith('###')) {
        return <h3 key={idx} className="text-lg font-bold text-slate-900 mt-4 mb-2">{cleanLine.replace('###', '').trim()}</h3>;
      }
      if (cleanLine.startsWith('##')) {
        return <h2 key={idx} className="text-xl font-bold text-slate-900 mt-5 mb-3 border-b border-slate-200 pb-1">{cleanLine.replace('##', '').trim()}</h2>;
      }
      if (cleanLine.startsWith('#')) {
        return <h1 key={idx} className="text-2xl font-extrabold text-slate-900 mt-6 mb-4">{cleanLine.replace('#', '').trim()}</h1>;
      }
      if (cleanLine.startsWith('-') || cleanLine.startsWith('*')) {
        return (
          <li key={idx} className="ml-5 list-disc text-slate-700 my-1">
            {parseBold(cleanLine.substring(1).trim())}
          </li>
        );
      }
      if (cleanLine) {
        return <p key={idx} className="text-slate-700 my-2 leading-relaxed">{parseBold(cleanLine)}</p>;
      }
      return <div key={idx} className="h-2" />;
    });
  };

  return (
    <div className="max-w-6xl mx-auto p-6 md:p-8 space-y-8">
      {/* Recruiter Preview Banner */}
      {activeRole !== 'Candidate' && (
        <div className="bg-amber-50 border border-amber-200 text-amber-800 px-4 py-3 rounded-xl flex items-center justify-between text-sm shadow-sm mb-6">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-amber-500" />
            <span className="font-semibold">Recruiter Preview Mode:</span>
            <span>You are viewing the portal exactly as the candidate sees it.</span>
          </div>
        </div>
      )}

      {/* Header Profile Info Banner */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between space-y-4 md:space-y-0 pb-6 border-b border-slate-200">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-indigo-50 rounded-xl text-indigo-500 shadow-inner">
            <Target className="w-8 h-8 text-indigo-600" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-slate-900">Career Strategy Portal</h1>
            <p className="text-slate-500 mt-1 flex items-center space-x-1.5">
              <FileText className="w-4 h-4 text-slate-400" />
              <span>Report for: <span className="font-semibold text-slate-700">{filename}</span></span>
            </p>
          </div>
        </div>

        {/* Live Payload Status Badge */}
        <div className="flex items-center space-x-3">
          {isUsingLive ? (
            <div className="flex items-center space-x-2 bg-emerald-50 text-emerald-700 border border-emerald-250 px-4 py-1.5 rounded-full text-xs font-semibold shadow-inner">
              <span className="w-2 h-2 bg-emerald-500 rounded-full animate-ping" />
              <span>Live Evaluation Loaded</span>
              <button 
                onClick={handleClearCache}
                className="ml-2 text-emerald-900 hover:text-emerald-950 underline font-normal transition text-[10px]"
              >
                Reset
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-2 bg-indigo-50/50 text-indigo-700 border border-indigo-100 px-4 py-1.5 rounded-full text-xs font-semibold shadow-inner">
              <HelpCircle className="w-3.5 h-3.5" />
              <span>Mock Profile Preview</span>
            </div>
          )}
        </div>
      </div>

      {/* Primary Columns Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        
        {/* Left Side: Score & Skills badging (4 cols) */}
        <div className="lg:col-span-4 space-y-6">
          
          {/* Overall Match Score Card */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm text-center space-y-2">
            <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">Overall Match Score</h3>
            <div className="text-5xl font-black text-indigo-600 font-sans">
              {overallScorePercent}%
            </div>
            <p className="text-xs text-slate-400">Weighted comparison of semantic similarity and hard requirements match.</p>
          </div>

          {/* Core Strengths Section */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-2">
              <Award className="w-5 h-5 text-emerald-500" />
              <span>Your Key Strengths ({matchedSkills.length})</span>
            </h3>
            <p className="text-xs text-slate-400 leading-snug">Skills matched directly or satisfied via mapped concept taxonomies:</p>
            <div className="flex flex-wrap gap-2 pt-1">
              {matchedSkills.map((skill, idx) => (
                <span key={idx} className="flex items-center space-x-1 px-3 py-1 bg-emerald-50 border border-emerald-100 rounded-full text-xs font-semibold text-emerald-700 transition hover:scale-[1.03]">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
                  <span>{skill}</span>
                </span>
              ))}
              {matchedSkills.length === 0 && (
                <p className="text-xs text-slate-400 italic">No strengths identified.</p>
              )}
            </div>
          </div>

          {/* Recommended Growth Areas Section */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-2">
              <BookOpen className="w-5 h-5 text-amber-500" />
              <span>Upskilling Roadmap ({missingSkills.length})</span>
            </h3>
            <p className="text-xs text-slate-400 leading-snug">Adding these skills will significantly raise your target fit eligibility:</p>
            <div className="flex flex-wrap gap-2 pt-1">
              {missingSkills.map((skill, idx) => (
                <span key={idx} className="flex items-center space-x-1 px-3 py-1 bg-amber-50 border border-amber-100 rounded-full text-xs font-semibold text-amber-700 transition hover:scale-[1.03]">
                  <ArrowRight className="w-3.5 h-3.5 text-amber-500 flex-shrink-0" />
                  <span>{skill}</span>
                </span>
              ))}
              {missingSkills.length === 0 && (
                <p className="text-xs text-slate-400 italic">Excellent! No missing skills detected.</p>
              )}
            </div>
          </div>

          {/* Resume Improvement Checklist */}
          {resumeFeedback.length > 0 && (
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-4">
              <h3 className="text-sm font-bold text-slate-800 uppercase tracking-wider flex items-center space-x-2">
                <FileText className="w-5 h-5 text-indigo-500" />
                <span>Resume Feedback Checks</span>
              </h3>
              <p className="text-xs text-slate-400 leading-snug">Actionable formatting and content improvements for your resume:</p>
              <div className="space-y-2 pt-1">
                {resumeFeedback.map((fb, idx) => (
                  <div key={idx} className="flex items-start space-x-2 bg-slate-50 border border-slate-100 rounded-lg p-2.5">
                    {fb.status === 'pass' ? (
                      <CheckCircle className="w-4 h-4 text-emerald-500 flex-shrink-0 mt-0.5" />
                    ) : (
                      <AlertCircle className="w-4 h-4 text-amber-500 flex-shrink-0 mt-0.5" />
                    )}
                    <span className="text-xs text-slate-600 font-semibold">{fb.label}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* Right Side: Career Growth Plan & Suggested Learning (8 cols) */}
        <div className="lg:col-span-8 space-y-6">
          
          {/* AI Coaching Feedback Report */}
          <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm relative">
            <div className="absolute top-0 right-0 p-4 text-indigo-500/10">
              <Sparkles className="w-12 h-12" />
            </div>
            
            <h3 className="text-lg font-bold text-slate-800 border-b border-slate-100 pb-3 mb-4 flex items-center space-x-2">
              <Sparkles className="w-5 h-5 text-indigo-500" />
              <span>Career Growth Plan</span>
            </h3>
            
            <div className="prose max-w-none text-slate-700 text-sm">
              {renderMarkdown(data.feedback_report)}
            </div>
          </div>

          {/* Learning Roadmap Mappings */}
          {learningCurve.length > 0 && (
            <div className="bg-white border border-slate-200 rounded-2xl p-6 shadow-sm space-y-6">
              <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider">Suggested Learning & Projects Transition Path</h3>
              <div className="space-y-4">
                {learningCurve.map((item, idx) => (
                  <div key={idx} className="border border-slate-100 rounded-xl p-4 bg-slate-50/40 hover:bg-slate-50 transition shadow-sm space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-slate-800">{item.skill}</span>
                      <span className="text-[10px] font-bold uppercase bg-indigo-50 text-indigo-600 border border-indigo-100 px-2 py-0.5 rounded">
                        Ramp Difficulty: {item.difficulty}
                      </span>
                    </div>
                    <p className="text-xs text-slate-600 font-medium leading-relaxed">{item.reason}</p>
                    <div className="flex items-center space-x-2 pt-2 border-t border-slate-100 text-[10px] text-slate-400 font-bold">
                      <Play className="w-3 h-3 text-indigo-500" />
                      <span>Suggested Action: Research concepts, build hands-on sandbox code repositories</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

      </div>
    </div>
  );
};

export default CandidatePortal;
