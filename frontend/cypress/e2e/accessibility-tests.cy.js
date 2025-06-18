// cypress/e2e/accessibility-tests.cy.js
// E2E tests focused on accessibility

describe('Accessibility Tests', () => {
    beforeEach(() => {
        // Register custom command that injects and runs axe-core
        cy.injectAxe();
    });

    it('checks login page accessibility', () => {
        cy.visit('/login');
        cy.checkA11y(null, {
            includedImpacts: ['critical', 'serious', 'moderate'],
        });
    });

    it('checks registration page accessibility', () => {
        cy.visit('/register');
        cy.checkA11y(null, {
            includedImpacts: ['critical', 'serious', 'moderate'],
        });
    });

    it('checks dashboard accessibility', () => {
        cy.programmaticLogin('test@example.com', 'user');
        cy.visit('/dashboard');
        cy.checkA11y(null, {
            includedImpacts: ['critical', 'serious', 'moderate'],
        });
    });

    it('checks project creation form accessibility', () => {
        cy.programmaticLogin('test@example.com', 'user');
        cy.visit('/projects/new');
        cy.checkA11y(null, {
            includedImpacts: ['critical', 'serious', 'moderate'],
        });
    });

    it('checks project detail page accessibility', () => {
        cy.programmaticLogin('test@example.com', 'user');
        cy.visit('/projects/1');
        cy.checkA11y(null, {
            includedImpacts: ['critical', 'serious', 'moderate'],
        });
    });

    it('checks analysis report accessibility', () => {
        cy.programmaticLogin('test@example.com', 'user');
        cy.visit('/projects/1/analyses/1');
        cy.checkA11y(null, {
            includedImpacts: ['critical', 'serious', 'moderate'],
        });
    });

    it('checks admin dashboard accessibility', () => {
        cy.programmaticLogin('admin@example.com', 'admin');
        cy.visit('/admin/dashboard');
        cy.checkA11y(null, {
            includedImpacts: ['critical', 'serious', 'moderate'],
        });
    });

    it('checks analytics dashboard accessibility', () => {
        cy.programmaticLogin('admin@example.com', 'admin');
        cy.visit('/admin/analytics');
        cy.checkA11y(null, {
            includedImpacts: ['critical', 'serious', 'moderate'],
        });
    });

    it('checks user management page accessibility', () => {
        cy.programmaticLogin('admin@example.com', 'admin');
        cy.visit('/admin/users');
        cy.checkA11y(null, {
            includedImpacts: ['critical', 'serious', 'moderate'],
        });
    });

    it('checks settings page accessibility', () => {
        cy.programmaticLogin('test@example.com', 'user');
        cy.visit('/settings');
        cy.checkA11y(null, {
            includedImpacts: ['critical', 'serious', 'moderate'],
        });
    });

    it('checks modal accessibility', () => {
        cy.programmaticLogin('test@example.com', 'user');
        cy.visit('/projects/1');

        // Open a modal
        cy.get('[data-testid="new-analysis-button"]').click();

        // Check modal accessibility
        cy.checkA11y('[data-testid="modal"]', {
            includedImpacts: ['critical', 'serious', 'moderate'],
        });
    });

    it('checks keyboard navigation', () => {
        cy.visit('/login');

        // Focus on email field
        cy.get('input[type="email"]').focus();

        // Tab to password field
        cy.tab();
        cy.focused().should('have.attr', 'type', 'password');

        // Tab to submit button
        cy.tab();
        cy.focused().should('have.attr', 'type', 'submit');

        // Tab to forgot password link
        cy.tab();
        cy.focused().contains(/forgot password/i);
    });

    it('checks screen reader text', () => {
        cy.visit('/login');

        // Check for proper labels and aria attributes
        cy.get('input[type="email"]').should('have.attr', 'aria-label');
        cy.get('input[type="password"]').should('have.attr', 'aria-label');

        // Check for appropriate heading structure
        cy.get('h1').should('exist');
    });

    it('checks color contrast ratios', () => {
        cy.visit('/login');

        // Run axe with focus on color contrast
        cy.checkA11y(null, {
            includedImpacts: ['serious'],
            rules: {
                'color-contrast': { enabled: true }
            }
        });
    });

    it('checks dark mode accessibility', () => {
        cy.programmaticLogin('test@example.com', 'user');
        cy.visit('/dashboard');

        // Toggle to dark mode
        cy.toggleTheme();

        // Check accessibility in dark mode
        cy.checkA11y(null, {
            includedImpacts: ['critical', 'serious', 'moderate'],
        });
    });
});
