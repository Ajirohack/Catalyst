// chrome_extension/config/api.config.js
// Configuration management for Chrome Extension

/**
 * Extension configuration for different environments
 */
export const EXTENSION_CONFIG = {
    development: {
        apiBaseUrl: 'http://localhost:8000/api',
        wsBaseUrl: 'ws://localhost:8000/ws',
        webAppUrl: 'http://localhost:3000',
        debug: true,
    },
    staging: {
        apiBaseUrl: 'https://api-staging.catalyst.example.com/api',
        wsBaseUrl: 'wss://api-staging.catalyst.example.com/ws',
        webAppUrl: 'https://staging.catalyst.example.com',
        debug: false,
    },
    production: {
        apiBaseUrl: 'https://api.catalyst.example.com/api',
        wsBaseUrl: 'wss://api.catalyst.example.com/ws',
        webAppUrl: 'https://catalyst.example.com',
        debug: false,
    }
};

/**
 * Get current environment based on manifest or stored settings
 */
export const getCurrentEnvironment = async () => {
    try {
        // Check if environment is stored in extension settings
        const { environment } = await chrome.storage.sync.get(['environment']);
        if (environment && EXTENSION_CONFIG[environment]) {
            return environment;
        }

        // Default to development for local testing
        return 'development';
    } catch (error) {
        console.warn('Failed to get environment, defaulting to development:', error);
        return 'development';
    }
};

/**
 * Get configuration for current environment
 */
export const getExtensionConfig = async () => {
    const environment = await getCurrentEnvironment();
    const config = EXTENSION_CONFIG[environment];

    // Allow override from extension options/settings
    try {
        const stored = await chrome.storage.sync.get(['customApiUrl', 'customWebAppUrl']);

        return {
            ...config,
            environment,
            // Allow custom URLs from extension options
            apiBaseUrl: stored.customApiUrl || config.apiBaseUrl,
            webAppUrl: stored.customWebAppUrl || config.webAppUrl,
        };
    } catch (error) {
        console.warn('Failed to get stored config, using defaults:', error);
        return {
            ...config,
            environment,
        };
    }
};

/**
 * Update environment configuration
 */
export const setEnvironment = async (environment) => {
    if (!EXTENSION_CONFIG[environment]) {
        throw new Error(`Invalid environment: ${environment}`);
    }

    await chrome.storage.sync.set({ environment });
    return environment;
};

/**
 * Update custom API URLs
 */
export const updateCustomUrls = async (apiUrl, webAppUrl) => {
    const updates = {};

    if (apiUrl) updates.customApiUrl = apiUrl;
    if (webAppUrl) updates.customWebAppUrl = webAppUrl;

    await chrome.storage.sync.set(updates);
};

/**
 * Storage keys for extension data
 */
export const STORAGE_KEYS = {
    USER_SETTINGS: 'catalyst_user_settings',
    ACTIVE_PROJECT: 'catalyst_active_project',
    SESSION_DATA: 'catalyst_session_data',
    API_TOKEN: 'catalyst_api_token',
    WHISPER_HISTORY: 'catalyst_whisper_history',
    PROJECT_LIST: 'catalyst_project_list',
    ENVIRONMENT: 'catalyst_environment',
    CUSTOM_API_URL: 'catalyst_custom_api_url',
    CUSTOM_WEB_APP_URL: 'catalyst_custom_web_app_url',
};

/**
 * Default extension settings
 */
export const DEFAULT_SETTINGS = {
    enabled: true,
    autoAnalysis: true,
    realTimeCoaching: true,
    privacyMode: false,
    analysisFrequency: 'medium', // low, medium, high
    environment: 'development',
    supportedPlatforms: {
        whatsapp: true,
        messenger: true,
        instagram: true,
        facebook: true,
        discord: true,
        slack: true,
        teams: true,
        telegram: true,
        reddit: false,
        twitter: false,
    },
    notifications: {
        analysis: true,
        insights: true,
        suggestions: true,
        errors: true,
    },
    ui: {
        showOnboardingTips: true,
        compactMode: false,
        theme: 'auto', // light, dark, auto
    }
};
