// Catalyst Chrome Extension - Background Script
// Handles extension lifecycle, API communication, and data synchronization

const CATALYST_API_BASE = 'http://localhost:8000';
const STORAGE_KEYS = {
  USER_SETTINGS: 'catalyst_user_settings',
  ACTIVE_PROJECT: 'catalyst_active_project',
  SESSION_DATA: 'catalyst_session_data',
  API_TOKEN: 'catalyst_api_token'
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
    discord: true,
    slack: true,
    teams: true,
    telegram: true
  },
  notifications: {
    insights: true,
    goals: true,
    milestones: true
  }
};

// Extension installation and updates
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('Catalyst extension installed/updated:', details.reason);
  
  if (details.reason === 'install') {
    // First time installation
    await initializeExtension();
    
    // Open welcome page
    chrome.tabs.create({
      url: chrome.runtime.getURL('welcome.html')
    });
  } else if (details.reason === 'update') {
    // Extension updated
    await migrateSettings(details.previousVersion);
  }
});

// Initialize extension with default settings
async function initializeExtension() {
  try {
    await chrome.storage.sync.set({
      [STORAGE_KEYS.USER_SETTINGS]: DEFAULT_SETTINGS,
      [STORAGE_KEYS.SESSION_DATA]: {
        sessionId: generateSessionId(),
        startTime: Date.now(),
        messageCount: 0,
        analysisCount: 0
      }
    });
    
    console.log('Catalyst extension initialized successfully');
  } catch (error) {
    console.error('Failed to initialize extension:', error);
  }
}

// Migrate settings from previous versions
async function migrateSettings(previousVersion) {
  try {
    const result = await chrome.storage.sync.get([STORAGE_KEYS.USER_SETTINGS]);
    const currentSettings = result[STORAGE_KEYS.USER_SETTINGS] || {};
    
    // Merge with new default settings
    const migratedSettings = { ...DEFAULT_SETTINGS, ...currentSettings };
    
    await chrome.storage.sync.set({
      [STORAGE_KEYS.USER_SETTINGS]: migratedSettings
    });
    
    console.log(`Settings migrated from version ${previousVersion}`);
  } catch (error) {
    console.error('Failed to migrate settings:', error);
  }
}

// Handle messages from content scripts and popup
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  console.log('Background received message:', message.type);
  
  switch (message.type) {
    case 'ANALYZE_MESSAGE':
      handleMessageAnalysis(message.data, sender.tab.id)
        .then(sendResponse)
        .catch(error => sendResponse({ error: error.message }));
      return true; // Keep message channel open for async response
      
    case 'GET_SETTINGS':
      getSettings()
        .then(sendResponse)
        .catch(error => sendResponse({ error: error.message }));
      return true;
      
    case 'UPDATE_SETTINGS':
      updateSettings(message.data)
        .then(sendResponse)
        .catch(error => sendResponse({ error: error.message }));
      return true;
      
    case 'GET_ACTIVE_PROJECT':
      getActiveProject()
        .then(sendResponse)
        .catch(error => sendResponse({ error: error.message }));
      return true;
      
    case 'SET_ACTIVE_PROJECT':
      setActiveProject(message.data)
        .then(sendResponse)
        .catch(error => sendResponse({ error: error.message }));
      return true;
      
    case 'GET_WHISPER_SUGGESTION':
      getWhisperSuggestion(message.data)
        .then(sendResponse)
        .catch(error => sendResponse({ error: error.message }));
      return true;
      
    case 'TRACK_EVENT':
      trackEvent(message.data)
        .then(sendResponse)
        .catch(error => sendResponse({ error: error.message }));
      return true;
      
    default:
      console.warn('Unknown message type:', message.type);
      sendResponse({ error: 'Unknown message type' });
  }
});

// Analyze message content
async function handleMessageAnalysis(messageData, tabId) {
  try {
    const settings = await getSettings();
    
    if (!settings.enabled || !settings.autoAnalysis) {
      return { success: false, reason: 'Analysis disabled' };
    }
    
    // Get active project
    const activeProject = await getActiveProject();
    if (!activeProject) {
      return { success: false, reason: 'No active project' };
    }
    
    // Send to Catalyst API for analysis
    const analysisResult = await sendToAPI('/analysis/analyze', {
      text: messageData.text,
      sender: messageData.sender,
      timestamp: messageData.timestamp,
      platform: messageData.platform,
      projectId: activeProject.id,
      context: messageData.context
    });
    
    // Update session data
    await updateSessionData({
      messageCount: 1,
      analysisCount: 1
    });
    
    // Send real-time coaching if enabled
    if (settings.realTimeCoaching && analysisResult.suggestions) {
      await sendWhisperToTab(tabId, analysisResult.suggestions);
    }
    
    return { success: true, analysis: analysisResult };
  } catch (error) {
    console.error('Message analysis failed:', error);
    return { success: false, error: error.message };
  }
}

// Get user settings
async function getSettings() {
  try {
    const result = await chrome.storage.sync.get([STORAGE_KEYS.USER_SETTINGS]);
    return result[STORAGE_KEYS.USER_SETTINGS] || DEFAULT_SETTINGS;
  } catch (error) {
    console.error('Failed to get settings:', error);
    return DEFAULT_SETTINGS;
  }
}

// Update user settings
async function updateSettings(newSettings) {
  try {
    const currentSettings = await getSettings();
    const updatedSettings = { ...currentSettings, ...newSettings };
    
    await chrome.storage.sync.set({
      [STORAGE_KEYS.USER_SETTINGS]: updatedSettings
    });
    
    return { success: true, settings: updatedSettings };
  } catch (error) {
    console.error('Failed to update settings:', error);
    throw error;
  }
}

// Get active project
async function getActiveProject() {
  try {
    const result = await chrome.storage.sync.get([STORAGE_KEYS.ACTIVE_PROJECT]);
    return result[STORAGE_KEYS.ACTIVE_PROJECT] || null;
  } catch (error) {
    console.error('Failed to get active project:', error);
    return null;
  }
}

// Set active project
async function setActiveProject(project) {
  try {
    await chrome.storage.sync.set({
      [STORAGE_KEYS.ACTIVE_PROJECT]: project
    });
    
    return { success: true, project };
  } catch (error) {
    console.error('Failed to set active project:', error);
    throw error;
  }
}

// Get whisper suggestion from API
async function getWhisperSuggestion(context) {
  try {
    const activeProject = await getActiveProject();
    if (!activeProject) {
      throw new Error('No active project');
    }
    
    const suggestion = await sendToAPI('/analysis/whisper-stream', {
      context: context.text,
      sender: context.sender,
      platform: context.platform,
      projectId: activeProject.id,
      urgency: context.urgency || 'normal'
    });
    
    return { success: true, suggestion };
  } catch (error) {
    console.error('Failed to get whisper suggestion:', error);
    throw error;
  }
}

// Send whisper suggestion to content script
async function sendWhisperToTab(tabId, suggestions) {
  try {
    await chrome.tabs.sendMessage(tabId, {
      type: 'SHOW_WHISPER',
      data: { suggestions }
    });
  } catch (error) {
    console.error('Failed to send whisper to tab:', error);
  }
}

// Track events for analytics
async function trackEvent(eventData) {
  try {
    const sessionData = await getSessionData();
    
    const event = {
      ...eventData,
      sessionId: sessionData.sessionId,
      timestamp: Date.now(),
      extensionVersion: chrome.runtime.getManifest().version
    };
    
    // Send to analytics endpoint (if implemented)
    // await sendToAPI('/analytics/track', event);
    
    console.log('Event tracked:', event);
    return { success: true };
  } catch (error) {
    console.error('Failed to track event:', error);
    throw error;
  }
}

// Get session data
async function getSessionData() {
  try {
    const result = await chrome.storage.sync.get([STORAGE_KEYS.SESSION_DATA]);
    return result[STORAGE_KEYS.SESSION_DATA] || {
      sessionId: generateSessionId(),
      startTime: Date.now(),
      messageCount: 0,
      analysisCount: 0
    };
  } catch (error) {
    console.error('Failed to get session data:', error);
    return {
      sessionId: generateSessionId(),
      startTime: Date.now(),
      messageCount: 0,
      analysisCount: 0
    };
  }
}

// Update session data
async function updateSessionData(updates) {
  try {
    const currentData = await getSessionData();
    const updatedData = {
      ...currentData,
      messageCount: currentData.messageCount + (updates.messageCount || 0),
      analysisCount: currentData.analysisCount + (updates.analysisCount || 0)
    };
    
    await chrome.storage.sync.set({
      [STORAGE_KEYS.SESSION_DATA]: updatedData
    });
    
    return updatedData;
  } catch (error) {
    console.error('Failed to update session data:', error);
    throw error;
  }
}

// Send request to Catalyst API
async function sendToAPI(endpoint, data) {
  try {
    const response = await fetch(`${CATALYST_API_BASE}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Extension-Version': chrome.runtime.getManifest().version
      },
      body: JSON.stringify(data)
    });
    
    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
}

// Utility functions
function generateSessionId() {
  return 'session_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}

// Handle extension icon click
chrome.action.onClicked.addListener(async (tab) => {
  // Open Catalyst dashboard in new tab
  chrome.tabs.create({
    url: 'http://localhost:3000'
  });
});

// Handle tab updates to inject content script if needed
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    const settings = await getSettings();
    
    if (!settings.enabled) {
      return;
    }
    
    // Check if this is a supported platform
    const supportedDomains = [
      'web.whatsapp.com',
      'www.messenger.com',
      'discord.com',
      'slack.com',
      'teams.microsoft.com',
      'telegram.org'
    ];
    
    const url = new URL(tab.url);
    if (supportedDomains.some(domain => url.hostname.includes(domain))) {
      try {
        // Inject content script if not already injected
        await chrome.scripting.executeScript({
          target: { tabId: tabId },
          files: ['content_script.js']
        });
        
        console.log('Content script injected into:', url.hostname);
      } catch (error) {
        console.error('Failed to inject content script:', error);
      }
    }
  }
});

// Cleanup on extension shutdown
chrome.runtime.onSuspend.addListener(() => {
  console.log('Catalyst extension suspending...');
  // Perform any necessary cleanup
});

// Handle storage changes
chrome.storage.onChanged.addListener((changes, namespace) => {
  console.log('Storage changed:', changes, namespace);
  
  // Notify content scripts of setting changes
  if (changes[STORAGE_KEYS.USER_SETTINGS]) {
    chrome.tabs.query({}, (tabs) => {
      tabs.forEach(tab => {
        chrome.tabs.sendMessage(tab.id, {
          type: 'SETTINGS_UPDATED',
          data: changes[STORAGE_KEYS.USER_SETTINGS].newValue
        }).catch(() => {
          // Ignore errors for tabs without content script
        });
      });
    });
  }
});

console.log('Catalyst background script loaded');