// cypress/e2e/user-settings.cy.js
// E2E tests for user settings functionality

describe('User Settings', () => {
    beforeEach(() => {
        // Use our custom command to login programmatically without UI
        cy.programmaticLogin('test@example.com', 'user');
        cy.visit('/settings');
    });

    it('displays user profile information', () => {
        cy.get('[data-testid="user-profile"]').should('be.visible');
        cy.get('[data-testid="user-name"]').should('contain', 'Test User');
        cy.get('[data-testid="user-email"]').should('contain', 'test@example.com');
    });

    it('allows updating profile information', () => {
        // Mock the profile update API call
        cy.intercept('PUT', '**/api/users/profile', {
            statusCode: 200,
            body: {
                success: true,
                message: 'Profile updated successfully',
            },
        }).as('updateProfile');

        // Click the edit profile button
        cy.get('[data-testid="edit-profile-button"]').click();

        // Update the name field
        cy.get('[data-testid="profile-name-input"]').clear().type('Updated User Name');

        // Submit the form
        cy.get('[data-testid="save-profile-button"]').click();

        // Wait for the API call to complete
        cy.wait('@updateProfile');

        // Verify success toast appears
        cy.verifyToast('Profile updated successfully');

        // Verify the name was updated
        cy.get('[data-testid="user-name"]').should('contain', 'Updated User Name');
    });

    it('shows validation error for invalid email', () => {
        // Click the edit profile button
        cy.get('[data-testid="edit-profile-button"]').click();

        // Enter an invalid email
        cy.get('[data-testid="profile-email-input"]').clear().type('invalid-email');

        // Submit the form
        cy.get('[data-testid="save-profile-button"]').click();

        // Verify validation error appears
        cy.assertFormError('email', 'Please enter a valid email address');
    });

    it('allows changing password', () => {
        // Mock the password update API call
        cy.intercept('PUT', '**/api/users/password', {
            statusCode: 200,
            body: {
                success: true,
                message: 'Password updated successfully',
            },
        }).as('updatePassword');

        // Click the change password tab/button
        cy.get('[data-testid="change-password-tab"]').click();

        // Fill in the password form
        cy.get('[data-testid="current-password-input"]').type('currentpassword');
        cy.get('[data-testid="new-password-input"]').type('newpassword123');
        cy.get('[data-testid="confirm-password-input"]').type('newpassword123');

        // Submit the form
        cy.get('[data-testid="save-password-button"]').click();

        // Wait for the API call to complete
        cy.wait('@updatePassword');

        // Verify success toast appears
        cy.verifyToast('Password updated successfully');
    });

    it('shows validation error for password mismatch', () => {
        // Click the change password tab/button
        cy.get('[data-testid="change-password-tab"]').click();

        // Fill in the password form with mismatched passwords
        cy.get('[data-testid="current-password-input"]').type('currentpassword');
        cy.get('[data-testid="new-password-input"]').type('newpassword123');
        cy.get('[data-testid="confirm-password-input"]').type('differentpassword');

        // Submit the form
        cy.get('[data-testid="save-password-button"]').click();

        // Verify validation error appears
        cy.assertFormError('confirmPassword', 'Passwords do not match');
    });

    it('allows setting up two-factor authentication', () => {
        // Mock the 2FA setup API call
        cy.intercept('POST', '**/api/users/2fa/setup', {
            statusCode: 200,
            body: {
                qrCode: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
                secret: 'ABCDEFGHIJKLMNOP',
                recoveryCodes: [
                    'ABCD-EFGH-IJKL-MNOP',
                    '1234-5678-9012-3456',
                ],
            },
        }).as('setup2FA');

        // Mock the 2FA verification API call
        cy.intercept('POST', '**/api/users/2fa/verify', {
            statusCode: 200,
            body: {
                success: true,
                message: '2FA setup successful',
            },
        }).as('verify2FA');

        // Click the security tab/button
        cy.get('[data-testid="security-tab"]').click();

        // Click the setup 2FA button
        cy.get('[data-testid="setup-2fa-button"]').click();

        // Wait for QR code to appear
        cy.get('[data-testid="2fa-qr-code"]').should('be.visible');
        cy.get('[data-testid="2fa-secret-key"]').should('contain', 'ABCDEFGHIJKLMNOP');

        // Continue to next step
        cy.get('[data-testid="2fa-continue-button"]').click();

        // Enter verification code
        cy.get('[data-testid="2fa-code-input"]').type('123456');

        // Verify code
        cy.get('[data-testid="2fa-verify-button"]').click();

        // Wait for verification
        cy.wait('@verify2FA');

        // Check that recovery codes are displayed
        cy.get('[data-testid="recovery-code"]').should('have.length', 2);

        // Finish setup
        cy.get('[data-testid="2fa-finish-button"]').click();

        // Verify success toast appears
        cy.verifyToast('2FA setup successful');

        // Verify 2FA is now enabled
        cy.get('[data-testid="2fa-status"]').should('contain', 'Enabled');
    });

    it('allows toggling notification preferences', () => {
        // Mock the notification preferences update API call
        cy.intercept('PUT', '**/api/users/notifications', {
            statusCode: 200,
            body: {
                success: true,
                message: 'Notification preferences updated',
            },
        }).as('updateNotifications');

        // Click the notifications tab/button
        cy.get('[data-testid="notifications-tab"]').click();

        // Toggle email notifications
        cy.get('[data-testid="email-notifications-toggle"]').click();

        // Toggle in-app notifications
        cy.get('[data-testid="in-app-notifications-toggle"]').click();

        // Save preferences
        cy.get('[data-testid="save-notifications-button"]').click();

        // Wait for the API call to complete
        cy.wait('@updateNotifications');

        // Verify success toast appears
        cy.verifyToast('Notification preferences updated');
    });

    it('checks accessibility of settings pages', () => {
        // Run accessibility checks on the main settings page
        cy.checkA11y();

        // Check profile edit form
        cy.get('[data-testid="edit-profile-button"]').click();
        cy.checkA11y();

        // Check password change form
        cy.get('[data-testid="change-password-tab"]').click();
        cy.checkA11y();

        // Check notifications page
        cy.get('[data-testid="notifications-tab"]').click();
        cy.checkA11y();
    });
});
