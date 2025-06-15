#!/bin/bash
# Catalyst Whisper Coach - Open Test UI

echo "🧪 Opening Catalyst Whisper Coach Test UI..."

# Determine the full path to the test UI
TEST_UI_PATH="$(pwd)/testing/test_ui.html"

# Check if the file exists
if [ ! -f "$TEST_UI_PATH" ]; then
    echo "❌ Test UI file not found at: $TEST_UI_PATH"
    exit 1
fi

# Open the test UI in Chrome
if [ "$(uname)" == "Darwin" ]; then
    # macOS
    open -a "Google Chrome" "$TEST_UI_PATH"
elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
    # Linux
    google-chrome "$TEST_UI_PATH" || xdg-open "$TEST_UI_PATH"
elif [ "$(expr substr $(uname -s) 1 10)" == "MINGW32_NT" ] || [ "$(expr substr $(uname -s) 1 10)" == "MINGW64_NT" ]; then
    # Windows Git Bash
    start chrome "$TEST_UI_PATH"
else
    echo "❌ Unable to determine OS. Please open the file manually:"
    echo "$TEST_UI_PATH"
    exit 1
fi

echo "✅ Test UI opened in Chrome. You can now test the extension functionality."
echo "📋 Test reports will be saved in the testing/platforms directory."
