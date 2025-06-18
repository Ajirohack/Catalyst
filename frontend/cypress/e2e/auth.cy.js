// cypress/e2e/auth.cy.js

describe('Authentication Flow', () => {
  beforeEach(() => {
    // Reset any previous state
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  it('should redirect to login page when accessing protected route', () => {
    // Visit dashboard which should be protected
    cy.visit('/dashboard');

    // Should redirect to login
    cy.url().should('include', '/login');
    cy.contains('Login to your account').should('be.visible');
  });

  it('should login with valid credentials', () => {
    // Visit login page
    cy.visit('/login');

    // Fill out login form
    cy.get('input[type="email"]').type('user@example.com');
    cy.get('input[type="password"]').type('password123');

    // Submit form
    cy.get('button[type="submit"]').click();

    // Should redirect to dashboard
    cy.url().should('include', '/dashboard');
    cy.contains('Dashboard').should('be.visible');
  });

  it('should show error message with invalid credentials', () => {
    // Visit login page
    cy.visit('/login');

    // Fill out login form with incorrect password
    cy.get('input[type="email"]').type('user@example.com');
    cy.get('input[type="password"]').type('wrongpassword');

    // Submit form
    cy.get('button[type="submit"]').click();

    // Should show error message
    cy.contains('Invalid email or password').should('be.visible');

    // Should remain on login page
    cy.url().should('include', '/login');
  });

  it('should be able to logout', () => {
    // Login first
    cy.visit('/login');
    cy.get('input[type="email"]').type('user@example.com');
    cy.get('input[type="password"]').type('password123');
    cy.get('button[type="submit"]').click();

    // Wait for dashboard to load
    cy.url().should('include', '/dashboard');

    // Find and click logout button (adjust selector as needed)
    cy.get('[data-testid="user-menu"]').click();
    cy.contains('Logout').click();

    // Should redirect back to login
    cy.url().should('include', '/login');
  });
});

describe('Registration Flow', () => {
  beforeEach(() => {
    // Reset any previous state
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  it('should register a new user', () => {
    // Visit register page
    cy.visit('/register');

    // Generate unique email to avoid conflicts in repeated test runs
    const uniqueEmail = `user${Date.now()}@example.com`;

    // Fill out registration form
    cy.get('input[name="name"]').type('Test User');
    cy.get('input[type="email"]').type(uniqueEmail);
    cy.get('input[type="password"]').type('SecurePass123!');
    cy.get('input[name="confirmPassword"]').type('SecurePass123!');

    // Submit form
    cy.get('button[type="submit"]').click();

    // Should redirect to onboarding or dashboard
    cy.url().should('include', '/onboarding');
    cy.contains('Welcome').should('be.visible');
  });

  it('should show error for existing email', () => {
    // Visit register page
    cy.visit('/register');

    // Use email that already exists
    cy.get('input[name="name"]').type('Duplicate User');
    cy.get('input[type="email"]').type('user@example.com'); // Existing email
    cy.get('input[type="password"]').type('SecurePass123!');
    cy.get('input[name="confirmPassword"]').type('SecurePass123!');

    // Submit form
    cy.get('button[type="submit"]').click();

    // Should show error
    cy.contains('Email already registered').should('be.visible');
    cy.url().should('include', '/register');
  });

  it('should validate password requirements', () => {
    // Visit register page
    cy.visit('/register');

    // Try with weak password
    cy.get('input[name="name"]').type('Test User');
    cy.get('input[type="email"]').type('newuser@example.com');
    cy.get('input[type="password"]').type('weak');
    cy.get('input[name="confirmPassword"]').type('weak');

    // Submit form
    cy.get('button[type="submit"]').click();

    // Should show password requirements error
    cy.contains('Password must be at least 8 characters').should('be.visible');
    cy.url().should('include', '/register');
  });
});

describe('Password Reset Flow', () => {
  beforeEach(() => {
    cy.clearLocalStorage();
    cy.clearCookies();
  });

  it('should request password reset', () => {
    // Visit forgot password page
    cy.visit('/forgot-password');

    // Enter email
    cy.get('input[type="email"]').type('user@example.com');

    // Submit form
    cy.get('button[type="submit"]').click();

    // Should show success message
    cy.contains('Password reset email sent').should('be.visible');
  });

  it('should reset password with valid token', () => {
    // In a real test, you would need to intercept the email or mock the API
    // Here we'll simulate having a valid token
    cy.visit('/reset-password?token=valid-mock-token');

    // Enter new password
    cy.get('input[name="password"]').type('NewSecurePass123!');
    cy.get('input[name="confirmPassword"]').type('NewSecurePass123!');

    // Submit form
    cy.get('button[type="submit"]').click();

    // Should show success and redirect to login
    cy.contains('Password reset successful').should('be.visible');
    cy.url().should('include', '/login');
  });

  it('should show error with invalid token', () => {
    // Simulate invalid token
    cy.visit('/reset-password?token=invalid-token');

    // Enter new password
    cy.get('input[name="password"]').type('NewSecurePass123!');
    cy.get('input[name="confirmPassword"]').type('NewSecurePass123!');

    // Submit form
    cy.get('button[type="submit"]').click();

    // Should show error
    cy.contains('Invalid or expired token').should('be.visible');
  });
});

describe('MFA Setup Flow', () => {
  beforeEach(() => {
    // Login first
    cy.login('user@example.com', 'password123');
  });

  it('should navigate to MFA setup page', () => {
    // Go to settings
    cy.visit('/settings');

    // Find and click on security settings
    cy.contains('Security').click();

    // Find and click on Enable 2FA button
    cy.get('[data-testid="enable-2fa-button"]').click();

    // Should navigate to MFA setup
    cy.url().should('include', '/mfa-setup');
    cy.contains('Set up Two-Factor Authentication').should('be.visible');
  });

  it('should display QR code and secret key', () => {
    // Direct visit to MFA setup
    cy.visit('/mfa-setup');

    // Should show QR code
    cy.get('img[alt="QR Code"]').should('be.visible');

    // Should show secret key
    cy.get('[data-testid="secret-key"]').should('be.visible');
  });

  it('should proceed through verification step', () => {
    cy.visit('/mfa-setup');

    // Click continue to move to verification step
    cy.get('[data-testid="continue-button"]').click();

    // Should show verification input
    cy.contains('Verify your code').should('be.visible');

    // Enter verification code (in real test this would need to be generated)
    cy.get('input[placeholder*="code"]').type('123456');

    // Submit code
    cy.get('[data-testid="verify-button"]').click();

    // Should show recovery codes
    cy.contains('Recovery Codes').should('be.visible');
    cy.get('[data-testid="recovery-codes"]').should('be.visible');
  });

  it('should complete MFA setup and verify on next login', () => {
    // Complete setup (simplified)
    cy.visit('/mfa-setup');
    cy.get('[data-testid="continue-button"]').click();
    cy.get('input[placeholder*="code"]').type('123456');
    cy.get('[data-testid="verify-button"]').click();
    cy.get('[data-testid="complete-button"]').click();

    // Logout
    cy.get('[data-testid="user-menu"]').click();
    cy.contains('Logout').click();

    // Login again
    cy.visit('/login');
    cy.get('input[type="email"]').type('user@example.com');
    cy.get('input[type="password"]').type('password123');
    cy.get('button[type="submit"]').click();

    // Should now prompt for MFA code
    cy.contains('Enter verification code').should('be.visible');
    cy.get('input[placeholder*="code"]').type('123456');
    cy.get('[data-testid="verify-button"]').click();

    // Should complete login
    cy.url().should('include', '/dashboard');
  });
});

describe('Role-Based Access Control', () => {
  it('should allow admin to access admin dashboard', () => {
    // Login as admin
    cy.login('admin@example.com', 'adminpassword');

    // Try to access admin dashboard
    cy.visit('/admin');

    // Should be able to access
    cy.url().should('include', '/admin');
    cy.contains('Admin Dashboard').should('be.visible');
  });

  it('should redirect regular user from admin pages', () => {
    // Login as regular user
    cy.login('user@example.com', 'password123');

    // Try to access admin dashboard
    cy.visit('/admin');

    // Should be redirected to regular dashboard
    cy.url().should('include', '/dashboard');
    cy.url().should('not.include', '/admin');
  });

  it('should display appropriate navigation based on role', () => {
    // Login as admin
    cy.login('admin@example.com', 'adminpassword');

    // Check for admin navigation items
    cy.get('[data-testid="main-nav"]').within(() => {
      cy.contains('User Management').should('be.visible');
      cy.contains('System Monitoring').should('be.visible');
    });

    // Logout
    cy.get('[data-testid="user-menu"]').click();
    cy.contains('Logout').click();

    // Login as regular user
    cy.login('user@example.com', 'password123');

    // Check that admin navigation items are not visible
    cy.get('[data-testid="main-nav"]').within(() => {
      cy.contains('User Management').should('not.exist');
      cy.contains('System Monitoring').should('not.exist');
    });
  });
});
