# Catalyst Whisper Coach - Onboarding Guide

This document provides detailed instructions for setting up and using the Catalyst Whisper Coach extension.

## Installation

### For End Users

1. **Install from Chrome Web Store**
   - Navigate to the Chrome Web Store
   - Search for "Catalyst Whisper Coach"
   - Click "Add to Chrome"
   - Confirm the installation when prompted

2. **First-time Setup**
   - After installation, the extension icon will appear in your browser toolbar
   - Click the icon to open the extension popup
   - You'll be prompted to log in with your Catalyst account
   - If you don't have an account, you'll be able to create one

### For Developers

1. **Load Unpacked Extension**
   - Clone or download the Catalyst repository
   - Open Chrome and navigate to `chrome://extensions`
   - Enable "Developer mode" using the toggle in the top-right corner
   - Click "Load unpacked" and select the `chrome_extension` directory
   - The extension should now be installed and visible in your browser toolbar

2. **Developer Setup**
   - Make sure the Catalyst backend is running (`cd backend && python main.py`)
   - Check that the API endpoint in `background.js` points to your local server
   - Use the VS Code tasks to test and package the extension

## Usage Guide

### Connecting to Supported Platforms

The extension works with the following messaging platforms:

- WhatsApp Web
- Facebook Messenger
- Instagram DMs
- Discord
- Slack
- Microsoft Teams
- Telegram Web

To use the extension on these platforms:

1. Log in to your account on the supported platform
2. Make sure the extension is enabled (toggle in the popup)
3. Start or continue a conversation
4. The extension will monitor your messages and provide real-time coaching

### Extension Features

#### Whisper Suggestions

Whisper suggestions are real-time coaching tips that appear in the extension popup or as a widget on the page:

- **Real-time Analysis**: The extension analyzes conversation context, sentiment, and emotional patterns
- **Personalized Coaching**: Suggestions are tailored to your specific conversation and relationship goals
- **Actionable Tips**: Get practical advice on how to respond effectively

#### Settings and Customization

Customize your experience through the extension options:

1. **Access Settings**: Click the extension icon and navigate to the Settings tab, or right-click the extension icon and select "Options"

2. **General Settings**:
   - Enable/disable the extension
   - Toggle auto-analysis
   - Toggle real-time coaching
   - Enable privacy mode to limit data sent for analysis

3. **Whisper Settings**:
   - Adjust analysis frequency (low, medium, high)
   - Configure auto-display of suggestions
   - Set display duration
   - Choose display mode (widget, popup, inline)
   - Set whisper frequency

4. **Platform Settings**:
   - Enable/disable monitoring for specific platforms

5. **Notification Settings**:
   - Toggle insights notifications
   - Toggle goals notifications
   - Toggle milestone notifications

## Troubleshooting

If you encounter issues with the extension:

1. **Extension Not Working**:
   - Make sure you're logged in to your Catalyst account
   - Check that the extension is enabled
   - Verify you're on a supported messaging platform
   - Try refreshing the page

2. **No Suggestions Appearing**:
   - Check your whisper settings
   - Make sure auto-analysis is enabled
   - Verify your conversation is long enough for meaningful analysis

3. **Extension Disconnected**:
   - Check your internet connection
   - Verify the Catalyst backend is accessible
   - Try logging out and back in

4. **Performance Issues**:
   - Adjust analysis frequency to a lower setting
   - Disable real-time coaching on platforms you're not actively using

## Privacy and Security

The Catalyst Whisper Coach extension takes your privacy seriously:

- **Privacy Mode**: When enabled, only essential data is sent for analysis
- **Data Encryption**: All communication with the Catalyst backend is encrypted
- **Local Processing**: Some analysis happens locally to minimize data transmission
- **User Control**: You can disable the extension for specific platforms

## Getting Help

If you need additional assistance:

- Check the [Catalyst Documentation](http://localhost:8000/docs)
- Visit the [Support Portal](http://localhost:8000/support)
- Contact us at [support@catalyst.example.com](mailto:support@catalyst.example.com)
