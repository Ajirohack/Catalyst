// Catalyst Whisper Coach - Login Script
document.addEventListener('DOMContentLoaded', () => {
    // Check if already logged in
    checkAuthentication();

    // Login button click
    document.getElementById('login-btn').addEventListener('click', handleLogin);

    // Form inputs
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');

    // Enable form submission on Enter key
    passwordInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleLogin();
        }
    });

    // Forgot password link
    document.getElementById('forgot-password-link').addEventListener('click', (e) => {
        e.preventDefault();
        chrome.tabs.create({ url: 'http://localhost:8000/auth/reset-password' });
    });
});

// Check if user is already authenticated
async function checkAuthentication() {
    try {
        const isAuthenticated = await sendMessageToBackground('CHECK_AUTH');

        if (isAuthenticated) {
            // Redirect to popup.html
            window.location.href = 'popup.html';
        }
    } catch (error) {
        console.error('Authentication check failed:', error);
    }
}

// Handle login form submission
async function handleLogin() {
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const errorMessage = document.getElementById('error-message');
    const loginBtn = document.getElementById('login-btn');
    const loading = document.getElementById('loading');

    // Get input values
    const email = emailInput.value.trim();
    const password = passwordInput.value;

    // Validate inputs
    if (!email) {
        showError('Please enter your email');
        emailInput.focus();
        return;
    }

    if (!password) {
        showError('Please enter your password');
        passwordInput.focus();
        return;
    }

    // Show loading state
    loginBtn.disabled = true;
    loading.style.display = 'block';
    errorMessage.style.display = 'none';

    try {
        // Send login request
        const response = await sendMessageToBackground('LOGIN_USER', {
            email,
            password
        });

        if (response.error) {
            throw new Error(response.error);
        }

        // Redirect to popup on success
        window.location.href = 'popup.html';
    } catch (error) {
        console.error('Login failed:', error);
        showError(error.message || 'Login failed. Please try again.');

        // Reset loading state
        loginBtn.disabled = false;
        loading.style.display = 'none';
    }
}

// Show error message
function showError(message) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
}

// Send message to background script
function sendMessageToBackground(type, data = null) {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage({ type, data }, response => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } else if (response && response.error) {
                reject(new Error(response.error));
            } else {
                resolve(response);
            }
        });
    });
}
