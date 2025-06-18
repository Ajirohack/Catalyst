// cypress/e2e/analytics-dashboard.cy.js

describe('Analytics Dashboard', () => {
    beforeEach(() => {
        // Login as admin
        cy.login('admin@example.com', 'adminpassword');

        // Visit analytics dashboard
        cy.visit('/admin/analytics');
    });

    it('should display all analytics charts and metrics', () => {
        // Verify page title
        cy.contains('Analytics Dashboard').should('be.visible');

        // Check for key metrics sections
        cy.get('[data-testid="user-growth-chart"]').should('be.visible');
        cy.get('[data-testid="project-metrics"]').should('be.visible');
        cy.get('[data-testid="platform-usage-chart"]').should('be.visible');
        cy.get('[data-testid="engagement-metrics"]').should('be.visible');

        // Verify data is loaded in charts (check for specific metric values)
        cy.contains('Total Projects').next().should('not.be.empty');
        cy.contains('Active Projects').next().should('not.be.empty');
    });

    it('should filter analytics by date range', () => {
        // Select date range filter
        cy.get('[data-testid="date-range-select"]').click();
        cy.contains('Last 30 Days').click();

        // Verify loading state appears
        cy.get('[data-testid="loading-indicator"]').should('be.visible');

        // Wait for data to load
        cy.get('[data-testid="loading-indicator"]').should('not.exist');

        // Verify filtered data is displayed
        cy.get('[data-testid="date-range-display"]').should('contain', '30 Days');
    });

    it('should allow downloading analytics reports', () => {
        // Click export button
        cy.get('[data-testid="export-button"]').click();

        // Select export format
        cy.contains('Export as CSV').click();

        // Verify download starts (this is tricky in Cypress, we'll check for the API call)
        cy.intercept('GET', '/api/analytics/export?format=csv').as('exportRequest');
        cy.wait('@exportRequest').its('response.statusCode').should('eq', 200);
    });

    it('should display user activity details when clicking on user metrics', () => {
        // Click on user activity section
        cy.get('[data-testid="user-activity-section"]').click();

        // Verify detailed view opens
        cy.get('[data-testid="user-activity-detail"]').should('be.visible');

        // Check for user activity table
        cy.contains('User Activity Log').should('be.visible');
        cy.get('table').contains('th', 'User').should('be.visible');
        cy.get('table').contains('th', 'Action').should('be.visible');
        cy.get('table').contains('th', 'Timestamp').should('be.visible');
    });

    it('should update real-time metrics automatically', () => {
        // Get initial values
        cy.get('[data-testid="active-users-count"]').invoke('text').as('initialActiveUsers');

        // Mock a change in active users
        cy.intercept('GET', '/api/analytics/real-time', {
            body: {
                activeUsers: 42,
                activeSessions: 38,
                requestsPerMinute: 120
            }
        }).as('realTimeUpdate');

        // Wait for auto-refresh (typically 30s, but we'll force it)
        cy.get('[data-testid="refresh-button"]').click();

        // Verify new value is different
        cy.get('[data-testid="active-users-count"]').invoke('text').should('eq', '42');
    });
});

// Add custom command for admin login if needed
Cypress.Commands.add('adminLogin', () => {
    cy.login('admin@example.com', 'adminpassword');
});
