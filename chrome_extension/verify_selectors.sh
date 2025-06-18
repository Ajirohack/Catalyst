#!/bin/bash

# Automatic platform selector verification for Catalyst Chrome Extension
# This script validates all selectors in platform_selectors.js against the manifest.json permissions

echo "🔍 Catalyst Selector Verification Tool"
echo "📅 Date: $(date)"
echo "=================================================="

# Files to check
MANIFEST_FILE="manifest.json"
SELECTORS_FILE="platform_selectors.js"

# Test results directory
TEST_DIR="./testing/verification_results"
mkdir -p $TEST_DIR

# Log file
TIMESTAMP=$(date +%Y%m%d%H%M%S)
LOG_FILE="$TEST_DIR/selector_verification_$TIMESTAMP.log"
HTML_REPORT="$TEST_DIR/selector_verification_$TIMESTAMP.html"

echo "📝 Results will be logged to $LOG_FILE"
echo "📊 HTML report will be generated at $HTML_REPORT"

# Check if files exist
if [ ! -f "$MANIFEST_FILE" ]; then
    echo "❌ Error: $MANIFEST_FILE not found"
    exit 1
fi

if [ ! -f "$SELECTORS_FILE" ]; then
    echo "❌ Error: $SELECTORS_FILE not found"
    exit 1
fi

if [ ! -f "$SELECTORS_FILE" ]; then
    echo "❌ Error: $SELECTORS_FILE not found"
    exit 1
fi

echo "📝 Analyzing manifest.json and platform_selectors.js..."

# Extract host permissions from manifest.json
HOST_PERMISSIONS=$(grep -o '"https://[^"]*' "$MANIFEST_FILE" | sed 's/"https:\/\///g' | sed 's/\/\*//g')

# Extract platform selectors from platform_selectors.js
# This is a bit tricky since it's JavaScript, not JSON
PLATFORMS=$(grep -o "'[^']*': {" "$SELECTORS_FILE" | sed "s/': {//g" | sed "s/'//g")
if [ -z "$PLATFORMS" ]; then
    # Try with double quotes
    PLATFORMS=$(grep -o '"[^"]*": {' "$SELECTORS_FILE" | sed 's/": {//g' | sed 's/"//g')
fi

echo -e "\n🔍 Checking manifest.json host permissions against platform_selectors.js..."

# Compare manifest.json host permissions with platform_selectors.js
echo -e "\n📋 Platforms in selector file:"
MATCHED_COUNT=0
MISSING_COUNT=0

# Create temporary files for comparison
echo "$PLATFORMS" > platforms_temp.txt
echo "$HOST_PERMISSIONS" > permissions_temp.txt

# Go through each platform
while read -r platform; do
    if [ -z "$platform" ]; then continue; fi
    
    FOUND=false
    while read -r permission; do
        if [ -z "$permission" ]; then continue; fi
        
        if [[ "$platform" == *"$permission"* || "$permission" == *"$platform"* ]]; then
            echo "  ✅ $platform"
            FOUND=true
            MATCHED_COUNT=$((MATCHED_COUNT + 1))
            break
        fi
    done < permissions_temp.txt
    
    if [ "$FOUND" = false ]; then
        echo "  ❌ $platform (NO MATCHING PERMISSION)"
        MISSING_COUNT=$((MISSING_COUNT + 1))
    fi
done < platforms_temp.txt

echo -e "\n📋 Host permissions without matching platform selectors:"
UNUSED_COUNT=0

# Go through each permission
while read -r permission; do
    if [ -z "$permission" ]; then continue; fi
    
    FOUND=false
    while read -r platform; do
        if [ -z "$platform" ]; then continue; fi
        
        if [[ "$platform" == *"$permission"* || "$permission" == *"$platform"* ]]; then
            FOUND=true
            break
        fi
    done < platforms_temp.txt
    
    if [ "$FOUND" = false ]; then
        echo "  ❓ $permission"
        UNUSED_COUNT=$((UNUSED_COUNT + 1))
    fi
done < permissions_temp.txt

# Check required selectors for each platform
echo -e "\n🔍 Verifying required selectors for each platform..."
REQUIRED_SELECTORS=("messageContainer" "messages" "messageText" "sender" "timestamp" "inputField" "sendButton")

# Count platforms and permissions
PLATFORM_COUNT=$(grep -c . platforms_temp.txt)
PERMISSION_COUNT=$(grep -c . permissions_temp.txt)

while read -r platform; do
    if [ -z "$platform" ]; then continue; fi
    
    echo -e "\n📱 Platform: $platform"
    PLATFORM_BLOCK=$(sed -n "/'$platform': {/,/}/p" "$SELECTORS_FILE")
    if [ -z "$PLATFORM_BLOCK" ]; then
        # Try with double quotes
        PLATFORM_BLOCK=$(sed -n "/$platform\": {/,/}/p" "$SELECTORS_FILE")
    fi
    
    if [ -z "$PLATFORM_BLOCK" ]; then
        echo "  ❌ Platform block not found in selectors file"
        continue
    fi
    
    for selector in "${REQUIRED_SELECTORS[@]}"; do
        if [[ "$PLATFORM_BLOCK" == *"$selector"* ]]; then
            echo "  ✅ $selector"
        else
            echo "  ❌ $selector (MISSING)"
        fi
    done
done < platforms_temp.txt

# Extract required selectors for each platform
echo -e "\n🔍 Validating selector completeness for each platform..."

REQUIRED_SELECTORS=("messageContainer" "messages" "messageText" "sender" "timestamp" "inputField" "sendButton")
MISSING_SELECTORS=0
PLATFORM_COUNT=0
SELECTOR_ISSUES=()

# Function to log to both console and file
log() {
    echo "$1" | tee -a "$LOG_FILE"
}

# Function to check if a platform has all required selectors
check_platform_selectors() {
    local platform=$1
    local platform_section
    platform_section=$(sed -n "/'$platform': {/,/},/p" "$SELECTORS_FILE")
    
    if [ -z "$platform_section" ]; then
        # Try with double quotes
        platform_section=$(sed -n "/$platform\": {/,/},/p" "$SELECTORS_FILE")
    fi
    
    if [ -z "$platform_section" ]; then
        log "  ❌ Could not extract selector section for $platform"
        return 1
    fi
    
    local missing=0
    local missing_list=""
    
    for selector in "${REQUIRED_SELECTORS[@]}"; do
        if ! echo "$platform_section" | grep -q "$selector:"; then
            missing=$((missing + 1))
            missing_list="$missing_list $selector"
        fi
    done
    
    if [ $missing -eq 0 ]; then
        log "  ✅ $platform has all required selectors"
        return 0
    else
        log "  ❌ $platform is missing $missing selectors:$missing_list"
        SELECTOR_ISSUES+=("$platform:$missing_list")
        MISSING_SELECTORS=$((MISSING_SELECTORS + missing))
        return 1
    fi
}

# Check selectors for each platform
while read -r platform; do
    if [ -z "$platform" ]; then continue; fi
    
    PLATFORM_COUNT=$((PLATFORM_COUNT + 1))
    log "Checking selectors for: $platform"
    check_platform_selectors "$platform"
done < platforms_temp.txt

# Generate HTML report
echo -e "\n📊 Generating HTML report..."

cat > "$HTML_REPORT" << EOF
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catalyst Selector Verification Report</title>
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
        .success {
            color: #27ae60;
        }
        .warning {
            color: #f39c12;
        }
        .error {
            color: #e74c3c;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f2f2f2;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .platform-table tr.missing td {
            background-color: #ffecec;
        }
        .platform-table tr.valid td {
            background-color: #efffef;
        }
        code {
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: monospace;
        }
        .test-instructions {
            background-color: #e9f7fe;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <h1>Catalyst Selector Verification Report</h1>
    <p class="timestamp">Generated on: $(date)</p>
    
    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Platforms analyzed:</strong> $PLATFORM_COUNT</p>
        <p><strong>Platforms with matching permissions:</strong> $MATCHED_COUNT</p>
        <p><strong>Platforms missing permissions:</strong> $MISSING_COUNT</p>
        <p><strong>Unused host permissions:</strong> $UNUSED_COUNT</p>
        <p><strong>Missing selectors:</strong> $MISSING_SELECTORS</p>
        
        <div class="status">
EOF

# Add overall status to HTML report
if [ $MISSING_COUNT -eq 0 ] && [ $UNUSED_COUNT -eq 0 ] && [ $MISSING_SELECTORS -eq 0 ]; then
    echo '<p class="success">✅ All platforms have proper permissions and selectors.</p>' >> "$HTML_REPORT"
elif [ $MISSING_COUNT -eq 0 ] && [ $MISSING_SELECTORS -eq 0 ]; then
    echo '<p class="warning">⚠️ All platforms have proper permissions and selectors, but there are unused host permissions.</p>' >> "$HTML_REPORT"
else
    echo '<p class="error">❌ There are issues with platform permissions or selectors. See details below.</p>' >> "$HTML_REPORT"
fi

cat >> "$HTML_REPORT" << EOF
        </div>
    </div>
    
    <h2>Platform Selector Details</h2>
    <table class="platform-table">
        <tr>
            <th>Platform</th>
            <th>Has Permission</th>
            <th>Selectors Status</th>
            <th>Missing Selectors</th>
        </tr>
EOF

# Add platform details to HTML report
while read -r platform; do
    if [ -z "$platform" ]; then continue; fi
    
    # Check if platform has permission
    PERMISSION_STATUS="❌ Missing"
    PERMISSION_CLASS="missing"
    
    while read -r permission; do
        if [ -z "$permission" ]; then continue; fi
        
        if [[ "$platform" == *"$permission"* || "$permission" == *"$platform"* ]]; then
            PERMISSION_STATUS="✅ Valid"
            PERMISSION_CLASS="valid"
            break
        fi
    done < permissions_temp.txt
    
    # Check if platform has all selectors
    SELECTORS_STATUS="✅ Complete"
    MISSING_LIST=""
    ROW_CLASS="valid"
    
    for issue in "${SELECTOR_ISSUES[@]}"; do
        IFS=':' read -r issue_platform issue_selectors <<< "$issue"
        if [ "$issue_platform" = "$platform" ]; then
            SELECTORS_STATUS="❌ Incomplete"
            MISSING_LIST="$issue_selectors"
            ROW_CLASS="missing"
            break
        fi
    done
    
    echo "<tr class=\"$ROW_CLASS\">" >> "$HTML_REPORT"
    echo "  <td>$platform</td>" >> "$HTML_REPORT"
    echo "  <td>$PERMISSION_STATUS</td>" >> "$HTML_REPORT"
    echo "  <td>$SELECTORS_STATUS</td>" >> "$HTML_REPORT"
    echo "  <td>$MISSING_LIST</td>" >> "$HTML_REPORT"
    echo "</tr>" >> "$HTML_REPORT"
done < platforms_temp.txt

cat >> "$HTML_REPORT" << EOF
    </table>
    
    <div class="test-instructions">
        <h2>How to Test Selectors in Browser</h2>
        <p>A browser verification script has been generated to help you test selectors directly in supported platforms.</p>
        <ol>
            <li>Open Chrome and navigate to one of the supported platforms</li>
            <li>Open Chrome DevTools (F12 or Ctrl+Shift+I)</li>
            <li>Copy the contents of this file: <code>$BROWSER_SCRIPT</code></li>
            <li>Paste the script into the DevTools Console and press Enter</li>
            <li>Review the results to verify if selectors are working correctly</li>
        </ol>
        <p><strong>Note:</strong> You need to be logged in to the platform for most selectors to be testable.</p>
    </div>
    
    <h2>Recommendations</h2>
    <ul>
EOF

# Add recommendations based on findings
if [ $MISSING_COUNT -gt 0 ]; then
    echo "<li class=\"error\">Add missing host permissions to manifest.json for platforms without permissions</li>" >> "$HTML_REPORT"
fi

if [ $UNUSED_COUNT -gt 0 ]; then
    echo "<li class=\"warning\">Consider removing unused host permissions from manifest.json</li>" >> "$HTML_REPORT"
fi

if [ $MISSING_SELECTORS -gt 0 ]; then
    echo "<li class=\"error\">Add missing selectors to platform_selectors.js</li>" >> "$HTML_REPORT"
fi

cat >> "$HTML_REPORT" << EOF
        <li>Use the browser verification script to validate selectors on each platform</li>
        <li>Test the extension on all supported platforms to ensure functionality</li>
    </ul>
    
    <footer>
        <p>Catalyst Whisper Coach Extension - Selector Verification Report</p>
    </footer>
</body>
</html>
EOF

echo "✅ HTML report generated at: $HTML_REPORT"

# Clean up temporary files
rm -f platforms_temp.txt permissions_temp.txt

# Summary
echo -e "\n📊 Verification Summary:"
echo "------------------------------------------------"
echo "Platforms analyzed:             $PLATFORM_COUNT"
echo "Platforms with permissions:     $MATCHED_COUNT"
echo "Platforms missing permissions:  $MISSING_COUNT"
echo "Unused host permissions:        $UNUSED_COUNT"
echo "Missing selectors:              $MISSING_SELECTORS"
echo "------------------------------------------------"

if [ $MISSING_COUNT -eq 0 ] && [ $UNUSED_COUNT -eq 0 ] && [ $MISSING_SELECTORS -eq 0 ]; then
    echo "✅ All platforms have proper permissions and selectors."
elif [ $MISSING_COUNT -eq 0 ] && [ $MISSING_SELECTORS -eq 0 ]; then
    echo "⚠️ All platforms have proper permissions and selectors, but there are unused host permissions."
else
    echo "❌ There are issues with platform permissions or selectors. See HTML report for details."
fi

echo -e "\n📝 Next steps:"
echo "1. Review the HTML report for detailed information"
echo "2. Use the browser verification script to test selectors on each platform"
echo "3. Fix any issues found in platform_selectors.js or manifest.json"
echo "4. Run the comprehensive platform testing using test_platforms.sh"
