import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Configure the QueryClient with production defaults
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes stale time
      gcTime: 10 * 60 * 1000, // 10 minutes cache garbage collection
      refetchOnWindowFocus: false, // Prevent unnecessary requests on window focus shifts
      retry: (failureCount, error) => {
        // Only retry transient network/server failures up to 3 times
        if (failureCount >= 3) return false;
        
        const statusCode = (error as any)?.statusCode;
        if (statusCode && statusCode >= 500) {
          return true;
        }
        return false;
      },
      retryDelay: (attempt) => Math.min(attempt * 1000 * 2, 30000), // Exponential backoff
    },
  },
});

interface QueryProviderProps {
  children: React.ReactNode;
}

export const QueryProvider: React.FC<QueryProviderProps> = ({ children }) => {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};
export default QueryProvider;
