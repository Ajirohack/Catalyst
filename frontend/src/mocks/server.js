// src/mocks/server.js
// Sets up MSW server for backend mocking
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// Setup requests interception using the given handlers
export const server = setupServer(...handlers);

// Start the server before all tests
beforeAll(() => server.listen());

// Reset any request handlers that we may add during the tests
afterEach(() => server.resetHandlers());

// Clean up after the tests are finished
afterAll(() => server.close());
