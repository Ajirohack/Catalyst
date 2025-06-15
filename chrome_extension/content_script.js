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

  // Platform-specific selectors
  const PLATFORM_SELECTORS = {
    'web.whatsapp.com': {
      messageContainer: '[data-testid="conversation-panel-messages"]',
      messages: '[data-testid="msg-container"]',
      messageText: '.selectable-text span',
      sender: '[data-testid="msg-meta"] span[dir="auto"]',
      timestamp: '[data-testid="msg-meta"] span[title]',
      inputField: '[data-testid="conversation-compose-box-input"]',
      sendButton: '[data-testid="compose-btn-send"]'
    },
    'www.messenger.com': {
      messageContainer: '[role="main"] [data-testid="conversation"]',
      messages: '[data-testid="message_container"]',
      messageText: '[data-testid="message_text"]',
      sender: '[data-testid="message_sender"]',
      timestamp: '[data-testid="message_timestamp"]',
      inputField: '[contenteditable="true"][role="textbox"]',
      sendButton: '[data-testid="send_button"]'
    },
    'instagram.com': {
      messageContainer: 'div[role="dialog"] div[style*="overflow-y: auto"]',
      messages: 'div[role="row"]',
      messageText: 'div[style*="max-width"] > div > div > span',
      sender: 'div[role="row"] h4',
      timestamp: 'time',
      inputField: 'div[contenteditable="true"]',
      sendButton: 'button[type="submit"]'
    },
    'www.facebook.com': {
      messageContainer: '[role="main"] [data-pagelet="MWChat"]',
      messages: '[data-testid="message_container"]',
      messageText: '[data-testid="message_text"]',
      sender: '[data-testid="message_sender"]',
      timestamp: '[data-testid="message_timestamp"]',
      inputField: '[contenteditable="true"][role="textbox"]',
      sendButton: '[data-testid="send_button"]'
    },
    'discord.com': {
      messageContainer: '[data-list-id="chat-messages"]',
      messages: '[id^="chat-messages-"]',
      messageText: '[id^="message-content-"]',
      sender: '.username',
      timestamp: '.timestamp',
      inputField: '[role="textbox"][data-slate-editor="true"]',
      sendButton: '[data-testid="send-button"]'
    },
    'slack.com': {
      messageContainer: '.c-virtual_list__scroll_container',
      messages: '.c-message_kit__background',
      messageText: '.c-message_kit__text',
      sender: '.c-message__sender',
      timestamp: '.c-timestamp',
      inputField: '[data-qa="message_input"]',
      sendButton: '[data-qa="send_message_button"]'
    },
    'teams.microsoft.com': {
      messageContainer: '[data-tid="chat-pane-list"]',
      messages: '[data-tid="chat-pane-message"]',
      messageText: '[data-tid="message-body-content"]',
      sender: '[data-tid="message-author-name"]',
      timestamp: '[data-tid="message-timestamp"]',
      inputField: '[data-tid="ckeditor"]',
      sendButton: '[data-tid="send-message-button"]'
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

      if (!isEnabled) {
        console.log('Catalyst: Extension disabled');
        return;
      }

      // Get active project
      const projectResponse = await sendMessageToBackground('GET_ACTIVE_PROJECT');
      activeProject = projectResponse.error ? null : projectResponse;

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
      // First, get project settings for API authentication
      const settings = await sendMessageToBackground('GET_SETTINGS');
      const token = settings.apiToken;

      if (!token) {
        console.warn('Catalyst: No API token available for message analysis');
        return;
      }

      // Prepare whisper data
      const whisperData = {
        context: messageData.text,
        conversation: conversationHistory,
        project_id: activeProject ? activeProject.id : null,
        platform: currentPlatform,
        urgency: 'normal',
        frequency: settings.whisperSettings?.whisperFrequency || 'medium'
      };

      // Send to background for API request to avoid CORS issues
      const response = await sendMessageToBackground('ANALYZE_WHISPER', whisperData);

      if (response.error) {
        console.error('Catalyst: Whisper analysis failed:', response.error);
        return;
      }

      if (response.success && response.analysis) {
        handleAnalysisResult(response.analysis, messageData);
      }
    } catch (error) {
      console.error('Catalyst: Failed to send message for analysis:', error);
    }
  }

  // Extract message data from DOM element
  function extractMessageData(messageElement) {
    try {
      const textElement = messageElement.querySelector(selectors.messageText);
      const senderElement = messageElement.querySelector(selectors.sender);
      const timestampElement = messageElement.querySelector(selectors.timestamp);

      if (!textElement) {
        return null;
      }

      const text = textElement.textContent?.trim();
      if (!text || text.length > CONFIG.maxMessageLength) {
        return null;
      }

      return {
        text,
        sender: senderElement?.textContent?.trim() || 'Unknown',
        timestamp: extractTimestamp(timestampElement),
        platform: currentPlatform,
        url: window.location.href,
        context: {
          messageElement: messageElement.outerHTML.substring(0, 500), // Limited for privacy
          conversationId: extractConversationId()
        }
      };
    } catch (error) {
      console.error('Catalyst: Failed to extract message data:', error);
      return null;
    }
  }

  // Extract timestamp from element
  function extractTimestamp(timestampElement) {
    if (!timestampElement) {
      return Date.now();
    }

    const title = timestampElement.getAttribute('title');
    const text = timestampElement.textContent;

    // Try to parse various timestamp formats
    const timeString = title || text;
    const parsed = new Date(timeString);

    return isNaN(parsed.getTime()) ? Date.now() : parsed.getTime();
  }

  // Extract conversation ID for context
  function extractConversationId() {
    const url = new URL(window.location.href);

    switch (currentPlatform) {
      case 'web.whatsapp.com':
        return url.pathname.split('/').pop() || 'unknown';
      case 'www.messenger.com':
        return url.pathname.split('/t/')[1] || 'unknown';
      case 'discord.com':
        return url.pathname.split('/channels/')[1] || 'unknown';
      default:
        return 'unknown';
    }
  }

  // Send message for analysis
  async function analyzeMessage(messageData) {
    try {
      const response = await sendMessageToBackground('ANALYZE_MESSAGE', messageData);

      if (response.error) {
        console.error('Catalyst: Analysis failed:', response.error);
        return;
      }

      if (response.success && response.analysis) {
        handleAnalysisResult(response.analysis, messageData);
      }
    } catch (error) {
      console.error('Catalyst: Failed to send message for analysis:', error);
    }
  }

  // Handle analysis result
  function handleAnalysisResult(analysis, originalMessage) {
    // Track analysis event
    sendMessageToBackground('TRACK_EVENT', {
      type: 'message_analyzed',
      platform: currentPlatform,
      sentiment: analysis.sentiment,
      messageLength: originalMessage.text.length
    });

    // Show whisper suggestions if available
    if (analysis.suggestions && analysis.suggestions.length > 0) {
      showWhisperSuggestions(analysis.suggestions);
    }
  }

  // Create whisper widget
  function createWhisperWidget() {
    if (whisperWidget) {
      return;
    }

    whisperWidget = document.createElement('div');
    whisperWidget.id = 'catalyst-whisper-widget';
    whisperWidget.innerHTML = `
      <div class="catalyst-whisper-container">
        <div class="catalyst-whisper-header">
          <span class="catalyst-whisper-title">💡 Catalyst Suggestion</span>
          <button class="catalyst-whisper-close">&times;</button>
        </div>
        <div class="catalyst-whisper-content">
          <p class="catalyst-whisper-text"></p>
          <div class="catalyst-whisper-actions">
            <button class="catalyst-whisper-apply">Apply</button>
            <button class="catalyst-whisper-dismiss">Dismiss</button>
          </div>
        </div>
      </div>
    `;

    // Add styles
    const styles = document.createElement('style');
    styles.textContent = `
      #catalyst-whisper-widget {
        position: fixed;
        top: 20px;
        right: 20px;
        width: 320px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        transform: translateX(100%);
        transition: transform 0.3s ease;
        border: 1px solid #e0e0e0;
      }
      
      #catalyst-whisper-widget.show {
        transform: translateX(0);
      }
      
      .catalyst-whisper-container {
        padding: 0;
      }
      
      .catalyst-whisper-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 12px 12px 0 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      
      .catalyst-whisper-title {
        font-weight: 600;
        font-size: 14px;
      }
      
      .catalyst-whisper-close {
        background: none;
        border: none;
        color: white;
        font-size: 18px;
        cursor: pointer;
        padding: 0;
        width: 24px;
        height: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        transition: background 0.2s;
      }
      
      .catalyst-whisper-close:hover {
        background: rgba(255, 255, 255, 0.2);
      }
      
      .catalyst-whisper-content {
        padding: 16px;
      }
      
      .catalyst-whisper-text {
        margin: 0 0 12px 0;
        font-size: 14px;
        line-height: 1.4;
        color: #333;
      }
      
      .catalyst-whisper-actions {
        display: flex;
        gap: 8px;
      }
      
      .catalyst-whisper-apply,
      .catalyst-whisper-dismiss {
        padding: 8px 16px;
        border: none;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
      }
      
      .catalyst-whisper-apply {
        background: #4caf50;
        color: white;
      }
      
      .catalyst-whisper-apply:hover {
        background: #45a049;
      }
      
      .catalyst-whisper-dismiss {
        background: #f5f5f5;
        color: #666;
      }
      
      .catalyst-whisper-dismiss:hover {
        background: #e0e0e0;
      }
    `;

    document.head.appendChild(styles);
    document.body.appendChild(whisperWidget);

    // Add event listeners
    whisperWidget.querySelector('.catalyst-whisper-close').addEventListener('click', hideWhisperWidget);
    whisperWidget.querySelector('.catalyst-whisper-dismiss').addEventListener('click', hideWhisperWidget);
    whisperWidget.querySelector('.catalyst-whisper-apply').addEventListener('click', applyWhisperSuggestion);
  }

  // Show whisper suggestions
  function showWhisperSuggestions(suggestions) {
    if (!whisperWidget || suggestions.length === 0) {
      return;
    }

    const suggestion = suggestions[0]; // Show first suggestion
    const textElement = whisperWidget.querySelector('.catalyst-whisper-text');
    textElement.textContent = suggestion.text || suggestion.message || 'Consider improving your communication approach.';

    whisperWidget.classList.add('show');

    // Auto-hide after 10 seconds
    setTimeout(() => {
      hideWhisperWidget();
    }, 10000);
  }

  // Hide whisper widget
  function hideWhisperWidget() {
    if (whisperWidget) {
      whisperWidget.classList.remove('show');
    }
  }

  // Apply whisper suggestion
  function applyWhisperSuggestion() {
    const inputField = document.querySelector(selectors.inputField);
    const suggestion = whisperWidget.querySelector('.catalyst-whisper-text').textContent;

    if (inputField && suggestion) {
      // Focus input field
      inputField.focus();

      // Insert suggestion text
      if (inputField.contentEditable === 'true') {
        inputField.textContent = suggestion;
      } else {
        inputField.value = suggestion;
      }

      // Trigger input event
      inputField.dispatchEvent(new Event('input', { bubbles: true }));

      // Track application
      sendMessageToBackground('TRACK_EVENT', {
        type: 'whisper_applied',
        platform: currentPlatform
      });
    }

    hideWhisperWidget();
  }

  // Handle messages from background script
  function handleBackgroundMessage(message, sender, sendResponse) {
    switch (message.type) {
      case 'SHOW_WHISPER':
        showWhisperSuggestions(message.data.suggestions);
        sendResponse({ success: true });
        break;

      case 'SETTINGS_UPDATED':
        isEnabled = message.data.enabled;
        if (!isEnabled && messageObserver) {
          messageObserver.disconnect();
          hideWhisperWidget();
        } else if (isEnabled && !messageObserver) {
          startMessageMonitoring();
        }
        sendResponse({ success: true });
        break;

      default:
        sendResponse({ error: 'Unknown message type' });
    }
  }

  // Send message to background script
  function sendMessageToBackground(type, data = null) {
    return new Promise((resolve) => {
      chrome.runtime.sendMessage({ type, data }, (response) => {
        if (chrome.runtime.lastError) {
          resolve({ error: chrome.runtime.lastError.message });
        } else {
          resolve(response || {});
        }
      });
    });
  }

  // Utility functions
  function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  // Cleanup on page unload
  window.addEventListener('beforeunload', () => {
    if (messageObserver) {
      messageObserver.disconnect();
    }

    if (whisperWidget) {
      whisperWidget.remove();
    }
  });

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }

})();