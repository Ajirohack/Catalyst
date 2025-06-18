// src/config/test.config.js
// Configuration for different test environments

export const testConfig = {
    // API endpoints for different environments
    api: {
        baseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000/api',
        timeout: 5000,
    },

    // Test data configuration
    testData: {
        defaultUser: {
            email: 'test@example.com',
            password: 'password123',
        },
        adminUser: {
            email: 'admin@example.com',
            password: 'adminpassword',
        },
    },

    // Performance test thresholds
    performance: {
        pageLoadTime: 3000, // 3 seconds
        apiResponseTime: 2000, // 2 seconds
        renderTime: 1000, // 1 second
    },

    // Accessibility test configuration
    accessibility: {
        includedImpacts: ['critical', 'serious', 'moderate'],
        rules: {
            'color-contrast': { enabled: true },
            'keyboard-navigation': { enabled: true },
            'focus-management': { enabled: true },
        },
    },

    // Mock service worker configuration
    msw: {
        onUnhandledRequest: 'warn',
        delayResponse: 100, // Add realistic delay to API responses
    },

    // Feature flags for testing
    features: {
        enableNewDesign: true,
        enableAnalytics: true,
        enableWhisperPanel: true,
        enableRealTimeUpdates: false, // Disable for testing stability
    },

    // Database configuration for integration tests
    database: {
        testDb: 'catalyst_test',
        seedData: true,
        resetBetweenTests: true,
    },

    // External service mocks
    externalServices: {
        emailService: {
            mock: true,
            provider: 'mock',
        },
        smsService: {
            mock: true,
            provider: 'mock',
        },
        analyticsService: {
            mock: true,
            trackEvents: false,
        },
    },
};

// Environment-specific overrides
if (process.env.NODE_ENV === 'test') {
    testConfig.api.baseUrl = 'http://localhost:8000/api';
    testConfig.msw.onUnhandledRequest = 'error';
}

if (process.env.CI === 'true') {
    testConfig.performance.pageLoadTime = 5000; // More lenient on CI
    testConfig.performance.apiResponseTime = 3000;
    testConfig.msw.delayResponse = 0; // No delay on CI for speed
}

export default testConfig;
