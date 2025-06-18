// .eslintrc.cypress.js
// This is a special ESLint configuration for Cypress tests
module.exports = {
    extends: [
        './.eslintrc.js', // Extend the base ESLint config
    ],
    plugins: ['cypress'],
    env: {
        'cypress/globals': true,
    },
    rules: {
        // Disable certain rules for Cypress tests
        'no-unused-expressions': 'off',
        'testing-library/await-async-query': 'off',
    },
};
