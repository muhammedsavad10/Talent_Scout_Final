import React from 'react';
import { Users, UploadCloud } from 'lucide-react';

const RecruiterDashboard = () => {
  return (
    <div className="max-w-7xl mx-auto p-8">
      <div className="flex items-center space-x-3 mb-8">
        <Users className="w-8 h-8 text-brand-500" />
        <h1 className="text-3xl font-bold text-slate-900">Recruiter Command Center</h1>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card col-span-2">
          <h2 className="text-xl font-semibold mb-4">Batch Processing</h2>
          <div className="border-2 border-dashed border-slate-300 rounded-lg p-12 text-center bg-slate-50 hover:bg-slate-100 transition">
            <UploadCloud className="w-12 h-12 text-slate-400 mx-auto mb-4" />
            <p className="text-slate-600">Drag & drop PDF resumes here, or click to browse</p>
            <button className="mt-4 btn-primary">Select Files</button>
          </div>
        </div>
        <div className="glass-card">
          <h2 className="text-xl font-semibold mb-4">Job Description</h2>
          <textarea 
            className="w-full h-48 p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
            placeholder="Paste technical requirements here..."
          ></textarea>
        </div>
      </div>
    </div>
  );
};

export default RecruiterDashboard;
