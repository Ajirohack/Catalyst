/**
 * Security Utilities for Catalyst
 * Handles secure token storage, device fingerprinting, and other security-related functions
 */

import { jwtDecode } from "jwt-decode";
import { UAParser } from "ua-parser-js";
import { v4 as uuidv4 } from "uuid";
import CryptoJS from "crypto-js";

// Secret key for local encryption (this is just for additional protection in browser storage)
// In a real app, consider using a more sophisticated approach or the Web Crypto API
const STORAGE_ENCRYPTION_KEY = "catalyst-secure-storage-key";

const securityUtils = {
    /**
     * Set access and refresh tokens in secure storage
     */
    setTokens: (accessToken, refreshToken) => {
        if (accessToken) {
            const encryptedAccessToken = CryptoJS.AES.encrypt(
                accessToken,
                STORAGE_ENCRYPTION_KEY
            ).toString();
            localStorage.setItem("auth_access_token", encryptedAccessToken);
        }

        if (refreshToken) {
            const encryptedRefreshToken = CryptoJS.AES.encrypt(
                refreshToken,
                STORAGE_ENCRYPTION_KEY
            ).toString();
            localStorage.setItem("auth_refresh_token", encryptedRefreshToken);
        }

        // Store token issue time for additional validation
        localStorage.setItem("auth_token_issued", Date.now().toString());
    },

    /**
     * Get the access token from storage
     */
    getAccessToken: () => {
        const encryptedToken = localStorage.getItem("auth_access_token");
        if (!encryptedToken) return null;

        try {
            const decryptedToken = CryptoJS.AES.decrypt(
                encryptedToken,
                STORAGE_ENCRYPTION_KEY
            ).toString(CryptoJS.enc.Utf8);

            // Validate the token format
            if (!decryptedToken || !decryptedToken.split(".").length === 3) {
                return null;
            }

            // Verify token hasn't expired locally
            const decodedToken = jwtDecode(decryptedToken);
            if (decodedToken.exp * 1000 < Date.now()) {
                securityUtils.clearTokens();
                return null;
            }

            return decryptedToken;
        } catch (error) {
            console.error("Error decrypting access token:", error);
            return null;
        }
    },

    /**
     * Get the refresh token from storage
     */
    getRefreshToken: () => {
        const encryptedToken = localStorage.getItem("auth_refresh_token");
        if (!encryptedToken) return null;

        try {
            return CryptoJS.AES.decrypt(
                encryptedToken,
                STORAGE_ENCRYPTION_KEY
            ).toString(CryptoJS.enc.Utf8);
        } catch (error) {
            console.error("Error decrypting refresh token:", error);
            return null;
        }
    },

    /**
     * Clear all tokens and auth-related data
     */
    clearTokens: () => {
        localStorage.removeItem("auth_access_token");
        localStorage.removeItem("auth_refresh_token");
        localStorage.removeItem("auth_token_issued");
        localStorage.removeItem("auth_csrf_token");

        // Keep the device ID for analytics purposes
        // localStorage.removeItem("device_id");
    },

    /**
     * Store CSRF token
     */
    setCSRFToken: (token) => {
        localStorage.setItem("auth_csrf_token", token);
    },

    /**
     * Get CSRF token
     */
    getCSRFToken: () => {
        return localStorage.getItem("auth_csrf_token");
    },

    /**
     * Generate and retrieve a persistent device ID
     */
    getOrCreateDeviceId: () => {
        let deviceId = localStorage.getItem("device_id");

        if (!deviceId) {
            deviceId = uuidv4();
            localStorage.setItem("device_id", deviceId);
        }

        return deviceId;
    },

    /**
     * Get detailed device and browser information
     * This helps with security monitoring and fraud detection
     */
    getDeviceInfo: () => {
        const parser = new UAParser();
        const result = parser.getResult();

        // Get screen dimensions
        const screenData = {
            width: window.screen.width,
            height: window.screen.height,
            availWidth: window.screen.availWidth,
            availHeight: window.screen.availHeight,
            colorDepth: window.screen.colorDepth,
            pixelDepth: window.screen.pixelDepth,
        };

        // Get timezone information
        const timezoneOffset = new Date().getTimezoneOffset();
        const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone;

        // Check for browser features
        const featureDetection = {
            localStorage: !!window.localStorage,
            sessionStorage: !!window.sessionStorage,
            cookiesEnabled: navigator.cookieEnabled,
            touchSupport: "ontouchstart" in window,
            webGL: !!window.WebGLRenderingContext,
        };

        // Get device ID (created if doesn't exist)
        const deviceId = securityUtils.getOrCreateDeviceId();

        return {
            deviceId,
            userAgent: navigator.userAgent,
            browser: {
                name: result.browser.name,
                version: result.browser.version,
            },
            engine: {
                name: result.engine.name,
                version: result.engine.version,
            },
            os: {
                name: result.os.name,
                version: result.os.version,
            },
            device: {
                vendor: result.device.vendor,
                model: result.device.model,
                type: result.device.type,
            },
            screen: screenData,
            timezone: {
                offset: timezoneOffset,
                zone: timezone,
            },
            language: navigator.language,
            languages: navigator.languages,
            features: featureDetection,
            timestamp: new Date().toISOString(),
        };
    },

    /**
     * Record a failed login attempt and return the current count
     */
    recordLoginAttempt: () => {
        const now = Date.now();
        const attemptWindow = 10 * 60 * 1000; // 10 minutes

        // Get stored attempts
        let attempts = JSON.parse(localStorage.getItem("login_attempts") || "[]");

        // Filter out old attempts
        attempts = attempts.filter(
            (timestamp) => now - timestamp < attemptWindow
        );

        // Add the current attempt
        attempts.push(now);

        // Store updated attempts
        localStorage.setItem("login_attempts", JSON.stringify(attempts));

        return attempts.length;
    },

    /**
     * Enable login cooldown for a specified number of seconds
     */
    enableLoginCooldown: (seconds) => {
        const now = Date.now();
        const expiry = now + seconds * 1000;

        localStorage.setItem("login_cooldown", expiry.toString());
    },

    /**
     * Check if login is in cooldown period
     * Returns the number of seconds remaining, or 0 if no cooldown
     */
    getLoginCooldownRemaining: () => {
        const cooldownExpiry = parseInt(localStorage.getItem("login_cooldown") || "0");
        const now = Date.now();

        if (cooldownExpiry > now) {
            return Math.ceil((cooldownExpiry - now) / 1000);
        }

        return 0;
    },

    /**
     * Validate password strength
     * Returns an object with validity and a reason if invalid
     */
    validatePasswordStrength: (password) => {
        if (!password || password.length < 8) {
            return { valid: false, reason: "Password must be at least 8 characters long" };
        }

        // Check for at least one uppercase letter
        if (!/[A-Z]/.test(password)) {
            return { valid: false, reason: "Password must contain at least one uppercase letter" };
        }

        // Check for at least one lowercase letter
        if (!/[a-z]/.test(password)) {
            return { valid: false, reason: "Password must contain at least one lowercase letter" };
        }

        // Check for at least one number
        if (!/\d/.test(password)) {
            return { valid: false, reason: "Password must contain at least one number" };
        }

        // Check for at least one special character
        if (!/[^A-Za-z0-9]/.test(password)) {
            return { valid: false, reason: "Password must contain at least one special character" };
        }

        // Additional check for commonly used passwords
        const commonPasswords = [
            "Password1!", "Admin123!", "Welcome1!", "Catalyst1!"
        ];

        if (commonPasswords.includes(password)) {
            return { valid: false, reason: "Password is too common and easily guessed" };
        }

        return { valid: true };
    },

    /**
     * Generate a password strength score (0-100)
     */
    getPasswordStrengthScore: (password) => {
        if (!password) return 0;

        let score = 0;

        // Length contribution (up to 25 points)
        score += Math.min(25, password.length * 2);

        // Character variety contribution
        if (/[A-Z]/.test(password)) score += 10; // uppercase
        if (/[a-z]/.test(password)) score += 10; // lowercase
        if (/\d/.test(password)) score += 10;    // numbers
        if (/[^A-Za-z0-9]/.test(password)) score += 15; // special chars

        // Variety of character types
        const charTypes = [/[A-Z]/, /[a-z]/, /\d/, /[^A-Za-z0-9]/].filter(regex => regex.test(password)).length;
        score += charTypes * 5;

        // Penalize for patterns
        if (/(.)\1\1/.test(password)) score -= 10; // repeated characters
        if (/12345|qwerty|asdfg|zxcvb/i.test(password)) score -= 15; // common sequences

        // Ensure score is between 0-100
        return Math.max(0, Math.min(100, score));
    },

    /**
     * Generate a TOTP (Time-based One-Time Password) secret
     * This would typically be stored with the user's account on the server
     */
    generateTOTPSecret: () => {
        // In production, this would use a proper library like otplib
        // This is a simplified version for demonstration purposes
        const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'; // Base32 encoding
        let secret = '';
        for (let i = 0; i < 16; i++) {
            secret += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return secret;
    },

    /**
     * Get a QR code URL for setting up MFA with authenticator apps
     */
    getTOTPQRCodeUrl: (secret, email, issuer = 'Catalyst') => {
        const encodedIssuer = encodeURIComponent(issuer);
        const encodedEmail = encodeURIComponent(email);
        return `https://chart.googleapis.com/chart?chs=200x200&chld=M|0&cht=qr&chl=otpauth://totp/${encodedIssuer}:${encodedEmail}?secret=${secret}&issuer=${encodedIssuer}`;
    },

    /**
     * Store MFA settings locally (the server would also store this)
     */
    storeMFASettings: (isEnabled, method = 'app') => {
        const settings = {
            enabled: isEnabled,
            method: method,
            setupDate: new Date().toISOString()
        };

        localStorage.setItem('mfa_settings', JSON.stringify(settings));
    },

    /**
     * Get MFA settings
     */
    getMFASettings: () => {
        const settings = localStorage.getItem('mfa_settings');
        if (!settings) {
            return { enabled: false };
        }

        try {
            return JSON.stringify(settings);
        } catch (error) {
            console.error('Error parsing MFA settings:', error);
            return { enabled: false };
        }
    },

    /**
     * Get session security score based on multiple factors
     * Higher score means more secure session
     */
    getSessionSecurityScore: () => {
        let score = 0;

        // HTTPS adds 25 points
        if (window.location.protocol === 'https:') {
            score += 25;
        }

        // MFA adds 30 points
        const mfaSettings = securityUtils.getMFASettings();
        if (mfaSettings.enabled) {
            score += 30;
        }

        // Recent token issuance adds up to 15 points
        const tokenIssuedStr = localStorage.getItem('auth_token_issued');
        if (tokenIssuedStr) {
            const tokenAge = Date.now() - parseInt(tokenIssuedStr);
            const tokenAgeHours = tokenAge / (1000 * 60 * 60);
            if (tokenAgeHours < 1) {
                score += 15;
            } else if (tokenAgeHours < 6) {
                score += 10;
            } else if (tokenAgeHours < 24) {
                score += 5;
            }
        }

        // Consistent device adds 10 points
        const deviceId = securityUtils.getOrCreateDeviceId();
        const knownDevices = JSON.parse(localStorage.getItem('known_devices') || '[]');
        if (knownDevices.includes(deviceId)) {
            score += 10;
        }

        // Secure password (if we know it was recently validated) adds 20 points
        const passwordValidated = localStorage.getItem('password_validated');
        if (passwordValidated && (Date.now() - parseInt(passwordValidated)) < (7 * 24 * 60 * 60 * 1000)) {
            score += 20;
        }

        return score;
    },

    /**
     * Store a trusted device
     */
    addTrustedDevice: (deviceInfo) => {
        const deviceId = deviceInfo.deviceId || securityUtils.getOrCreateDeviceId();
        let trustedDevices = JSON.parse(localStorage.getItem('trusted_devices') || '[]');

        // Check if device already exists
        const existingIndex = trustedDevices.findIndex(device => device.deviceId === deviceId);

        if (existingIndex >= 0) {
            // Update existing device information
            trustedDevices[existingIndex] = {
                ...trustedDevices[existingIndex],
                ...deviceInfo,
                lastSeen: new Date().toISOString()
            };
        } else {
            // Add new device
            trustedDevices.push({
                ...deviceInfo,
                deviceId,
                trusted: true,
                firstSeen: new Date().toISOString(),
                lastSeen: new Date().toISOString()
            });
        }

        // Add to known devices list for quick lookups
        let knownDevices = JSON.parse(localStorage.getItem('known_devices') || '[]');
        if (!knownDevices.includes(deviceId)) {
            knownDevices.push(deviceId);
            localStorage.setItem('known_devices', JSON.stringify(knownDevices));
        }

        localStorage.setItem('trusted_devices', JSON.stringify(trustedDevices));
        return deviceId;
    },
};

export default securityUtils;
