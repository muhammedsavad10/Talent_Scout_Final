import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { ROUTES } from '@/shared/constants/routes';
import { SidebarLayout } from '../layouts/SidebarLayout';

// Placeholder Pages
import { DashboardPage } from '@/features/dashboard/pages/DashboardPage';
import { UploadPage } from '@/features/upload/pages/UploadPage';
import { BatchPage } from '@/features/batch/pages/BatchPage';
import { CandidatePage } from '@/features/candidate/pages/CandidatePage';
import { SettingsPage } from '@/features/settings/pages/SettingsPage';

export const AppRouter: React.FC = () => {
  return (
    <Routes>
      <Route element={<SidebarLayout />}>
        <Route path={ROUTES.DASHBOARD} element={<DashboardPage />} />
        <Route path={ROUTES.UPLOAD} element={<UploadPage />} />
        <Route path={ROUTES.BATCH} element={<BatchPage />} />
        <Route path={ROUTES.CANDIDATE} element={<CandidatePage />} />
        <Route path={ROUTES.SETTINGS} element={<SettingsPage />} />
        {/* Redirect unknown routes */}
        <Route path="*" element={<Navigate to={ROUTES.DASHBOARD} replace />} />
      </Route>
    </Routes>
  );
};
export default AppRouter;
