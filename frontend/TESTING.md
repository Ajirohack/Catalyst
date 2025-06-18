# Catalyst Frontend Testing Guide

This document outlines the comprehensive testing strategy for the Catalyst frontend application.

## Types of Tests

The Catalyst frontend uses multiple testing approaches:

1. **Unit Tests** - Test individual components and functions in isolation
2. **Integration Tests** - Test multiple components working together
3. **Component Tests** - Visual testing of components using Storybook
4. **End-to-End Tests** - Test complete user flows using Cypress
5. **Performance Tests** - Measure and ensure good application performance
6. **Accessibility Tests** - Ensure the application is accessible to all users
7. **API Tests** - Test API integration without UI interaction

## Testing Tools

- **Jest** - Unit and integration test runner
- **React Testing Library** - Component testing utilities
- **Storybook** - Component development and visual testing
- **Cypress** - End-to-end testing
- **MSW (Mock Service Worker)** - API mocking for tests
- **Axe-core** - Accessibility testing

## Test Directory Structure

```bash
/src
  /__tests__/         # Unit tests for components
  /__integration__/   # Integration tests for features
  /components/        # Components with their stories
    /Button/
      Button.jsx
      Button.stories.jsx
  /hooks/             # Custom hooks and their tests
    useAuth.js
    useAuth.test.js
/cypress
  /e2e/              # End-to-end tests
  /fixtures/         # Test data
  /support/          # Cypress helpers and commands
/.storybook          # Storybook configuration
```

## Running Tests

### Unit and Integration Tests

```bash
# Run all tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch

# Run a specific test file
npm test -- Button.test.jsx
```

### Component Tests with Storybook

```bash
# Start Storybook
npm run storybook

# Build Storybook
npm run build-storybook
```

### End-to-End Tests with Cypress

```bash
# Open Cypress UI
npm run cypress:open

# Run all Cypress tests headlessly
npm run cypress:run

# Run a specific test file
npm run cypress:run -- --spec "cypress/e2e/auth.cy.js"
```

## Writing Tests

### Unit Tests

Unit tests should focus on testing a single component or function in isolation. Use mocks for dependencies.

Example of a component unit test:

```jsx
import { render, screen, fireEvent } from '@testing-library/react';
import Button from '../components/Button/Button';

describe('Button Component', () => {
  test('renders correctly', () => {
    render(<Button>Click Me</Button>);
    expect(screen.getByText('Click Me')).toBeInTheDocument();
  });

  test('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);
    fireEvent.click(screen.getByText('Click Me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

### Integration Tests

Integration tests should verify that multiple components work together correctly.

Example of an integration test:

```jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Login from '../pages/auth/Login';

describe('Login Flow', () => {
  test('redirects to dashboard after successful login', async () => {
    render(
      <BrowserRouter>
        <Login />
      </BrowserRouter>
    );

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password' },
    });
    fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(window.location.pathname).toBe('/dashboard');
    });
  });
});
```

### Writing Component Stories

Use Storybook to document and visually test components in isolation.

Example of a component story:

```jsx
import Button from './Button';

const meta = {
  title: 'Components/Button',
  component: Button,
  argTypes: {
    variant: {
      control: { type: 'select' },
      options: ['primary', 'secondary', 'danger'],
    },
  },
};

export default meta;

export const Primary = {
  args: {
    children: 'Primary Button',
    variant: 'primary',
  },
};

export const Secondary = {
  args: {
    children: 'Secondary Button',
    variant: 'secondary',
  },
};
```

### Writing E2E Tests

End-to-end tests should verify complete user flows through the application.

Example of an E2E test:

```js
describe('Authentication Flow', () => {
  it('allows users to login and access dashboard', () => {
    cy.visit('/login');
    cy.get('input[type="email"]').type('test@example.com');
    cy.get('input[type="password"]').type('password');
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
    cy.get('[data-testid="user-greeting"]').should('contain', 'Welcome');
  });
});
```

## Best Practices

1. **Test Behavior, Not Implementation** - Focus on what the component does, not how it's implemented.
2. **Use Data Attributes** - Use `data-testid` attributes to select elements for testing.
3. **Mock External Dependencies** - Use MSW to mock API calls.
4. **Test Accessibility** - Include accessibility checks in your tests.
5. **Keep Tests Fast** - Tests should run quickly to encourage frequent running.
6. **Test Edge Cases** - Test error states, loading states, and edge cases.
7. **Maintain Test Independence** - Tests shouldn't rely on the state from other tests.
8. **Use Descriptive Test Names** - Test names should describe the behavior being tested.
9. **Run Tests on CI** - Configure CI to run tests on every pull request.
10. **Keep Coverage High** - Aim for high test coverage, especially for critical paths.

## Continuous Integration

All tests are run as part of the CI pipeline. Tests must pass before code can be merged to the main branch.

## Debugging Tests

### Jest Tests

For unit and integration tests, use Jest's debug mode:

```bash
# Add debugger statements in your code, then:
node --inspect-brk node_modules/.bin/jest --runInBand MyComponent.test.jsx
```

### Cypress Tests

For Cypress tests, use the Cypress UI to debug:

```bash
npm run cypress:open
```

Then click on the test you want to debug. You can use the browser's dev tools to debug as the test runs.

## Additional Resources

- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [React Testing Library Documentation](https://testing-library.com/docs/react-testing-library/intro/)
- [Cypress Documentation](https://docs.cypress.io/guides/overview/why-cypress)
- [Storybook Documentation](https://storybook.js.org/docs/react/get-started/introduction)
- [MSW Documentation](https://mswjs.io/docs/)
