#!/bin/bash
# Catalyst Whisper Coach - Testing Script
# This script automates testing of the Chrome Extension components

echo "🧪 Starting Catalyst Whisper Coach Extension Tests"
echo "=================================================="

# Testing directory
TEST_DIR="./test_results"
mkdir -p $TEST_DIR

# Log file
LOG_FILE="$TEST_DIR/test_$(date +%Y%m%d%H%M%S).log"
echo "📝 Logging test results to $LOG_FILE"

# Function to log messages
log() {
  echo "$1" | tee -a $LOG_FILE
}

# Function to check file existence
check_file() {
  if [ -f "$1" ]; then
    log "✅ File exists: $1"
    return 0
  else
    log "❌ File missing: $1"
    return 1
  fi
}

# Function to check directory existence
check_dir() {
  if [ -d "$1" ]; then
    log "✅ Directory exists: $1"
    return 0
  else
    log "❌ Directory missing: $1"
    return 1
  fi
}

# Function to validate JSON files
validate_json() {
  if jq . "$1" >/dev/null 2>&1; then
    log "✅ Valid JSON: $1"
    return 0
  else
    log "❌ Invalid JSON: $1"
    return 1
  fi
}

# Function to check JavaScript files for syntax errors
check_js_syntax() {
  # Requires node to be installed
  if command -v node >/dev/null 2>&1; then
    if node --check "$1" >/dev/null 2>&1; then
      log "✅ JS syntax valid: $1"
      return 0
    else
      log "❌ JS syntax errors in: $1"
      node --check "$1" 2>&1 | tee -a $LOG_FILE
      return 1
    fi
  else
    log "⚠️ Node.js not found, skipping JS syntax check for: $1"
    return 0
  fi
}

# Function to check HTML files
check_html() {
  # Basic check for opening and closing tags
  if grep -q "<html" "$1" && grep -q "</html>" "$1"; then
    log "✅ HTML format looks valid: $1"
    return 0
  else
    log "❌ HTML may have issues: $1"
    return 1
  fi
}

# Start tests
log "🔍 Starting file existence tests..."

# Check essential files
REQUIRED_FILES=(
  "manifest.json"
  "background.js"
  "content_script.js"
  "popup.html"
  "popup.js"
  "options.html"
  "options.js"
  "login.html"
  "login.js"
  "welcome.html"
  "content_styles.css"
)

FAILED=0
for file in "${REQUIRED_FILES[@]}"; do
  if ! check_file "$file"; then
    FAILED=$((FAILED+1))
  fi
done

# Check icons directory
check_dir "icons"

# Count icon files
if [ -d "icons" ]; then
  ICON_COUNT=$(ls -1 icons/*.png 2>/dev/null | wc -l)
  log "🖼️ Found $ICON_COUNT icon files"
  
  if [ $ICON_COUNT -lt 4 ]; then
    log "⚠️ Less than 4 icon sizes found, recommended to have 16px, 32px, 48px, and 128px icons"
  fi
fi

# Validate manifest.json
log "🔍 Validating manifest.json..."
if [ -f "manifest.json" ]; then
  validate_json "manifest.json"
  
  # Check manifest version
  MANIFEST_VERSION=$(jq .manifest_version manifest.json)
  log "📋 Manifest version: $MANIFEST_VERSION"
  
  if [ "$MANIFEST_VERSION" != "3" ]; then
    log "⚠️ Manifest version should be 3 for modern Chrome extensions"
  fi
  
  # Check permissions
  PERMISSIONS=$(jq -r '.permissions | join(", ")' manifest.json)
  log "🔐 Permissions: $PERMISSIONS"
  
  # Check content scripts
  CONTENT_SCRIPTS_COUNT=$(jq '.content_scripts | length' manifest.json)
  log "📜 Content scripts entries: $CONTENT_SCRIPTS_COUNT"
  
  # Check host permissions
  HOST_PERMISSIONS=$(jq -r '.host_permissions | join(", ")' manifest.json)
  log "🌐 Host permissions: $HOST_PERMISSIONS"
fi

# Check JavaScript syntax
log "🔍 Checking JavaScript files syntax..."
JS_FILES=(
  "background.js"
  "content_script.js"
  "popup.js"
  "options.js"
  "login.js"
)

for file in "${JS_FILES[@]}"; do
  if [ -f "$file" ]; then
    check_js_syntax "$file"
  fi
done

# Check HTML files
log "🔍 Checking HTML files..."
HTML_FILES=(
  "popup.html"
  "options.html"
  "login.html"
  "welcome.html"
)

for file in "${HTML_FILES[@]}"; do
  if [ -f "$file" ]; then
    check_html "$file"
  fi
done

# Check API endpoint in background.js
log "🔍 Checking API endpoint configuration..."
if [ -f "background.js" ]; then
  API_ENDPOINT=$(grep -o "CATALYST_API_BASE = '[^']*'" background.js | cut -d "'" -f 2)
  log "🌐 API Endpoint: $API_ENDPOINT"
  
  if [[ "$API_ENDPOINT" == *"localhost"* ]]; then
    log "⚠️ Using localhost API endpoint. Make sure to update before production deployment."
  fi
fi

# Check permissions
log "🔍 Verifying permissions align with functionality..."
REQUIRED_PERMISSIONS=("storage" "activeTab")
MANIFEST_PERMISSIONS=$(jq -r '.permissions[]' manifest.json 2>/dev/null)

for perm in "${REQUIRED_PERMISSIONS[@]}"; do
  if echo "$MANIFEST_PERMISSIONS" | grep -q "$perm"; then
    log "✅ Required permission present: $perm"
  else
    log "❌ Missing required permission: $perm"
    FAILED=$((FAILED+1))
  fi
done

# Calculate total size of extension
TOTAL_SIZE=$(du -sh . | cut -f1)
log "📦 Total extension size: $TOTAL_SIZE"

# Summary
log "\n📊 Test Summary"
log "================"
if [ $FAILED -eq 0 ]; then
  log "🎉 All tests passed successfully!"
else
  log "⚠️ $FAILED tests failed. Please review the log for details."
fi

log "✅ Testing completed at $(date)"
log "=================================================="

echo "Testing completed. Results saved to $LOG_FILE"
