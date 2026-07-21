import React, { useState } from 'react';
import { UploadCloud, FileText, ChevronRight, AlertCircle } from 'lucide-react';
import { useEvaluation } from '../../evaluation/context/EvaluationContext';
import { batchService } from '../../../services/batchService';

export default function UploadWizard() {
  const { state, dispatch } = useEvaluation();
  const { jdText, jdSkills, files, isLoading, error } = state;
  const [dragActive, setDragActive] = useState(false);

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
        dispatch({ type: 'INGEST/ADD_FILES', payload: droppedFiles });
      }
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files) {
      const selected = Array.from(e.target.files).filter(f => f.name.endsWith('.pdf'));
      dispatch({ type: 'INGEST/ADD_FILES', payload: selected });
    }
  };

  const removeFile = (index) => {
    dispatch({ type: 'INGEST/REMOVE_FILE', payload: index });
  };

  const handleSubmitEvaluation = async (e) => {
    e.preventDefault();
    if (files.length === 0 || !jdText.trim()) return;

    dispatch({ type: 'INGEST/START_LOADING' });
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

      dispatch({ type: 'BATCH/SUBMIT_SUCCESS', payload: data });
      
      // Call standard dashboard flow for poll
      // (Dashboard page handles polling side effects via useEffect on activeBatchId)
    } catch (err) {
      console.error("❌ Upload Error:", err);
      dispatch({ type: 'INGEST/SET_ERROR', payload: err.message || "Batch upload failed." });
    }
  };

  return (
    <div className="bg-white dark:bg-surface-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-sm space-y-6">
      <div className="flex items-center space-x-2">
        <div className="p-2 bg-indigo-50 dark:bg-indigo-950/40 rounded-lg text-indigo-600 dark:text-indigo-400">
          <UploadCloud className="w-5 h-5" />
        </div>
        <h2 className="text-lg font-bold text-slate-800 dark:text-slate-100">1. Ingest Resume & Job Parameters</h2>
      </div>

      <form onSubmit={handleSubmitEvaluation} className="space-y-6">
        <div className="space-y-2">
          <label htmlFor="jd-text-area" className="block text-sm font-semibold text-slate-700 dark:text-slate-300">Job Description *</label>
          <textarea
            id="jd-text-area"
            className="w-full h-48 p-3 border border-slate-200 dark:border-slate-850 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none transition text-slate-700 dark:text-slate-200 bg-slate-50/30 dark:bg-surface-950 text-sm font-medium"
            placeholder="Paste core Job Description text here..."
            value={jdText}
            onChange={(e) => dispatch({ type: 'INGEST/SET_JD_TEXT', payload: e.target.value })}
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="jd-skills-input" className="block text-sm font-semibold text-slate-700 dark:text-slate-300">
            Skills Overrides <span className="text-slate-400 dark:text-slate-500 font-normal">(Optional, comma-separated)</span>
          </label>
          <input
            id="jd-skills-input"
            type="text"
            className="w-full p-3 border border-slate-200 dark:border-slate-850 rounded-xl focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 focus:outline-none transition text-slate-700 dark:text-slate-200 bg-slate-50/30 dark:bg-surface-950 text-sm"
            placeholder="e.g. AWS, Python, Kubernetes"
            value={jdSkills}
            onChange={(e) => dispatch({ type: 'INGEST/SET_JD_SKILLS', payload: e.target.value })}
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="resume-file-input" className="block text-sm font-semibold text-slate-700 dark:text-slate-300">Resume PDF *</label>
          <div
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition ${
              dragActive 
                ? 'border-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/20' 
                : 'border-slate-200 dark:border-slate-800 hover:bg-slate-50/80 dark:hover:bg-surface-950/80 bg-slate-50/10 dark:bg-surface-950/10'
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
              <UploadCloud className="w-10 h-10 text-slate-400 dark:text-slate-500 mx-auto" />
              {files.length > 0 ? (
                <div className="space-y-2">
                  <p className="text-sm font-bold text-slate-700 dark:text-slate-300">{files.length} file(s) selected</p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {files.map((f, idx) => (
                      <div key={idx} className="flex items-center space-x-1.5 bg-indigo-50 dark:bg-indigo-950/40 px-2 py-1 rounded-lg border border-indigo-100 dark:border-indigo-900/40">
                        <FileText className="w-3.5 h-3.5 text-indigo-600 dark:text-indigo-400" />
                        <span className="text-xs font-bold text-indigo-800 dark:text-indigo-300 max-w-[120px] truncate">{f.name}</span>
                        <button 
                          type="button" 
                          onClick={(e) => { e.preventDefault(); e.stopPropagation(); removeFile(idx); }}
                          className="text-indigo-400 dark:text-indigo-500 hover:text-indigo-600 dark:hover:text-indigo-300 ml-1"
                        >
                          &times;
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div>
                  <p className="text-sm font-medium text-slate-700 dark:text-slate-300">Drag and drop PDF resumes here, or click to browse</p>
                  <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Supports multiple standard PDFs up to 10MB each</p>
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
              ? 'bg-slate-300 dark:bg-slate-800 text-slate-500 dark:text-slate-600 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-700 text-white'
          }`}
        >
          <span>{files.length > 1 ? `Evaluate ${files.length} Candidates` : 'Evaluate Candidate'}</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      </form>

      {error && (
        <div className="flex items-start space-x-3 p-4 bg-rose-50 dark:bg-rose-950/30 border border-rose-100 dark:border-rose-900/30 rounded-xl text-rose-800 dark:text-rose-300 text-xs shadow-sm">
          <AlertCircle className="w-4 h-4 text-rose-500 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
