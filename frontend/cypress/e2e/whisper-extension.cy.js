// cypress/e2e/whisper-extension.cy.js

describe('Whisper Extension Integration', () => {
    beforeEach(() => {
        // Login as user
        cy.login('user@example.com', 'password123');

        // We can't directly test the Chrome extension, but we can test the web interface
        // that interacts with the extension
        cy.visit('/extension-config');
    });

    it('should display extension connection status', () => {
        // Check for extension status indicator
        cy.get('[data-testid="extension-status"]').should('be.visible');

        // Depending on the current state, show connected or disconnected
        cy.get('[data-testid="extension-status"]').then(($status) => {
            // We'll assert it's either connected or disconnected
            const text = $status.text().toLowerCase();
            expect(text).to.match(/connected|disconnected/);
        });
    });

    it('should allow configuring extension settings', () => {
        // Check for settings form
        cy.get('[data-testid="extension-settings-form"]').should('be.visible');

        // Toggle a setting
        cy.get('[data-testid="auto-suggest-toggle"]').click();

        // Save settings
        cy.get('[data-testid="save-settings-button"]').click();

        // Verify success message
        cy.contains('Settings saved').should('be.visible');

        // Reload the page and verify persistence
        cy.reload();

        // Check if the toggle state persisted
        cy.get('[data-testid="auto-suggest-toggle"]').should('be.checked');
    });

    it('should display whisper history from extension', () => {
        // Navigate to history tab
        cy.contains('Whisper History').click();

        // Check for history list
        cy.get('[data-testid="whisper-history-list"]').should('be.visible');

        // Should show at least one history item (or empty state)
        cy.get('[data-testid="whisper-history-list"]').then(($list) => {
            if ($list.find('[data-testid="history-item"]').length > 0) {
                // Has history items
                cy.get('[data-testid="history-item"]').first().should('be.visible');
            } else {
                // Empty state
                cy.contains('No whisper history found').should('be.visible');
            }
        });
    });

    it('should allow testing whisper panel in sandbox mode', () => {
        // Navigate to test tab
        cy.contains('Test Whisper').click();

        // Should show sandbox environment
        cy.get('[data-testid="whisper-sandbox"]').should('be.visible');

        // Type a test message
        cy.get('[data-testid="sandbox-input"]').type('This is a test message');

        // Click send button
        cy.get('[data-testid="sandbox-send-button"]').click();

        // Should show loading state
        cy.get('[data-testid="loading-indicator"]').should('be.visible');

        // Wait for response
        cy.get('[data-testid="whisper-response"]', { timeout: 10000 }).should('be.visible');

        // Verify response contains meaningful content
        cy.get('[data-testid="whisper-response"]').invoke('text').should('have.length.gt', 20);
    });

    it('should show analytics for whisper usage', () => {
        // Navigate to analytics tab
        cy.contains('Usage Analytics').click();

        // Check for analytics section
        cy.get('[data-testid="whisper-analytics"]').should('be.visible');

        // Verify usage metrics are displayed
        cy.contains('Suggestions Received').should('be.visible');
        cy.contains('Suggestions Applied').should('be.visible');
        cy.contains('Average Response Time').should('be.visible');

        // Check for usage charts
        cy.get('[data-testid="usage-chart"]').should('be.visible');
    });
});
