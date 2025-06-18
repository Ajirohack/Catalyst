// cypress/e2e/performance-tests.cy.js
// E2E tests that focus on performance metrics

describe('Performance Tests', () => {
    beforeEach(() => {
        // Clear all performance marks and measures
        performance.clearMarks();
        performance.clearMeasures();

        // Login programmatically for faster tests
        cy.programmaticLogin('test@example.com', 'user');
    });

    it('measures dashboard loading performance', () => {
        // Start performance measurement
        performance.mark('dashboard-start');

        // Visit the dashboard
        cy.visit('/dashboard');

        // Wait for the dashboard to fully load
        cy.get('[data-testid="dashboard-loaded"]').should('exist');

        // End performance measurement
        performance.mark('dashboard-end');
        performance.measure('dashboard-load-time', 'dashboard-start', 'dashboard-end');

        // Get the performance measure
        const dashboardLoadTime = performance.getEntriesByName('dashboard-load-time')[0].duration;

        // Log the performance measurement
        cy.log(`Dashboard load time: ${dashboardLoadTime.toFixed(2)}ms`);

        // Assert that dashboard loads in under 3 seconds
        expect(dashboardLoadTime).to.be.lessThan(3000);
    });

    it('measures project list rendering performance', () => {
        // Create multiple projects first (mock the API)
        cy.intercept('GET', '**/api/projects', {
            statusCode: 200,
            body: Array(50).fill(0).map((_, i) => ({
                id: i + 1,
                name: `Performance Test Project ${i + 1}`,
                description: `Project for performance testing ${i + 1}`,
                status: i % 3 === 0 ? 'active' : i % 3 === 1 ? 'completed' : 'archived',
                createdAt: new Date().toISOString(),
                updatedAt: new Date().toISOString(),
            })),
        }).as('getProjects');

        // Start performance measurement
        performance.mark('project-list-start');

        // Visit projects page
        cy.visit('/projects');

        // Wait for all projects to load
        cy.wait('@getProjects');
        cy.get('[data-testid="project-card"]').should('have.length.at.least', 10);

        // End performance measurement
        performance.mark('project-list-end');
        performance.measure('project-list-render-time', 'project-list-start', 'project-list-end');

        // Get the performance measure
        const projectListRenderTime = performance.getEntriesByName('project-list-render-time')[0].duration;

        // Log the performance measurement
        cy.log(`Project list render time: ${projectListRenderTime.toFixed(2)}ms`);

        // Assert that project list renders in under 2 seconds
        expect(projectListRenderTime).to.be.lessThan(2000);
    });

    it('measures whisper suggestion performance', () => {
        // Mock the whisper API with a delayed response
        cy.intercept('POST', '**/api/whisper/suggest', {
            statusCode: 200,
            body: {
                suggestions: [
                    'This is a test suggestion',
                    'This is another suggestion',
                    'And here is a third suggestion',
                ],
                context: 'Test context',
                messageId: 'perf-test-123',
            },
            delay: 200, // Add a delay to simulate processing time
        }).as('whisperSuggestion');

        // Visit the test page for whisper extension
        cy.visit('/test-extension');

        // Start performance measurement
        performance.mark('whisper-start');

        // Trigger the whisper panel
        cy.get('[data-testid="extension-trigger-button"]').click();

        // Wait for suggestions to load
        cy.wait('@whisperSuggestion');
        cy.get('[data-testid="suggestion-item"]').should('have.length', 3);

        // End performance measurement
        performance.mark('whisper-end');
        performance.measure('whisper-response-time', 'whisper-start', 'whisper-end');

        // Get the performance measure
        const whisperResponseTime = performance.getEntriesByName('whisper-response-time')[0].duration;

        // Log the performance measurement
        cy.log(`Whisper response time: ${whisperResponseTime.toFixed(2)}ms`);

        // Assert that whisper response time is under 2 seconds (including the 200ms delay)
        expect(whisperResponseTime).to.be.lessThan(2000);
    });

    it('measures analysis report generation performance', () => {
        // Mock the analysis API with a delayed response
        cy.intercept('GET', '**/api/projects/*/analyses/*', {
            statusCode: 200,
            body: {
                id: 1,
                name: 'Performance Test Analysis',
                status: 'completed',
                createdAt: new Date().toISOString(),
                results: {
                    sentimentScore: 0.75,
                    toneAnalysis: {
                        positive: 65,
                        neutral: 25,
                        negative: 10,
                    },
                    keyThemes: ['communication', 'trust', 'respect'],
                    suggestedResponses: [
                        'I understand how you feel about that.',
                        'Let me share my perspective on this.',
                        'I appreciate your honesty about this issue.',
                    ],
                },
            },
            delay: 300, // Add a delay to simulate processing time
        }).as('getAnalysis');

        // Start performance measurement
        performance.mark('analysis-start');

        // Visit the analysis report page
        cy.visit('/projects/1/analyses/1');

        // Wait for the analysis report to fully load
        cy.wait('@getAnalysis');
        cy.get('[data-testid="analysis-complete"]').should('exist');

        // End performance measurement
        performance.mark('analysis-end');
        performance.measure('analysis-load-time', 'analysis-start', 'analysis-end');

        // Get the performance measure
        const analysisLoadTime = performance.getEntriesByName('analysis-load-time')[0].duration;

        // Log the performance measurement
        cy.log(`Analysis report load time: ${analysisLoadTime.toFixed(2)}ms`);

        // Assert that analysis report loads in under 3 seconds
        expect(analysisLoadTime).to.be.lessThan(3000);
    });

    it('measures memory usage during intensive operations', () => {
        // Mock the API to return a large dataset
        cy.intercept('GET', '**/api/analytics/dashboard', {
            statusCode: 200,
            body: {
                userGrowth: Array(365).fill(0).map((_, i) => ({
                    date: new Date(2025, 0, i + 1).toISOString().split('T')[0],
                    count: Math.floor(Math.random() * 100) + 10,
                })),
                projectMetrics: {
                    total: 1500,
                    active: 750,
                    completed: 500,
                    abandoned: 250,
                },
                platformUsage: [
                    { platform: 'WhatsApp', count: 450 },
                    { platform: 'Messenger', count: 300 },
                    { platform: 'Slack', count: 250 },
                    { platform: 'Teams', count: 200 },
                    { platform: 'Discord', count: 150 },
                    { platform: 'Others', count: 150 },
                ],
                engagementMetrics: Array(365).fill(0).map((_, i) => ({
                    date: new Date(2025, 0, i + 1).toISOString().split('T')[0],
                    messages: Math.floor(Math.random() * 1000) + 100,
                    suggestions: Math.floor(Math.random() * 200) + 20,
                })),
                userMetrics: {
                    messagesSent: 125000,
                    messagesSentGrowth: 15,
                    suggestionsReceived: 32000,
                    suggestionsReceivedGrowth: 8,
                    avgResponseTime: 1.5,
                    avgResponseTimeGrowth: -5,
                },
            },
        }).as('getAnalytics');

        // Login as admin
        cy.programmaticLogin('admin@example.com', 'admin');

        // Record memory usage before loading analytics
        cy.window().then((win) => {
            const memoryBefore = (win.performance.memory?.usedJSHeapSize || 0) / (1024 * 1024);
            cy.log(`Memory usage before: ${memoryBefore.toFixed(2)} MB`);
        });

        // Visit the analytics dashboard with large dataset
        cy.visit('/admin/analytics');

        // Wait for analytics to load
        cy.wait('@getAnalytics');
        cy.get('[data-testid="analytics-loaded"]').should('exist');

        // Check memory usage after
        cy.window().then((win) => {
            const memoryAfter = (win.performance.memory?.usedJSHeapSize || 0) / (1024 * 1024);
            cy.log(`Memory usage after: ${memoryAfter.toFixed(2)} MB`);

            // If performance.memory is available (Chrome only)
            if (win.performance.memory) {
                const memoryDiff = memoryAfter - memoryBefore;
                cy.log(`Memory increase: ${memoryDiff.toFixed(2)} MB`);

                // Assert that memory increase is reasonable (less than 50MB)
                expect(memoryDiff).to.be.lessThan(50);
            }
        });
    });
});
