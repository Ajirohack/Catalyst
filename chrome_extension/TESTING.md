# Catalyst Whisper Coach Extension - Testing Guide

This document provides guidance for testing the Catalyst Whisper Coach extension across different platforms and scenarios.

## Test Environment Setup

1. **Local Development Server**:

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Chrome Extension**:
   - Open Chrome and navigate to `chrome://extensions/`
   - Enable "Developer mode" (toggle in top right corner)
   - Click "Load unpacked" and select the `chrome_extension` directory
   - Pin the extension to your toolbar

## Supported Platforms

The Catalyst Chrome Extension now supports the following messaging platforms:

1. WhatsApp Web - `web.whatsapp.com`
2. Facebook Messenger - `www.messenger.com`
3. Instagram DMs - `www.instagram.com/direct/inbox`
4. Discord - `discord.com/channels/@me`
5. Slack - `slack.com`
6. Microsoft Teams - `teams.microsoft.com`
7. Telegram Web - `web.telegram.org`
8. Google Meet - `meet.google.com`
9. Zoom - `zoom.us`
10. ChatGPT - `chat.openai.com`
11. Gmail - `mail.google.com`
12. LinkedIn Messaging - `www.linkedin.com/messaging`
13. Twitter/X DMs - `twitter.com`
14. Outlook - `outlook.live.com`
15. Reddit Chat - `www.reddit.com`
16. Skype Web - `web.skype.com`
| Invalid Login | Enter invalid credentials, click Sign In | Shows error message |
| Remember Login | Login, close popup, reopen extension icon | Stays logged in, shows popup |
| Logout | Click logout button | Redirects to login page |

### 2. Platform Support Tests

| Platform | URL to Test | DOM Elements to Verify |
|----------|------------|------------------------|
| WhatsApp Web | <https://web.whatsapp.com/> | Message container, messages, input field |
| Facebook Messenger | <https://www.messenger.com/> | Message container, messages, input field |
| Instagram DMs | <https://www.instagram.com/direct/inbox/> | Message container, messages, input field |
| Discord | <https://discord.com/channels/@me> | Message container, messages, input field |
| Slack | <https://app.slack.com/> | Message container, messages, input field |
| Microsoft Teams | <https://teams.microsoft.com/> | Message container, messages, input field |
| Telegram Web | <https://web.telegram.org/> | Message container, messages, input field |

### 3. Feature Tests

| Feature | Test Steps | Expected Result |
|---------|------------|-----------------|
| Message Detection | Send and receive messages on platform | Messages detected, appear in extension log |
| Whisper Generation | Send messages with emotional content | Receives whisper suggestions |
| Whisper Display | Trigger suggestions through conversation | Whisper widget appears correctly |
| Settings Persistence | Change settings, close and reopen | Settings remain changed |
| Platform Toggle | Disable a platform, visit that site | No message detection happens |
| Manual Suggestion | Enter text in popup, click Get Suggestion | Shows relevant whisper suggestion |
| Suggestion History | Generate multiple suggestions | History tab shows all suggestions |

### 4. Performance Tests

| Test | Method | Acceptable Range |
|------|--------|------------------|
| CPU Usage | Check Task Manager during active use | < 5% average |
| Memory Usage | Check Task Manager | < 100MB |
| Response Time | Time from message to suggestion | < 2 seconds |
| DOM Impact | Use Chrome DevTools Performance tab | No significant frame drops |

## Test Helper Functions

Add these debug functions to the content script for testing:

```javascript
// Debug helpers - add to content_script.js
window.catalystDebug = {
  // Test DOM selectors
  testSelectors: () => {
    const results = {};
    const selectors = PLATFORM_SELECTORS[window.location.hostname];
    
    if (!selectors) {
      return { error: 'No selectors for this platform' };
    }
    
    for (const [key, selector] of Object.entries(selectors)) {
      const elements = document.querySelectorAll(selector);
      results[key] = {
        selector,
        found: elements.length,
        sample: elements.length > 0 ? elements[0].outerHTML.substring(0, 100) + '...' : null
      };
    }
    
    return results;
  },
  
  // Force suggestion for testing
  forceSuggestion: async (text) => {
    const response = await chrome.runtime.sendMessage({
      type: 'GET_WHISPER_SUGGESTION',
      data: {
        text: text || 'This is a test message to generate a suggestion',
        platform: getPlatformFromUrl(window.location.hostname),
        urgency: 'normal'
      }
    });
    
    return response;
  },
  
  // Log detected messages
  logMessages: (count = 5) => {
    const messages = [];
    const messageElements = document.querySelectorAll(
      PLATFORM_SELECTORS[window.location.hostname].messages
    );
    
    for (let i = Math.max(0, messageElements.length - count); i < messageElements.length; i++) {
      const el = messageElements[i];
      const textEl = el.querySelector(
        PLATFORM_SELECTORS[window.location.hostname].messageText
      );
      const senderEl = el.querySelector(
        PLATFORM_SELECTORS[window.location.hostname].sender
      );
      
      messages.push({
        text: textEl ? textEl.textContent : 'No text found',
        sender: senderEl ? senderEl.textContent : 'Unknown',
        element: el.outerHTML.substring(0, 100) + '...'
      });
    }
    
    return messages;
  }
};

// Add this to the initialize function in content_script.js
console.log('Catalyst debug helpers available via window.catalystDebug');
```

## How to Use Debug Functions

1. Open Chrome DevTools console on any supported messaging platform
2. Access debug functions:

   ```javascript
   // Test DOM selectors for current platform
   window.catalystDebug.testSelectors()
   
   // Force a suggestion to appear
   window.catalystDebug.forceSuggestion("I'm feeling upset about what happened yesterday")
   
   // Log last 5 detected messages
   window.catalystDebug.logMessages(5)
   ```

## Troubleshooting Common Issues

1. **Selectors Not Working**:
   - Use `window.catalystDebug.testSelectors()` to identify which selectors are failing
   - Update selectors in PLATFORM_SELECTORS in content_script.js

2. **No Suggestions Appearing**:
   - Check console for errors
   - Verify backend API is running
   - Check authentication status
   - Test with `window.catalystDebug.forceSuggestion()`

3. **Extension Not Loading**:
   - Check Chrome extension errors in chrome://extensions/
   - Look for syntax errors in background.js or content_script.js
   - Verify manifest.json permissions are correct

## Regression Testing Checklist

Before each release, verify:

- [ ] Login/logout functionality works
- [ ] All supported platforms are detected correctly
- [ ] Whisper suggestions are generated and displayed
- [ ] Settings are saved and applied correctly
- [ ] History tab shows accurate suggestion history
- [ ] No console errors during normal operation
- [ ] CPU/memory usage remains within acceptable limits

## Automated Testing

For automated UI testing, we recommend using Puppeteer to:

1. Launch Chrome with the extension loaded
2. Navigate to supported platforms
3. Simulate user interactions
4. Verify DOM changes and extension behavior

Sample test script coming soon.
