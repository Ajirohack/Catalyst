// Catalyst Chrome Extension - Content Script
// Reads chat DOM elements and streams conversation data to backend

(function () {
  'use strict';

  // Prevent multiple injections
  if (window.catalystInjected) {
    return;
  }
  window.catalystInjected = true;

  console.log('Catalyst content script loaded on:', window.location.hostname);

  // Configuration
  const CONFIG = {
    debounceDelay: 1000, // ms to wait before processing new messages
    maxMessageLength: 5000, // max characters to analyze
    retryAttempts: 3,
    retryDelay: 1000
  };

  // State management
  let isEnabled = true;
  let activeProject = null;
  let lastProcessedMessage = null;
  let messageObserver = null;
  let whisperWidget = null;
  let processingQueue = [];
  let isProcessing = false;
  let apiBaseUrl = '';
  let therapeuticInsightsEnabled = true;
  let realTimeAnalysisEnabled = true;

  // Enhanced state for Phase 2.2
  let currentAIModel = null;
  let suggestionContext = {};
  let personalizedCoachingData = {};
  let contextualInsightsQueue = [];

  // Phase 2.2: Enhanced suggestion system settings
  let contextAwareMode = true;
  let therapeuticHintsEnabled = true;
  let personalizedCoachingEnabled = true;

  // Import platform selectors from external file if available
  // This is loaded via the manifest.json before content_script.js
  const PLATFORM_SELECTORS = window.PLATFORM_SELECTORS || {
    // Fallback to default selectors if the external file failed to load
    'web.whatsapp.com': {
      messageContainer: '[data-testid="conversation-panel-messages"]',
      messages: '[data-testid="msg-container"]',
      messageText: '.selectable-text span',
      sender: '[data-testid="msg-meta"] span[dir="auto"]',
      timestamp: '[data-testid="msg-meta"] span[title]',
      inputField: '[data-testid="conversation-compose-box-input"]',
      sendButton: '[data-testid="compose-btn-send"]'
    },
    'chat.openai.com': {
      messageContainer: '.react-scroll-to-bottom--css-gqgbgc-79elbk',
      messages: '.group.w-full',
      messageText: '.markdown',
      sender: '.font-semibold',
      timestamp: '.text-gray-400.text-xs',
      inputField: '#prompt-textarea',
      sendButton: 'button[data-testid="send-button"]'
    },
    'mail.google.com': { // Gmail
      messageContainer: '.adn.ads',
      messages: '.gs',
      messageText: '.a3s.aiL',
      sender: '.gD',
      timestamp: '.g3',
      inputField: '[role="textbox"][aria-label*="Body"]',
      sendButton: '[data-tooltip="Send"]'
    },
    'linkedin.com': {
      messageContainer: '.msg-conversations-container__conversations-list',
      messages: '.msg-s-message-list__event',
      messageText: '.msg-s-event-listitem__body',
      sender: '.msg-s-message-group__name',
      timestamp: '.msg-s-message-group__timestamp',
      inputField: '.msg-form__contenteditable',
      sendButton: '.msg-form__send-button'
    },
    'twitter.com': {
      messageContainer: '[data-testid="DMDrawer"] [role="region"]',
      messages: '[data-testid="messageEntry"]',
      messageText: '[data-testid="tweetText"]',
      sender: '[data-testid="User-Name"]',
      timestamp: '[data-testid="timestamp"]',
      inputField: '[data-testid="dmComposerTextInput"]',
      sendButton: '[data-testid="dmComposerSendButton"]'
    },
    'outlook.live.com': {
      messageContainer: '[role="main"]',
      messages: '.ItemBody',
      messageText: '.ReadMsgBody',
      sender: '.ItemAddress',
      timestamp: '.ItemDate',
      inputField: '[contenteditable="true"][role="textbox"]',
      sendButton: '[title="Send"]'
    },
    'reddit.com': {
      messageContainer: '.ModeratorChatThreadPage',
      messages: '.ChatMessage',
      messageText: '.ChatMessage__body',
      sender: '.ChatMessage__author',
      timestamp: '.ChatMessage__timestamp',
      inputField: '.ChatInput__textarea',
      sendButton: 'button[type="submit"]'
    },
    'telegram.org': {
      messageContainer: '.messages-container',
      messages: '.message',
      messageText: '.message-content',
      sender: '.peer-title',
      timestamp: '.time',
      inputField: '#editable-message-text',
      sendButton: '.btn-send'
    }
  };

  // Get current platform
  const currentPlatform = window.location.hostname;
  const selectors = PLATFORM_SELECTORS[currentPlatform];

  if (!selectors) {
    console.warn('Catalyst: Unsupported platform:', currentPlatform);
    return;
  }

  // Initialize content script
  async function initialize() {
    try {
      // Get settings from background script
      const response = await sendMessageToBackground('GET_SETTINGS');
      if (response.error) {
        throw new Error(response.error);
      }

      isEnabled = response.enabled;
      therapeuticInsightsEnabled = response.therapeuticInsights !== false;
      realTimeAnalysisEnabled = response.realTimeAnalysis !== false;

      if (!isEnabled) {
        console.log('Catalyst: Extension disabled');
        return;
      }

      // Get active project
      const projectResponse = await sendMessageToBackground('GET_ACTIVE_PROJECT');
      activeProject = projectResponse.error ? null : projectResponse;

      // Initialize therapeutic insights if enabled
      if (therapeuticInsightsEnabled && window.catalystTherapeuticInsights) {
        window.catalystTherapeuticInsights.initialize();
      }

      // Start monitoring messages
      startMessageMonitoring();

      // Create whisper widget
      createWhisperWidget();

      // Listen for background messages
      chrome.runtime.onMessage.addListener(handleBackgroundMessage);

      console.log('Catalyst: Content script initialized successfully');
    } catch (error) {
      console.error('Catalyst: Failed to initialize:', error);
    }
  }

  // Start monitoring for new messages
  function startMessageMonitoring() {
    const messageContainer = document.querySelector(selectors.messageContainer);

    if (!messageContainer) {
      console.warn('Catalyst: Message container not found, retrying...');
      setTimeout(startMessageMonitoring, 2000);
      return;
    }

    // Create mutation observer
    messageObserver = new MutationObserver(debounce(handleDOMChanges, CONFIG.debounceDelay));

    messageObserver.observe(messageContainer, {
      childList: true,
      subtree: true,
      characterData: true
    });

    console.log('Catalyst: Message monitoring started');
  }

  // Handle DOM changes
  function handleDOMChanges(mutations) {
    if (!isEnabled || !activeProject) {
      return;
    }

    mutations.forEach(mutation => {
      if (mutation.type === 'childList') {
        mutation.addedNodes.forEach(node => {
          if (node.nodeType === Node.ELEMENT_NODE) {
            const messages = node.matches && node.matches(selectors.messages)
              ? [node]
              : node.querySelectorAll(selectors.messages);

            messages.forEach(processMessage);
          }
        });
      }
    });
  }

  // Process individual message
  async function processMessage(messageElement) {
    try {
      const messageData = extractMessageData(messageElement);

      if (!messageData || !messageData.text || messageData.text === lastProcessedMessage) {
        return;
      }

      lastProcessedMessage = messageData.text;

      // Process with therapeutic insights if enabled
      if (therapeuticInsightsEnabled && window.catalystTherapeuticInsights) {
        window.catalystTherapeuticInsights.processMessage(messageData.text, messageData.sender, messageData.timestamp);
      }

      // Real-time analysis for conflict detection
      if (realTimeAnalysisEnabled) {
        await performRealTimeAnalysis(messageData);
      }

      // Add to processing queue
      processingQueue.push(messageData);

      // Process queue if not already processing
      if (!isProcessing) {
        processMessageQueue();
      }
    } catch (error) {
      console.error('Catalyst: Failed to process message:', error);
    }
  }

  // Process message queue
  async function processMessageQueue() {
    if (isProcessing || processingQueue.length === 0) {
      return;
    }

    isProcessing = true;

    while (processingQueue.length > 0) {
      const messageData = processingQueue.shift();

      try {
        // Get recent conversation history for context
        const conversationHistory = await getConversationHistory();

        // Analyze message with conversation context
        await analyzeMessageWithContext(messageData, conversationHistory);
      } catch (error) {
        console.error('Catalyst: Failed to analyze message:', error);
      }

      // Small delay between processing
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    isProcessing = false;
  }

  // Get recent conversation history
  async function getConversationHistory(limit = 10) {
    try {
      const messages = document.querySelectorAll(selectors.messages);
      const history = [];

      // Process the last 'limit' messages (or fewer if not available)
      const startIdx = Math.max(0, messages.length - limit);

      for (let i = startIdx; i < messages.length; i++) {
        const messageData = extractMessageData(messages[i]);
        if (messageData) {
          history.push({
            content: messageData.text,
            sender: messageData.sender,
            timestamp: messageData.timestamp,
            platform: currentPlatform
          });
        }
      }

      return history;
    } catch (error) {
      console.error('Catalyst: Failed to get conversation history:', error);
      return [];
    }
  }

  // Send message for analysis with conversation context
  async function analyzeMessageWithContext(messageData, conversationHistory) {
    try {
      // Initialize enhanced suggestion system if needed
      if (!personalizedCoachingData.communicationStyle) {
        await initializeEnhancedSuggestionSystem();
      }

      // Generate context-aware suggestions
      const suggestions = await generateContextAwareSuggestions(messageData, conversationHistory);

      // Process suggestions and show enhanced UI
      if (suggestions.length > 0) {
        showEnhancedSuggestions(suggestions, {
          model: currentAIModel,
          confidence: Math.max(...suggestions.map(s => s.confidence)),
          timestamp: Date.now()
        });
      }

      // Send to background for backend analysis (existing functionality)
      const analysisResponse = await sendMessageToBackground('ANALYZE_MESSAGE', {
        messageData,
        conversationHistory,
        activeProject: activeProject?.id,
        analysis_type: 'enhanced_ai',
        context: suggestionContext
      });

      if (analysisResponse && !analysisResponse.error) {
        await handleEnhancedAnalysisResults(analysisResponse, messageData);
      }

    } catch (error) {
      console.error('Catalyst: Failed to analyze message with enhanced context:', error);
    }
  }

  async function handleEnhancedAnalysisResults(analysisResponse, messageData) {
    const { analysis, confidence, model } = analysisResponse;

    // Update current model info
    currentAIModel = model;
    updateModelIndicator();

    // Handle different types of analysis results
    if (analysis.suggestions && analysis.suggestions.length > 0) {
      const enhancedSuggestions = analysis.suggestions.map(suggestion => ({
        ...suggestion,
        id: `backend_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        source: 'backend_ai',
        model: model,
        confidence: suggestion.confidence || confidence
      }));

      // Merge with any existing suggestions
      const existingSuggestions = Array.from(document.querySelectorAll('.catalyst-suggestion'))
        .map(el => el.dataset.suggestionId);

      const newSuggestions = enhancedSuggestions.filter(s =>
        !existingSuggestions.includes(s.id));

      if (newSuggestions.length > 0) {
        showEnhancedSuggestions(newSuggestions, {
          model: model,
          confidence: confidence,
          source: 'backend'
        });
      }
    }

    // Handle therapeutic insights
    if (analysis.therapeutic && analysis.therapeutic.risk_level !== 'low') {
      await handleTherapeuticInsights(analysis.therapeutic, messageData);
    }

    // Update context for future suggestions
    suggestionContext = {
      ...suggestionContext,
      lastAnalysis: analysis,
      lastConfidence: confidence,
      lastModel: model,
      timestamp: Date.now()
    };
  }

  // Enhanced suggestion system methods for Phase 2.2
  // Context-aware suggestions with therapeutic intervention hints

  // Initialize enhanced suggestion system
  async function initializeEnhancedSuggestionSystem() {
    try {
      // Load personalized coaching data from storage
      const result = await chrome.storage.sync.get(['personalizedCoachingData', 'suggestionPreferences']);
      personalizedCoachingData = result.personalizedCoachingData || {
        communicationStyle: 'neutral',
        preferredTone: 'professional',
        emotionalIntelligenceLevel: 'medium',
        triggerWords: [],
        successfulPatterns: [],
        learningProgress: {}
      };

      // Initialize suggestion context
      suggestionContext = {
        conversationFlow: [],
        emotionalState: 'neutral',
        communicationPatterns: [],
        riskFactors: [],
        positiveReinforcement: []
      };

      console.log('Enhanced suggestion system initialized');
    } catch (error) {
      console.error('Failed to initialize enhanced suggestion system:', error);
    }
  }

  // Generate context-aware suggestions
  async function generateContextAwareSuggestions(messageData, conversationHistory) {
    if (!contextAwareMode) return [];

    try {
      // Analyze conversation context
      const context = await analyzeConversationContext(messageData, conversationHistory);

      // Get AI model recommendation
      const modelResponse = await sendMessageToBackground('SELECT_OPTIMAL_MODEL', {
        context: context.type,
        urgency: context.urgency,
        complexity: context.complexity
      });

      currentAIModel = modelResponse.model || 'local';

      // Generate suggestions based on context
      const suggestions = [];

      // Emotional intelligence suggestions
      if (context.emotionalTension > 0.6) {
        suggestions.push(...generateEmotionalIntelligenceSuggestions(context));
      }

      // Communication style improvements
      if (context.communicationIssues.length > 0) {
        suggestions.push(...generateCommunicationStyleSuggestions(context));
      }

      // Therapeutic intervention hints
      if (therapeuticHintsEnabled && context.riskLevel !== 'low') {
        suggestions.push(...generateTherapeuticInterventionHints(context));
      }

      // Personalized coaching patterns
      if (personalizedCoachingEnabled) {
        suggestions.push(...generatePersonalizedCoachingPatterns(context, messageData));
      }

      // Platform-specific suggestions
      suggestions.push(...generatePlatformSpecificSuggestions(context, currentPlatform));

      return suggestions.filter(s => s.confidence >= 0.5);
    } catch (error) {
      console.error('Failed to generate context-aware suggestions:', error);
      return [];
    }
  }

  // Analyze conversation context for enhanced suggestions
  async function analyzeConversationContext(messageData, conversationHistory) {
    const context = {
      type: 'general',
      urgency: 'low',
      complexity: 'medium',
      emotionalTension: 0,
      communicationIssues: [],
      riskLevel: 'low',
      participants: new Set(),
      timePattern: 'normal',
      topicShifts: 0
    };

    // Analyze participants
    conversationHistory.forEach(msg => context.participants.add(msg.sender));

    // Detect emotional tension
    const emotionalWords = ['angry', 'frustrated', 'upset', 'confused', 'stressed', 'worried'];
    const tensionScore = emotionalWords.reduce((score, word) => {
      const regex = new RegExp(word, 'gi');
      return score + (messageData.text.match(regex) || []).length;
    }, 0);
    context.emotionalTension = Math.min(tensionScore / 5, 1);

    // Detect communication issues
    if (messageData.text.includes('?') && messageData.text.split('?').length > 3) {
      context.communicationIssues.push('excessive_questioning');
    }
    if (messageData.text.toUpperCase() === messageData.text && messageData.text.length > 10) {
      context.communicationIssues.push('caps_lock_usage');
    }
    if (messageData.text.split('!').length > 3) {
      context.communicationIssues.push('excessive_exclamation');
    }

    // Assess risk level
    const riskKeywords = ['suicide', 'harm', 'hurt', 'kill', 'die', 'end it all'];
    const hasRiskKeywords = riskKeywords.some(keyword =>
      messageData.text.toLowerCase().includes(keyword));

    if (hasRiskKeywords) {
      context.riskLevel = 'high';
      context.urgency = 'critical';
    } else if (context.emotionalTension > 0.7) {
      context.riskLevel = 'medium';
      context.urgency = 'high';
    }

    // Determine conversation type
    if (context.participants.size === 2) {
      context.type = 'private';
    } else if (context.participants.size > 10) {
      context.type = 'large_group';
    } else {
      context.type = 'group';
    }

    return context;
  }

  // Generate emotional intelligence suggestions
  function generateEmotionalIntelligenceSuggestions(context) {
    const suggestions = [];

    if (context.emotionalTension > 0.8) {
      suggestions.push({
        id: `ei_deescalation_${Date.now()}`,
        type: 'emotional_intelligence',
        category: 'de-escalation',
        title: 'De-escalation Suggestion',
        content: 'Consider acknowledging the other person\'s feelings before presenting your viewpoint. This can help reduce tension.',
        confidence: 0.85,
        reasoning: 'High emotional tension detected',
        actionable: true,
        urgency: 'high'
      });
    }

    if (context.communicationIssues.includes('excessive_questioning')) {
      suggestions.push({
        id: `ei_questioning_${Date.now()}`,
        type: 'emotional_intelligence',
        category: 'communication_style',
        title: 'Question Management',
        content: 'Try grouping related questions together or prioritizing the most important ones to avoid overwhelming the conversation.',
        confidence: 0.75,
        reasoning: 'Excessive questioning pattern detected',
        actionable: true,
        urgency: 'medium'
      });
    }

    return suggestions;
  }

  // Generate therapeutic intervention hints
  function generateTherapeuticInterventionHints(context) {
    const hints = [];

    if (context.riskLevel === 'high') {
      hints.push({
        id: `therapeutic_crisis_${Date.now()}`,
        type: 'therapeutic_intervention',
        category: 'crisis_support',
        title: 'Crisis Support Needed',
        content: 'This conversation may require professional intervention. Consider suggesting crisis support resources.',
        confidence: 0.95,
        reasoning: 'High-risk language detected',
        actionable: true,
        urgency: 'critical',
        resources: [
          { name: 'National Suicide Prevention Lifeline', contact: '988' },
          { name: 'Crisis Text Line', contact: 'Text HOME to 741741' }
        ]
      });
    }

    if (context.emotionalTension > 0.6 && context.type === 'private') {
      hints.push({
        id: `therapeutic_active_listening_${Date.now()}`,
        type: 'therapeutic_intervention',
        category: 'active_listening',
        title: 'Active Listening Opportunity',
        content: 'This seems like a good moment to practice reflective listening. Try paraphrasing what you\'ve heard.',
        confidence: 0.7,
        reasoning: 'Emotional conversation in private setting',
        actionable: true,
        urgency: 'medium'
      });
    }

    return hints;
  }

  // Generate personalized coaching patterns
  function generatePersonalizedCoachingPatterns(context, messageData) {
    const patterns = [];

    // Check against user's historical successful patterns
    const successfulPattern = personalizedCoachingData.successfulPatterns.find(pattern =>
      pattern.context.type === context.type &&
      pattern.context.emotionalTension >= context.emotionalTension - 0.2
    );

    if (successfulPattern) {
      patterns.push({
        id: `coaching_successful_pattern_${Date.now()}`,
        type: 'personalized_coaching',
        category: 'proven_strategy',
        title: 'Proven Strategy Available',
        content: successfulPattern.suggestion,
        confidence: successfulPattern.successRate,
        reasoning: `Similar situation resolved successfully ${successfulPattern.usageCount} times`,
        actionable: true,
        urgency: 'medium',
        personalizedData: {
          previousSuccess: true,
          successRate: successfulPattern.successRate,
          lastUsed: successfulPattern.lastUsed
        }
      });
    }

    // Adaptive coaching based on communication style
    if (personalizedCoachingData.communicationStyle === 'direct' && context.emotionalTension > 0.5) {
      patterns.push({
        id: `coaching_style_adaptation_${Date.now()}`,
        type: 'personalized_coaching',
        category: 'style_adaptation',
        title: 'Communication Style Adjustment',
        content: 'Based on your direct communication style, consider softening your approach in this emotional situation.',
        confidence: 0.8,
        reasoning: 'Personal communication style vs. current context mismatch',
        actionable: true,
        urgency: 'medium'
      });
    }

    return patterns;
  }

  // Generate platform-specific suggestions
  function generatePlatformSpecificSuggestions(context, platform) {
    const suggestions = [];

    switch (platform) {
      case 'web.whatsapp.com':
        if (context.type === 'group' && context.emotionalTension > 0.6) {
          suggestions.push({
            id: `platform_whatsapp_group_${Date.now()}`,
            type: 'platform_specific',
            category: 'group_management',
            title: 'WhatsApp Group Etiquette',
            content: 'Consider moving this sensitive conversation to a private chat to avoid group dynamics escalation.',
            confidence: 0.75,
            reasoning: 'Emotional conversation in WhatsApp group',
            actionable: true,
            urgency: 'medium'
          });
        }
        break;

      case 'linkedin.com':
        if (context.emotionalTension > 0.4) {
          suggestions.push({
            id: `platform_linkedin_professional_${Date.now()}`,
            type: 'platform_specific',
            category: 'professional_tone',
            title: 'Professional Context Reminder',
            content: 'Remember this is a professional platform. Consider maintaining a diplomatic tone.',
            confidence: 0.85,
            reasoning: 'Emotional content on professional platform',
            actionable: true,
            urgency: 'high'
          });
        }
        break;

      case 'twitter.com':
        if (messageData.text.length > 240) {
          suggestions.push({
            id: `platform_twitter_length_${Date.now()}`,
            type: 'platform_specific',
            category: 'content_optimization',
            title: 'Twitter Thread Suggestion',
            content: 'Consider breaking this into a thread for better readability and engagement.',
            confidence: 0.8,
            reasoning: 'Long content for Twitter format',
            actionable: true,
            urgency: 'low'
          });
        }
        break;
    }

    return suggestions;
  }

  // Enhanced UI for displaying suggestions with confidence indicators
  function showEnhancedSuggestions(suggestions, metadata) {
    if (!whisperWidget) {
      createEnhancedWhisperWidget();
    }

    // Clear previous content
    const suggestionsContainer = whisperWidget.querySelector('.catalyst-suggestions-container');
    if (suggestionsContainer) {
      suggestionsContainer.innerHTML = '';
    }

    // Add header with AI model info
    const headerElement = createSuggestionHeader(metadata);
    suggestionsContainer.appendChild(headerElement);

    // Group suggestions by type for better organization
    const groupedSuggestions = groupSuggestionsByType(suggestions);

    // Create suggestion groups
    Object.entries(groupedSuggestions).forEach(([type, typeSuggestions]) => {
      const groupElement = createSuggestionGroup(type, typeSuggestions);
      suggestionsContainer.appendChild(groupElement);
    });

    // Show widget with enhanced animation
    showWhisperWidgetWithAnimation();

    // Auto-hide based on urgency
    const maxUrgency = Math.max(...suggestions.map(s => getUrgencyLevel(s.urgency)));
    const hideDelay = maxUrgency >= 3 ? 15000 : 10000; // Keep critical suggestions longer

    setTimeout(() => {
      hideWhisperWidget();
    }, hideDelay);
  }

  // Create enhanced whisper widget with confidence indicators
  function createEnhancedWhisperWidget() {
    // Remove existing widget if present
    if (whisperWidget) {
      whisperWidget.remove();
    }

    whisperWidget = document.createElement('div');
    whisperWidget.className = 'catalyst-whisper-widget enhanced';
    whisperWidget.id = 'catalyst-whisper-widget';

    whisperWidget.innerHTML = `
    <div class="catalyst-widget-header">
      <div class="catalyst-logo">
        <img src="${chrome.runtime.getURL('icons/catalyst-icon-48.png')}" alt="Catalyst" />
        <span>Catalyst AI Coach</span>
      </div>
      <div class="catalyst-model-indicator">
        <span class="model-name">AI Model: <span id="current-model">Loading...</span></span>
        <div class="confidence-indicator">
          <span class="confidence-label">Confidence:</span>
          <div class="confidence-bar">
            <div class="confidence-fill" id="confidence-fill"></div>
          </div>
          <span class="confidence-value" id="confidence-value">--</span>
        </div>
      </div>
      <button class="catalyst-close-btn" id="catalyst-close-btn">×</button>
    </div>
    <div class="catalyst-suggestions-container">
      <div class="catalyst-loading">
        <div class="loading-spinner"></div>
        <span>Analyzing conversation...</span>
      </div>
    </div>
    <div class="catalyst-widget-footer">
      <div class="catalyst-controls">
        <button class="catalyst-btn toggle-hints" id="toggle-therapeutic-hints">
          <span class="btn-icon">🏥</span>
          <span class="btn-text">Therapeutic Hints</span>
        </button>
        <button class="catalyst-btn toggle-coaching" id="toggle-personalized-coaching">
          <span class="btn-icon">🎯</span>
          <span class="btn-text">Personal Coaching</span>
        </button>
        <button class="catalyst-btn toggle-context" id="toggle-context-aware">
          <span class="btn-icon">🧠</span>
          <span class="btn-text">Context Aware</span>
        </button>
      </div>
    </div>
  `;

    // Add event listeners
    whisperWidget.querySelector('#catalyst-close-btn').addEventListener('click', hideWhisperWidget);
    whisperWidget.querySelector('#toggle-therapeutic-hints').addEventListener('click', toggleTherapeuticHints);
    whisperWidget.querySelector('#toggle-personalized-coaching').addEventListener('click', togglePersonalizedCoaching);
    whisperWidget.querySelector('#toggle-context-aware').addEventListener('click', toggleContextAware);

    // Apply enhanced styles
    applyEnhancedWidgetStyles();

    // Position widget
    positionWidget();

    document.body.appendChild(whisperWidget);
    console.log('Enhanced Catalyst whisper widget created');
  }

  // Helper functions for enhanced suggestion system
  function groupSuggestionsByType(suggestions) {
    return suggestions.reduce((groups, suggestion) => {
      const type = suggestion.type || 'general';
      if (!groups[type]) {
        groups[type] = [];
      }
      groups[type].push(suggestion);
      return groups;
    }, {});
  }

  function createSuggestionHeader(metadata) {
    const header = document.createElement('div');
    header.className = 'suggestion-header';

    const confidence = metadata.confidence || 0;
    const confidenceClass = confidence >= 0.8 ? 'high' : confidence >= 0.6 ? 'medium' : 'low';

    header.innerHTML = `
    <div class="analysis-info">
      <span class="model-used">Model: ${metadata.model || currentAIModel}</span>
      <span class="confidence-badge ${confidenceClass}">
        ${getConfidenceIcon(confidence)} ${(confidence * 100).toFixed(0)}%
      </span>
    </div>
  `;

    return header;
  }

  function createSuggestionGroup(type, suggestions) {
    const group = document.createElement('div');
    group.className = `suggestion-group ${type}`;

    const header = document.createElement('div');
    header.className = 'group-header';
    header.innerHTML = `
    <span class="group-icon">${getSuggestionTypeIcon(type)}</span>
    <span class="group-title">${formatSuggestionType(type)}</span>
    <span class="group-count">(${suggestions.length})</span>
  `;

    group.appendChild(header);

    suggestions.forEach(suggestion => {
      const suggestionElement = createEnhancedSuggestionElement(suggestion);
      group.appendChild(suggestionElement);
    });

    return group;
  }

  function createEnhancedSuggestionElement(suggestion) {
    const element = document.createElement('div');
    element.className = `catalyst-suggestion ${suggestion.type} ${suggestion.urgency}`;
    element.dataset.suggestionId = suggestion.id;

    const confidenceClass = suggestion.confidence >= 0.8 ? 'high' :
      suggestion.confidence >= 0.6 ? 'medium' : 'low';

    element.innerHTML = `
    <div class="suggestion-header">
      <span class="suggestion-title">${suggestion.title}</span>
      <div class="suggestion-meta">
        <span class="confidence-indicator ${confidenceClass}">
          ${getConfidenceIcon(suggestion.confidence)}
        </span>
        <span class="urgency-indicator ${suggestion.urgency}">
          ${getUrgencyIcon(suggestion.urgency)}
        </span>
      </div>
    </div>
    <div class="suggestion-content">${suggestion.content}</div>
    ${suggestion.reasoning ? `<div class="suggestion-reasoning">💡 ${suggestion.reasoning}</div>` : ''}
    ${suggestion.resources ? createResourcesElement(suggestion.resources) : ''}
    <div class="suggestion-actions">
      <button class="catalyst-btn-small apply-suggestion" data-suggestion-id="${suggestion.id}">
        Apply
      </button>
      <button class="catalyst-btn-small dismiss-suggestion" data-suggestion-id="${suggestion.id}">
        Dismiss
      </button>
      ${suggestion.personalizedData ?
        `<button class="catalyst-btn-small save-pattern" data-suggestion-id="${suggestion.id}">
          Save Pattern
        </button>` : ''
      }
    </div>
  `;

    // Add event listeners
    element.querySelector('.apply-suggestion').addEventListener('click', () => applySuggestion(suggestion));
    element.querySelector('.dismiss-suggestion').addEventListener('click', () => dismissSuggestion(suggestion));

    if (element.querySelector('.save-pattern')) {
      element.querySelector('.save-pattern').addEventListener('click', () => saveSuccessfulPattern(suggestion));
    }

    return element;
  }

  // Enhanced utility functions
  function getSuggestionTypeIcon(type) {
    const icons = {
      'emotional_intelligence': '🧠',
      'therapeutic_intervention': '🏥',
      'personalized_coaching': '🎯',
      'platform_specific': '📱',
      'contextual': '🎭',
      'general': '💡'
    };
    return icons[type] || '💡';
  }

  function getUrgencyIcon(urgency) {
    const icons = {
      'critical': '🚨',
      'high': '⚠️',
      'medium': '⚡',
      'low': 'ℹ️'
    };
    return icons[urgency] || 'ℹ️';
  }

  function getUrgencyLevel(urgency) {
    const levels = {
      'critical': 4,
      'high': 3,
      'medium': 2,
      'low': 1
    };
    return levels[urgency] || 1;
  }

  function createResourcesElement(resources) {
    if (!resources || resources.length === 0) return '';

    const resourcesHtml = resources.map(resource =>
      `<div class="resource-item">
      <span class="resource-name">${resource.name}</span>
      <span class="resource-contact">${resource.contact}</span>
    </div>`
    ).join('');

    return `<div class="suggestion-resources">
    <div class="resources-header">📞 Support Resources:</div>
    ${resourcesHtml}
  </div>`;
  }

  // Toggle functions for enhanced features
  function toggleTherapeuticHints() {
    therapeuticHintsEnabled = !therapeuticHintsEnabled;
    updateToggleButtonState('toggle-therapeutic-hints', therapeuticHintsEnabled);

    // Save preference
    chrome.storage.sync.set({ therapeuticHintsEnabled });

    console.log(`Therapeutic hints ${therapeuticHintsEnabled ? 'enabled' : 'disabled'}`);
  }

  function togglePersonalizedCoaching() {
    personalizedCoachingEnabled = !personalizedCoachingEnabled;
    updateToggleButtonState('toggle-personalized-coaching', personalizedCoachingEnabled);

    // Save preference
    chrome.storage.sync.set({ personalizedCoachingEnabled });

    console.log(`Personalized coaching ${personalizedCoachingEnabled ? 'enabled' : 'disabled'}`);
  }

  function toggleContextAware() {
    contextAwareMode = !contextAwareMode;
    updateToggleButtonState('toggle-context-aware', contextAwareMode);

    // Save preference
    chrome.storage.sync.set({ contextAwareMode });

    console.log(`Context-aware mode ${contextAwareMode ? 'enabled' : 'disabled'}`);
  }

  function updateToggleButtonState(buttonId, isEnabled) {
    const button = document.getElementById(buttonId);
    if (button) {
      button.classList.toggle('active', isEnabled);
      button.style.opacity = isEnabled ? '1' : '0.6';
    }
  }

  // Enhanced suggestion actions
  async function applySuggestion(suggestion) {
    try {
      // Log suggestion usage for learning
      await sendMessageToBackground('LOG_SUGGESTION_USAGE', {
        suggestionId: suggestion.id,
        action: 'applied',
        context: suggestionContext,
        timestamp: Date.now()
      });

      // Apply suggestion based on type
      switch (suggestion.type) {
        case 'therapeutic_intervention':
          if (suggestion.category === 'crisis_support') {
            await showCrisisSupportDialog(suggestion);
          }
          break;

        case 'personalized_coaching':
          await applyPersonalizedCoaching(suggestion);
          break;

        case 'platform_specific':
          await applyPlatformSpecificSuggestion(suggestion);
          break;

        default:
          // Generic application - could be copying text or opening resources
          if (suggestion.content) {
            await copyToClipboard(suggestion.content);
            showNotification('Suggestion copied to clipboard', 'success');
          }
      }

      // Mark suggestion as applied
      const suggestionElement = document.querySelector(`[data-suggestion-id="${suggestion.id}"]`);
      if (suggestionElement) {
        suggestionElement.classList.add('applied');
      }

      console.log('Suggestion applied:', suggestion.id);
    } catch (error) {
      console.error('Failed to apply suggestion:', error);
      showNotification('Failed to apply suggestion', 'error');
    }
  }

  async function dismissSuggestion(suggestion) {
    try {
      // Log dismissal for learning
      await sendMessageToBackground('LOG_SUGGESTION_USAGE', {
        suggestionId: suggestion.id,
        action: 'dismissed',
        context: suggestionContext,
        timestamp: Date.now()
      });

      // Remove suggestion from UI
      const suggestionElement = document.querySelector(`[data-suggestion-id="${suggestion.id}"]`);
      if (suggestionElement) {
        suggestionElement.style.transition = 'opacity 0.3s ease';
        suggestionElement.style.opacity = '0';
        setTimeout(() => {
          suggestionElement.remove();
        }, 300);
      }

      console.log('Suggestion dismissed:', suggestion.id);
    } catch (error) {
      console.error('Failed to dismiss suggestion:', error);
    }
  }

  async function saveSuccessfulPattern(suggestion) {
    try {
      // Add to successful patterns
      const pattern = {
        id: `pattern_${Date.now()}`,
        suggestion: suggestion.content,
        context: {
          type: suggestionContext.type || 'general',
          emotionalTension: suggestionContext.emotionalTension || 0,
          platform: currentPlatform
        },
        successRate: 1.0,
        usageCount: 1,
        lastUsed: Date.now(),
        created: Date.now()
      };

      personalizedCoachingData.successfulPatterns.push(pattern);

      // Save to storage
      await chrome.storage.sync.set({ personalizedCoachingData });

      showNotification('Pattern saved for future use', 'success');
      console.log('Successful pattern saved:', pattern.id);
    } catch (error) {
      console.error('Failed to save pattern:', error);
      showNotification('Failed to save pattern', 'error');
    }
  }

  // Enhanced widget animation and positioning
  function showWhisperWidgetWithAnimation() {
    if (!whisperWidget) return;

    whisperWidget.style.display = 'block';
    whisperWidget.style.transform = 'translateY(20px)';
    whisperWidget.style.opacity = '0';

    // Animate in
    requestAnimationFrame(() => {
      whisperWidget.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
      whisperWidget.style.transform = 'translateY(0)';
      whisperWidget.style.opacity = '1';
    });

    // Update model indicator
    updateModelIndicator();
  }

  function updateModelIndicator() {
    const modelNameElement = document.getElementById('current-model');
    const confidenceFillElement = document.getElementById('confidence-fill');
    const confidenceValueElement = document.getElementById('confidence-value');

    if (modelNameElement) {
      modelNameElement.textContent = currentAIModel || 'Local';
    }

    // Update confidence indicator based on analysis results
    const confidence = analysisResponse?.confidence || 0; // Use value from analysis or default to 0
    if (confidenceFillElement && confidenceValueElement) {
      confidenceFillElement.style.width = `${confidence * 100}%`;
      confidenceValueElement.textContent = `${(confidence * 100).toFixed(0)}%`;

      // Update color based on confidence
      const color = confidence >= 0.8 ? '#4ade80' :
        confidence >= 0.6 ? '#fbbf24' : '#ef4444';
      confidenceFillElement.style.backgroundColor = color;
    }
  }

  // Integration with existing message processing
  // This replaces the existing analyzeMessageWithContext function

  async function analyzeMessageWithContext(messageData, conversationHistory) {
    try {
      // Initialize enhanced suggestion system if needed
      if (!personalizedCoachingData.communicationStyle) {
        await initializeEnhancedSuggestionSystem();
      }

      // Generate context-aware suggestions
      const suggestions = await generateContextAwareSuggestions(messageData, conversationHistory);

      // Process suggestions and show enhanced UI
      if (suggestions.length > 0) {
        showEnhancedSuggestions(suggestions, {
          model: currentAIModel,
          confidence: Math.max(...suggestions.map(s => s.confidence)),
          timestamp: Date.now()
        });
      }

      // Send to background for backend analysis (existing functionality)
      const analysisResponse = await sendMessageToBackground('ANALYZE_MESSAGE', {
        messageData,
        conversationHistory,
        activeProject: activeProject?.id,
        analysis_type: 'enhanced_ai',
        context: suggestionContext
      });

      if (analysisResponse && !analysisResponse.error) {
        await handleEnhancedAnalysisResults(analysisResponse, messageData);
      }

    } catch (error) {
      console.error('Catalyst: Failed to analyze message with enhanced context:', error);
    }
  }

  async function handleEnhancedAnalysisResults(analysisResponse, messageData) {
    const { analysis, confidence, model } = analysisResponse;

    // Update current model info
    currentAIModel = model;
    updateModelIndicator();

    // Handle different types of analysis results
    if (analysis.suggestions && analysis.suggestions.length > 0) {
      const enhancedSuggestions = analysis.suggestions.map(suggestion => ({
        ...suggestion,
        id: `backend_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
        source: 'backend_ai',
        model: model,
        confidence: suggestion.confidence || confidence
      }));

      // Merge with any existing suggestions
      const existingSuggestions = Array.from(document.querySelectorAll('.catalyst-suggestion'))
        .map(el => el.dataset.suggestionId);

      const newSuggestions = enhancedSuggestions.filter(s =>
        !existingSuggestions.includes(s.id));

      if (newSuggestions.length > 0) {
        showEnhancedSuggestions(newSuggestions, {
          model: model,
          confidence: confidence,
          source: 'backend'
        });
      }
    }

    // Handle therapeutic insights
    if (analysis.therapeutic && analysis.therapeutic.risk_level !== 'low') {
      await handleTherapeuticInsights(analysis.therapeutic, messageData);
    }

    // Update context for future suggestions
    suggestionContext = {
      ...suggestionContext,
      lastAnalysis: analysis,
      lastConfidence: confidence,
      lastModel: model,
      timestamp: Date.now()
    };
  }

  // Enhanced styles for the widget
  function applyEnhancedWidgetStyles() {
    // This would be injected via content_styles.css, but we can also add dynamic styles
    const style = document.createElement('style');
    style.textContent = `
    .catalyst-whisper-widget.enhanced {
      min-width: 400px;
      max-width: 500px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
      border-radius: 12px;
      overflow: hidden;
    }

    .catalyst-widget-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 12px 16px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .catalyst-logo {
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
    }

    .catalyst-logo img {
      width: 24px;
      height: 24px;
    }

    .catalyst-model-indicator {
      font-size: 12px;
      opacity: 0.9;
    }

    .confidence-indicator {
      display: flex;
      align-items: center;
      gap: 6px;
      margin-top: 4px;
    }

    .confidence-bar {
      width: 60px;
      height: 4px;
      background: rgba(255, 255, 255, 0.3);
      border-radius: 2px;
      overflow: hidden;
    }

    .confidence-fill {
      height: 100%;
      background: #4ade80;
      transition: width 0.3s ease;
    }

    .suggestion-group {
      margin-bottom: 16px;
    }

    .group-header {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      background: rgba(0, 0, 0, 0.05);
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      font-weight: 600;
      font-size: 14px;
    }

    .catalyst-suggestion {
      padding: 12px;
      border-bottom: 1px solid rgba(0, 0, 0, 0.1);
      transition: all 0.3s ease;
    }

    .catalyst-suggestion:hover {
      background: rgba(0, 0, 0, 0.02);
    }

    .catalyst-suggestion.applied {
      opacity: 0.6;
      background: rgba(34, 197, 94, 0.1);
    }

    .suggestion-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 8px;
    }

    .suggestion-title {
      font-weight: 600;
      color: #1f2937;
    }

    .suggestion-meta {
      display: flex;
      gap: 6px;
    }

    .confidence-indicator.high { color: #22c55e; }
    .confidence-indicator.medium { color: #f59e0b; }
    .confidence-indicator.low { color: #ef4444; }

    .urgency-indicator.critical { color: #dc2626; }
    .urgency-indicator.high { color: #f59e0b; }
    .urgency-indicator.medium { color: #3b82f6; }
    .urgency-indicator.low { color: #6b7280; }

    .catalyst-widget-footer {
      padding: 12px;
      background: #f9fafb;
      border-top: 1px solid rgba(0, 0, 0, 0.1);
    }

    .catalyst-controls {
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }

    .catalyst-btn {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 12px;
      background: white;
      border: 1px solid #d1d5db;
      border-radius: 6px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .catalyst-btn:hover {
      background: #f3f4f6;
    }

    .catalyst-btn.active {
      background: #3b82f6;
      color: white;
      border-color: #3b82f6;
    }
  `;

    document.head.appendChild(style);
  }

  // Enhanced utility functions for notifications and clipboard
  async function copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (error) {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand('copy');
      document.body.removeChild(textarea);
      return true;
    }
  }

  function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `catalyst-notification ${type}`;
    notification.textContent = message;

    notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 16px;
    background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6'};
    color: white;
    border-radius: 6px;
    font-size: 14px;
    z-index: 10001;
    opacity: 0;
    transform: translateY(-20px);
    transition: all 0.3s ease;
  `;

    document.body.appendChild(notification);

    // Animate in
    requestAnimationFrame(() => {
      notification.style.opacity = '1';
      notification.style.transform = 'translateY(0)';
    });

    // Auto remove
    setTimeout(() => {
      notification.style.opacity = '0';
      notification.style.transform = 'translateY(-20px)';
      setTimeout(() => {
        document.body.removeChild(notification);
      }, 300);
    }, 3000);
  }

  // Initialize enhanced suggestion system when content script loads
  document.addEventListener('DOMContentLoaded', () => {
    setTimeout(initializeEnhancedSuggestionSystem, 1000);
  });

  // Also initialize if DOM is already loaded
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      setTimeout(initializeEnhancedSuggestionSystem, 1000);
    });
  } else {
    setTimeout(initializeEnhancedSuggestionSystem, 1000);
  }

})(); // End of IIFE