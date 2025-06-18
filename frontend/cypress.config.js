// cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    pageLoadTimeout: 30000,
    experimentalStudio: true,
    retries: {
      runMode: 2,
      openMode: 0,
    },
    env: {
      apiUrl: 'http://localhost:8000/api',
      coverage: false,
    },
    setupNodeEvents(on, config) {
      // implement node event listeners here
      on('task', {
        log(message) {
          console.log(message);
          return null;
        },
        table(message) {
          console.table(message);
          return null;
        },
      });

      // Code coverage setup (if using @cypress/code-coverage)
      // require('@cypress/code-coverage/task')(on, config);

      return config;
    },
  },

  component: {
    devServer: {
      framework: 'react',
      bundler: 'webpack',
    },
    specPattern: 'src/**/*.cy.{js,jsx,ts,tsx}',
    viewportWidth: 1000,
    viewportHeight: 660,
  },

  // Global configuration
  chromeWebSecurity: false,
  watchForFileChanges: true,
  numTestsKeptInMemory: 50,

  // Environment-specific configuration
  ...(process.env.CI && {
    video: true,
    screenshotOnRunFailure: true,
    trashAssetsBeforeRuns: true,
  }),
});
