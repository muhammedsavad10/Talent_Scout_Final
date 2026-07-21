import React from 'react';
import { ThemeProvider } from '../providers/ThemeProvider';
import { ToastProvider } from '../providers/ToastProvider';

/**
 * AppProviders - Centralized provider composition.
 *
 * All context providers wrap the application here.
 * Order matters: outermost providers are available to inner ones.
 * Future providers (QueryProvider, AuthProvider) slot in here.
 */
export function AppProviders({ children }) {
  return (
    <ThemeProvider>
      <ToastProvider>
        {children}
      </ToastProvider>
    </ThemeProvider>
  );
}

export default AppProviders;
