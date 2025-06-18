// Debug helpers for Catalyst Whisper Coach testing
// Add this to content_script.js for comprehensive testing

// Create debug namespace
window.catalystDebug = {
  // Test DOM selectors
  testSelectors: () => {
    const results = {};
    const hostname = window.location.hostname;
    let platformKey = null;
    
    // Find matching platform key
    for (const key in PLATFORM_SELECTORS) {
      if (hostname.includes(key) || key.includes(hostname)) {
        platformKey = key;
        break;
      }
    }
    
    if (!platformKey) {
      return { error: 'No selectors found for this platform' };
    }
    
    const selectors = PLATFORM_SELECTORS[platformKey];
    
    for (const [key, selector] of Object.entries(selectors)) {
      try {
        const elements = document.querySelectorAll(selector);
        results[key] = {
          selector,
          count: elements.length,
          valid: elements.length > 0
        };
      } catch (error) {
        results[key] = {
          selector,
          error: error.message,
          valid: false
        };
      }
    }
    
    return {
      platform: platformKey,
      results
    };
  },
  
  // Force suggestion for testing
  forceSuggestion: async (text) => {
    if (!text) {
      text = "I'm feeling upset about how you ignored me yesterday";
    }
    
    const messageData = {
      sender: "TestUser",
      text: text,
      timestamp: new Date().toISOString(),
      platform: window.location.hostname
    };
    
    try {
      // Use the existing processChatMessage function if available
      if (typeof processChatMessage === 'function') {
        return processChatMessage(messageData);
      } else {
        // Fall back to sending a message to background script
        return new Promise((resolve, reject) => {
          chrome.runtime.sendMessage({
            type: 'ANALYZE_MESSAGE',
            message: messageData
          }, response => {
            if (chrome.runtime.lastError) {
              reject(chrome.runtime.lastError);
            } else {
              resolve(response);
            }
          });
        });
      }
    } catch (error) {
      console.error("Error forcing suggestion:", error);
      return { error: error.message };
    }
  },
  
  // Log detected messages
  logMessages: (count = 5) => {
    const hostname = window.location.hostname;
    let platformKey = null;
    
    // Find matching platform key
    for (const key in PLATFORM_SELECTORS) {
      if (hostname.includes(key) || key.includes(hostname)) {
        platformKey = key;
        break;
      }
    }
    
    if (!platformKey) {
      return { error: 'No selectors found for this platform' };
    }
    
    const selectors = PLATFORM_SELECTORS[platformKey];
    
    if (!selectors || !selectors.messages) {
      return { error: 'No message selector for this platform' };
    }
    
    try {
      const messages = [];
      const messageElements = document.querySelectorAll(selectors.messages);
      
      const maxCount = Math.min(count, messageElements.length);
      for (let i = messageElements.length - maxCount; i < messageElements.length; i++) {
        if < 0) continue;
        
        const el = messageElements[i];
        const textEl = el.querySelector(selectors.messageText);
        const senderEl = el.querySelector(selectors.sender);
        const timestampEl = el.querySelector(selectors.timestamp);
        
        messages.push({
          text: textEl ? textEl.textContent : 'No text found',
          sender: senderEl ? senderEl.textContent : 'Unknown sender',
          timestamp: timestampEl ? timestampEl.textContent : 'No timestamp',
          element: el
        });
      }
      
      return messages;
    } catch (error) {
      console.error("Error logging messages:", error);
      return { error: error.message };
    }
  },
  
  // Get extension status
  getStatus: () => {
    return {
      isEnabled,
      activeProject,
      platform: window.location.hostname,
      initialized: !!messageObserver
    };
  }
};

// Log that debug helpers are available
console.log('Catalyst Whisper Coach debug helpers available via window.catalystDebug');
