// Catalyst Whisper Coach - DOM Selector Verification Script
// This script can be pasted in the browser console to verify DOM selectors

(function() {
  console.clear();
  console.log('%c Catalyst Whisper Coach - DOM Selector Verification', 'font-weight: bold; font-size: 16px; color: #6772e5;');
  
  // Get current hostname
  const hostname = window.location.hostname;
  console.log('Current hostname:', hostname);
  
  // Platform detection
  let platform = 'unknown';
  if (hostname.includes('whatsapp')) platform = 'web.whatsapp.com';
  else if (hostname.includes('messenger')) platform = 'www.messenger.com';
  else if (hostname.includes('instagram')) platform = 'instagram.com';
  else if (hostname.includes('facebook')) platform = 'www.facebook.com';
  else if (hostname.includes('discord')) platform = 'discord.com';
  else if (hostname.includes('slack')) platform = 'slack.com';
  else if (hostname.includes('teams.microsoft')) platform = 'teams.microsoft.com';
  else if (hostname.includes('telegram')) platform = 'telegram.org';
  
  console.log('Detected platform:', platform);
  
  // Selectors map from content_script.js
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
      sender: '.message-sender-name',
      timestamp: '.message-time',
      inputField: '.composer-input',
      sendButton: '.send-button'
    }
  };
  
  // Get selectors for current platform
  const selectors = PLATFORM_SELECTORS[platform] || {};
  if (!selectors || Object.keys(selectors).length === 0) {
    console.error('No selectors defined for platform:', platform);
    return;
  }
  
  console.log('Testing selectors for', platform);
  
  // Test each selector and report results
  const results = {};
  
  for (const [key, selector] of Object.entries(selectors)) {
    try {
      const elements = document.querySelectorAll(selector);
      const count = elements.length;
      const status = count > 0 ? '✅ FOUND' : '❌ NOT FOUND';
      const color = count > 0 ? 'green' : 'red';
      
      console.log(
        '%c' + status + '%c ' + key + ': %c' + selector + '%c (' + count + ' elements)',
        'color: ' + color + '; font-weight: bold',
        'color: black; font-weight: bold',
        'color: blue',
        'color: gray'
      );
      
      results[key] = {
        selector,
        found: count > 0,
        count,
        elementsExample: count > 0 ? elements[0].outerHTML.slice(0, 150) + '...' : null
      };
      
      // For message container, try to extract the last few messages
      if (key === 'messages' && count > 0) {
        const messageTextSelector = selectors.messageText;
        if (messageTextSelector) {
          console.log('%cSample messages:', 'font-weight: bold');
          const msgs = [];
          
          Array.from(elements).slice(-5).forEach((el, i) => {
            const textEl = el.querySelector(messageTextSelector);
            if (textEl) {
              const text = textEl.textContent.trim();
              console.log(`  ${i+1}. "${text}"`);
              msgs.push(text);
            }
          });
          
          results.sampleMessages = msgs;
        }
      }
      
    } catch (error) {
      console.error(`Error testing selector ${key}: ${selector}`, error);
      results[key] = {
        selector,
        found: false,
        error: error.message
      };
    }
  }
  
  // Display summary and copy to clipboard
  console.log('%cSelector Test Results:', 'font-weight: bold; font-size: 14px');
  console.log(results);
  
  // Generate JSON for copying
  const jsonResults = JSON.stringify(results, null, 2);
  console.log('%cCopy these results to your test report:', 'font-weight: bold');
  console.log(jsonResults);
  
  // Try to copy to clipboard
  try {
    navigator.clipboard.writeText(jsonResults).then(
      () => console.log('%cResults copied to clipboard!', 'color: green; font-weight: bold'),
      () => console.log('%cFailed to copy results. Please copy manually.', 'color: red')
    );
  } catch (e) {
    console.log('%cPlease copy the results manually.', 'color: orange');
  }
  
  return results;
})();
