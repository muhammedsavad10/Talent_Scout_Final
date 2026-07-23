import { QueryProvider, ThemeProvider, RouterProvider } from '@/app/providers';
import { AppRouter } from '@/app/router';
import { ErrorBoundary } from '@/shared/ui';

function App() {
  return (
    <ErrorBoundary>
      <QueryProvider>
        <ThemeProvider>
          <RouterProvider>
            <AppRouter />
          </RouterProvider>
        </ThemeProvider>
      </QueryProvider>
    </ErrorBoundary>
  );
}

export default App;
