// Catalyst Selector Verification Script
// Generated on: Tue Jun 17 16:34:31 WAT 2025
// This script helps verify if DOM selectors for platforms are working correctly

console.log("Catalyst Selector Verification Script");
console.log("==================================");

// Platform selectors (copied from extension)
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
        messageText: '.message-text',
        sender: '.message-author',
        timestamp: '.message-date',
        inputField: '.composer-input',
        sendButton: '.send-button'
    },
    'meet.google.com': {
        messageContainer: '[aria-label="Chat panel"]',
        messages: '.GDhqjd',
        messageText: '.oIy2qc',
        sender: '.YTbUzc',
        timestamp: '.MuzmKe',
        inputField: '.KHxj8b[role="textbox"]',
        sendButton: '[aria-label="Send message"]'
    },
    'zoom.us': {
        messageContainer: '.chat-container__chat-list',
        messages: '.chat-message__text-box',
        messageText: '.chat-message__text',
        sender: '.chat-message__sender',
        timestamp: '.chat-message__time',
        inputField: '.chat-message__input',
        sendButton: '.chat-send-button'
    },
    'chat.openai.com': {
        messageContainer: '.flex.flex-col.items-center.text-sm',
        messages: '.markdown',
        messageText: '.markdown p',
        sender: '.font-semibold',
        timestamp: '.text-gray-400',
        inputField: 'textarea',
        sendButton: 'button[data-testid="send-button"]'
    },
    'mail.google.com': {
        messageContainer: '.Bs.nH.iY.bAt',
        messages: '.gs',
        messageText: '.a3s.aiL',
        sender: '.gD',
        timestamp: '.g3',
        inputField: '[role="textbox"]',
        sendButton: '[data-tooltip="Send ‪(⌘Enter)‬"]'
    },
    'www.linkedin.com': {
        messageContainer: '.msg-conversations-container__conversations-list',
        messages: '.msg-s-message-list__event',
        messageText: '.msg-s-event-listitem__body',
        sender: '.msg-s-message-group__name',
        timestamp: '.msg-s-message-group__timestamp',
        inputField: '.msg-form__contenteditable',
        sendButton: '.msg-form__send-button'
    },
    'twitter.com': {
        messageContainer: '.css-1dbjc4n.r-1jgb5lz.r-1ye8kvj',
        messages: '[data-testid="messageEntry"]',
        messageText: '[data-testid="tweetText"]',
        sender: '[data-testid="User-Name"]',
        timestamp: '[data-testid="timestamp"]',
        inputField: '[data-testid="dmComposerTextInput"]',
        sendButton: '[data-testid="dmComposerSendButton"]'
    },
    'outlook.live.com': {
        messageContainer: '[role="main"]',
        messages: '.ReadMsgContainer',
        messageText: '.ReadMsgBody',
        sender: '.ReadMsgHeaderFrom',
        timestamp: '.ReadMsgHeaderDate',
        inputField: '[aria-label="Message body"]',
        sendButton: '[aria-label="Send"]'
    },
    'reddit.com': {
        messageContainer: '.ListingLayout-backgroundContainer',
        messages: '.ChatMessageThread__messageContainer',
        messageText: '.ChatMessageContent',
        sender: '.ChatMessageHeader__username',
        timestamp: '.ChatMessageHeader__timestamp',
        inputField: '.ChatComposer__textarea',
        sendButton: '.ChatSubmitButton'
    },
    'meet.google.com': {
        messageContainer: '.z38b6',
        messages: '.GDhqjd',
        messageText: '.oIy2qc',
        sender: '.YTbUzc',
        timestamp: '.MuzmKe',
        inputField: '.KHxj8b',
        sendButton: '.VfPpkd-Bz112c-LgbsSe'
    },
    'zoom.us': {
        messageContainer: '.chat-list__container',
        messages: '.chat-message__container',
        messageText: '.chat-message__text',
        sender: '.chat-message__sender',
        timestamp: '.chat-message__time',
        inputField: '.chat-composer__input',
        sendButton: '.chat-composer__send-btn'
    },
    'web.skype.com': {
        messageContainer: '.ConversationView',
        messages: '.message',
        messageText: '.content',
        sender: '.sender',
        timestamp: '.timestamp',
        inputField: '[role="textbox"]',
        sendButton: '.send-button'
    }
};

// Export for use in content script
if (typeof module !== 'undefined') {
    module.exports = { PLATFORM_SELECTORS };
}

// Verification function
function verifySelectors() {
  const hostname = window.location.hostname;
  const selectors = PLATFORM_SELECTORS[hostname];
  
  if (!selectors) {
    console.error("No selectors defined for this platform:", hostname);
    return {
      platform: hostname,
      supported: false,
      error: "No selectors defined"
    };
  }
  
  console.log("Verifying selectors for:", hostname);
  
  const results = {
    platform: hostname,
    supported: true,
    selectors: {}
  };
  
  for (const [name, selector] of Object.entries(selectors)) {
    try {
      const elements = document.querySelectorAll(selector);
      const found = elements.length > 0;
      
      results.selectors[name] = {
        selector: selector,
        found: found,
        count: elements.length
      };
      
      console.log(`Selector: ${name} (${selector}) - ${found ? "✓" : "✗"} (${elements.length} elements found)`);
    } catch (error) {
      results.selectors[name] = {
        selector: selector,
        found: false,
        error: error.message
      };
      
      console.error(`Error testing selector ${name}: ${error.message}`);
    }
  }
  
  return results;
}

// Run verification and show results
const results = verifySelectors();
console.log("==================================");
console.log("Verification Results:", results);

// Add results to page for easy copying
const resultDiv = document.createElement("div");
resultDiv.style.position = "fixed";
resultDiv.style.top = "10px";
resultDiv.style.right = "10px";
resultDiv.style.padding = "10px";
resultDiv.style.background = "white";
resultDiv.style.border = "1px solid black";
resultDiv.style.zIndex = "9999";
resultDiv.style.maxHeight = "80vh";
resultDiv.style.overflow = "auto";
resultDiv.style.maxWidth = "400px";
resultDiv.style.fontSize = "12px";
resultDiv.style.fontFamily = "monospace";

resultDiv.innerHTML = `
  <h3>Catalyst Selector Verification</h3>
  <p>Platform: ${results.platform}</p>
  <p>Support: ${results.supported ? "✓" : "✗"}</p>
  <h4>Selectors:</h4>
  <table style="border-collapse: collapse; width: 100%;">
    <tr>
      <th style="border: 1px solid #ddd; padding: 4px; text-align: left;">Name</th>
      <th style="border: 1px solid #ddd; padding: 4px; text-align: left;">Found</th>
      <th style="border: 1px solid #ddd; padding: 4px; text-align: left;">Count</th>
    </tr>
    ${Object.entries(results.selectors).map(([name, info]) => `
      <tr>
        <td style="border: 1px solid #ddd; padding: 4px;">${name}</td>
        <td style="border: 1px solid #ddd; padding: 4px; color: ${info.found ? 'green' : 'red'};">${info.found ? "✓" : "✗"}</td>
        <td style="border: 1px solid #ddd; padding: 4px;">${info.count || 0}</td>
      </tr>
    `).join('')}
  </table>
  <button id="closeBtn" style="margin-top: 10px;">Close</button>
`;

document.body.appendChild(resultDiv);
document.getElementById("closeBtn").addEventListener("click", () => {
  resultDiv.remove();
});
