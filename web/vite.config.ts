/// <reference types="vitest/config" />
import react from '@vitejs/plugin-react';
import { defineConfig } from 'vite';

// Vite + React 18 + TypeScript (ADR-0011). No proxy and no API base URL is configured
// here: the owner API's origin is deployment configuration (contracts/ops/deployment.md),
// not a build-time constant, so `web/src/lib/api.ts` resolves it at runtime.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}', 'tests/**/*.test.{ts,tsx}'],
    // No live jobs: nothing in this suite may touch X, an AI provider or Telegram
    // (ADR-0011, CI row).
    testTimeout: 10_000,
  },
});
