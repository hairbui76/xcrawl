// Browser entry point. TanStack Query is installed at the root so the cards that add read
// models (ADR-0011: "TanStack Query cho read model") do not each create their own client.

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';

import App from './App';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // The app is single-user and mostly read-only; refetching on every window focus
      // would produce noise, not freshness.
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

const container = document.getElementById('root');
if (!container) {
  throw new Error('#root is missing from index.html');
}

createRoot(container).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
);
