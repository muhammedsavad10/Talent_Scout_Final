import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App.tsx';
import { sentry } from '@/shared/utils';

// Initialize logging and tracking monitors
sentry.init({
  dsn: 'https://mock-dsn@sentry.io/mock-project-id',
  environment: import.meta.env.MODE || 'production',
  tracesSampleRate: 0.1,
});

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
