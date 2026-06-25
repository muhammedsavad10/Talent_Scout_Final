import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import RecruiterDashboard from './pages/RecruiterDashboard';
import CandidatePortal from './pages/CandidatePortal';
import { checkHealth } from './services/api';
import { Briefcase, Activity } from 'lucide-react';

function App() {
  const [dbStatus, setDbStatus] = useState('Checking...');

  useEffect(() => {
    checkHealth()
      .then(data => setDbStatus(data.status === 'healthy' ? 'Online' : 'Degraded'))
      .catch(() => setDbStatus('Offline'));
  }, []);

  return (
    <Router>
      <div className="min-h-screen">
        {/* Enterprise Navigation Bar */}
        <nav className="bg-white border-b border-slate-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center space-x-8">
                <div className="flex items-center space-x-2">
                  <Briefcase className="w-6 h-6 text-brand-500" />
                  <span className="text-xl font-bold text-slate-900">TalentScout</span>
                </div>
                <div className="hidden md:flex space-x-4">
                  <Link to="/" className="text-slate-600 hover:text-brand-500 px-3 py-2 font-medium">Recruiter View</Link>
                  <Link to="/candidate" className="text-slate-600 hover:text-brand-500 px-3 py-2 font-medium">Candidate View</Link>
                </div>
              </div>
              <div className="flex items-center">
                <div className="flex items-center space-x-2 text-sm text-slate-500 bg-slate-50 px-3 py-1 rounded-full border border-slate-200">
                  <Activity className={`w-4 h-4 ${dbStatus === 'Online' ? 'text-green-500' : 'text-red-500'}`} />
                  <span>API: {dbStatus}</span>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Route Configuration */}
        <main>
          <Routes>
            <Route path="/" element={<RecruiterDashboard />} />
            <Route path="/candidate" element={<CandidatePortal />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
