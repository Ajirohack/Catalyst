// src/mocks/browser.js
// Sets up MSW in the browser for development mock API
import { setupWorker } from 'msw';
import { handlers } from './handlers';

// This configures a Service Worker with the given request handlers
export const worker = setupWorker(...handlers);
