#!/bin/bash
# Catalyst Whisper Coach - Platform Testing Script
# This script helps test the extension on each supported platform

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results directory
TEST_DIR="./testing/results"
mkdir -p $TEST_DIR

# Log file
LOG_FILE="$TEST_DIR/platform_test_$(date +%Y%m%d%H%M%S).log"
echo -e "${BLUE}📝 Logging test results to $LOG_FILE${NC}"

# Function to log messages
log() {
  echo -e "$1" | tee -a $LOG_FILE
}

# Function to display header
header() {
  log "\n${BLUE}==============================================${NC}"
  log "${BLUE}  $1${NC}"
  log "${BLUE}==============================================${NC}"
}

# Display supported platforms
platforms=(
  "WhatsApp Web (https://web.whatsapp.com)"
  "Facebook Messenger (https://www.messenger.com)"
  "Instagram DMs (https://www.instagram.com/direct/inbox)"
  "Discord (https://discord.com/channels/@me)"
  "Slack (Your workspace URL)"
  "Microsoft Teams (https://teams.microsoft.com)"
  "Telegram Web (https://web.telegram.org)"
)

# Start testing
header "Catalyst Whisper Coach - Platform Testing"
log "Starting platform testing on $(date)"
log "This script will guide you through testing the extension on each supported platform."
log "Make sure you have the extension installed in Chrome before proceeding."

# Check if Chrome is available
if ! command -v "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" &> /dev/null; then
  log "${RED}❌ Google Chrome not found. Please install Chrome to test the extension.${NC}"
  exit 1
fi

# Check if the extension directory exists
if [ ! -d "." ] || [ ! -f "manifest.json" ]; then
  log "${RED}❌ Not in the extension directory. Please run this script from the chrome_extension directory.${NC}"
  exit 1
fi

# Create platform test files
mkdir -p testing/platforms

# Display the list of platforms
log "\n${YELLOW}Supported Platforms:${NC}"
for i in "${!platforms[@]}"; do
  log "  ${GREEN}$((i+1))${NC}. ${platforms[$i]}"
done

log "\n${YELLOW}Platform Testing Instructions:${NC}"
log "1. Open Chrome with the extension loaded using the 'Run Chrome with Extension' VS Code task"
log "2. Navigate to each platform and log in with your test account"
log "3. Start a conversation or open an existing one"
log "4. Send test messages and verify that the extension detects them"
log "5. Check that whisper suggestions appear in the extension popup"
log "6. Record the results for each platform in this script"

# Create test files for each platform
create_platform_test_file() {
  local platform=$1
  local filename=$(echo $platform | tr '[:upper:]' '[:lower:]' | sed 's/ /_/g' | cut -d'(' -f1)
  local file="testing/platforms/${filename}_test.md"
  
  if [ ! -f "$file" ]; then
    cat > "$file" << EOF
# $platform Testing Report

## Test Environment
- **Date:** $(date +"%Y-%m-%d")
- **Chrome Version:** $(google-chrome --version 2>/dev/null || echo "Unknown")
- **Extension Version:** $(grep -o '"version": "[^"]*"' manifest.json | cut -d'"' -f4)
- **Tester:** YOUR_NAME

## Test Scenarios

### Basic Connection
- [ ] Platform loads correctly with extension active
- [ ] No console errors related to the extension
- [ ] Extension icon shows as active

### Message Detection
- [ ] Extension detects sent messages
- [ ] Extension detects received messages
- [ ] Message sender is correctly identified
- [ ] Message timestamp is correctly captured

### Whisper Functionality
- [ ] Whisper suggestions appear after sending messages
- [ ] Suggestions are contextually relevant
- [ ] Suggestion UI displays correctly

### DOM Selectors Verification
\`\`\`javascript
// Verify these selectors from content_script.js
// Update with actual results
{
  messageContainer: '?',
  messages: '?',
  messageText: '?',
  sender: '?',
  timestamp: '?',
  inputField: '?',
  sendButton: '?'
}
\`\`\`

## Issues Found
1. 

## Screenshots
(Attach screenshots here)

## Notes
- 
EOF
    log "${GREEN}✅ Created test template for $platform at $file${NC}"
  else
    log "${YELLOW}⚠️ Test file for $platform already exists at $file${NC}"
  fi
}

# Create test files for each platform
for platform in "${platforms[@]}"; do
  platform_name=$(echo $platform | cut -d'(' -f1 | xargs)
  create_platform_test_file "$platform_name"
done

# Create DOM selector verification script
cat > "testing/test_selectors.js" << EOF
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
              console.log(\`  \${i+1}. "\${text}"\`);
              msgs.push(text);
            }
          });
          
          results.sampleMessages = msgs;
        }
      }
      
    } catch (error) {
      console.error(\`Error testing selector \${key}: \${selector}\`, error);
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
EOF

log "${GREEN}✅ Created DOM selector verification script at testing/test_selectors.js${NC}"

# Create overall testing guide
cat > "testing/PLATFORM_TESTING_GUIDE.md" << EOF
# Catalyst Whisper Coach - Platform Testing Guide

This guide provides step-by-step instructions for testing the Catalyst Whisper Coach extension on supported messaging platforms.

## Prerequisites

- Google Chrome browser
- Test accounts for each platform you plan to test
- The Catalyst Whisper Coach extension loaded in Chrome

## Testing Process

### 1. Set Up Testing Environment

1. Clone the Catalyst repository if you haven't already
2. Open VS Code and navigate to the Catalyst project
3. Make sure the backend server is running:
   \`\`\`
   cd backend
   python main.py
   \`\`\`
4. Use the VS Code task "Run Chrome with Extension" to load the extension

### 2. Platform Testing Workflow

For each platform, follow these steps:

1. **Navigate to the platform**
   - Go to the platform's web interface (URLs listed below)
   - Log in with your test account

2. **Open or start a conversation**
   - Open an existing conversation or start a new one
   - Send a few test messages

3. **Verify DOM selectors**
   - Open Chrome DevTools (F12 or Right-click > Inspect)
   - Go to the Console tab
   - Copy and paste the content of \`testing/test_selectors.js\`
   - Review the results to verify that all selectors are working

4. **Test Whisper functionality**
   - Send various types of messages
   - Click the extension icon to see if whisper suggestions appear
   - Verify that suggestions are relevant to the conversation

5. **Document your findings**
   - Fill out the test template in \`testing/platforms/[platform]_test.md\`
   - Include screenshots if possible
   - Note any issues or discrepancies

### 3. Supported Platforms

- **WhatsApp Web**: https://web.whatsapp.com
- **Facebook Messenger**: https://www.messenger.com
- **Instagram DMs**: https://www.instagram.com/direct/inbox
- **Discord**: https://discord.com/channels/@me
- **Slack**: Your workspace URL
- **Microsoft Teams**: https://teams.microsoft.com
- **Telegram Web**: https://web.telegram.org

### 4. What to Look For

- **DOM Selector Issues**: If selectors are not finding elements, they may need to be updated
- **Message Detection**: Verify that the extension correctly detects messages being sent and received
- **Whisper Quality**: Assess the relevance and helpfulness of the whisper suggestions
- **Performance Impact**: Note any performance issues (slowdowns, high CPU usage, etc.)
- **Visual Integration**: Check that the extension UI displays correctly and doesn't interfere with the platform UI

### 5. Reporting Issues

For each issue found, document:
1. The platform where the issue occurs
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Screenshots if applicable

### 6. Updating Selectors

If you find that DOM selectors need to be updated:

1. Note the current selector that's not working
2. Use Chrome DevTools to identify the correct selector
3. Update the selector in \`content_script.js\`
4. Test the updated selector using the verification script
5. Document the changes in your test report

## Final Report

After testing all platforms, compile your findings into a comprehensive report that includes:

1. A summary of all platforms tested
2. Success rate for each platform
3. Common issues across platforms
4. Platform-specific issues
5. Recommendations for improvements

This report will be crucial for improving the extension's compatibility and performance across all supported platforms.
EOF

log "${GREEN}✅ Created platform testing guide at testing/PLATFORM_TESTING_GUIDE.md${NC}"

# Create a summary template
cat > "testing/PLATFORM_TESTING_SUMMARY.md" << EOF
# Catalyst Whisper Coach - Platform Testing Summary

## Overview

- **Testing Period:** [Start Date] to [End Date]
- **Extension Version:** $(grep -o '"version": "[^"]*"' manifest.json | cut -d'"' -f4)
- **Tester(s):** [Names]

## Platforms Tested

| Platform | Status | DOM Selectors | Message Detection | Whisper Suggestions | Notes |
|----------|--------|---------------|-------------------|---------------------|-------|
| WhatsApp Web | | | | | |
| Facebook Messenger | | | | | |
| Instagram DMs | | | | | |
| Discord | | | | | |
| Slack | | | | | |
| Microsoft Teams | | | | | |
| Telegram Web | | | | | |

## Key Findings

### Successes
- 

### Issues
- 

### Recommendations
- 

## Detailed Reports

See individual platform test reports in the \`testing/platforms\` directory.
EOF

log "${GREEN}✅ Created platform testing summary template at testing/PLATFORM_TESTING_SUMMARY.md${NC}"

# Instructions for running Chrome with the extension
header "How to Test the Extension"
log "1. Use the VS Code task 'Run Chrome with Extension' to open Chrome with the extension loaded"
log "2. Follow the testing guide in testing/PLATFORM_TESTING_GUIDE.md"
log "3. Fill out the test templates for each platform you test"
log "4. Compile your findings in the summary template"

log "\n${GREEN}✅ Setup complete! You're ready to start platform testing.${NC}"
log "The following files have been created to help with testing:"
log "  - ${BLUE}testing/PLATFORM_TESTING_GUIDE.md${NC}: Step-by-step testing instructions"
log "  - ${BLUE}testing/test_selectors.js${NC}: Script to verify DOM selectors"
log "  - ${BLUE}testing/platforms/*.md${NC}: Test templates for each platform"
log "  - ${BLUE}testing/PLATFORM_TESTING_SUMMARY.md${NC}: Summary template for findings"

log "\n${YELLOW}Happy testing!${NC}"
