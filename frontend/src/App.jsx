import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import RecruiterDashboard from './pages/RecruiterDashboard';
import CandidatePortal from './pages/CandidatePortal';
import AppLayout from './components/layout/AppLayout';
import { checkHealth } from './services/api';

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
      <AppLayout
        activeRole={activeRole}
        onRoleChange={handleRoleChange}
        dbStatus={dbStatus}
      >
        <Routes>
          <Route
            path="/"
            element={
              activeRole === 'Candidate'
                ? <Navigate to="/candidate" replace />
                : <RecruiterDashboard activeRole={activeRole} />
            }
          />
          <Route
            path="/candidate"
            element={<CandidatePortal activeRole={activeRole} />}
          />
          {/* Backward compatibility: /dashboard redirects to / */}
          <Route path="/dashboard" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
