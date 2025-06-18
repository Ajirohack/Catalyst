// cypress/e2e/project-workflow.cy.js

describe('Project Workflow', () => {
  beforeEach(() => {
    // Login before each test
    cy.login('user@example.com', 'password123');
  });

  it('should create a new project', () => {
    // Visit new project page
    cy.visit('/new-project');

    // Fill out project form
    cy.get('[data-testid="project-name-input"]').type('E2E Test Project');
    cy.get('[data-testid="project-description-input"]').type('Project created during E2E testing');

    // Select project type (assuming dropdown)
    cy.get('[data-testid="project-type-select"]').click();
    cy.contains('Personal').click();

    // Select platform
    cy.get('[data-testid="platform-select"]').click();
    cy.contains('WhatsApp').click();

    // Submit form
    cy.get('[data-testid="create-project-button"]').click();

    // Should redirect to project detail
    cy.url().should('include', '/projects/');
    cy.contains('E2E Test Project').should('be.visible');
  });

  it('should view project details and use the whisper panel', () => {
    // Create a project first or navigate to existing project
    cy.visit('/dashboard');
    cy.contains('E2E Test Project').click();

    // Verify project details page
    cy.contains('Project Details').should('be.visible');

    // Open whisper panel
    cy.get('[data-testid="open-whisper-button"]').click();
    cy.get('[data-testid="whisper-panel"]').should('be.visible');

    // Type a message
    cy.get('[data-testid="message-input"]').type('This is a test message from Cypress');
    cy.get('[data-testid="send-button"]').click();

    // Verify suggestion appears
    cy.contains('suggestion').should('be.visible');

    // Close whisper panel
    cy.get('[data-testid="close-whisper-button"]').click();
    cy.get('[data-testid="whisper-panel"]').should('not.exist');
  });

  it('should start analysis and view results', () => {
    // Navigate to a project
    cy.visit('/dashboard');
    cy.contains('E2E Test Project').click();

    // Start analysis
    cy.get('[data-testid="start-analysis-button"]').click();

    // Confirm analysis
    cy.get('[data-testid="confirm-analysis-button"]').click();

    // Wait for analysis to complete (this may take time in real scenarios)
    cy.get('[data-testid="analysis-progress"]', { timeout: 10000 }).should('be.visible');

    // Either wait for completion or mock it
    cy.get('[data-testid="analysis-complete"]', { timeout: 20000 }).should('be.visible');

    // View analysis results
    cy.get('[data-testid="view-results-button"]').click();

    // Verify results page
    cy.url().should('include', '/analysis/');
    cy.contains('Analysis Results').should('be.visible');
  });
});

// Custom command for login
Cypress.Commands.add('login', (email, password) => {
  cy.session([email, password], () => {
    cy.visit('/login');
    cy.get('input[type="email"]').type(email);
    cy.get('input[type="password"]').type(password);
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
  });
});
