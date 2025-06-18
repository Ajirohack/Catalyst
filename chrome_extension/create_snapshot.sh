#!/bin/bash

# Catalyst Whisper Coach - Extension State Snapshot
# This script creates a snapshot of the current extension state for future reference

echo "📸 Catalyst Extension State Snapshot"
echo "📅 Date: $(date)"
echo "=================================================="

# Create snapshot directory
SNAPSHOT_DIR="./snapshots/$(date +%Y%m%d%H%M%S)"
mkdir -p $SNAPSHOT_DIR

# Record extension version
VERSION=$(grep -o '"version": "[^"]*"' manifest.json | cut -d'"' -f4)
NAME=$(grep -o '"name": "[^"]*"' manifest.json | cut -d'"' -f4)
DESC=$(grep -o '"description": "[^"]*"' manifest.json | cut -d'"' -f4)

echo "📦 Extension: $NAME v$VERSION"
echo "Extension details saved to: $SNAPSHOT_DIR/extension_info.md"
cp content_script.js $SNAPSHOT_DIR/
cp background.js $SNAPSHOT_DIR/

# Generate platforms list
echo "# Supported Platforms" > $SNAPSHOT_DIR/platforms.md
echo "" >> $SNAPSHOT_DIR/platforms.md
grep -o '"https://[^"]*"' manifest.json | sort | uniq | sed 's/"https:\/\/\([^\/]*\)\/.*"/1. \1/g' >> $SNAPSHOT_DIR/platforms.md

# Create a platform selector summary
echo "# Platform Selector Summary" > $SNAPSHOT_DIR/selectors_summary.md
echo "" >> $SNAPSHOT_DIR/selectors_summary.md
echo "| Platform | Message Container | Messages | Message Text | Sender | Timestamp | Input Field | Send Button |" >> $SNAPSHOT_DIR/selectors_summary.md
echo "|----------|-------------------|---------|--------------|--------|-----------|-------------|-------------|" >> $SNAPSHOT_DIR/selectors_summary.md

# Extract selectors from platform_selectors.js
grep -o "'[^']*': {" platform_selectors.js | sed "s/'//g" | sed "s/: {//g" | while read -r platform; do
  # Skip empty lines
  if [ -z "$platform" ]; then
    continue
  fi
  
  # Extract selectors for this platform
  messageContainer=$(grep -A 1 "'$platform': {" platform_selectors.js | grep messageContainer | cut -d "'" -f 4)
  messages=$(grep -A 2 "'$platform': {" platform_selectors.js | grep messages | cut -d "'" -f 4)
  messageText=$(grep -A 3 "'$platform': {" platform_selectors.js | grep messageText | cut -d "'" -f 4)
  sender=$(grep -A 4 "'$platform': {" platform_selectors.js | grep sender | cut -d "'" -f 4)
  timestamp=$(grep -A 5 "'$platform': {" platform_selectors.js | grep timestamp | cut -d "'" -f 4)
  inputField=$(grep -A 6 "'$platform': {" platform_selectors.js | grep inputField | cut -d "'" -f 4)
  sendButton=$(grep -A 7 "'$platform': {" platform_selectors.js | grep sendButton | cut -d "'" -f 4)
  
  # Add to summary table
  echo "| $platform | $messageContainer | $messages | $messageText | $sender | $timestamp | $inputField | $sendButton |" >> $SNAPSHOT_DIR/selectors_summary.md
done

# Create test browser HTML file
cat > $SNAPSHOT_DIR/test_selectors.html << EOL
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Catalyst Selector Tester</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; margin: 20px; }
    h1 { color: #2563eb; }
    h2 { color: #4b5563; margin-top: 30px; }
    .platform { border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin-bottom: 20px; }
    .platform-name { font-weight: bold; font-size: 18px; margin-bottom: 10px; }
    .selectors { font-family: monospace; background: #f3f4f6; padding: 10px; border-radius: 4px; }
    .test-button { background: #2563eb; color: white; border: none; padding: 8px 16px; 
      border-radius: 4px; cursor: pointer; margin-top: 10px; }
    .test-button:hover { background: #1d4ed8; }
    .result { margin-top: 15px; }
    .success { color: #059669; }
    .error { color: #dc2626; }
  </style>
</head>
<body>
  <h1>Catalyst Selector Tester</h1>
  <p>This tool helps test selectors for each supported platform.</p>
  <p><strong>Instructions:</strong> Navigate to a supported platform in another tab, then return here and click "Test Selectors" for that platform.</p>
  
  <div id="platforms"></div>
  
  <script>
    // Import platform selectors
    const platformSelectors = ${cat platform_selectors.js | grep -v "// " | tr -d '\n'};
    
    const platformsDiv = document.getElementById('platforms');
    
    // Create platform test sections
    for (const [platform, selectors] of Object.entries(platformSelectors)) {
      const platformDiv = document.createElement('div');
      platformDiv.className = 'platform';
      
      const nameDiv = document.createElement('div');
      nameDiv.className = 'platform-name';
      nameDiv.textContent = platform;
      platformDiv.appendChild(nameDiv);
      
      const selectorsDiv = document.createElement('div');
      selectorsDiv.className = 'selectors';
      selectorsDiv.innerHTML = '<pre>' + JSON.stringify(selectors, null, 2) + '</pre>';
      platformDiv.appendChild(selectorsDiv);
      
      const testButton = document.createElement('button');
      testButton.className = 'test-button';
      testButton.textContent = 'Test Selectors';
      testButton.onclick = () => testPlatform(platform, selectors, platformDiv);
      platformDiv.appendChild(testButton);
      
      const resultDiv = document.createElement('div');
      resultDiv.className = 'result';
      platformDiv.appendChild(resultDiv);
      
      platformsDiv.appendChild(platformDiv);
    }
    
    // Function to test selectors on active platform
    function testPlatform(platform, selectors, platformDiv) {
      const resultDiv = platformDiv.querySelector('.result');
      resultDiv.innerHTML = 'Testing...';
      
      // Send message to content script through extension
      chrome.runtime.sendMessage({
        action: 'testSelectors',
        platform: platform
      }, response => {
        if (response && response.success) {
          let html = '<h3 class="success">✅ Selectors tested successfully!</h3>';
          html += '<table border="1" cellpadding="5" cellspacing="0">';
          html += '<tr><th>Selector</th><th>Found</th><th>Sample</th></tr>';
          
          for (const [key, result] of Object.entries(response.results)) {
            const status = result.found > 0 ? '✅' : '❌';
            html += '<tr>';
            html += '<td>' + key + '</td>';
            html += '<td>' + status + ' (' + result.found + ')</td>';
            html += '<td>' + (result.sample || 'N/A') + '</td>';
            html += '</tr>';
          }
          
          html += '</table>';
          resultDiv.innerHTML = html;
        } else {
          resultDiv.innerHTML = '<div class="error">❌ Error testing selectors: ' + 
            (response ? response.error : 'No response from extension') + '</div>';
        }
      });
    }
  </script>
</body>
</html>
EOL

# Create platform compatibility report
echo "# Platform Compatibility Report" > $SNAPSHOT_DIR/compatibility_report.md
echo "Generated: $(date)" >> $SNAPSHOT_DIR/compatibility_report.md
echo "" >> $SNAPSHOT_DIR/compatibility_report.md

# Check which platforms are in both manifest and selectors
echo "## Coverage Analysis" >> $SNAPSHOT_DIR/compatibility_report.md
echo "" >> $SNAPSHOT_DIR/compatibility_report.md
echo "| Platform | In Manifest | Has Selectors | Status |" >> $SNAPSHOT_DIR/compatibility_report.md
echo "|----------|-------------|--------------|--------|" >> $SNAPSHOT_DIR/compatibility_report.md

# Get platforms from manifest
manifest_platforms=$(grep -o '"https://[^"]*"' manifest.json | sed 's/"https:\/\/\([^\/]*\)\/.*"/\1/g' | sort | uniq)

# Get platforms from selectors
selector_platforms=$(grep -o "'[^']*': {" platform_selectors.js | sed "s/'//g" | sed "s/: {//g" | sort)

# Combine all unique platforms
all_platforms=$(echo "$manifest_platforms $selector_platforms" | tr ' ' '\n' | sort | uniq)

# Check each platform
for platform in $all_platforms; do
  # Skip empty lines
  if [ -z "$platform" ]; then
    continue
  fi
  
  # Check if in manifest
  if echo "$manifest_platforms" | grep -q "$platform"; then
    in_manifest="✅"
  else
    in_manifest="❌"
  fi
  
  # Check if has selectors
  if echo "$selector_platforms" | grep -q "$platform"; then
    has_selectors="✅"
  else
    has_selectors="❌"
  fi
  
  # Determine status
  if [ "$in_manifest" = "✅" ] && [ "$has_selectors" = "✅" ]; then
    status="✅ Ready"
  elif [ "$in_manifest" = "✅" ]; then
    status="⚠️ Missing selectors"
  elif [ "$has_selectors" = "✅" ]; then
    status="⚠️ Missing permissions"
  else
    status="❌ Not supported"
  fi
  
  # Add to report
  echo "| $platform | $in_manifest | $has_selectors | $status |" >> $SNAPSHOT_DIR/compatibility_report.md
done

# Create recommendations section
echo "" >> $SNAPSHOT_DIR/compatibility_report.md
echo "## Recommendations" >> $SNAPSHOT_DIR/compatibility_report.md
echo "" >> $SNAPSHOT_DIR/compatibility_report.md

# Check for missing selectors
missing_selectors=$(comm -23 <(echo "$manifest_platforms" | sort) <(echo "$selector_platforms" | sort))
if [ -n "$missing_selectors" ]; then
  echo "### Platforms missing selectors" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "The following platforms need selectors added to platform_selectors.js:" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "```" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "$missing_selectors" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "```" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "" >> $SNAPSHOT_DIR/compatibility_report.md
fi

# Check for missing permissions
missing_permissions=$(comm -23 <(echo "$selector_platforms" | sort) <(echo "$manifest_platforms" | sort))
if [ -n "$missing_permissions" ]; then
  echo "### Platforms missing permissions" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "The following platforms need permissions added to manifest.json:" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "```" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "$missing_permissions" >> $SNAPSHOT_DIR/compatibility_report.md
  echo "```" >> $SNAPSHOT_DIR/compatibility_report.md
fi

# Create detailed extension info markdown file
cat > $SNAPSHOT_DIR/extension_info.md << EOF
# Catalyst Extension Snapshot
**Date:** $(date)
**Snapshot ID:** $(basename $SNAPSHOT_DIR)

## Extension Details
- **Name:** $NAME
- **Version:** $VERSION
- **Description:** $DESC

## Supported Platforms
| # | Platform | Host Permission | Selectors Defined |
|---|----------|----------------|------------------|
EOF

# Get host permissions from manifest
HOST_PERMS=$(grep -A 30 '"host_permissions":' manifest.json | grep -o '"https://[^"]*"' | sed 's/"//g')

# Get all domains from platform_selectors.js
PLATFORMS=$(grep -o "'[^']*':" platform_selectors.js | sed "s/'//g" | sed "s/://g")

# Count for numbering
COUNT=1

# Process each platform
for PLATFORM in $PLATFORMS; do
  # Check if platform has host permission
  if echo "$HOST_PERMS" | grep -q "$PLATFORM"; then
    PERM_STATUS="✓"
  else
    PERM_STATUS="✗"
  fi
  
  # Check if platform has all required selectors
  SELECTOR_COUNT=$(grep -A 10 "'$PLATFORM':" platform_selectors.js | grep -c ":")
  if [ "$SELECTOR_COUNT" -ge 6 ]; then
    SELECTOR_STATUS="✓"
  else
    SELECTOR_STATUS="✗"
  fi
  
  # Add to markdown file
  echo "| $COUNT | $PLATFORM | $PERM_STATUS | $SELECTOR_STATUS |" >> $SNAPSHOT_DIR/extension_info.md
  
  # Print to console
  echo "Platform $COUNT: $PLATFORM - Permission: $PERM_STATUS, Selectors: $SELECTOR_STATUS"
  
  # Increment counter
  COUNT=$((COUNT+1))
done

# Add source files section
cat >> $SNAPSHOT_DIR/extension_info.md << EOF

## Source Files
| File | Lines | Description |
|------|-------|-------------|
| manifest.json | $(wc -l < manifest.json) | Extension manifest file |
| content_script.js | $(wc -l < content_script.js) | Content script for DOM interaction |
| platform_selectors.js | $(wc -l < platform_selectors.js) | Platform-specific DOM selectors |
| background.js | $(wc -l < background.js) | Background script for extension |

EOF

# Copy key files to snapshot directory
echo "📄 Copying source files..."
mkdir -p $SNAPSHOT_DIR/source
cp manifest.json $SNAPSHOT_DIR/source/
cp content_script.js $SNAPSHOT_DIR/source/
cp platform_selectors.js $SNAPSHOT_DIR/source/
cp background.js $SNAPSHOT_DIR/source/

# Check for potential issues
echo "🔍 Checking for potential issues..."

# Add issues section to markdown
cat >> $SNAPSHOT_DIR/extension_info.md << EOF
## Potential Issues
### Missing Host Permissions
EOF

# Check for missing platform permissions
MISSING_PERMS=0
for PLATFORM in $PLATFORMS; do
  if ! echo "$HOST_PERMS" | grep -q "$PLATFORM"; then
    echo "- Missing permission for: $PLATFORM" >> $SNAPSHOT_DIR/extension_info.md
    MISSING_PERMS=$((MISSING_PERMS+1))
  fi
done

if [ "$MISSING_PERMS" -eq 0 ]; then
  echo "No missing host permissions detected." >> $SNAPSHOT_DIR/extension_info.md
fi

# Add incomplete selectors section
cat >> $SNAPSHOT_DIR/extension_info.md << EOF

### Incomplete Selectors
EOF

# Check for incomplete platform selectors
INCOMPLETE_SELECTORS=0
for PLATFORM in $PLATFORMS; do
  SELECTOR_COUNT=$(grep -A 10 "'$PLATFORM':" platform_selectors.js | grep -c ":")
  if [ "$SELECTOR_COUNT" -lt 7 ]; then
    echo "- Incomplete selectors for: $PLATFORM (has $SELECTOR_COUNT of 7 required selectors)" >> $SNAPSHOT_DIR/extension_info.md
    INCOMPLETE_SELECTORS=$((INCOMPLETE_SELECTORS+1))
  fi
done

if [ "$INCOMPLETE_SELECTORS" -eq 0 ]; then
  echo "No incomplete selectors detected." >> $SNAPSHOT_DIR/extension_info.md
fi

# Create zip of the current state
cd $SNAPSHOT_DIR
zip -r extension_snapshot_v${VERSION}.zip *
cd - > /dev/null

echo "✅ Snapshot created at $SNAPSHOT_DIR"
echo "📦 Files included:"
ls -la $SNAPSHOT_DIR

# Generate summary information
echo "Snapshot created successfully in $SNAPSHOT_DIR"
echo "==============================================" 
echo "Summary:"
echo "- Version: $VERSION"
echo "- Files copied: manifest.json, platform_selectors.js, content_script.js, background.js"
echo "- Generated reports:"
echo "  - platforms.md: List of supported platforms"
echo "  - selectors_summary.md: Summary of all platform selectors"
echo "  - compatibility_report.md: Analysis of platform support"
echo "  - test_selectors.html: Interactive testing tool"

# Create README with instructions
cat > $SNAPSHOT_DIR/README.md << EOL
# Catalyst Extension Snapshot

**Date:** $(date)
**Version:** $VERSION

## Contents

This snapshot captures the current state of the Catalyst Chrome Extension for testing and reference purposes.

### Files

- **manifest.json**: Extension manifest with permissions and settings
- **platform_selectors.js**: DOM selectors for supported platforms
- **content_script.js**: Main content script injected into pages
- **background.js**: Background service worker

### Reports

- **platforms.md**: List of all supported platforms
- **selectors_summary.md**: Table of all platform selectors
- **compatibility_report.md**: Analysis of platform support coverage
- **test_selectors.html**: Interactive tool to test selectors on live platforms

## Testing Instructions

1. Install the extension from the development directory
2. Open test_selectors.html in Chrome
3. Navigate to a supported platform in another tab
4. Return to the test page and click "Test Selectors" for that platform
5. Review results and update selectors as needed

## Next Steps

1. Address any missing selectors or permissions identified in the compatibility report
2. Test all platforms using the interactive testing tool
3. Update documentation with any new findings
EOL

echo ""
echo "To use the testing tool:"
echo "1. Install the extension from the development directory"
echo "2. Open $SNAPSHOT_DIR/test_selectors.html in Chrome"
echo "3. Navigate to each platform in another tab and test its selectors"
echo ""
echo "See $SNAPSHOT_DIR/README.md for complete instructions"

# Create selectors verification file
echo "🔧 Creating selectors verification script..."

cat > $SNAPSHOT_DIR/verify_selectors.js << EOF
// Catalyst Selector Verification Script
// Generated on: $(date)
// This script helps verify if DOM selectors for platforms are working correctly

console.log("Catalyst Selector Verification Script");
console.log("==================================");

// Platform selectors (copied from extension)
const PLATFORM_SELECTORS = {
$(grep -A 500 "const PLATFORM_SELECTORS = {" platform_selectors.js | tail -n +2 | head -n 500)

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
      
      console.log(\`Selector: \${name} (\${selector}) - \${found ? "✓" : "✗"} (\${elements.length} elements found)\`);
    } catch (error) {
      results.selectors[name] = {
        selector: selector,
        found: false,
        error: error.message
      };
      
      console.error(\`Error testing selector \${name}: \${error.message}\`);
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

resultDiv.innerHTML = \`
  <h3>Catalyst Selector Verification</h3>
  <p>Platform: \${results.platform}</p>
  <p>Support: \${results.supported ? "✓" : "✗"}</p>
  <h4>Selectors:</h4>
  <table style="border-collapse: collapse; width: 100%;">
    <tr>
      <th style="border: 1px solid #ddd; padding: 4px; text-align: left;">Name</th>
      <th style="border: 1px solid #ddd; padding: 4px; text-align: left;">Found</th>
      <th style="border: 1px solid #ddd; padding: 4px; text-align: left;">Count</th>
    </tr>
    \${Object.entries(results.selectors).map(([name, info]) => \`
      <tr>
        <td style="border: 1px solid #ddd; padding: 4px;">\${name}</td>
        <td style="border: 1px solid #ddd; padding: 4px; color: \${info.found ? 'green' : 'red'};">\${info.found ? "✓" : "✗"}</td>
        <td style="border: 1px solid #ddd; padding: 4px;">\${info.count || 0}</td>
      </tr>
    \`).join('')}
  </table>
  <button id="closeBtn" style="margin-top: 10px;">Close</button>
\`;

document.body.appendChild(resultDiv);
document.getElementById("closeBtn").addEventListener("click", () => {
  resultDiv.remove();
});
EOF

# Create HTML instructions for running tests
cat > $SNAPSHOT_DIR/run_tests.html << EOF
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Catalyst Extension Testing Guide</title>
  <style>
    body { font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }
    h1 { color: #2c3e50; }
    h2 { color: #3498db; margin-top: 30px; }
    code { background: #f8f8f8; padding: 2px 5px; border-radius: 3px; }
    pre { background: #f8f8f8; padding: 15px; border-radius: 5px; overflow-x: auto; }
    .platform { margin-bottom: 20px; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
    .platform h3 { margin-top: 0; }
    .step { margin-bottom: 15px; }
    .step-number { display: inline-block; width: 24px; height: 24px; background: #3498db; color: white; 
                  border-radius: 50%; text-align: center; margin-right: 10px; }
  </style>
</head>
<body>
  <h1>Catalyst Extension Testing Guide</h1>
  <p>Generated on: $(date)</p>
  
  <h2>Supported Platforms</h2>
  <p>The following platforms are supported by the Catalyst extension. Click on each platform to test:</p>
  
  <div id="platforms">
EOF

# Add each platform to the HTML
COUNT=1
for PLATFORM in $PLATFORMS; do
  cat >> $SNAPSHOT_DIR/run_tests.html << EOF
    <div class="platform">
      <h3>$COUNT. $PLATFORM</h3>
      <p><a href="https://$PLATFORM" target="_blank">Open $PLATFORM</a> in a new tab</p>
      <p>Once on the platform:</p>
      <div class="step">
        <span class="step-number">1</span> Open browser console (F12 or Right-click > Inspect > Console)
      </div>
      <div class="step">
        <span class="step-number">2</span> Paste and run the following code:
        <pre><code>const script = document.createElement('script');
script.src = 'data:text/javascript;base64,$(base64 -w 0 $SNAPSHOT_DIR/verify_selectors.js)';
document.body.appendChild(script);</code></pre>
      </div>
      <div class="step">
        <span class="step-number">3</span> Check the results in the console and the overlay
      </div>
    </div>
EOF
  COUNT=$((COUNT+1))
done

# Finish HTML file
cat >> $SNAPSHOT_DIR/run_tests.html << EOF
  </div>

  <h2>Testing Instructions</h2>
  <p>For each platform, follow these steps:</p>
  <ol>
    <li>Click the link to open the platform</li>
    <li>Log in if necessary</li>
    <li>Navigate to a chat or message view</li>
    <li>Run the verification script in the console</li>
    <li>Check which selectors are working and which need to be updated</li>
    <li>Record the results for each platform</li>
  </ol>

  <h2>Updating Selectors</h2>
  <p>If you find selectors that aren't working, update them in the <code>platform_selectors.js</code> file:</p>
  <pre><code>// Example of updating a selector
PLATFORM_SELECTORS['web.whatsapp.com'] = {
  messageContainer: '.new-selector-for-container',
  messages: '.new-selector-for-messages',
  // ... other selectors ...
};</code></pre>

  <h2>Testing Results</h2>
  <p>Create a new file with your testing results and store it in the <code>test_results</code> directory.</p>
</body>
</html>
EOF

# Final output
cat >> $SNAPSHOT_DIR/extension_info.md << EOF

## Testing Notes
1. This snapshot represents the state of the extension as of $(date).
2. Use the included \`verify_selectors.js\` script to test selectors on each platform.
3. Open \`run_tests.html\` in a browser for step-by-step testing instructions.
4. Record your testing results and update selectors as needed.
EOF

echo "✅ Snapshot created successfully at: $SNAPSHOT_DIR"
echo "📊 Summary report: $SNAPSHOT_DIR/extension_info.md"
echo "🧪 Testing guide: $SNAPSHOT_DIR/run_tests.html"
echo ""
echo "Next steps:"
echo "1. Open $SNAPSHOT_DIR/run_tests.html in a browser"
echo "2. Follow the instructions to test each platform"
echo "3. Update selectors if needed and retest"
