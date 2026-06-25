import React from 'react';
import { Target } from 'lucide-react';

const CandidatePortal = () => {
  return (
    <div className="max-w-4xl mx-auto p-8">
      <div className="flex items-center space-x-3 mb-8">
        <Target className="w-8 h-8 text-brand-500" />
        <h1 className="text-3xl font-bold text-slate-900">Career Strategy Portal</h1>
      </div>
      <div className="glass-card text-center py-16">
        <h2 className="text-2xl font-semibold text-slate-800 mb-2">Evaluate Your Fit</h2>
        <p className="text-slate-600 mb-8">Upload your resume and the target Job Description to receive your XAI Gap Analysis.</p>
        <button className="btn-primary">Start Analysis</button>
      </div>
    </div>
  );
};

export default CandidatePortal;
