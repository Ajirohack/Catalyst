// Catalyst Chrome Extension - Background Script
// Handles extension lifecycle, API communication, and data synchronization

import { getExtensionConfig, STORAGE_KEYS, DEFAULT_SETTINGS } from './config/api.config.js';
import { api } from './lib/api.js';

// Global configuration - will be loaded asynchronously
let EXTENSION_CONFIG = null;

// Initialize configuration
async function initializeConfig() {
  try {
    EXTENSION_CONFIG = await getExtensionConfig();
    console.log('✅ Extension config loaded:', EXTENSION_CONFIG.environment);
  } catch (error) {
    console.error('❌ Failed to load extension config:', error);
    // Fallback to default development config
    EXTENSION_CONFIG = {
      apiBaseUrl: 'http://localhost:8000/api',
      webAppUrl: 'http://localhost:3000',
      environment: 'development',
      debug: true
    };
  }
}

// Get API base URL (with fallback)
const getApiBaseUrl = () => {
  return EXTENSION_CONFIG?.apiBaseUrl || 'http://localhost:8000/api';
};

// Extension installation and updates
chrome.runtime.onInstalled.addListener(async (details) => {
  console.log('Catalyst extension installed/updated:', details.reason);

  // Initialize config first
  await initializeConfig();

  if (details.reason === 'install') {
    // First time installation
    await initializeExtension();

    // Open welcome page
    chrome.tabs.create({
      url: chrome.runtime.getURL('welcome.html')
    });
  } else if (details.reason === 'update') {
    // Extension updated, refresh settings
    await refreshSettings();
  }

  // Setup context menu
  setupContextMenu();
});

// Initialize extension with default settings
async function initializeExtension() {
  try {
    // Get current config
    const config = await getExtensionConfig();

    // Save default settings
    await chrome.storage.sync.set({
      [STORAGE_KEYS.USER_SETTINGS]: DEFAULT_SETTINGS,
      apiBaseUrl: config.apiBaseUrl
    });

    console.log('Extension initialized with default settings');

    // Check if we have a saved token
    const token = await getSavedToken();
    if (token) {
      // Attempt to fetch user data and projects if already logged in
      await fetchUserData(token);
      await fetchProjects(token);
    }
  } catch (error) {
    console.error('Failed to initialize extension:', error);
  }
}

// Fetch user projects from the API
async function fetchProjects(token) {
  try {
    if (!token) {
      console.log('No authentication token, skipping project fetch');
      return;
    }

    // Use the new API client
    const projectsData = await api.projects.list();

    // Save projects to storage
    await chrome.storage.sync.set({
      [STORAGE_KEYS.PROJECT_LIST]: projectsData
    });

    console.log(`Fetched ${projectsData.length} projects`);
    return projectsData;
  } catch (error) {
    console.error('Failed to fetch projects:', error);
    return [];
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

// Message handlers
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  (async () => {
    try {
      const { type, data } = message;

      switch (type) {
        // Settings related
        case 'GET_SETTINGS':
          sendResponse(await getSettings());
          break;

        case 'UPDATE_SETTINGS':
          sendResponse(await updateSettings(data));
          break;

        // Project related
        case 'GET_ACTIVE_PROJECT':
          sendResponse(await getActiveProject());
          break;

        case 'SET_ACTIVE_PROJECT':
          sendResponse(await setActiveProject(data));
          break;

        // Authentication related
        case 'LOGIN_USER':
          sendResponse(await loginUser(data));
          break;

        case 'LOGOUT_USER':
          sendResponse(await logoutUser());
          break;

        case 'CHECK_AUTH':
          sendResponse(await checkAuthentication());
          break;

        // Analysis related
        case 'ANALYZE_MESSAGE':
          sendResponse(await analyzeMessage(data));
          break;

        case 'ANALYZE_WHISPER':
          sendResponse(await analyzeWhisper(data));
          break;

        case 'GET_WHISPER_HISTORY':
          sendResponse(await getWhisperHistory());
          break;

        // Tracking
        case 'TRACK_EVENT':
          sendResponse(await trackEvent(data));
          break;

        default:
          sendResponse({ error: 'Unknown message type' });
      }
    } catch (error) {
      console.error('Error handling message:', error);
      sendResponse({ error: error.message });
    }
  })();

  // Return true to indicate an asynchronous response
  return true;
});

// Settings management
async function getSettings() {
  try {
    const result = await chrome.storage.sync.get([STORAGE_KEYS.USER_SETTINGS]);
    return result[STORAGE_KEYS.USER_SETTINGS] || DEFAULT_SETTINGS;
  } catch (error) {
    console.error('Failed to get settings:', error);
    return DEFAULT_SETTINGS;
  }
}

async function updateSettings(settings) {
  try {
    const currentSettings = await getSettings();
    const updatedSettings = { ...currentSettings, ...settings };

    await chrome.storage.sync.set({
      [STORAGE_KEYS.USER_SETTINGS]: updatedSettings
    });

    // Notify all content scripts about settings update
    const tabs = await chrome.tabs.query({});
    tabs.forEach(tab => {
      try {
        chrome.tabs.sendMessage(tab.id, {
          type: 'SETTINGS_UPDATED',
          data: { enabled: updatedSettings.enabled }
        });
      } catch (e) {
        // Ignore errors for tabs that don't have content scripts
      }
    });

    return { success: true, settings: updatedSettings };
  } catch (error) {
    console.error('Failed to update settings:', error);
    return { error: error.message };
  }
}

// Project management
async function getActiveProject() {
  try {
    const result = await chrome.storage.sync.get([STORAGE_KEYS.ACTIVE_PROJECT]);
    return result[STORAGE_KEYS.ACTIVE_PROJECT] || null;
  } catch (error) {
    console.error('Failed to get active project:', error);
    return null;
  }
}

async function setActiveProject(project) {
  try {
    await chrome.storage.sync.set({
      [STORAGE_KEYS.ACTIVE_PROJECT]: project
    });

    return { success: true, project };
  } catch (error) {
    console.error('Failed to set active project:', error);
    return { error: error.message };
  }
}

// Authentication
async function loginUser(credentials) {
  try {
    const { email, password } = credentials;

    // Use the new API client for authentication
    const data = await api.auth.login({ email, password });

    // Store token and user info
    await chrome.storage.sync.set({
      [STORAGE_KEYS.API_TOKEN]: data.access_token
    });

    return { success: true, user: data.user };
  } catch (error) {
    console.error('Login failed:', error);
    return { error: error.message };
  }
}

async function logoutUser() {
  try {
    // Clear storage data
    await chrome.storage.sync.remove([
      STORAGE_KEYS.API_TOKEN,
      STORAGE_KEYS.USER_SETTINGS,
      STORAGE_KEYS.ACTIVE_PROJECT,
      STORAGE_KEYS.WHISPER_HISTORY
    ]);

    return { success: true };
  } catch (error) {
    console.error('Logout failed:', error);
    return { error: error.message };
  }
}

async function checkAuthentication() {
  try {
    const result = await chrome.storage.sync.get([STORAGE_KEYS.API_TOKEN]);
    return !!result[STORAGE_KEYS.API_TOKEN];
  } catch (error) {
    console.error('Auth check failed:', error);
    return false;
  }
}

// Analysis functions
async function analyzeMessage(messageData) {
  try {
    // Skip if not enabled
    const settings = await getSettings();
    if (!settings.enabled || !settings.autoAnalysis) {
      return { success: false, message: 'Analysis disabled' };
    }

    // For simple in-extension analysis, just use TextBlob-like sentiment
    const sentiment = simpleSentimentAnalysis(messageData.text);

    // Store for history
    await storeWhisperAnalysis({
      text: `Based on sentiment analysis: ${getSentimentSuggestion(sentiment)}`,
      timestamp: new Date().toISOString(),
      messageData,
      sentiment
    });

    return {
      success: true,
      analysis: {
        sentiment,
        suggestions: [
          {
            text: getSentimentSuggestion(sentiment),
            confidence: 0.7,
            type: 'sentiment'
          }
        ]
      }
    };
  } catch (error) {
    console.error('Message analysis failed:', error);
    return { error: error.message };
  }
}

// Function to analyze messages using the backend Whisper service
async function analyzeWhisper(whisperData) {
  try {
    // Skip if not enabled
    const settings = await getSettings();
    if (!settings.enabled || !settings.realTimeCoaching) {
      return { success: false, message: 'Whisper coaching disabled' };
    }

    // Get API token
    const result = await chrome.storage.sync.get([STORAGE_KEYS.API_TOKEN]);
    const token = result[STORAGE_KEYS.API_TOKEN];

    if (!token) {
      return { success: false, message: 'Not authenticated' };
    }

    // Use the new API client for whisper analysis
    const data = await api.analysis.whisper(whisperData);

    // Store in whisper history
    await storeWhisperAnalysis({
      text: data.text,
      timestamp: data.timestamp || new Date().toISOString(),
      project_id: whisperData.project_id,
      platform: whisperData.platform,
      metadata: data.metadata || {}
    });

    return {
      success: true,
      analysis: {
        suggestions: [
          {
            text: data.text,
            confidence: data.metadata?.confidence || 0.8,
            type: 'whisper'
          }
        ],
        metadata: data.metadata
      }
    };
  } catch (error) {
    console.error('Whisper analysis failed:', error);
    return { error: error.message };
  }
}

// Utility: Simple sentiment analysis for fallback
function simpleSentimentAnalysis(text) {
  // Very basic sentiment analysis
  const positiveWords = ['good', 'great', 'happy', 'love', 'excellent', 'amazing', 'wonderful', 'enjoy', 'thanks', 'thank', 'appreciate'];
  const negativeWords = ['bad', 'terrible', 'hate', 'sad', 'angry', 'upset', 'disappointed', 'sorry', 'fail', 'terrible', 'awful'];

  text = text.toLowerCase();
  const words = text.split(/\W+/);

  let positiveCount = 0;
  let negativeCount = 0;

  words.forEach(word => {
    if (positiveWords.includes(word)) {
      positiveCount++;
    } else if (negativeWords.includes(word)) {
      negativeCount++;
    }
  });

  const polarity = (positiveCount - negativeCount) / (words.length || 1);

  return {
    polarity,
    classification: polarity > 0.1 ? 'positive' : polarity < -0.1 ? 'negative' : 'neutral'
  };
}

// Utility: Get suggestion based on sentiment
function getSentimentSuggestion(sentiment) {
  if (sentiment.classification === 'positive') {
    return "Great positive tone! Keep the conversation upbeat.";
  } else if (sentiment.classification === 'negative') {
    return "Consider using more positive language to improve the tone.";
  } else {
    return "Your message is neutral. Consider adding some enthusiasm or personal connection.";
  }
}

// Whisper history management
async function storeWhisperAnalysis(whisperData) {
  try {
    const result = await chrome.storage.sync.get([STORAGE_KEYS.WHISPER_HISTORY]);
    const history = result[STORAGE_KEYS.WHISPER_HISTORY] || [];

    // Add to beginning of array (newest first)
    history.unshift({
      ...whisperData,
      id: Date.now().toString()
    });

    // Limit history size
    const limitedHistory = history.slice(0, 20);

    await chrome.storage.sync.set({
      [STORAGE_KEYS.WHISPER_HISTORY]: limitedHistory
    });

    return { success: true };
  } catch (error) {
    console.error('Failed to store whisper analysis:', error);
    return { error: error.message };
  }
}

async function getWhisperHistory() {
  try {
    const result = await chrome.storage.sync.get([STORAGE_KEYS.WHISPER_HISTORY]);
    return result[STORAGE_KEYS.WHISPER_HISTORY] || [];
  } catch (error) {
    console.error('Failed to get whisper history:', error);
    return [];
  }
}

// Event tracking
async function trackEvent(eventData) {
  try {
    const settings = await getSettings();
    if (!settings.enabled) {
      return { success: false };
    }

    // Get session data
    const result = await chrome.storage.sync.get([STORAGE_KEYS.SESSION_DATA]);
    const sessionData = result[STORAGE_KEYS.SESSION_DATA] || {
      sessionId: generateSessionId(),
      startTime: Date.now(),
      messageCount: 0,
      analysisCount: 0
    };

    // Update session data
    if (eventData.type === 'message_analyzed') {
      sessionData.analysisCount++;
    }

    if (eventData.type.includes('message')) {
      sessionData.messageCount++;
    }

    // Save updated session data
    await chrome.storage.sync.set({
      [STORAGE_KEYS.SESSION_DATA]: sessionData
    });

    // In a real implementation, you might send to a backend
    console.log('Event tracked:', eventData.type, {
      ...eventData,
      sessionId: sessionData.sessionId,
      timestamp: new Date().toISOString()
    });

    return { success: true };
  } catch (error) {
    console.error('Failed to track event:', error);
    return { error: error.message };
  }
}

// Utility: Generate random session ID
function generateSessionId() {
  return 'session_' + Math.random().toString(36).substring(2, 15);
}

// WebSocket connection for real-time whisper coaching
let whisperSocket = null;
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;

async function connectWhisperWebSocket() {
  try {
    const settings = await getSettings();
    if (!settings.enabled || !settings.realTimeCoaching) {
      return;
    }

    // Get API token
    const result = await chrome.storage.sync.get([STORAGE_KEYS.API_TOKEN]);
    const token = result[STORAGE_KEYS.API_TOKEN];

    if (!token) {
      console.log('Catalyst: WebSocket connection skipped - not authenticated');
      return;
    }

    // Generate session ID
    const sessionId = generateSessionId();

    // Connect to WebSocket
    const wsUrl = `${EXTENSION_CONFIG?.wsBaseUrl || getApiBaseUrl().replace('http', 'ws')}/analysis/whisper-ws/${sessionId}`;
    whisperSocket = new WebSocket(wsUrl);

    whisperSocket.onopen = () => {
      console.log('Catalyst: WebSocket connected');
      reconnectAttempts = 0;

      // Send authentication message
      whisperSocket.send(JSON.stringify({
        type: 'authenticate',
        token
      }));
    };

    whisperSocket.onclose = () => {
      console.log('Catalyst: WebSocket disconnected');
      whisperSocket = null;

      // Attempt to reconnect
      if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
        reconnectAttempts++;
        setTimeout(connectWhisperWebSocket, 5000 * reconnectAttempts);
      }
    };

    whisperSocket.onerror = (error) => {
      console.error('Catalyst: WebSocket error:', error);
    };

    whisperSocket.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        handleWhisperWebSocketMessage(message);
      } catch (error) {
        console.error('Catalyst: Failed to parse WebSocket message:', error);
      }
    };
  } catch (error) {
    console.error('Catalyst: Failed to connect WebSocket:', error);
  }
}

function handleWhisperWebSocketMessage(message) {
  switch (message.type) {
    case 'whisper_response':
      // Store whisper
      storeWhisperAnalysis({
        text: message.text,
        timestamp: message.timestamp || new Date().toISOString(),
        project_id: message.project_id,
        platform: message.platform,
        metadata: {}
      });

      // Send to active tab
      notifyActiveTabAboutWhisper(message);
      break;

    case 'error':
      console.error('Catalyst: WebSocket error:', message.error);
      break;

    default:
      console.log('Catalyst: Received WebSocket message:', message);
  }
}

async function notifyActiveTabAboutWhisper(whisperData) {
  try {
    const tabs = await chrome.tabs.query({ active: true });

    if (tabs.length > 0) {
      chrome.tabs.sendMessage(tabs[0].id, {
        type: 'SHOW_WHISPER',
        data: {
          suggestions: [
            {
              text: whisperData.text,
              confidence: 0.9,
              type: 'whisper'
            }
          ]
        }
      });
    }
  } catch (error) {
    console.error('Catalyst: Failed to notify tab about whisper:', error);
  }
}

// Connect WebSocket when extension starts
connectWhisperWebSocket();