// cypress/support/e2e.js

// Import commands.js using ES2015 syntax:
import './commands';

// Import accessibility testing if enabled
// Requires cypress-axe to be installed
if (Cypress.env('checkAccessibility')) {
    import('cypress-axe').then(() => {
        afterEach(() => {
            cy.checkA11y();
        });
    });
}

// Cypress configuration for e2e tests
beforeEach(() => {
    // Preserve cookies between tests to maintain login state when needed
    Cypress.Cookies.preserveOnce('sessionId', 'authToken');
});

// Configure global error handling
Cypress.on('uncaught:exception', (err, runnable) => {
    // Return false to prevent Cypress from failing the test
    // This is useful when testing 3rd party libraries that throw errors
    console.log('Uncaught exception:', err.message);
    return false;
});

// Add custom assertion for checking if element has specific data
chai.Assertion.addMethod('hasData', function (attr) {
    const obj = this._obj;
    const value = obj.data(attr);
    this.assert(
        value !== undefined && value !== null,
        `expected #{this} to have data attribute '${attr}'`,
        `expected #{this} not to have data attribute '${attr}'`
    );
});

// Set default viewport
Cypress.config('viewportWidth', 1280);
Cypress.config('viewportHeight', 800);

// Disable scrolling animations for more reliable tests
Cypress.config('scrollBehavior', 'nearest');

// Log environment info
Cypress.env('environment') && console.log(`Running tests in ${Cypress.env('environment')} environment`);
