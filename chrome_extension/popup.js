// Catalyst Whisper Coach - Popup Script
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication first
    await checkAuthentication();

    // Tab switching
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs and tab contents
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            const tabId = tab.getAttribute('data-tab');
            document.getElementById(`${tabId}-tab`).classList.add('active');

            // Load tab-specific content
            if (tabId === 'suggestions') {
                loadSuggestions();
            } else if (tabId === 'history') {
                loadSuggestionHistory();
            } else if (tabId === 'settings') {
                loadSettings();
            }
        });
    });

    // Toggle extension enabled/disabled
    const enableToggle = document.getElementById('enableToggle');
    enableToggle.addEventListener('change', async () => {
        await updateSettings({ enabled: enableToggle.checked });
    });

    // Refresh suggestions button
    document.getElementById('refresh-btn').addEventListener('click', loadSuggestions);

    // Get suggestion button
    document.getElementById('get-suggestion-btn').addEventListener('click', requestNewSuggestion);

    // Clear history button
    document.getElementById('clear-history-btn').addEventListener('click', clearSuggestionHistory);

    // Save settings button
    document.getElementById('save-settings-btn').addEventListener('click', saveSettings);

    // Logout button
    const logoutBtn = document.createElement('button');
    logoutBtn.textContent = 'Log Out';
    logoutBtn.className = 'btn btn-small btn-secondary';
    logoutBtn.style.marginLeft = '10px';

    logoutBtn.addEventListener('click', async () => {
        if (confirm('Are you sure you want to log out?')) {
            try {
                await sendMessageToBackground('LOGOUT_USER');
                window.location.href = 'login.html';
            } catch (error) {
                console.error('Logout failed:', error);
                alert(`Logout failed: ${error.message}`);
            }
        }
    });

    // Add logout button to header
    const header = document.querySelector('.header');
    header.appendChild(logoutBtn);

    // Initialize
    await loadSettings();
    loadSuggestions();
});

// Check authentication status
async function checkAuthentication() {
    try {
        const isAuthenticated = await sendMessageToBackground('CHECK_AUTH');

        if (!isAuthenticated) {
            // Redirect to login page
            window.location.href = 'login.html';
            return;
        }
    } catch (error) {
        console.error('Authentication check failed:', error);
        window.location.href = 'login.html';
    }
}

// Load suggestions
async function loadSuggestions() {
    const suggestionsContainer = document.getElementById('suggestions-container');
    suggestionsContainer.innerHTML = `<div class="loading"><div class="loading-spinner"></div></div>`;

    try {
        // Get active suggestions
        const response = await sendMessageToBackground('GET_WHISPER_HISTORY');
        const suggestions = response.slice(0, 3); // Get the 3 most recent suggestions

        if (suggestions.length === 0) {
            suggestionsContainer.innerHTML = `
        <div class="empty-state">
          <img src="icons/empty-state.svg" alt="No suggestions">
          <p>No active suggestions</p>
          <p>Try requesting a new suggestion below</p>
        </div>
      `;
            return;
        }

        // Render suggestions
        suggestionsContainer.innerHTML = suggestions.map(suggestion => {
            const date = new Date(suggestion.timestamp);
            const formattedDate = `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;

            return `
        <div class="suggestion">
          <p class="suggestion-text">${suggestion.text}</p>
          <div class="suggestion-meta">
            <span>${suggestion.platform || 'Unknown Platform'}</span>
            <span>${formattedDate}</span>
          </div>
        </div>
      `;
        }).join('');

    } catch (error) {
        console.error('Failed to load suggestions:', error);
        suggestionsContainer.innerHTML = `
      <div class="empty-state">
        <p>Failed to load suggestions</p>
        <p>${error.message}</p>
      </div>
    `;
    }
}

// Load suggestion history
async function loadSuggestionHistory() {
    const historyContainer = document.getElementById('history-container');
    historyContainer.innerHTML = `<div class="loading"><div class="loading-spinner"></div></div>`;

    try {
        // Get suggestion history
        const history = await sendMessageToBackground('GET_WHISPER_HISTORY');

        if (history.length === 0) {
            historyContainer.innerHTML = `
        <div class="empty-state">
          <img src="icons/empty-state.svg" alt="No history">
          <p>No suggestion history</p>
        </div>
      `;
            return;
        }

        // Render history
        historyContainer.innerHTML = history.map(suggestion => {
            const date = new Date(suggestion.timestamp);
            const formattedDate = `${date.toLocaleDateString()} ${date.toLocaleTimeString()}`;

            return `
        <div class="suggestion">
          <p class="suggestion-text">${suggestion.text}</p>
          <div class="suggestion-meta">
            <span>${suggestion.platform || 'Unknown Platform'}</span>
            <span>${formattedDate}</span>
          </div>
        </div>
      `;
        }).join('');

    } catch (error) {
        console.error('Failed to load suggestion history:', error);
        historyContainer.innerHTML = `
      <div class="empty-state">
        <p>Failed to load suggestion history</p>
        <p>${error.message}</p>
      </div>
    `;
    }
}

// Request new suggestion
async function requestNewSuggestion() {
    const contextInput = document.getElementById('context-input');
    const context = contextInput.value.trim();

    if (!context) {
        alert('Please enter conversation context');
        return;
    }

    const getSuggestionBtn = document.getElementById('get-suggestion-btn');
    getSuggestionBtn.textContent = 'Getting Suggestion...';
    getSuggestionBtn.disabled = true;

    try {
        // Get active tab
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        const currentTab = tabs[0];
        const url = new URL(currentTab.url);
        const platform = getPlatformFromUrl(url.hostname);

        // Request suggestion from background script
        const response = await sendMessageToBackground('GET_WHISPER_SUGGESTION', {
            text: context,
            platform: platform,
            urgency: 'normal'
        });

        if (response.error) {
            throw new Error(response.error);
        }

        // Clear input
        contextInput.value = '';

        // Reload suggestions
        loadSuggestions();

    } catch (error) {
        console.error('Failed to get suggestion:', error);
        alert(`Failed to get suggestion: ${error.message}`);
    } finally {
        getSuggestionBtn.textContent = 'Get Suggestion';
        getSuggestionBtn.disabled = false;
    }
}

// Clear suggestion history
async function clearSuggestionHistory() {
    if (!confirm('Are you sure you want to clear all suggestion history?')) {
        return;
    }

    try {
        await sendMessageToBackground('CLEAR_WHISPER_HISTORY');
        loadSuggestionHistory();
    } catch (error) {
        console.error('Failed to clear suggestion history:', error);
        alert(`Failed to clear suggestion history: ${error.message}`);
    }
}

// Load settings
async function loadSettings() {
    try {
        const settings = await sendMessageToBackground('GET_SETTINGS');

        // Update UI with settings
        document.getElementById('enableToggle').checked = settings.enabled;
        document.getElementById('autoAnalysisToggle').checked = settings.autoAnalysis;
        document.getElementById('realTimeCoachingToggle').checked = settings.realTimeCoaching;
        document.getElementById('privacyModeToggle').checked = settings.privacyMode;
        document.getElementById('analysisFrequencySelect').value = settings.analysisFrequency;

        // Whisper settings
        if (settings.whisperSettings) {
            document.getElementById('autoDisplayToggle').checked = settings.whisperSettings.autoDisplay;
            document.getElementById('displayDurationSelect').value = settings.whisperSettings.displayDuration.toString();
            document.getElementById('displayModeSelect').value = settings.whisperSettings.displayMode;
            document.getElementById('whisperFrequencySelect').value = settings.whisperSettings.whisperFrequency;
        }

        // Platform toggles
        if (settings.supportedPlatforms) {
            document.getElementById('whatsappToggle').checked = settings.supportedPlatforms.whatsapp;
            document.getElementById('messengerToggle').checked = settings.supportedPlatforms.messenger;
            document.getElementById('instagramToggle').checked = settings.supportedPlatforms.instagram;
            document.getElementById('discordToggle').checked = settings.supportedPlatforms.discord;
            document.getElementById('slackToggle').checked = settings.supportedPlatforms.slack;
            document.getElementById('teamsToggle').checked = settings.supportedPlatforms.teams;
            document.getElementById('telegramToggle').checked = settings.supportedPlatforms.telegram;
        }

    } catch (error) {
        console.error('Failed to load settings:', error);
    }
}

// Save settings
async function saveSettings() {
    try {
        const newSettings = {
            enabled: document.getElementById('enableToggle').checked,
            autoAnalysis: document.getElementById('autoAnalysisToggle').checked,
            realTimeCoaching: document.getElementById('realTimeCoachingToggle').checked,
            privacyMode: document.getElementById('privacyModeToggle').checked,
            analysisFrequency: document.getElementById('analysisFrequencySelect').value,

            supportedPlatforms: {
                whatsapp: document.getElementById('whatsappToggle').checked,
                messenger: document.getElementById('messengerToggle').checked,
                instagram: document.getElementById('instagramToggle').checked,
                discord: document.getElementById('discordToggle').checked,
                slack: document.getElementById('slackToggle').checked,
                teams: document.getElementById('teamsToggle').checked,
                telegram: document.getElementById('telegramToggle').checked
            },

            whisperSettings: {
                autoDisplay: document.getElementById('autoDisplayToggle').checked,
                displayDuration: parseInt(document.getElementById('displayDurationSelect').value),
                displayMode: document.getElementById('displayModeSelect').value,
                whisperFrequency: document.getElementById('whisperFrequencySelect').value
            }
        };

        await sendMessageToBackground('UPDATE_SETTINGS', newSettings);

        // Show success message
        const saveButton = document.getElementById('save-settings-btn');
        const originalText = saveButton.textContent;
        saveButton.textContent = 'Settings Saved!';

        setTimeout(() => {
            saveButton.textContent = originalText;
        }, 2000);

    } catch (error) {
        console.error('Failed to save settings:', error);
        alert(`Failed to save settings: ${error.message}`);
    }
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

// Get platform from URL
function getPlatformFromUrl(hostname) {
    if (hostname.includes('whatsapp.com')) {
        return 'whatsapp';
    } else if (hostname.includes('messenger.com')) {
        return 'messenger';
    } else if (hostname.includes('instagram.com')) {
        return 'instagram';
    } else if (hostname.includes('facebook.com')) {
        return 'facebook';
    } else if (hostname.includes('discord.com')) {
        return 'discord';
    } else if (hostname.includes('slack.com')) {
        return 'slack';
    } else if (hostname.includes('teams.microsoft.com')) {
        return 'teams';
    } else if (hostname.includes('telegram.org')) {
        return 'telegram';
    } else {
        return 'unknown';
    }
}
