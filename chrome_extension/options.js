// Catalyst Whisper Coach - Options Script

// Constants
const STORAGE_KEYS = {
    USER_SETTINGS: 'catalyst_user_settings',
    ACTIVE_PROJECT: 'catalyst_active_project',
    SESSION_DATA: 'catalyst_session_data',
    API_TOKEN: 'catalyst_api_token',
    WHISPER_HISTORY: 'catalyst_whisper_history'
};

// Default settings
const DEFAULT_SETTINGS = {
    enabled: true,
    autoAnalysis: true,
    realTimeCoaching: true,
    privacyMode: false,
    analysisFrequency: 'medium', // low, medium, high
    supportedPlatforms: {
        whatsapp: true,
        messenger: true,
        instagram: true,
        facebook: true,
        discord: true,
        slack: true,
        teams: true,
        telegram: true
    },
    notifications: {
        insights: true,
        goals: true,
        milestones: true
    },
    whisperSettings: {
        autoDisplay: true,
        displayDuration: 10, // seconds
        displayMode: 'widget', // widget, popup, inline
        whisperFrequency: 'medium' // low, medium, high
    }
};

// Elements
const elements = {
    // General settings
    enableToggle: document.getElementById('enableToggle'),
    autoAnalysisToggle: document.getElementById('autoAnalysisToggle'),
    realTimeCoachingToggle: document.getElementById('realTimeCoachingToggle'),
    privacyModeToggle: document.getElementById('privacyModeToggle'),

    // Whisper settings
    analysisFrequency: document.getElementById('analysisFrequency'),
    autoDisplayToggle: document.getElementById('autoDisplayToggle'),
    displayDuration: document.getElementById('displayDuration'),
    displayMode: document.getElementById('displayMode'),
    whisperFrequency: document.getElementById('whisperFrequency'),

    // Platform toggles
    platformWhatsapp: document.getElementById('platform-whatsapp'),
    platformMessenger: document.getElementById('platform-messenger'),
    platformInstagram: document.getElementById('platform-instagram'),
    platformFacebook: document.getElementById('platform-facebook'),
    platformDiscord: document.getElementById('platform-discord'),
    platformSlack: document.getElementById('platform-slack'),
    platformTeams: document.getElementById('platform-teams'),
    platformTelegram: document.getElementById('platform-telegram'),

    // Notification toggles
    notificationsInsights: document.getElementById('notifications-insights'),
    notificationsGoals: document.getElementById('notifications-goals'),
    notificationsMilestones: document.getElementById('notifications-milestones'),

    // Buttons
    saveBtn: document.getElementById('saveBtn'),
    resetBtn: document.getElementById('resetBtn'),

    // Messages
    successMessage: document.getElementById('successMessage'),
    errorMessage: document.getElementById('errorMessage')
};

// Event listeners
document.addEventListener('DOMContentLoaded', loadSettings);
elements.saveBtn.addEventListener('click', saveSettings);
elements.resetBtn.addEventListener('click', resetSettings);

// Load settings
async function loadSettings() {
    try {
        // Check authentication
        const isAuthenticated = await checkAuthentication();
        if (!isAuthenticated) {
            showError('Not authenticated. Please log in first.');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
            return;
        }

        // Get settings from storage
        const result = await chrome.storage.sync.get([STORAGE_KEYS.USER_SETTINGS]);
        const settings = result[STORAGE_KEYS.USER_SETTINGS] || DEFAULT_SETTINGS;

        // Apply settings to form
        applySettingsToForm(settings);
    } catch (error) {
        showError(`Failed to load settings: ${error.message}`);
    }
}

// Apply settings to form
function applySettingsToForm(settings) {
    // General settings
    elements.enableToggle.checked = settings.enabled;
    elements.autoAnalysisToggle.checked = settings.autoAnalysis;
    elements.realTimeCoachingToggle.checked = settings.realTimeCoaching;
    elements.privacyModeToggle.checked = settings.privacyMode;

    // Whisper settings
    elements.analysisFrequency.value = settings.analysisFrequency;
    elements.autoDisplayToggle.checked = settings.whisperSettings.autoDisplay;
    elements.displayDuration.value = settings.whisperSettings.displayDuration;
    elements.displayMode.value = settings.whisperSettings.displayMode;
    elements.whisperFrequency.value = settings.whisperSettings.whisperFrequency;

    // Platform toggles
    elements.platformWhatsapp.checked = settings.supportedPlatforms.whatsapp;
    elements.platformMessenger.checked = settings.supportedPlatforms.messenger;
    elements.platformInstagram.checked = settings.supportedPlatforms.instagram;
    elements.platformFacebook.checked = settings.supportedPlatforms.facebook;
    elements.platformDiscord.checked = settings.supportedPlatforms.discord;
    elements.platformSlack.checked = settings.supportedPlatforms.slack;
    elements.platformTeams.checked = settings.supportedPlatforms.teams;
    elements.platformTelegram.checked = settings.supportedPlatforms.telegram;

    // Notification toggles
    elements.notificationsInsights.checked = settings.notifications.insights;
    elements.notificationsGoals.checked = settings.notifications.goals;
    elements.notificationsMilestones.checked = settings.notifications.milestones;
}

// Save settings
async function saveSettings() {
    try {
        // Collect settings from form
        const settings = getSettingsFromForm();

        // Save to storage
        await chrome.storage.sync.set({
            [STORAGE_KEYS.USER_SETTINGS]: settings
        });

        // Notify background script
        await chrome.runtime.sendMessage({
            type: 'UPDATE_SETTINGS',
            data: settings
        });

        showSuccess('Settings saved successfully!');
    } catch (error) {
        showError(`Failed to save settings: ${error.message}`);
    }
}

// Reset settings
async function resetSettings() {
    if (confirm('Reset all settings to default values?')) {
        try {
            // Apply default settings to form
            applySettingsToForm(DEFAULT_SETTINGS);

            // Save default settings
            await chrome.storage.sync.set({
                [STORAGE_KEYS.USER_SETTINGS]: DEFAULT_SETTINGS
            });

            // Notify background script
            await chrome.runtime.sendMessage({
                type: 'UPDATE_SETTINGS',
                data: DEFAULT_SETTINGS
            });

            showSuccess('Settings reset to defaults.');
        } catch (error) {
            showError(`Failed to reset settings: ${error.message}`);
        }
    }
}

// Get settings from form
function getSettingsFromForm() {
    return {
        enabled: elements.enableToggle.checked,
        autoAnalysis: elements.autoAnalysisToggle.checked,
        realTimeCoaching: elements.realTimeCoachingToggle.checked,
        privacyMode: elements.privacyModeToggle.checked,
        analysisFrequency: elements.analysisFrequency.value,
        supportedPlatforms: {
            whatsapp: elements.platformWhatsapp.checked,
            messenger: elements.platformMessenger.checked,
            instagram: elements.platformInstagram.checked,
            facebook: elements.platformFacebook.checked,
            discord: elements.platformDiscord.checked,
            slack: elements.platformSlack.checked,
            teams: elements.platformTeams.checked,
            telegram: elements.platformTelegram.checked
        },
        notifications: {
            insights: elements.notificationsInsights.checked,
            goals: elements.notificationsGoals.checked,
            milestones: elements.notificationsMilestones.checked
        },
        whisperSettings: {
            autoDisplay: elements.autoDisplayToggle.checked,
            displayDuration: parseInt(elements.displayDuration.value, 10) || 10,
            displayMode: elements.displayMode.value,
            whisperFrequency: elements.whisperFrequency.value
        }
    };
}

// Check authentication
async function checkAuthentication() {
    try {
        const result = await chrome.storage.sync.get([STORAGE_KEYS.API_TOKEN]);
        return !!result[STORAGE_KEYS.API_TOKEN];
    } catch (error) {
        console.error('Auth check failed:', error);
        return false;
    }
}

// Show success message
function showSuccess(message) {
    elements.successMessage.textContent = message;
    elements.successMessage.style.display = 'block';
    elements.errorMessage.style.display = 'none';

    setTimeout(() => {
        elements.successMessage.style.display = 'none';
    }, 3000);
}

// Show error message
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorMessage.style.display = 'block';
    elements.successMessage.style.display = 'none';

    setTimeout(() => {
        elements.errorMessage.style.display = 'none';
    }, 3000);
}
