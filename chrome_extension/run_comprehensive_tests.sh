#!/bin/bash
# Catalyst Whisper Coach - Comprehensive Platform Testing Script
# This script automates the process of testing the extension across all supported platforms
# Updated: June 17, 2025

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results directory
TEST_DIR="./testing/comprehensive_tests"
mkdir -p $TEST_DIR

# Current timestamp
TIMESTAMP=$(date +%Y%m%d%H%M%S)

# Log file
LOG_FILE="$TEST_DIR/comprehensive_test_$TIMESTAMP.log"
HTML_REPORT="$TEST_DIR/comprehensive_test_$TIMESTAMP.html"
HTML_REPORT="$TEST_DIR/comprehensive_test_$TIMESTAMP.html"

echo -e "${BLUE}🔍 Catalyst Whisper Coach - Comprehensive Platform Testing${NC}"
echo -e "${BLUE}📅 Date: $(date)${NC}"
echo -e "${BLUE}===================================================${NC}"
echo -e "${BLUE}📝 Logging results to $LOG_FILE${NC}"

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

# List of supported platforms
platforms=(
  "web.whatsapp.com"
  "www.messenger.com"
  "www.instagram.com/direct/inbox"
  "discord.com/channels/@me"
  "slack.com"
  "teams.microsoft.com"
  "web.telegram.org"
  "meet.google.com"
  "zoom.us"
  "chat.openai.com"
  "mail.google.com"
  "www.linkedin.com/messaging"
  "twitter.com"
  "outlook.live.com"
  "reddit.com"
  "web.skype.com"
)

# Step 1: Verify prerequisites
header "Verifying Prerequisites"

# Check Chrome browser
if command -v "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" &> /dev/null; then
  log "${GREEN}✅ Google Chrome is installed${NC}"
  CHROME_VERSION=$("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version | awk '{print $3}')
  log "   Chrome version: $CHROME_VERSION"
else
  log "${RED}❌ Google Chrome not found. Please install Chrome to test the extension.${NC}"
  exit 1
fi

# Check extension files
if [ ! -f "manifest.json" ] || [ ! -f "content_script.js" ] || [ ! -f "platform_selectors.js" ]; then
  log "${RED}❌ Extension files not found. Please run this script from the chrome_extension directory.${NC}"
  exit 1
else
  log "${GREEN}✅ Extension files found${NC}"
  EXTENSION_VERSION=$(grep -o '"version": "[^"]*"' manifest.json | cut -d'"' -f4)
  log "   Extension version: $EXTENSION_VERSION"
fi

# Check if back-end server is running
if curl -s "http://localhost:8000/health" | grep -q "status"; then
  log "${GREEN}✅ Backend server is running${NC}"
else
  log "${YELLOW}⚠️ Backend server might not be running. Some tests may fail.${NC}"
  log "   To start the server: cd ../backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000"
fi

# Step 2: Verify selectors
header "Verifying Platform Selectors"

# Run selector verification script if it exists
if [ -f "verify_selectors.sh" ]; then
  log "Running selector verification script..."
  ./verify_selectors.sh > /dev/null
  
  # Get the most recent verification report
  RECENT_VERIFICATION=$(ls -t ./testing/verification_results/selector_verification_*.html 2>/dev/null | head -n 1)
  
  if [ -n "$RECENT_VERIFICATION" ]; then
    log "${GREEN}✅ Selector verification completed${NC}"
    log "   Report: $RECENT_VERIFICATION"
    
    # Check for missing permissions or selectors
    if grep -q "All platforms have proper permissions and selectors" "$RECENT_VERIFICATION"; then
      log "${GREEN}✅ All platform selectors are valid${NC}"
    else
      log "${YELLOW}⚠️ There might be issues with platform selectors. Review the verification report.${NC}"
    fi
  else
    log "${YELLOW}⚠️ Could not find verification report. Selectors might not be verified.${NC}"
  fi
else
  log "${YELLOW}⚠️ verify_selectors.sh not found. Skipping selector verification.${NC}"
fi

# Step 3: Start comprehensive platform testing
header "Preparing for Platform Testing"

# Create test directories and files
mkdir -p $TEST_DIR/screenshots
mkdir -p $TEST_DIR/platforms

# Generate platform test templates
log "Generating test templates for each platform..."

for platform in "${platforms[@]}"; do
  platform_name=$(echo $platform | cut -d'/' -f1)
  test_file="$TEST_DIR/platforms/${platform_name}_test.md"
  
  cat > "$test_file" << EOF
# $platform Test Results

## Test Environment
- **Date:** $(date +"%Y-%m-%d")
- **Chrome Version:** $CHROME_VERSION
- **Extension Version:** $EXTENSION_VERSION
- **Tester:** $(whoami)

## Message Detection Test
- [ ] Extension detects sent messages
- [ ] Extension detects received messages
- [ ] Message sender is correctly identified
- [ ] Message timestamp is correctly captured

## Whisper Functionality Test
- [ ] Whisper suggestions appear after emotional content
- [ ] Suggestions are contextually relevant
- [ ] Suggestion UI displays correctly

## Notes:
<!-- Add any additional notes here -->

## Screenshots:
<!-- Add links to screenshots here -->
EOF

  log "  ${GREEN}✓${NC} Created test template for $platform_name"
done

# Step 4: Start Chrome with the extension
header "Starting Chrome with Extension"

log "Launching Chrome with the extension loaded..."
log "${YELLOW}NOTE: This will open a new Chrome window. Please do not close it until testing is complete.${NC}"

# Create a launch script
CHROME_LAUNCH_SCRIPT="$TEST_DIR/launch_chrome.sh"

cat > "$CHROME_LAUNCH_SCRIPT" << EOF
#!/bin/bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --load-extension="$(pwd)" --no-first-run --user-data-dir=/tmp/catalyst-test-profile
EOF

chmod +x "$CHROME_LAUNCH_SCRIPT"

# Launch Chrome in the background
$CHROME_LAUNCH_SCRIPT &
CHROME_PID=$!

log "${GREEN}✅ Chrome launched with extension${NC}"
log "   Process ID: $CHROME_PID"
log "   To manually launch Chrome later, run: $CHROME_LAUNCH_SCRIPT"

# Step 5: Create the browser test script
header "Creating Browser Test Script"

BROWSER_TEST_SCRIPT="$TEST_DIR/browser_test_script.js"

cat > "$BROWSER_TEST_SCRIPT" << 'EOF'
// Catalyst Whisper Coach - Browser Test Script
// Paste this script in the browser console to test the extension on a platform

(function() {
  console.clear();
  console.log('%c Catalyst Whisper Coach - Platform Testing', 'font-weight: bold; font-size: 16px; color: #6772e5;');
  
  // Current hostname and URL
  const hostname = window.location.hostname;
  const url = window.location.href;
  console.log('%cTesting platform:', 'font-weight: bold', hostname);
  console.log('URL:', url);
  
  // Check if extension is loaded
  if (typeof window.catalystInjected === 'undefined') {
    console.log('%c❌ Extension not detected on this page!', 'color: red; font-weight: bold');
    console.log('Make sure the extension is loaded and permissions are granted for this domain.');
    return false;
  }
  
  console.log('%c✅ Extension detected!', 'color: green; font-weight: bold');
  
  // Platform detection
  let platformName = 'unknown';
  if (hostname.includes('whatsapp')) platformName = 'WhatsApp';
  else if (hostname.includes('messenger')) platformName = 'Facebook Messenger';
  else if (hostname.includes('instagram')) platformName = 'Instagram';
  else if (hostname.includes('discord')) platformName = 'Discord';
  else if (hostname.includes('slack')) platformName = 'Slack';
  else if (hostname.includes('teams')) platformName = 'Microsoft Teams';
  else if (hostname.includes('telegram')) platformName = 'Telegram';
  else if (hostname.includes('meet.google')) platformName = 'Google Meet';
  else if (hostname.includes('zoom')) platformName = 'Zoom';
  else if (hostname.includes('chat.openai')) platformName = 'ChatGPT';
  else if (hostname.includes('mail.google')) platformName = 'Gmail';
  else if (hostname.includes('linkedin')) platformName = 'LinkedIn';
  else if (hostname.includes('twitter') || hostname.includes('x.com')) platformName = 'Twitter/X';
  else if (hostname.includes('outlook')) platformName = 'Outlook';
  else if (hostname.includes('reddit')) platformName = 'Reddit';
  else if (hostname.includes('skype')) platformName = 'Skype';
  
  console.log('Detected platform:', platformName);
  
  // Check content script functions
  if (typeof window.catalystDebug !== 'undefined') {
    console.log('%c✅ Debug helpers available!', 'color: green');
    
    console.log('\n%cTesting DOM selectors...', 'font-weight: bold');
    const selectorResults = window.catalystDebug.testSelectors();
    console.log('Selector test results:', selectorResults);
    
    // Test message detection
    console.log('\n%cTesting message detection...', 'font-weight: bold');
    const messages = window.catalystDebug.logMessages(3);
    if (messages && messages.length > 0) {
      console.log('%c✅ Detected ' + messages.length + ' messages!', 'color: green');
      console.log('Sample messages:', messages);
    } else {
      console.log('%c❌ No messages detected', 'color: orange');
      console.log('Either there are no messages in the conversation or selectors might need adjustment.');
    }
    
    // Test whisper generation
    console.log('\n%cTesting whisper generation...', 'font-weight: bold');
    console.log('Requesting a test whisper suggestion...');
    
    window.catalystDebug.forceSuggestion("I'm feeling upset about what happened yesterday")
      .then(response => {
        if (response && response.suggestions) {
          console.log('%c✅ Whisper suggestion generated!', 'color: green');
          console.log('Suggestion:', response.suggestions[0]);
        } else {
          console.log('%c❌ Failed to generate whisper suggestion', 'color: red');
          console.log('Response:', response);
        }
      })
      .catch(error => {
        console.log('%c❌ Error generating whisper suggestion', 'color: red');
        console.log('Error:', error);
      });
  } else {
    console.log('%c❌ Debug helpers not available!', 'color: red');
    console.log('Make sure content_script.js includes the debug helpers.');
  }
  
  // Return test status
  return {
    extensionDetected: typeof window.catalystInjected !== 'undefined',
    debugHelpersAvailable: typeof window.catalystDebug !== 'undefined',
    platform: platformName,
    url: url,
    timestamp: new Date().toISOString()
  };
})();
EOF

log "${GREEN}✅ Browser test script created at $BROWSER_TEST_SCRIPT${NC}"
log "To use this script:"
log "1. Navigate to each platform in Chrome"
log "2. Open Chrome DevTools (F12 or Ctrl+Shift+I)"
log "3. Paste the script into the console"
log "4. Review the results and record them in the test templates"

# Step 6: Create a platform testing guide
header "Creating Testing Guide"

TESTING_GUIDE="$TEST_DIR/TESTING_GUIDE.md"

cat > "$TESTING_GUIDE" << 'EOF'
# Catalyst Whisper Coach - Comprehensive Testing Guide

This guide will help you test the Catalyst Whisper Coach extension across all supported platforms.

## Testing Process

For each platform, follow these steps:

1. **Navigate to the platform** in the Chrome browser that was launched with the extension
2. **Log in** with your test account (if required)
3. **Open or start a conversation**
4. **Open Chrome DevTools** (F12 or Ctrl+Shift+I)
5. **Paste the browser test script** from `browser_test_script.js` into the console
6. **Review the results** in the console
7. **Send a few test messages** with emotional content to trigger whisper suggestions
8. **Take screenshots** of the extension in action
9. **Fill out the test template** for the platform

## What to Test on Each Platform

### 1. Extension Detection
- The extension should be detected on the platform
- Debug helpers should be available

### 2. DOM Selectors
- All required selectors should find elements on the page
- Check the selector test results in the console

### 3. Message Detection
- Send a few messages in the conversation
- Check if the extension detects the messages
- Verify sender and timestamp information

### 4. Whisper Functionality
- Send messages with emotional content
- Check if whisper suggestions appear
- Verify that suggestions are relevant
- Make sure the UI displays correctly

### 5. UI Integration
- The extension UI should integrate well with the platform
- No visual glitches or overlap issues

## Taking Screenshots

Take screenshots of:
1. The platform with the extension active
2. The console showing test results
3. Whisper suggestions appearing
4. Any issues or bugs encountered

## Filling Out Test Templates

For each platform, fill out the test template in the `platforms` directory:
- Check off the test items that pass
- Add notes about any issues
- Include links to screenshots

## Reporting Issues

If you encounter issues:
1. Describe the issue in detail
2. Note the steps to reproduce
3. Include screenshots
4. Specify the platform and exact URL
5. Record any error messages from the console

## After Testing All Platforms

When you've completed testing all platforms:
1. Run the `generate_test_report.sh` script to create a consolidated report
2. Review the report for any patterns or common issues
3. Prioritize issues based on severity and impact
4. Make recommendations for improvements
EOF

log "${GREEN}✅ Testing guide created at $TESTING_GUIDE${NC}"

# Step 7: Create a report generation script
header "Creating Report Generation Script"

REPORT_SCRIPT="$TEST_DIR/generate_test_report.sh"

cat > "$REPORT_SCRIPT" << 'EOF'
#!/bin/bash
# Script to generate a consolidated test report

# Directory containing test results
TEST_DIR=$(dirname "$0")
PLATFORMS_DIR="$TEST_DIR/platforms"
SCREENSHOTS_DIR="$TEST_DIR/screenshots"

# Output file
REPORT_FILE="$TEST_DIR/consolidated_report.md"

echo "Generating consolidated test report..."

# Create report header
cat > "$REPORT_FILE" << HEADER
# Catalyst Whisper Coach - Consolidated Test Report

**Generated on:** $(date)

## Test Environment
- **Chrome Version:** $(grep -m 1 "Chrome Version" $PLATFORMS_DIR/*.md | head -n 1 | cut -d':' -f2 | xargs)
- **Extension Version:** $(grep -m 1 "Extension Version" $PLATFORMS_DIR/*.md | head -n 1 | cut -d':' -f2 | xargs)

## Summary

| Platform | Message Detection | Whisper Functionality | Status |
|----------|-------------------|----------------------|--------|
HEADER

# Process each platform test file
for test_file in "$PLATFORMS_DIR"/*.md; do
    platform=$(basename "$test_file" _test.md)
    
    # Extract test results
    message_detection=$(grep -c "\[x\]" <<< "$(grep "Extension detects" "$test_file")")
    message_detection_total=$(grep -c "Extension detects" "$test_file")
    
    whisper_functionality=$(grep -c "\[x\]" <<< "$(grep "Whisper" "$test_file")")
    whisper_functionality_total=$(grep -c "Whisper" "$test_file")
    
    # Determine status
    if [ "$message_detection" -eq "$message_detection_total" ] && [ "$whisper_functionality" -eq "$whisper_functionality_total" ]; then
        status="✅ Pass"
    elif [ "$message_detection" -eq 0 ] || [ "$whisper_functionality" -eq 0 ]; then
        status="❌ Fail"
    else
        status="⚠️ Partial"
    fi
    
    # Add to report
    echo "| $platform | $message_detection/$message_detection_total | $whisper_functionality/$whisper_functionality_total | $status |" >> "$REPORT_FILE"
done

# Add issues section
cat >> "$REPORT_FILE" << ISSUES

## Issues Found

ISSUES

# Extract issues from test files
for test_file in "$PLATFORMS_DIR"/*.md; do
    platform=$(basename "$test_file" _test.md)
    notes=$(sed -n '/## Notes:/,/## Screenshots:/p' "$test_file" | grep -v "## Notes:" | grep -v "## Screenshots:" | grep -v "<!--")
    
    if [ -n "$notes" ]; then
        echo "### $platform" >> "$REPORT_FILE"
        echo "$notes" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
done

# Add recommendations section
cat >> "$REPORT_FILE" << RECOMMENDATIONS

## Recommendations

- Review all platforms marked as "Fail" or "Partial"
- Prioritize fixing DOM selectors for platforms with message detection issues
- Test the extension on additional accounts for each platform
- Consider adding automated testing for critical platforms

## Next Steps

1. Address critical issues identified in this report
2. Retest platforms with issues after fixes are implemented
3. Expand testing to include more edge cases
4. Prepare for user acceptance testing (UAT)
RECOMMENDATIONS

echo "Report generated at: $REPORT_FILE"
EOF

chmod +x "$REPORT_SCRIPT"
log "${GREEN}✅ Report generation script created at $REPORT_SCRIPT${NC}"

# Step 8: Create test debug helpers for content_script.js
header "Creating Test Debug Helpers"

# Create a patch file for content_script.js
DEBUG_HELPERS_PATCH="$TEST_DIR/debug_helpers.js"

cat > "$DEBUG_HELPERS_PATCH" << 'EOF'
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
EOF

log "${GREEN}✅ Debug helpers created at $DEBUG_HELPERS_PATCH${NC}"
log "${YELLOW}⚠️ Important: Add these debug helpers to content_script.js for testing${NC}"
log "To add debug helpers:"
log "1. Open content_script.js"
log "2. Add the contents of $DEBUG_HELPERS_PATCH at the end of the file"
log "3. Reload the extension in Chrome"

# Step 9: Generate HTML report
header "Generating HTML Report"

cat > "$HTML_REPORT" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catalyst Comprehensive Testing Report</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .timestamp {
            color: #7f8c8d;
            font-style: italic;
        }
        .summary {
            background-color: #f8f9fa;
            border-radius: 5px;
            padding: 15px;
            margin: 20px 0;
        }
        .platform-list {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .platform-card {
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 15px;
            background-color: #fff;
        }
        .platform-card h3 {
            margin-top: 0;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }
        .step {
            margin-bottom: 20px;
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
        }
        .step h3 {
            margin-top: 0;
        }
        .step-number {
            display: inline-block;
            width: 25px;
            height: 25px;
            background-color: #2c3e50;
            color: white;
            border-radius: 50%;
            text-align: center;
            margin-right: 10px;
        }
        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        .file-path {
            font-family: monospace;
            background-color: #f0f0f0;
            padding: 5px;
            border-radius: 3px;
        }
    </style>
</head>
<body>
    <h1>Catalyst Whisper Coach - Comprehensive Testing</h1>
    <p class="timestamp">Generated on: $(date)</p>
    
    <div class="summary">
        <h2>Testing Setup Complete</h2>
        <p>All necessary files and scripts have been created to perform comprehensive testing of the Catalyst Whisper Coach extension across all supported platforms.</p>
        <p><strong>Chrome Version:</strong> $CHROME_VERSION</p>
        <p><strong>Extension Version:</strong> $EXTENSION_VERSION</p>
    </div>
    
    <h2>Supported Platforms</h2>
    <div class="platform-list">
EOF

# Add platform cards to HTML report
for platform in "${platforms[@]}"; do
  platform_name=$(echo $platform | cut -d'/' -f1)
  readable_name=$(echo $platform_name | sed 's/\.com//' | sed 's/www\.//' | sed 's/web\.//' | tr '.' ' ' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2)} 1')
  
  cat >> "$HTML_REPORT" << EOF
        <div class="platform-card">
            <h3>$readable_name</h3>
            <p><strong>Domain:</strong> $platform_name</p>
            <p><strong>Test File:</strong> <span class="file-path">$TEST_DIR/platforms/${platform_name}_test.md</span></p>
        </div>
EOF
done

cat >> "$HTML_REPORT" << EOF
    </div>
    
    <h2>Testing Process</h2>
    
    <div class="step">
        <h3><span class="step-number">1</span> Prepare Test Environment</h3>
        <p>The testing environment has been set up with the following components:</p>
        <ul>
            <li>Chrome browser with the extension loaded</li>
            <li>Test templates for each platform</li>
            <li>Browser test script for verifying extension functionality</li>
            <li>Debug helpers for content_script.js</li>
        </ul>
    </div>
    
    <div class="step">
        <h3><span class="step-number">2</span> Test Each Platform</h3>
        <p>For each platform, follow these steps:</p>
        <ol>
            <li>Navigate to the platform in Chrome</li>
            <li>Log in with your test account</li>
            <li>Open Chrome DevTools (F12)</li>
            <li>Paste the browser test script from <span class="file-path">$BROWSER_TEST_SCRIPT</span></li>
            <li>Review the test results in the console</li>
            <li>Fill out the test template for the platform</li>
        </ol>
    </div>
    
    <div class="step">
        <h3><span class="step-number">3</span> Generate Consolidated Report</h3>
        <p>After testing all platforms, run the report generation script to create a consolidated report:</p>
        <code>$REPORT_SCRIPT</code>
        <p>This will analyze all test results and generate a comprehensive report with findings and recommendations.</p>
    </div>
    
    <h2>Test Files</h2>
    <ul>
        <li><strong>Chrome Launch Script:</strong> <span class="file-path">$CHROME_LAUNCH_SCRIPT</span></li>
        <li><strong>Browser Test Script:</strong> <span class="file-path">$BROWSER_TEST_SCRIPT</span></li>
        <li><strong>Testing Guide:</strong> <span class="file-path">$TESTING_GUIDE</span></li>
        <li><strong>Report Generation Script:</strong> <span class="file-path">$REPORT_SCRIPT</span></li>
        <li><strong>Debug Helpers:</strong> <span class="file-path">$DEBUG_HELPERS_PATCH</span></li>
    </ul>
    
    <h2>Next Steps</h2>
    <ol>
        <li>Add the debug helpers to content_script.js</li>
        <li>Test each platform using the browser test script</li>
        <li>Document your findings in the test templates</li>
        <li>Generate a consolidated report</li>
        <li>Fix any issues found during testing</li>
    </ol>
    
    <footer>
        <p>Catalyst Whisper Coach Extension - Comprehensive Testing Report</p>
        <p class="timestamp">Generated on: $(date)</p>
    </footer>
</body>
</html>
EOF

log "${GREEN}✅ HTML report generated at $HTML_REPORT${NC}"

# Step 10: Summary
header "Comprehensive Testing Setup Complete"

log "${GREEN}✅ All necessary files and scripts have been created for comprehensive testing.${NC}"
log "\n${YELLOW}📋 Testing Files:${NC}"
log "  ${BLUE}→${NC} Chrome Launch Script:     $CHROME_LAUNCH_SCRIPT"
log "  ${BLUE}→${NC} Browser Test Script:      $BROWSER_TEST_SCRIPT"
log "  ${BLUE}→${NC} Testing Guide:            $TESTING_GUIDE"
log "  ${BLUE}→${NC} Report Generation Script: $REPORT_SCRIPT"
log "  ${BLUE}→${NC} Debug Helpers:            $DEBUG_HELPERS_PATCH"
log "  ${BLUE}→${NC} HTML Report:              $HTML_REPORT"

log "\n${YELLOW}📋 Next Steps:${NC}"
log "1. Add the debug helpers to content_script.js"
log "2. Test each platform using the browser test script"
log "3. Document your findings in the test templates"
log "4. Generate a consolidated report using $REPORT_SCRIPT"
log "5. Fix any issues found during testing"

log "\n${GREEN}🚀 Start testing by opening Chrome and navigating to each supported platform.${NC}"
log "Refer to the testing guide at $TESTING_GUIDE for detailed instructions."
log "\n${BLUE}Happy testing!${NC}"

# Open HTML report in browser
open "$HTML_REPORT" &

exit 0

# Function to log messages
log_message() {
  echo -e "$1" | tee -a "$LOG_FILE"
}

log_message "# Catalyst Comprehensive Test - $TIMESTAMP"
log_message "Starting comprehensive platform testing for Catalyst Chrome Extension"
log_message "==============================================================="

# Get list of platforms from platform_selectors.js
PLATFORMS=$(grep -o "'[^']*':" platform_selectors.js | sed "s/'//g" | sed "s/://g")

# Create HTML report header
cat > "$HTML_REPORT" << EOF
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Catalyst Comprehensive Test Report</title>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 1200px; margin: 0 auto; padding: 20px; }
    h1 { color: #2c3e50; }
    h2 { color: #3498db; margin-top: 30px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
    .platform-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }
    .platform-card { border: 1px solid #ddd; border-radius: 8px; padding: 20px; transition: all 0.3s; }
    .platform-card:hover { box-shadow: 0 5px 15px rgba(0,0,0,0.1); }
    .platform-card h3 { margin-top: 0; color: #2c3e50; }
    .status { display: inline-block; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; margin-top: 5px; }
    .pass { background-color: #d4edda; color: #155724; }
    .fail { background-color: #f8d7da; color: #721c24; }
    .partial { background-color: #fff3cd; color: #856404; }
    .step-list { margin-top: 15px; }
    .step-list li { margin-bottom: 8px; }
    .notes { margin-top: 20px; }
    table { width: 100%; border-collapse: collapse; margin-top: 20px; }
    th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
    th { background-color: #f8f9fa; }
    .summary-box { background-color: #f8f9fa; border-radius: 8px; padding: 20px; margin-top: 20px; }
  </style>
</head>
<body>
  <h1>Catalyst Extension Comprehensive Test Report</h1>
  <p><strong>Date:</strong> $(date)</p>
  <p><strong>Test ID:</strong> $TIMESTAMP</p>
  
  <div class="summary-box">
    <h2>Test Summary</h2>
    <p>This report contains the results of comprehensive testing of the Catalyst Chrome Extension across all supported platforms.</p>
  </div>
  
  <h2>Platform Support Testing</h2>
  <div class="platform-grid">
EOF

# Function to test each platform
test_platform() {
  local platform=$1
  log_message "## Testing Platform: $platform"
  
  # Add platform to HTML report
  cat >> "$HTML_REPORT" << EOF
    <div class="platform-card">
      <h3>$platform</h3>
      <div class="status partial">Test Required</div>
      <div class="step-list">
        <h4>Testing Steps:</h4>
        <ol>
          <li>Navigate to <a href="https://$platform" target="_blank">$platform</a></li>
          <li>Login if necessary</li>
          <li>Open browser console (F12)</li>
          <li>Paste and run the verification script</li>
          <li>Check results and update status</li>
        </ol>
      </div>
      <div class="notes">
        <h4>Notes:</h4>
        <p>Add your testing notes here...</p>
      </div>
    </div>
EOF
  
  echo -e "\n${YELLOW}Testing $platform${NC}"
  echo -e "1. Navigate to ${BLUE}https://$platform${NC}"
  echo -e "2. Run the DOM selector verification script in the console"
  echo -e "3. Check if all selectors are working properly"
  
  # In a real automated test, we would use Puppeteer or similar to automate this
  # For now, we'll just provide guidance for manual testing
  
  log_message "- Manual testing required for $platform"
  log_message "- Check selectors using verify_dom_selectors.js"
}

# Generate selector verification bookmarklet
VERIFICATION_SCRIPT_BASE64=$(base64 -w 0 verify_dom_selectors.js)
BOOKMARKLET="javascript:(function(){const s=document.createElement('script');s.textContent=atob('$VERIFICATION_SCRIPT_BASE64');document.body.appendChild(s);})()"

# Add verification tool to HTML report
cat >> "$HTML_REPORT" << EOF
  </div>
  
  <h2>Verification Tools</h2>
  <div class="summary-box">
    <h3>DOM Selector Verification</h3>
    <p>Use one of these methods to verify selectors on each platform:</p>
    <ol>
      <li>
        <strong>Bookmarklet Method:</strong> 
        <a href="$BOOKMARKLET">Verify Selectors</a> 
        (Drag this link to your bookmarks bar, then click it when on a platform)
      </li>
      <li>
        <strong>Console Method:</strong> 
        Copy and paste the contents of the <code>verify_dom_selectors.js</code> file into the browser console
      </li>
    </ol>
  </div>
  
  <h2>Testing Checklist</h2>
  <table>
    <thead>
      <tr>
        <th>Feature</th>
        <th>Status</th>
        <th>Notes</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Extension Installation</td>
        <td class="status partial">Test Required</td>
        <td></td>
      </tr>
      <tr>
        <td>Authentication</td>
        <td class="status partial">Test Required</td>
        <td></td>
      </tr>
      <tr>
        <td>Message Detection</td>
        <td class="status partial">Test Required</td>
        <td></td>
      </tr>
      <tr>
        <td>Whisper Generation</td>
        <td class="status partial">Test Required</td>
        <td></td>
      </tr>
      <tr>
        <td>UI Rendering</td>
        <td class="status partial">Test Required</td>
        <td></td>
      </tr>
      <tr>
        <td>Performance</td>
        <td class="status partial">Test Required</td>
        <td></td>
      </tr>
    </tbody>
  </table>
  
  <h2>Conclusion</h2>
  <div class="summary-box">
    <p>Testing in progress. This report will be updated as testing proceeds.</p>
    <p><strong>Next Steps:</strong> Complete testing for all platforms and update this report.</p>
  </div>
</body>
</html>
EOF

# Test each platform
for platform in $PLATFORMS; do
  test_platform "$platform"
done

# Create an executable file to update the HTML report with test results
cat > "$TEST_DIR/update_report.sh" << 'EOF'
#!/bin/bash
# This script updates the HTML report with test results

if [ $# -lt 3 ]; then
  echo "Usage: $0 [report_file] [platform] [status] [notes]"
  echo "  status: pass, fail, partial"
  echo "  notes: Optional notes in quotes"
  exit 1
fi

REPORT_FILE=$1
PLATFORM=$2
STATUS=$3
NOTES=${4:-"No notes provided"}

# Validate status
if [[ ! "$STATUS" =~ ^(pass|fail|partial)$ ]]; then
  echo "Invalid status. Use pass, fail, or partial."
  exit 1
fi

# Update the platform status in the HTML file
sed -i '' "s/<div class=\"status [^\"]*\">Test Required<\/div>/<div class=\"status $STATUS\">${STATUS^}<\/div>/" "$REPORT_FILE"

# Update the notes section
sed -i '' "s/<p>Add your testing notes here...<\/p>/<p>$NOTES<\/p>/" "$REPORT_FILE"

echo "Updated $PLATFORM status to $STATUS in $REPORT_FILE"
EOF

chmod +x "$TEST_DIR/update_report.sh"

# Output instructions
echo -e "\n${GREEN}Test setup complete!${NC}"
echo -e "1. Test each platform manually using the DOM selector verification script"
echo -e "2. HTML report generated: ${BLUE}$HTML_REPORT${NC}"
echo -e "3. Update test results using: ${YELLOW}$TEST_DIR/update_report.sh $HTML_REPORT [platform] [status] [notes]${NC}"
echo -e "4. Example: ${YELLOW}$TEST_DIR/update_report.sh $HTML_REPORT web.whatsapp.com pass \"All selectors working correctly\"${NC}"

# Open HTML report in browser if possible
if [[ "$OSTYPE" == "darwin"* ]]; then
  open "$HTML_REPORT"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
  xdg-open "$HTML_REPORT" &>/dev/null
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
  start "$HTML_REPORT"
else
  echo -e "Please open the HTML report manually: ${BLUE}$HTML_REPORT${NC}"
fi

log_message "\nTest setup completed. HTML report generated at: $HTML_REPORT"
log_message "==============================================================="
