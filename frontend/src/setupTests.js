// jest-setup.js
import '@testing-library/jest-dom';

// Mock IntersectionObserver
const mockIntersectionObserver = jest.fn();
mockIntersectionObserver.mockReturnValue({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn()
});
window.IntersectionObserver = mockIntersectionObserver;

// Mock ResizeObserver
window.ResizeObserver = jest.fn().mockImplementation(() => ({
    observe: jest.fn(),
    unobserve: jest.fn(),
    disconnect: jest.fn()
}));

// Mock matchMedia
window.matchMedia = query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn()
});

// Mock localStorage
const localStorageMock = (() => {
    let store = {};
    return {
        getItem: jest.fn(key => store[key] || null),
        setItem: jest.fn((key, value) => {
            store[key] = value.toString();
        }),
        removeItem: jest.fn(key => {
            delete store[key];
        }),
        clear: jest.fn(() => {
            store = {};
        })
    };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

// Mock sessionStorage
const sessionStorageMock = (() => {
    let store = {};
    return {
        getItem: jest.fn(key => store[key] || null),
        setItem: jest.fn((key, value) => {
            store[key] = value.toString();
        }),
        removeItem: jest.fn(key => {
            delete store[key];
        }),
        clear: jest.fn(() => {
            store = {};
        })
    };
})();
Object.defineProperty(window, 'sessionStorage', { value: sessionStorageMock });

// Suppress React 18 console errors/warnings
const originalConsoleError = console.error;
console.error = (...args) => {
    if (/Warning.*not wrapped in act/.test(args[0])) {
        return;
    }
    originalConsoleError(...args);
};
