#!/bin/bash
# Catalyst Whisper Coach - Packaging Script
# This script prepares the extension for Chrome Web Store submission

echo "📦 Packaging Catalyst Whisper Coach Extension"
echo "=============================================="

# Output directory
OUTPUT_DIR="./dist"
mkdir -p $OUTPUT_DIR

# Package name with version
VERSION=$(grep -o '"version": "[^"]*"' manifest.json | cut -d'"' -f4)
PACKAGE_NAME="catalyst-whisper-coach-v$VERSION"
PACKAGE_FILE="$OUTPUT_DIR/$PACKAGE_NAME.zip"

# Function to log messages
log() {
  echo "📝 $1"
}

# Clean up any previous packages
if [ -f "$PACKAGE_FILE" ]; then
  log "Removing previous package: $PACKAGE_FILE"
  rm "$PACKAGE_FILE"
fi

# Check for required files
REQUIRED_FILES=(
  "manifest.json"
  "background.js"
  "content_script.js"
  "content_styles.css"
  "popup.html"
  "popup.js"
  "options.html"
  "options.js"
  "login.html"
  "login.js"
  "welcome.html"
)

MISSING_FILES=0
for file in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    log "❌ Missing required file: $file"
    MISSING_FILES=$((MISSING_FILES+1))
  fi
done

if [ $MISSING_FILES -gt 0 ]; then
  log "⚠️ $MISSING_FILES required files are missing. Aborting packaging."
  exit 1
fi

# Check for icons
if [ ! -d "icons" ] || [ $(ls -1 icons/*.png 2>/dev/null | wc -l) -lt 1 ]; then
  log "❌ Missing icons directory or no icon files found. Aborting packaging."
  exit 1
fi

# Validate manifest.json
if ! jq . "manifest.json" >/dev/null 2>&1; then
  log "❌ Invalid manifest.json. Aborting packaging."
  exit 1
fi

# Create production version of manifest.json with updated settings
log "Creating production manifest.json..."
cat manifest.json | jq '.version = $newVal' --arg newVal "$VERSION" > "$OUTPUT_DIR/manifest.json"

# Get API endpoint from background.js
API_ENDPOINT=$(grep -o "CATALYST_API_BASE = '[^']*'" background.js | cut -d "'" -f 2)
if [[ "$API_ENDPOINT" == *"localhost"* ]]; then
  log "⚠️ Found localhost API endpoint in background.js"
  
  # Ask for production API endpoint
  read -p "Enter production API endpoint (leave empty to keep $API_ENDPOINT): " PROD_API_ENDPOINT
  
  if [ ! -z "$PROD_API_ENDPOINT" ]; then
    log "Updating API endpoint to: $PROD_API_ENDPOINT"
    sed "s|CATALYST_API_BASE = '$API_ENDPOINT'|CATALYST_API_BASE = '$PROD_API_ENDPOINT'|" background.js > "$OUTPUT_DIR/background.js"
  else
    log "Keeping localhost API endpoint. Make sure to update before final submission."
    cp background.js "$OUTPUT_DIR/background.js"
  fi
else
  cp background.js "$OUTPUT_DIR/background.js"
fi

# Copy all necessary files to the dist directory
log "Copying files to dist directory..."
cp content_script.js content_styles.css popup.html popup.js options.html options.js login.html login.js welcome.html "$OUTPUT_DIR/"
cp -r icons "$OUTPUT_DIR/"

# Create the zip package
log "Creating zip package: $PACKAGE_FILE"
cd "$OUTPUT_DIR"
zip -r "../$PACKAGE_FILE" .
cd ..

# Create screenshots directory if submitting to Chrome Web Store
SCREENSHOTS_DIR="$OUTPUT_DIR/screenshots"
mkdir -p "$SCREENSHOTS_DIR"

log "📸 Remember to add screenshots to: $SCREENSHOTS_DIR"
log "Required screenshots for Chrome Web Store:"
log "1. At least one screenshot (1280x800 or 640x400)"
log "2. Small promotional tile (440x280)"
log "3. Large promotional tile (920x680) (optional)"

# Create promotional description file
PROMO_FILE="$OUTPUT_DIR/promotional_description.txt"
cat > "$PROMO_FILE" << EOL
# Catalyst Whisper Coach - Chrome Extension

## Short Description (up to 132 characters)
Real-time AI relationship coach that analyzes your conversations and provides instant communication guidance.

## Detailed Description
Catalyst Whisper Coach is an AI-powered relationship communication assistant that works alongside your favorite messaging platforms. As you chat with your partner, friends, or colleagues, Whisper Coach analyzes the conversation and provides real-time suggestions to improve your communication.

### Key Features:
• Real-time conversation analysis across multiple platforms
• AI-powered coaching tailored to your communication style
• Personalized suggestions based on context and relationship goals
• Privacy-focused with optional data minimization
• Works with WhatsApp, Messenger, Instagram, Discord, Slack, Teams, and Telegram

### How It Works:
1. Install the extension and connect to your Catalyst account
2. Chat normally on your favorite messaging platforms
3. Receive discrete "whispers" with contextual communication coaching
4. Apply suggestions directly to your conversation with one click

### Benefits:
• Strengthen relationships through improved communication
• Develop greater emotional awareness in conversations
• Identify and correct negative communication patterns
• Build more empathetic and supportive interactions
• Track your communication progress over time

Catalyst Whisper Coach integrates seamlessly with the Catalyst relationship intelligence platform, allowing you to track goals, analyze communication patterns, and achieve measurable improvements in your relationships.

### Privacy & Security:
We take your privacy seriously. All data is encrypted, and you can enable Privacy Mode to minimize data sent for analysis. Your conversations remain private and secure.

Get started with Catalyst Whisper Coach today and transform your digital communication!
EOL

log "📄 Created promotional description file: $PROMO_FILE"

# Success message
log "✅ Packaging completed successfully!"
log "📦 Package created: $PACKAGE_FILE"
log "📊 Package size: $(du -sh $PACKAGE_FILE | cut -f1)"
log "🔍 Next steps:"
log "1. Test the packaged extension thoroughly"
log "2. Add screenshots to $SCREENSHOTS_DIR"
log "3. Review promotional content in $PROMO_FILE"
log "4. Submit to Chrome Web Store Developer Dashboard"

echo "=============================================="
