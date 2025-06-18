// cypress/support/commands.js

// Login command - reusable across tests
Cypress.Commands.add('login', (email, password) => {
    cy.session([email, password], () => {
        cy.visit('/login');
        cy.get('input[type="email"]').type(email);
        cy.get('input[type="password"]').type(password);
        cy.get('button[type="submit"]').click();
        cy.url().should('include', '/dashboard');
    });
});

// Admin login command
Cypress.Commands.add('adminLogin', () => {
    cy.login('admin@example.com', 'adminpassword');
});

// Programmatic login without UI (faster)
Cypress.Commands.add('programmaticLogin', (email = 'test@example.com', role = 'user') => {
    cy.window().then((window) => {
        window.localStorage.setItem('auth', JSON.stringify({
            token: 'fake-jwt-token',
            user: {
                id: role === 'admin' ? 2 : 1,
                name: role === 'admin' ? 'Admin User' : 'Test User',
                email,
                role,
            },
        }));
    });

    // Visit dashboard based on role
    cy.visit(role === 'admin' ? '/admin/dashboard' : '/dashboard');
});

// Create project command - reusable for tests that need a project
Cypress.Commands.add('createProject', (projectName = 'Test Project', description = 'Project for testing') => {
    cy.visit('/new-project');
    cy.get('[data-testid="project-name-input"]').type(projectName);
    cy.get('[data-testid="project-description-input"]').type(description);
    cy.get('[data-testid="project-type-select"]').click();
    cy.contains('Personal').click();
    cy.get('[data-testid="platform-select"]').click();
    cy.contains('WhatsApp').click();
    cy.get('[data-testid="create-project-button"]').click();
    cy.url().should('include', '/projects/');
    cy.contains(projectName).should('be.visible');
});

// Mock whisper API response
Cypress.Commands.add('mockWhisperResponse', (response = {
    suggestions: ['This is a test suggestion'],
    context: 'Test context',
    messageId: 'test-123'
}) => {
    cy.intercept('POST', '/api/whisper/suggest', {
        statusCode: 200,
        body: response,
        delay: 500 // Add a small delay to simulate API call
    }).as('whisperSuggestion');
});

// Verify toast notification
Cypress.Commands.add('verifyToast', (message) => {
    cy.get('[data-testid="toast-message"]').should('contain', message);
});

// Command to start a Whisper analysis for a project
Cypress.Commands.add('startAnalysis', (projectId = 1, name = 'E2E Test Analysis') => {
    cy.visit(`/projects/${projectId}`);
    cy.get('[data-testid="new-analysis-button"]').click();
    cy.get('[data-testid="analysis-name-input"]').type(name);
    cy.get('[data-testid="start-analysis-button"]').click();

    // Wait for the analysis to appear in the list
    cy.contains(name).should('be.visible');
});

// Command to intercept API requests with fixture
Cypress.Commands.add('mockApiCall', (method, url, fixture) => {
    cy.intercept(method, `**/api/${url}`, {
        fixture,
    }).as(url.replace(/\//g, '_'));
});

// Command to verify form validation errors
Cypress.Commands.add('assertFormError', (field, message) => {
    cy.get(`[data-testid="form-error-${field}"]`).should('contain', message);
});

// Command to test light/dark mode toggle
Cypress.Commands.add('toggleTheme', () => {
    cy.get('[data-testid="theme-toggle"]').click();
    // Verify the theme changed
    cy.get('html').should('have.attr', 'data-theme');
});

// Command to check accessibility issues (using axe-core)
Cypress.Commands.add('checkA11y', (context = null, options = null) => {
    cy.injectAxe();
    cy.checkA11y(context, options);
});

// Command to verify dashboard stats
Cypress.Commands.add('verifyDashboardStats', () => {
    cy.get('[data-testid="total-projects"]').should('be.visible');
    cy.get('[data-testid="active-projects"]').should('be.visible');
    cy.get('[data-testid="completed-projects"]').should('be.visible');
});

// Custom command to drag and drop elements
Cypress.Commands.add('dragAndDrop', (subject, target) => {
    cy.get(subject).trigger('mousedown', { button: 0 });
    cy.get(target).trigger('mousemove').trigger('mouseup', { force: true });
});

// Navigate to a specific page in the authenticated area
Cypress.Commands.add('navigateTo', (page) => {
    cy.get('[data-testid="main-nav"]').within(() => {
        cy.contains(page).click();
    });
});

// Check if user has admin privileges
Cypress.Commands.add('hasAdminAccess', () => {
    cy.get('body').then(($body) => {
        return $body.find('[data-testid="admin-panel-link"]').length > 0;
    });
});

// Handle MFA verification when needed
Cypress.Commands.add('enterMfaCode', (code = '123456') => {
    cy.get('body').then(($body) => {
        // Check if MFA prompt is present
        if ($body.find('input[placeholder*="code"]').length > 0) {
            cy.get('input[placeholder*="code"]').type(code);
            cy.get('[data-testid="verify-button"]').click();
        }
    });
});

// Clear all data from a form
Cypress.Commands.add('clearForm', (formSelector) => {
    cy.get(formSelector).within(() => {
        cy.get('input, textarea').not('[type="submit"]').not('[type="button"]').each(($el) => {
            cy.wrap($el).clear();
        });
        cy.get('select').each(($el) => {
            cy.wrap($el).select(0);
        });
    });
});
