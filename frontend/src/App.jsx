import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Navigate } from 'react-router-dom';
import RecruiterDashboard from './pages/RecruiterDashboard';
import CandidatePortal from './pages/CandidatePortal';
import { checkHealth } from './services/api';
import { Briefcase, Activity, Shield, Users } from 'lucide-react';

const DEMO_MODE = import.meta.env.VITE_DEMO_MODE !== 'false'; // Enables the Role Switcher dropdown dynamically

function App() {
  const [dbStatus, setDbStatus] = useState('Checking...');
  const [activeRole, setActiveRole] = useState(() => {
    return localStorage.getItem('activeRole') || 'Recruiter';
  });

  useEffect(() => {
    checkHealth()
      .then(data => setDbStatus(data.status === 'healthy' ? 'Online' : 'Degraded'))
      .catch(() => setDbStatus('Offline'));
  }, []);

  const handleRoleChange = (e) => {
    const newRole = e.target.value;
    setActiveRole(newRole);
    localStorage.setItem('activeRole', newRole);
  };

  return (
    <Router>
      <div className="min-h-screen bg-slate-50 text-slate-800 antialiased font-sans">
        {/* Enterprise Navigation Bar */}
        <nav className="bg-white border-b border-slate-200 sticky top-0 z-50 shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex items-center space-x-8">
                <div className="flex items-center space-x-2">
                  <div className="p-2 bg-indigo-600 rounded-lg text-white">
                    <Briefcase className="w-5 h-5" />
                  </div>
                  <span className="text-xl font-bold tracking-tight text-slate-900">TalentScout</span>
                </div>
                
                {/* Navigation Links based on RBAC */}
                <div className="hidden md:flex space-x-1">
                  {activeRole !== 'Candidate' && (
                    <Link 
                      to="/" 
                      className="text-slate-600 hover:text-indigo-600 hover:bg-slate-50 px-4 py-2 rounded-lg font-medium transition-colors"
                    >
                      Recruiter View
                    </Link>
                  )}
                  <Link 
                    to="/candidate" 
                    className="text-slate-600 hover:text-indigo-600 hover:bg-slate-50 px-4 py-2 rounded-lg font-medium transition-colors"
                  >
                    Candidate View
                  </Link>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                {/* Demo Role Switcher Dropdown */}
                {DEMO_MODE && (
                  <div className="flex items-center space-x-2 bg-slate-100 rounded-xl px-3 py-1.5 border border-slate-200">
                    <Shield className="w-4 h-4 text-indigo-600" />
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider hidden sm:inline">Role:</span>
                    <select
                      value={activeRole}
                      onChange={handleRoleChange}
                      className="bg-transparent text-sm font-bold text-slate-700 focus:outline-none cursor-pointer pr-2"
                    >
                      <option value="Admin">Admin</option>
                      <option value="Recruiter">Recruiter</option>
                      <option value="Hiring Manager">Hiring Manager</option>
                      <option value="Interviewer">Interviewer</option>
                      <option value="Candidate">Candidate</option>
                    </select>
                  </div>
                )}

                {/* API Status Badge */}
                <div className="flex items-center space-x-2 text-sm text-slate-500 bg-slate-50 px-3 py-1.5 rounded-xl border border-slate-200">
                  <Activity className={`w-4 h-4 ${dbStatus === 'Online' ? 'text-green-500 animate-pulse' : 'text-red-500'}`} />
                  <span className="font-medium">API: {dbStatus}</span>
                </div>
              </div>
            </div>
          </div>
        </nav>

        {/* Route Configuration */}
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <Routes>
            <Route 
              path="/" 
              element={activeRole === 'Candidate' ? <Navigate to="/candidate" replace /> : <RecruiterDashboard activeRole={activeRole} />} 
            />
            <Route path="/candidate" element={<CandidatePortal activeRole={activeRole} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
