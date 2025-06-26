// Catalyst Chrome Extension - Background Script
// Handles extension lifecycle, API communication, and data synchronization

import { getExtensionConfig, STORAGE_KEYS, DEFAULT_SETTINGS } from './config/api.config.js';
import { getAIConfig, getOptimalModel, AI_STORAGE_KEYS, CONFIDENCE_THRESHOLDS, SUGGESTION_CATEGORIES, THERAPEUTIC_PATTERNS } from './config/ai.config.js';
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

  // Initialize AI models (Phase 2.2)
  await initializeAIModels();
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

        // AI Model Management (Phase 2.2)
        case 'GET_AI_CONFIG':
          sendResponse(await getAIConfiguration());
          break;

        case 'UPDATE_AI_CONFIG':
          sendResponse(await updateAIConfiguration(data));
          break;

        case 'GET_OPTIMAL_MODEL':
          sendResponse(await getOptimalModelForTask(data));
          break;

        case 'ANALYZE_WITH_AI':
          sendResponse(await analyzeWithAI(data));
          break;

        case 'GET_THERAPEUTIC_INSIGHTS':
          sendResponse(await getTherapeuticInsights(data));
          break;

        case 'GET_CONTEXTUAL_SUGGESTIONS':
          sendResponse(await getContextualSuggestions(data));
          break;

        // Enhanced Phase 2.2 Handlers
        case 'SELECT_OPTIMAL_MODEL':
          sendResponse(await selectOptimalModelForContext(data));
          break;

        case 'LOG_SUGGESTION_USAGE':
          sendResponse(await logSuggestionUsage(data));
          break;

        case 'UPDATE_PERSONALIZED_COACHING':
          sendResponse(await updatePersonalizedCoachingData(data));
          break;

        case 'GET_SUGGESTION_ANALYTICS':
          sendResponse(await getSuggestionAnalytics(data));
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

// Analysis functions (Enhanced with AI Models - Phase 2.2)
async function analyzeMessage(messageData) {
  try {
    // Skip if not enabled
    const settings = await getSettings();
    if (!settings.enabled || !settings.autoAnalysis) {
      return { success: false, message: 'Analysis disabled' };
    }

    // Get AI configuration for context-aware analysis
    const aiConfig = await getAIConfig();

    // Enhanced context preparation
    const enhancedContext = {
      content: messageData.text,
      platform: messageData.platform,
      conversationHistory: messageData.conversationHistory || [],
      urgent: messageData.urgent || false,
      high_stakes: isHighStakesContext(messageData.text),
      privacy_sensitive: isPrivacySensitive(messageData.text),
      task: 'conversation'
    };

    // Select optimal model with enhanced criteria
    const optimalModel = await selectOptimalModel('conversation', enhancedContext);

    // Try enhanced backend analysis first, then fallback to local
    let analysis;
    try {
      analysis = await performEnhancedBackendAnalysis(messageData, optimalModel, aiConfig);
    } catch (error) {
      console.warn('Backend analysis failed, using local analysis:', error);
      analysis = await performEnhancedLocalAnalysis(messageData, optimalModel, aiConfig);
    }

    // Add confidence indicators and model information
    analysis.model_info = {
      model: optimalModel.model,
      provider: optimalModel.provider || 'unknown',
      confidence_indicator: optimalModel.confidence_indicator,
      selection_reason: optimalModel.selection_reason
    };

    // Store for history with enhanced metadata
    await storeWhisperAnalysis({
      text: analysis.primarySuggestion,
      timestamp: new Date().toISOString(),
      messageData,
      analysis,
      confidence: analysis.confidence,
      model_used: optimalModel.model,
      backend_enhanced: analysis.backend_enhanced || false,
      context: enhancedContext
    });

    return {
      success: true,
      analysis,
      model: optimalModel.model,
      confidence: analysis.confidence,
      model_info: analysis.model_info
    };
  } catch (error) {
    console.error('Message analysis failed:', error);
    return { error: error.message };
  }
}

// Enhanced analysis using AI models
async function performEnhancedAnalysis(messageData, model, aiConfig) {
  try {
    // Multi-layer analysis approach
    const results = {
      sentiment: await analyzeSentiment(messageData.text, model),
      therapeutic: await analyzeTherapeuticPatterns(messageData.text),
      contextual: await getContextualAnalysis(messageData, model),
      confidence: 0
    };

    // Generate suggestions based on analysis
    const suggestions = await generateAISuggestions(results, aiConfig);

    // Calculate overall confidence
    results.confidence = calculateOverallConfidence(results, suggestions);

    // Primary suggestion (highest confidence)
    results.primarySuggestion = suggestions.length > 0
      ? suggestions[0].text
      : getSentimentSuggestion(results.sentiment);

    results.suggestions = suggestions;

    return results;
  } catch (error) {
    console.error('Enhanced analysis failed:', error);
    // Fallback to simple analysis
    const sentiment = simpleSentimentAnalysis(messageData.text);
    return {
      sentiment,
      therapeutic: { patterns: [], risk_level: 'low' },
      contextual: { category: 'general', urgency: 'low' },
      suggestions: [{ text: getSentimentSuggestion(sentiment), confidence: 0.5, type: 'sentiment' }],
      confidence: 0.5,
      primarySuggestion: getSentimentSuggestion(sentiment)
    };
  }
}

// Analyze sentiment with AI models
async function analyzeSentiment(text, model) {
  try {
    // For now, use enhanced local analysis until backend AI integration is complete
    const basicSentiment = simpleSentimentAnalysis(text);

    // Enhanced sentiment with emotional context
    const emotionalMarkers = {
      joy: /(happy|excited|love|wonderful|amazing|great)/i.test(text),
      anger: /(angry|furious|mad|hate|stupid|ridiculous)/i.test(text),
      sadness: /(sad|hurt|depressed|disappointed|upset)/i.test(text),
      fear: /(scared|worried|anxious|nervous|afraid)/i.test(text),
      surprise: /(surprised|shocked|unexpected|wow|amazing)/i.test(text)
    };

    return {
      ...basicSentiment,
      emotions: emotionalMarkers,
      confidence: 0.7 + (Object.values(emotionalMarkers).filter(Boolean).length * 0.1)
    };
  } catch (error) {
    console.error('Sentiment analysis failed:', error);
    return simpleSentimentAnalysis(text);
  }
}

// Analyze therapeutic patterns
async function analyzeTherapeuticPatterns(text) {
  const patterns = [];
  let riskLevel = 'low';

  for (const [patternName, pattern] of Object.entries(THERAPEUTIC_PATTERNS)) {
    if (pattern.pattern.test(text)) {
      patterns.push({
        name: patternName,
        severity: pattern.severity,
        intervention: pattern.intervention,
        replacementSuggestion: pattern.replacement_suggestion
      });

      // Update risk level based on severity
      if (pattern.severity === 'critical' || riskLevel === 'low') {
        riskLevel = pattern.severity === 'critical' ? 'critical' :
          pattern.severity === 'high' ? 'high' :
            riskLevel === 'low' ? 'medium' : riskLevel;
      }
    }
  }

  return {
    patterns,
    risk_level: riskLevel,
    confidence: patterns.length > 0 ? 0.8 : 0.3
  };
}

// Get contextual analysis
async function getContextualAnalysis(messageData, model) {
  const text = messageData.text.toLowerCase();

  // Determine conversation category
  let category = 'general';
  let urgency = 'low';

  // Check for relationship categories
  if (/(relationship|love|dating|partner|together)/.test(text)) {
    category = 'relationship';
  } else if (/(work|job|stress|busy|meeting)/.test(text)) {
    category = 'work';
  } else if (/(family|parents|kids|children)/.test(text)) {
    category = 'family';
  } else if (/(conflict|argument|fight|angry|upset)/.test(text)) {
    category = 'conflict';
    urgency = 'high';
  }

  // Determine urgency
  if (/(urgent|emergency|important|serious|breaking up|crisis)/.test(text)) {
    urgency = 'critical';
  } else if (/(soon|quickly|asap|hurry|worried)/.test(text)) {
    urgency = 'high';
  }

  return {
    category,
    urgency,
    platform: messageData.platform || 'unknown',
    confidence: 0.6
  };
}

// Generate AI-powered suggestions
async function generateAISuggestions(analysis, aiConfig) {
  const suggestions = [];
  const confidenceThreshold = CONFIDENCE_THRESHOLDS.suggestions[aiConfig.confidence_level];

  // Generate suggestions based on therapeutic patterns
  if (analysis.therapeutic.patterns.length > 0) {
    for (const pattern of analysis.therapeutic.patterns) {
      if (pattern.replacementSuggestion) {
        suggestions.push({
          text: pattern.intervention,
          confidence: 0.8,
          type: 'therapeutic',
          category: pattern.name,
          urgent: pattern.severity === 'critical'
        });
      }
    }
  }

  // Generate contextual suggestions
  const contextualSuggestions = await getContextualSuggestionsForCategory(
    analysis.contextual.category,
    analysis.sentiment,
    analysis.contextual.urgency
  );

  suggestions.push(...contextualSuggestions);

  // Filter by confidence threshold
  return suggestions
    .filter(s => s.confidence >= confidenceThreshold)
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 3); // Limit to top 3 suggestions
}

// Get contextual suggestions for category
async function getContextualSuggestionsForCategory(category, sentiment, urgency) {
  const suggestions = [];

  // Find matching suggestion categories
  for (const [catName, catData] of Object.entries(SUGGESTION_CATEGORIES[category] || {})) {
    // Check if sentiment/context matches triggers
    const hasMatch = catData.triggers.some(trigger =>
      sentiment.label?.toLowerCase().includes(trigger) ||
      Object.keys(sentiment.emotions || {}).some(emotion =>
        sentiment.emotions[emotion] && trigger.includes(emotion)
      )
    );

    if (hasMatch) {
      // Add suggestions from this category
      catData.suggestions.forEach(suggestion => {
        suggestions.push({
          text: suggestion,
          confidence: catData.confidence_required + (urgency === 'critical' ? 0.2 : urgency === 'high' ? 0.1 : 0),
          type: 'contextual',
          category: catName,
          urgent: urgency === 'critical'
        });
      });
    }
  }

  return suggestions;
}

// Calculate overall confidence
function calculateOverallConfidence(analysis, suggestions) {
  const weights = {
    sentiment: 0.3,
    therapeutic: 0.4,
    contextual: 0.3
  };

  const sentimentConf = analysis.sentiment.confidence || 0.5;
  const therapeuticConf = analysis.therapeutic.confidence || 0.5;
  const contextualConf = analysis.contextual.confidence || 0.5;

  const baseConfidence =
    sentimentConf * weights.sentiment +
    therapeuticConf * weights.therapeutic +
    contextualConf * weights.contextual;

  // Boost confidence if we have high-confidence suggestions
  const suggestionBoost = suggestions.length > 0
    ? Math.min(0.2, suggestions[0].confidence * 0.2)
    : 0;

  return Math.min(0.95, baseConfidence + suggestionBoost);
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

// Enhanced local analysis as fallback
async function performEnhancedLocalAnalysis(messageData, model, aiConfig) {
  try {
    // Multi-layer analysis approach with enhanced context
    const results = {
      sentiment: await analyzeSentiment(messageData.text, model),
      therapeutic: await analyzeTherapeuticPatterns(messageData.text),
      contextual: await getContextualAnalysis(messageData, model),
      communication_style: await analyzeCommunicationStyle(messageData.text),
      emotional_intelligence: await analyzeEmotionalIntelligence(messageData.text),
      confidence: 0
    };

    // Generate suggestions based on enhanced analysis
    const suggestions = await generateAISuggestions(results, aiConfig);

    // Apply personalized coaching patterns
    const personalizedSuggestions = await applyPersonalizedCoaching(suggestions, messageData);

    // Calculate overall confidence with enhanced metrics
    results.confidence = calculateOverallConfidence(results, personalizedSuggestions);

    // Primary suggestion (highest confidence)
    results.primarySuggestion = personalizedSuggestions.length > 0
      ? personalizedSuggestions[0].text
      : getSentimentSuggestion(results.sentiment);

    results.suggestions = personalizedSuggestions;
    results.backend_enhanced = false;

    return results;
  } catch (error) {
    console.error('Enhanced local analysis failed:', error);
    // Ultimate fallback to simple analysis
    const sentiment = simpleSentimentAnalysis(messageData.text);
    return {
      sentiment,
      therapeutic: { patterns: [], risk_level: 'low' },
      contextual: { category: 'general', urgency: 'low' },
      suggestions: [{ text: getSentimentSuggestion(sentiment), confidence: 0.5, type: 'sentiment' }],
      confidence: 0.5,
      primarySuggestion: getSentimentSuggestion(sentiment),
      backend_enhanced: false
    };
  }
}

// Analyze communication style
async function analyzeCommunicationStyle(text) {
  const styles = {
    direct: 0,
    gentle: 0,
    analytical: 0,
    emotional: 0
  };

  const lowerText = text.toLowerCase();

  // Direct style indicators
  if (/\b(clearly|obviously|definitely|exactly|precisely)\b/.test(lowerText)) styles.direct += 0.3;
  if (/\b(need to|have to|must|should)\b/.test(lowerText)) styles.direct += 0.2;
  if (text.split('.').length <= 2 && text.length < 100) styles.direct += 0.2;

  // Gentle style indicators
  if (/\b(maybe|perhaps|possibly|might|could)\b/.test(lowerText)) styles.gentle += 0.3;
  if (/\b(please|thank you|sorry|excuse me)\b/.test(lowerText)) styles.gentle += 0.2;
  if (/\b(i feel|i think|in my opinion)\b/.test(lowerText)) styles.gentle += 0.2;

  // Analytical style indicators
  if (/\b(because|therefore|however|although|furthermore)\b/.test(lowerText)) styles.analytical += 0.3;
  if (/\b(data|analysis|research|study|evidence)\b/.test(lowerText)) styles.analytical += 0.2;
  if (text.split(',').length > 3) styles.analytical += 0.2;

  // Emotional style indicators
  if (/\b(feel|felt|feeling|emotions|heart)\b/.test(lowerText)) styles.emotional += 0.3;
  if (/[!]{2,}/.test(text)) styles.emotional += 0.2;
  if (/\b(love|hate|excited|frustrated|angry|happy|sad)\b/.test(lowerText)) styles.emotional += 0.3;

  const dominantStyle = Object.keys(styles).reduce((a, b) => styles[a] > styles[b] ? a : b);

  return {
    style: dominantStyle,
    scores: styles,
    confidence: Math.max(...Object.values(styles))
  };
}

// Analyze emotional intelligence
async function analyzeEmotionalIntelligence(text) {
  const indicators = {
    self_awareness: 0,
    empathy: 0,
    emotional_regulation: 0,
    social_skills: 0
  };

  const lowerText = text.toLowerCase();

  // Self-awareness indicators
  if (/\b(i feel|i'm feeling|i realize|i understand about myself)\b/.test(lowerText)) indicators.self_awareness += 0.4;
  if (/\b(i need|i want|my)\b/.test(lowerText)) indicators.self_awareness += 0.2;

  // Empathy indicators
  if (/\b(you feel|you might|understand you|your perspective)\b/.test(lowerText)) indicators.empathy += 0.4;
  if (/\b(i can see|i understand|that must be)\b/.test(lowerText)) indicators.empathy += 0.3;

  // Emotional regulation indicators
  if (/\b(let me think|take a breath|calm down|step back)\b/.test(lowerText)) indicators.emotional_regulation += 0.4;
  if (!/\b(angry|furious|hate|stupid|idiot)\b/.test(lowerText)) indicators.emotional_regulation += 0.2;

  // Social skills indicators
  if (/\b(we could|let's|together|compromise)\b/.test(lowerText)) indicators.social_skills += 0.4;
  if (/\b(please|thank you|appreciate|grateful)\b/.test(lowerText)) indicators.social_skills += 0.3;

  const overallScore = Object.values(indicators).reduce((a, b) => a + b, 0) / 4;

  return {
    indicators,
    overall_score: overallScore,
    level: overallScore > 0.7 ? 'high' : overallScore > 0.4 ? 'medium' : 'low'
  };
}

// Context detection helpers
function isHighStakesContext(text) {
  const highStakesKeywords = [
    'breaking up', 'divorce', 'separation', 'ending', 'over between us',
    'serious talk', 'important decision', 'future together', 'marriage',
    'moving in', 'moving out', 'relationship status'
  ];

  const lowerText = text.toLowerCase();
  return highStakesKeywords.some(keyword => lowerText.includes(keyword));
}

function isPrivacySensitive(text) {
  const privacyKeywords = [
    'private', 'confidential', 'secret', 'personal', 'between us',
    'don\'t tell', 'keep this', 'just us', 'private matter'
  ];

  const lowerText = text.toLowerCase();
  return privacyKeywords.some(keyword => lowerText.includes(keyword));
}

function getModelSelectionReason(model, context) {
  if (context.urgent || context.high_stakes) return 'High-stakes conversation requires best quality model';
  if (context.privacy_sensitive) return 'Privacy-sensitive content using secure model';
  if (context.rapid_response) return 'Fast response needed, using optimized model';
  return 'Standard model selection based on strategy';
}

function calculateContextComplexity(context) {
  let complexity = 0;

  if (context.conversationHistory && context.conversationHistory.length > 5) complexity += 0.2;
  if (context.high_stakes) complexity += 0.3;
  if (context.urgent) complexity += 0.1;
  if (context.privacy_sensitive) complexity += 0.1;

  return Math.min(complexity, 1.0);
}

// Get fallback models
async function getFallbackModel(task, currentModel) {
  const aiConfig = await getAIConfig();
  const strategy = MODEL_STRATEGIES[aiConfig.strategy];
  const fallbackProvider = strategy.fallback;

  return AI_MODELS[task]?.[fallbackProvider] || AI_MODELS.conversation[fallbackProvider];
}

async function getHighQualityModel(task) {
  const qualityStrategy = MODEL_STRATEGIES.quality;
  const provider = qualityStrategy[task] || qualityStrategy.fallback;

  return AI_MODELS[task]?.[provider] || AI_MODELS.conversation[provider];
}

async function getPrivacyFriendlyModel(task) {
  const privacyStrategy = MODEL_STRATEGIES.privacy;
  const provider = privacyStrategy[task] || privacyStrategy.fallback;

  return AI_MODELS[task]?.[provider] || AI_MODELS.conversation[provider];
}

// Enhanced Phase 2.2 Handler Functions

// Select optimal model based on context
async function selectOptimalModelForContext(data) {
  try {
    const { context, urgency, complexity } = data;

    // Load AI configuration
    const aiConfig = await getAIConfig();

    // Determine optimal model based on context factors
    let selectedModel = 'local'; // Default fallback

    if (urgency === 'critical') {
      // For critical situations, prioritize speed
      selectedModel = getOptimalModel('speed', context?.type || 'conversation');
    } else if (complexity === 'high') {
      // For complex analysis, prioritize quality
      selectedModel = getOptimalModel('quality', context?.type || 'conversation');
    } else {
      // Balance performance and privacy
      selectedModel = getOptimalModel('balanced', context?.type || 'conversation');
    }

    return {
      model: selectedModel.model || selectedModel,
      provider: selectedModel.provider || 'local',
      confidence: selectedModel.confidence || 0.7,
      latency: selectedModel.latency || 'medium',
      reasoning: `Selected for ${urgency} urgency and ${complexity} complexity`
    };
  } catch (error) {
    console.error('Failed to select optimal model:', error);
    return {
      model: 'local',
      provider: 'local',
      confidence: 0.5,
      latency: 'low',
      reasoning: 'Fallback due to error'
    };
  }
}

// Log suggestion usage for learning and analytics
async function logSuggestionUsage(data) {
  try {
    const { suggestionId, action, context, timestamp } = data;

    // Get existing usage data
    const result = await chrome.storage.local.get(['suggestionUsageLog']);
    const usageLog = result.suggestionUsageLog || [];

    // Add new usage entry
    const usageEntry = {
      suggestionId,
      action, // 'applied', 'dismissed', 'saved'
      context,
      timestamp: timestamp || Date.now(),
      url: context?.url || '',
      platform: context?.platform || 'unknown'
    };

    usageLog.push(usageEntry);

    // Keep only last 1000 entries to prevent storage bloat
    if (usageLog.length > 1000) {
      usageLog.splice(0, usageLog.length - 1000);
    }

    // Save updated log
    await chrome.storage.local.set({ suggestionUsageLog: usageLog });

    // Update personalized patterns if suggestion was successful
    if (action === 'applied') {
      await updateSuccessfulPatterns(suggestionId, context);
    }

    console.log(`Suggestion usage logged: ${action} for ${suggestionId}`);
    return { success: true, logged: usageEntry };
  } catch (error) {
    console.error('Failed to log suggestion usage:', error);
    return { success: false, error: error.message };
  }
}

// Update personalized coaching data based on user interactions
async function updatePersonalizedCoachingData(data) {
  try {
    const { type, updates } = data;

    // Get current coaching data
    const result = await chrome.storage.sync.get(['personalizedCoachingData']);
    const coachingData = result.personalizedCoachingData || {
      communicationStyle: 'neutral',
      preferredTone: 'professional',
      emotionalIntelligenceLevel: 'medium',
      triggerWords: [],
      successfulPatterns: [],
      learningProgress: {}
    };

    // Apply updates based on type
    switch (type) {
      case 'communication_style':
        coachingData.communicationStyle = updates.style;
        break;
      case 'successful_pattern':
        coachingData.successfulPatterns.push(updates.pattern);
        break;
      case 'learning_progress':
        coachingData.learningProgress = {
          ...coachingData.learningProgress,
          ...updates.progress
        };
        break;
      case 'preferences':
        Object.assign(coachingData, updates);
        break;
    }

    // Save updated data
    await chrome.storage.sync.set({ personalizedCoachingData: coachingData });

    console.log(`Personalized coaching data updated: ${type}`);
    return { success: true, data: coachingData };
  } catch (error) {
    console.error('Failed to update personalized coaching data:', error);
    return { success: false, error: error.message };
  }
}

// Get analytics about suggestion usage and effectiveness
async function getSuggestionAnalytics(data) {
  try {
    const { timeRange = '7d', type = 'all' } = data;

    // Get usage log
    const result = await chrome.storage.local.get(['suggestionUsageLog']);
    const usageLog = result.suggestionUsageLog || [];

    // Calculate time range
    const now = Date.now();
    const timeRangeMs = {
      '1d': 24 * 60 * 60 * 1000,
      '7d': 7 * 24 * 60 * 60 * 1000,
      '30d': 30 * 24 * 60 * 60 * 1000
    };
    const cutoffTime = now - (timeRangeMs[timeRange] || timeRangeMs['7d']);

    // Filter log by time range
    const filteredLog = usageLog.filter(entry => entry.timestamp >= cutoffTime);

    // Calculate analytics
    const analytics = {
      totalSuggestions: filteredLog.length,
      appliedSuggestions: filteredLog.filter(e => e.action === 'applied').length,
      dismissedSuggestions: filteredLog.filter(e => e.action === 'dismissed').length,
      savedPatterns: filteredLog.filter(e => e.action === 'saved').length,
      applicationRate: 0,
      topPlatforms: {},
      topSuggestionTypes: {},
      improvementTrend: []
    };

    // Calculate application rate
    if (analytics.totalSuggestions > 0) {
      analytics.applicationRate = (analytics.appliedSuggestions / analytics.totalSuggestions) * 100;
    }

    // Analyze platforms
    filteredLog.forEach(entry => {
      const platform = entry.context?.platform || 'unknown';
      analytics.topPlatforms[platform] = (analytics.topPlatforms[platform] || 0) + 1;
    });

    // Analyze suggestion types
    filteredLog.forEach(entry => {
      const type = entry.context?.type || 'unknown';
      analytics.topSuggestionTypes[type] = (analytics.topSuggestionTypes[type] || 0) + 1;
    });

    return { success: true, analytics };
  } catch (error) {
    console.error('Failed to get suggestion analytics:', error);
    return { success: false, error: error.message };
  }
}

// Helper function to update successful patterns
async function updateSuccessfulPatterns(suggestionId, context) {
  try {
    // This would analyze the suggestion and context to extract reusable patterns
    const pattern = {
      id: suggestionId,
      context: {
        type: context?.type || 'general',
        platform: context?.platform || 'unknown',
        emotionalTension: context?.emotionalTension || 0
      },
      successRate: 1.0, // Initial success
      usageCount: 1,
      lastUsed: Date.now(),
      created: Date.now()
    };

    // Update personalized coaching data
    await updatePersonalizedCoachingData({
      type: 'successful_pattern',
      updates: { pattern }
    });
  } catch (error) {
    console.error('Failed to update successful patterns:', error);
  }
}