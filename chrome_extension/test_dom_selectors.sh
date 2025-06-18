#!/bin/bash

# Catalyst Whisper Coach - DOM Selector Test Tool
# This script helps verify and fix DOM selectors for supported platforms

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================================${NC}"
echo -e "${BLUE}  Catalyst DOM Selector Test Tool${NC}"
echo -e "${BLUE}==============================================${NC}"
echo -e "This tool helps verify and update selectors for supported platforms."
echo -e "Date: $(date)"
echo ""

# Create a temporary directory for our testing files
TEMP_DIR="./temp_selector_test"
mkdir -p $TEMP_DIR

# Function to extract platform selectors
extract_platform_selectors() {
  local platform=$1
  
  echo -e "${CYAN}Extracting selectors for $platform...${NC}"
  
  # Extract the selector block for this platform
  SELECTORS=$(grep -A 10 "'$platform': {" platform_selectors.js)
  
  if [[ -z $SELECTORS ]]; then
    echo -e "${RED}No selectors found for $platform${NC}"
    return 1
  fi
  
  # Extract individual selectors
  MESSAGE_CONTAINER=$(echo "$SELECTORS" | grep "messageContainer" | sed "s/.*messageContainer: '//g" | sed "s/'.*//g")
  MESSAGES=$(echo "$SELECTORS" | grep "messages: " | sed "s/.*messages: '//g" | sed "s/'.*//g")
  MESSAGE_TEXT=$(echo "$SELECTORS" | grep "messageText: " | sed "s/.*messageText: '//g" | sed "s/'.*//g")
  SENDER=$(echo "$SELECTORS" | grep "sender: " | sed "s/.*sender: '//g" | sed "s/'.*//g")
  TIMESTAMP=$(echo "$SELECTORS" | grep "timestamp: " | sed "s/.*timestamp: '//g" | sed "s/'.*//g")
  INPUT_FIELD=$(echo "$SELECTORS" | grep "inputField: " | sed "s/.*inputField: '//g" | sed "s/'.*//g")
  SEND_BUTTON=$(echo "$SELECTORS" | grep "sendButton: " | sed "s/.*sendButton: '//g" | sed "s/'.*//g")
  
  echo -e "${GREEN}Selectors extracted successfully${NC}"
  echo -e "messageContainer: ${YELLOW}$MESSAGE_CONTAINER${NC}"
  echo -e "messages: ${YELLOW}$MESSAGES${NC}"
  echo -e "messageText: ${YELLOW}$MESSAGE_TEXT${NC}"
  echo -e "sender: ${YELLOW}$SENDER${NC}"
  echo -e "timestamp: ${YELLOW}$TIMESTAMP${NC}"
  echo -e "inputField: ${YELLOW}$INPUT_FIELD${NC}"
  echo -e "sendButton: ${YELLOW}$SEND_BUTTON${NC}"
  
  return 0
}

# Function to create a selector testing script
create_testing_script() {
  local platform=$1
  local outfile="$TEMP_DIR/test_${platform//./_}.js"
  
  echo -e "${CYAN}Creating testing script for $platform...${NC}"
  
  cat > "$outfile" << EOL
// Catalyst Selector Testing Script for $platform
// Run this in the browser console when on $platform

console.log("🔍 Testing selectors for $platform...");

// Selectors from platform_selectors.js
const selectors = {
  messageContainer: '$MESSAGE_CONTAINER',
  messages: '$MESSAGES',
  messageText: '$MESSAGE_TEXT',
  sender: '$SENDER',
  timestamp: '$TIMESTAMP',
  inputField: '$INPUT_FIELD',
  sendButton: '$SEND_BUTTON'
};

// Test results
const results = {};

// Test each selector
for (const [name, selector] of Object.entries(selectors)) {
  try {
    const elements = document.querySelectorAll(selector);
    const count = elements.length;
    let sampleText = '';
    
    // Try to get sample text content for verification
    if (count > 0) {
      if (elements[0].textContent) {
        sampleText = elements[0].textContent.trim().substring(0, 50);
        if (sampleText.length >= 50) sampleText += '...';
      } else if (elements[0].value) {
        sampleText = elements[0].value.trim().substring(0, 50);
        if (sampleText.length >= 50) sampleText += '...';
      } else {
        sampleText = '[No text content]';
      }
    }
    
    results[name] = {
      selector,
      count,
      sampleText,
      success: count > 0
    };
  } catch (err) {
    results[name] = {
      selector,
      count: 0,
      sampleText: null,
      success: false,
      error: err.message
    };
  }
}

// Print summary
console.table(results);

// Overall success check
const allSuccessful = Object.values(results).every(r => r.success);
if (allSuccessful) {
  console.log("%c✅ All selectors are working correctly!", "color: green; font-weight: bold");
} else {
  console.log("%c❌ Some selectors are not working. See details above.", "color: red; font-weight: bold");
  
  // Suggestions for broken selectors
  console.log("📝 Suggestions for broken selectors:");
  
  for (const [name, result] of Object.entries(results)) {
    if (!result.success) {
      console.log(\`%c${name}: %c${result.selector} %c- not working\`, "font-weight: bold", "color: blue", "color: red");
      
      // Try to suggest alternatives based on common patterns
      switch (name) {
        case 'messageContainer':
          console.log("Try these alternatives:");
          console.log("- [role='main']");
          console.log("- .messages-container");
          console.log("- .chat-container");
          console.log("- [data-testid*='message'] or [data-testid*='conversation']");
          break;
          
        case 'messages':
          console.log("Try these alternatives:");
          console.log("- [role='row']");
          console.log("- .message");
          console.log("- [data-testid*='message']");
          break;
          
        case 'messageText':
          console.log("Try these alternatives:");
          console.log("- .message-text");
          console.log("- .text-content");
          console.log("- [data-testid*='text']");
          break;
          
        case 'sender':
          console.log("Try these alternatives:");
          console.log("- .sender");
          console.log("- .author");
          console.log("- .username");
          console.log("- [data-testid*='sender'] or [data-testid*='author']");
          break;
          
        case 'timestamp':
          console.log("Try these alternatives:");
          console.log("- time");
          console.log("- .timestamp");
          console.log("- [datetime]");
          console.log("- [data-testid*='time']");
          break;
          
        case 'inputField':
          console.log("Try these alternatives:");
          console.log("- [contenteditable='true']");
          console.log("- textarea");
          console.log("- .composer");
          console.log("- [role='textbox']");
          console.log("- [data-testid*='input']");
          break;
          
        case 'sendButton':
          console.log("Try these alternatives:");
          console.log("- [type='submit']");
          console.log("- button:has(svg)");
          console.log("- [aria-label*='send' i]");
          console.log("- [data-testid*='send']");
          break;
      }
    }
  }
}

// Helper function to interactively discover selectors
window.findSelector = (description) => {
  console.log(\`🔍 Let's find a selector for: \${description}\`);
  console.log("Click on an element in the page to get its selector...");
  
  document.body.style.cursor = 'crosshair';
  
  const clickHandler = (event) => {
    event.preventDefault();
    event.stopPropagation();
    
    const element = event.target;
    console.log("Element:", element);
    
    // Try to generate selectors
    const selectors = [];
    
    // ID-based selector (most specific)
    if (element.id) {
      selectors.push(\`#\${element.id}\`);
    }
    
    // Class-based selectors
    if (element.className && typeof element.className === 'string') {
      const classes = element.className.trim().split(/\\s+/);
      if (classes.length > 0 && classes[0] !== '') {
        selectors.push(\`.\${classes.join('.')}\`);
        
        // Also try with just the first class
        if (classes.length > 1) {
          selectors.push(\`.\${classes[0]}\`);
        }
      }
    }
    
    // Attribute-based selectors
    if (element.getAttribute('data-testid')) {
      selectors.push(\`[data-testid="\${element.getAttribute('data-testid')}"]\`);
    }
    
    if (element.getAttribute('role')) {
      selectors.push(\`[role="\${element.getAttribute('role')}"]\`);
    }
    
    if (element.getAttribute('aria-label')) {
      selectors.push(\`[aria-label="\${element.getAttribute('aria-label')}"]\`);
    }
    
    // Tag-based selector (least specific)
    selectors.push(element.tagName.toLowerCase());
    
    // Print results
    console.log("Suggested selectors:");
    for (const selector of selectors) {
      const count = document.querySelectorAll(selector).length;
      console.log(\`%c\${selector} %c- matched \${count} element(s)\`, "color: blue", count === 1 ? "color: green" : "color: orange");
    }
    
    // Reset cursor
    document.body.style.cursor = 'default';
    document.removeEventListener('click', clickHandler, true);
    console.log("Selector finder deactivated. Call window.findSelector() again if needed.");
  };
  
  document.addEventListener('click', clickHandler, true);
  console.log("Click on an element to analyze it, or refresh the page to cancel.");
};

console.log("%cℹ️ You can use window.findSelector() to interactively find selectors", "font-weight: bold");
console.log('Example: window.findSelector("the message container")');
EOL
  
  echo -e "${GREEN}Testing script created: $outfile${NC}"
  echo -e "To use this script:"
  echo -e "1. Navigate to $platform in Chrome"
  echo -e "2. Open Chrome DevTools (F12 or right-click > Inspect)"
  echo -e "3. Go to the Console tab"
  echo -e "4. Copy and paste the contents of $outfile into the console"
  echo -e "5. Use window.findSelector() to interactively find new selectors if needed"
  
  return 0
}

# Function to create an HTML helper for all platforms
create_html_helper() {
  local outfile="$TEMP_DIR/selector_helper.html"
  
  echo -e "${CYAN}Creating HTML selector helper for all platforms...${NC}"
  
  # Start HTML file
  cat > "$outfile" << EOL
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Catalyst Selector Helper</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; margin: 20px; }
    h1 { color: #2563eb; }
    h2 { color: #4b5563; margin-top: 30px; }
    .platform { border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin-bottom: 20px; }
    .platform-name { font-weight: bold; font-size: 18px; margin-bottom: 10px; }
    pre { background: #f3f4f6; padding: 10px; border-radius: 4px; overflow-x: auto; }
    .copy-button { background: #2563eb; color: white; border: none; padding: 8px 16px; 
      border-radius: 4px; cursor: pointer; margin-top: 10px; }
    .copy-button:hover { background: #1d4ed8; }
    .test-button { background: #059669; color: white; border: none; padding: 8px 16px; 
      border-radius: 4px; cursor: pointer; margin-left: 10px; }
    .test-button:hover { background: #047857; }
  </style>
</head>
<body>
  <h1>Catalyst Selector Helper</h1>
  <p>This tool helps you test and update selectors for all supported platforms.</p>
  <p><strong>Instructions:</strong> Click "Copy Script" for a platform, then paste it into the browser console when visiting that platform.</p>
  
  <div id="platforms">
EOL

  # Get all platforms from platform_selectors.js
  platforms=$(grep -o "'[^']*': {" platform_selectors.js | sed "s/'//g" | sed "s/: {//g")
  
  # Add each platform
  for platform in $platforms; do
    # Skip empty lines
    if [ -z "$platform" ]; then
      continue
    fi
    
    # Extract selectors for this platform
    extract_platform_selectors "$platform"
    
    # Create the testing script
    create_testing_script "$platform" > /dev/null
    
    # Script filename
    script_file="test_${platform//./_}.js"
    
    # Add to HTML
    cat >> "$outfile" << EOL
    <div class="platform">
      <div class="platform-name">$platform</div>
      <p>Visit: <a href="https://$platform" target="_blank">https://$platform</a></p>
      <pre id="script-$platform">$(cat "$TEMP_DIR/$script_file")</pre>
      <button class="copy-button" onclick="copyScript('script-$platform')">Copy Script</button>
      <a href="https://$platform" target="_blank" class="test-button">Open Platform</a>
    </div>
EOL
  done
  
  # Finish HTML file
  cat >> "$outfile" << EOL
  </div>
  
  <h2>How to Fix Broken Selectors</h2>
  <ol>
    <li>Use the scripts above to identify broken selectors</li>
    <li>Use window.findSelector() to interactively find new selectors</li>
    <li>Update platform_selectors.js with the new selectors</li>
    <li>Re-test to verify the new selectors work</li>
  </ol>
  
  <h2>Update Guide</h2>
  <p>When you have found a new working selector, edit platform_selectors.js in the following format:</p>
  <pre>
'platform.domain.com': {
    messageContainer: '.your-new-selector',
    messages: '.your-new-selector',
    messageText: '.your-new-selector',
    sender: '.your-new-selector',
    timestamp: '.your-new-selector',
    inputField: '.your-new-selector',
    sendButton: '.your-new-selector'
},</pre>
  
  <h2>Testing Checklist</h2>
  <ol>
    <li>messageContainer: Can find the container that holds all messages</li>
    <li>messages: Can find individual message containers</li>
    <li>messageText: Can extract the text content of messages</li>
    <li>sender: Can identify who sent each message</li>
    <li>timestamp: Can get when messages were sent</li>
    <li>inputField: Can locate where to type new messages</li>
    <li>sendButton: Can find the button to send messages</li>
  </ol>
  
  <script>
    function copyScript(id) {
      const scriptText = document.getElementById(id).textContent;
      navigator.clipboard.writeText(scriptText)
        .then(() => {
          alert('Script copied to clipboard! Paste it into the browser console.');
        })
        .catch(err => {
          console.error('Failed to copy: ', err);
          alert('Failed to copy script. Please select and copy manually.');
        });
    }
  </script>
</body>
</html>
EOL
  
  echo -e "${GREEN}HTML helper created: $outfile${NC}"
  echo -e "Open this file in a browser to easily access testing scripts for all platforms."
  
  return 0
}

# Main menu
PS3="Select an option: "
options=("Test Specific Platform" "Create HTML Helper for All Platforms" "Exit")
select opt in "${options[@]}"
do
  case $opt in
    "Test Specific Platform")
      # Let user select a platform
      echo -e "${CYAN}Available platforms:${NC}"
      platforms=$(grep -o "'[^']*': {" platform_selectors.js | sed "s/'//g" | sed "s/: {//g")
      PS3="Select platform to test: "
      select platform in $platforms "Cancel"
      do
        if [ "$platform" = "Cancel" ]; then
          break
        elif [ -n "$platform" ]; then
          extract_platform_selectors "$platform"
          create_testing_script "$platform"
          break
        else
          echo "Invalid option"
        fi
      done
      break
      ;;
    "Create HTML Helper for All Platforms")
      create_html_helper
      echo -e "${GREEN}Opening HTML helper in default browser...${NC}"
      if [[ "$OSTYPE" == "darwin"* ]]; then
        open "$TEMP_DIR/selector_helper.html"
      elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open "$TEMP_DIR/selector_helper.html"
      else
        echo -e "${YELLOW}Please open this file manually: $TEMP_DIR/selector_helper.html${NC}"
      fi
      break
      ;;
    "Exit")
      echo -e "${BLUE}Exiting selector test tool.${NC}"
      break
      ;;
    *) 
      echo "Invalid option $REPLY"
      ;;
  esac
done

echo -e "${BLUE}==============================================${NC}"
echo -e "${BLUE}  DOM Selector Test Tool completed${NC}"
echo -e "${BLUE}==============================================${NC}"
