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
            } else if (tabId === 'projects') {
                loadProjects();  // New project tab
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

    // Add project selection functionality
    const projectSelect = document.getElementById('project-select');
    if (projectSelect) {
        projectSelect.addEventListener('change', selectActiveProject);
    }

    // Load projects on startup
    loadProjects();

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

// New functions for project integration
async function loadProjects() {
    const projectsContainer = document.getElementById('projects-list');
    if (!projectsContainer) return;

    projectsContainer.innerHTML = '<div class="loading">Loading projects...</div>';

    try {
        // Get projects from storage or fetch from API
        const result = await chrome.storage.sync.get(['catalyst_project_list', 'catalyst_active_project']);
        const projects = result.catalyst_project_list || [];
        const activeProject = result.catalyst_active_project;

        if (projects.length === 0) {
            projectsContainer.innerHTML = `
                <div class="empty-state">
                    <p>No projects found.</p>
                    <button id="create-project-btn" class="btn primary">Create Project</button>
                    <button id="refresh-projects-btn" class="btn secondary">Refresh</button>
                </div>
            `;

            document.getElementById('create-project-btn').addEventListener('click', () => {
                // Open create project page in new tab
                chrome.tabs.create({ url: chrome.runtime.getURL('create-project.html') });
            });

            document.getElementById('refresh-projects-btn').addEventListener('click', loadProjects);
            return;
        }

        // Render projects list
        projectsContainer.innerHTML = `
            <div class="projects-header">
                <h3>Your Projects</h3>
                <button id="refresh-projects-btn" class="icon-btn" title="Refresh Projects">
                    <i class="fa fa-refresh"></i>
                </button>
            </div>
            <div class="project-select-container">
                <select id="project-select" class="project-select">
                    <option value="">Select a project</option>
                    ${projects.map(p => `
                        <option value="${p.id}" ${activeProject && activeProject.id === p.id ? 'selected' : ''}>
                            ${p.name}
                        </option>
                    `).join('')}
                </select>
            </div>
            <div id="active-project-details" class="project-details ${!activeProject ? 'hidden' : ''}">
                ${activeProject ? `
                    <div class="project-card">
                        <h4>${activeProject.name}</h4>
                        <div class="project-meta">
                            <span class="project-role">${formatRole(activeProject.role)}</span>
                            <span class="project-date">Created: ${formatDate(activeProject.created_at)}</span>
                        </div>
                        <div class="project-actions">
                            <button id="open-project-btn" class="btn secondary">Open in Dashboard</button>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;

        // Add event listeners
        document.getElementById('refresh-projects-btn').addEventListener('click', loadProjects);
        document.getElementById('project-select').addEventListener('change', selectActiveProject);

        if (activeProject) {
            document.getElementById('open-project-btn').addEventListener('click', () => {
                // Get base URL from storage
                chrome.storage.sync.get(['apiBaseUrl'], (result) => {
                    const baseUrl = result.apiBaseUrl || 'http://localhost:8000/api';
                    const frontendUrl = baseUrl.replace('/api', '');
                    chrome.tabs.create({ url: `${frontendUrl}/projects/${activeProject.id}` });
                });
            });
        }
    } catch (error) {
        console.error('Error loading projects:', error);
        projectsContainer.innerHTML = `
            <div class="error-state">
                <p>Failed to load projects. Please try again.</p>
                <button id="retry-projects-btn" class="btn secondary">Retry</button>
            </div>
        `;

        document.getElementById('retry-projects-btn').addEventListener('click', loadProjects);
    }
}

async function selectActiveProject(event) {
    const projectId = event.target.value;
    if (!projectId) {
        // Deselect project
        await chrome.storage.sync.remove(['catalyst_active_project']);
        document.getElementById('active-project-details').classList.add('hidden');
        return;
    }

    try {
        // Get project details from storage
        const result = await chrome.storage.sync.get(['catalyst_project_list']);
        const projects = result.catalyst_project_list || [];
        const selectedProject = projects.find(p => p.id === projectId);

        if (selectedProject) {
            // Save as active project
            await chrome.storage.sync.set({ 'catalyst_active_project': selectedProject });

            // Update UI
            const detailsContainer = document.getElementById('active-project-details');
            detailsContainer.classList.remove('hidden');
            detailsContainer.innerHTML = `
                <div class="project-card">
                    <h4>${selectedProject.name}</h4>
                    <div class="project-meta">
                        <span class="project-role">${formatRole(selectedProject.role)}</span>
                        <span class="project-date">Created: ${formatDate(selectedProject.created_at)}</span>
                    </div>
                    <div class="project-actions">
                        <button id="open-project-btn" class="btn secondary">Open in Dashboard</button>
                    </div>
                </div>
            `;

            document.getElementById('open-project-btn').addEventListener('click', () => {
                // Get base URL from storage
                chrome.storage.sync.get(['apiBaseUrl'], (result) => {
                    const baseUrl = result.apiBaseUrl || 'http://localhost:8000/api';
                    const frontendUrl = baseUrl.replace('/api', '');
                    chrome.tabs.create({ url: `${frontendUrl}/projects/${selectedProject.id}` });
                });
            });
        }
    } catch (error) {
        console.error('Error selecting project:', error);
        alert('Failed to select project. Please try again.');
    }
}

// Helper functions
function formatRole(role) {
    switch (role) {
        case 'coach': return 'Conversation Coach';
        case 'therapist': return 'Communication Therapist';
        case 'strategist': return 'Dialogue Strategist';
        default: return role;
    }
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString();
}

// Fix for popup.js - need to close the loadPlatformSpecificFeatures function
async function loadPlatformSpecificFeatures() {
    try {
        // Get current tab URL
        const tabs = await chrome.tabs.query({ active: true, currentWindow: true });
        const url = tabs[0]?.url || '';
        const hostname = new URL(url).hostname;

        // Platform-specific UI adjustments
        if (hostname.includes('web.whatsapp.com')) {
            // WhatsApp specific features
            document.getElementById('platform-name').textContent = 'WhatsApp Web';
            document.getElementById('platform-icon').className = 'fab fa-whatsapp';

            // Show WhatsApp specific settings
            document.querySelectorAll('.whatsapp-feature').forEach(el => {
                el.style.display = 'block';
            });
        } else if (hostname.includes('discord.com')) {
            // Discord specific features
            document.getElementById('platform-name').textContent = 'Discord';
            document.getElementById('platform-icon').className = 'fab fa-discord';
        } else if (hostname.includes('messenger.com') || hostname.includes('facebook.com')) {
            // Messenger specific features
            document.getElementById('platform-name').textContent = 'Messenger';
            document.getElementById('platform-icon').className = 'fab fa-facebook-messenger';
        } else if (hostname.includes('teams.microsoft.com')) {
            // Microsoft Teams specific features
            document.getElementById('platform-name').textContent = 'Microsoft Teams';
            document.getElementById('platform-icon').className = 'fab fa-microsoft';
        } else if (hostname.includes('slack.com')) {
            // Slack specific features
            document.getElementById('platform-name').textContent = 'Slack';
            document.getElementById('platform-icon').className = 'fab fa-slack';
        } else {
            // Generic or unsupported platform
            document.getElementById('platform-name').textContent = 'Current Site';
            document.getElementById('platform-icon').className = 'fas fa-globe';

            // Show unsupported message
            document.getElementById('platform-support-message').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading platform features:', error);
    }
}
