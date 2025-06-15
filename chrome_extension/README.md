# Catalyst Whisper Coach - Chrome Extension

Real-time relationship coaching and communication guidance in your browser.

## Overview

Catalyst Whisper Coach is a Chrome extension that monitors conversations on popular messaging platforms and provides real-time AI-powered coaching suggestions to improve your communication. It integrates with the Catalyst backend system to analyze conversation context, sentiment, and emotional patterns.

## Features

- **Real-time Monitoring**: Monitors conversations on WhatsApp, Facebook Messenger, Instagram DMs, Discord, Slack, Teams, and Telegram.
- **Contextual Analysis**: Analyzes message sentiment, emotional content, and conversation flow.
- **AI-Powered Suggestions**: Provides personalized coaching based on conversation context.
- **Multi-Platform Support**: Works seamlessly across major messaging platforms.
- **Privacy-Focused**: Includes privacy mode to limit data sent for analysis.
- **Customizable Experience**: Adjust settings for suggestion frequency and display preferences.

## Supported Platforms

- WhatsApp Web
- Facebook Messenger
- Instagram DMs
- Discord
- Slack
- Microsoft Teams
- Telegram Web

## Installation

### From Chrome Web Store (Recommended)

1. Visit the [Chrome Web Store](https://chrome.google.com/webstore)
2. Search for "Catalyst Whisper Coach"
3. Click "Add to Chrome"

### Manual Installation (Development)

1. Clone this repository
2. Open Chrome and navigate to `chrome://extensions/`
3. Enable "Developer mode" (toggle in the top-right corner)
4. Click "Load unpacked" and select the extension directory
5. The extension should now be installed and visible in your browser toolbar

## Setup

1. Click the Catalyst icon in your browser toolbar
2. Log in with your Catalyst account or enter your API token
3. Configure your preferences in the extension settings
4. Navigate to a supported messaging platform and start chatting

## Usage

1. **Login**: Connect the extension to your Catalyst account
2. **Chat**: Continue conversations as normal on supported platforms
3. **Receive Suggestions**: View real-time whisper suggestions in the extension popup
4. **Apply Suggestions**: Apply suggestions directly to your conversation with one click
5. **Customize**: Adjust settings to control suggestion frequency and display preferences

## Extension Structure

- `manifest.json`: Extension configuration
- `background.js`: Background service worker for extension lifecycle and API communication
- `content_script.js`: Content script injected into web pages to monitor conversations
- `content_styles.css`: Styles for the whisper widget and UI elements
- `popup.html/popup.js`: Extension popup UI for viewing suggestions
- `options.html/options.js`: Settings configuration page
- `login.html/login.js`: Authentication page
- `welcome.html`: Onboarding page for new users

## Backend Integration

The extension connects to the Catalyst backend API for analysis:

- **Authentication**: `/auth/login` and API token verification
- **Message Analysis**: `/analysis/whisper-stream` for real-time analysis
- **WebSocket Connection**: `/analysis/whisper-ws/{session_id}` for streaming updates

## Development

### Prerequisites

- Node.js and npm
- Chrome browser

### Local Development

1. Clone the repository
2. Run `npm install` (if package.json is present)
3. Load the extension in Chrome using Developer mode
4. Make changes to the code
5. Refresh the extension in Chrome to see changes

### Testing

Run the included test script to verify extension functionality:

```bash
chmod +x test_extension.sh
./test_extension.sh
```

### Packaging

To package the extension for distribution:

```bash
chmod +x package_extension.sh
./package_extension.sh
```

## Privacy

The extension processes conversation data to provide suggestions. Privacy features include:

- **Privacy Mode**: Limits the amount of data sent to the server
- **Local Processing**: Some analysis is performed locally when possible
- **Secure Transmission**: All data is encrypted in transit
- **User Control**: Users can disable the extension or limit platforms

## Troubleshooting

- **Extension not working**: Ensure you're on a supported platform and have enabled the extension
- **No suggestions appearing**: Check your connection to the Catalyst backend
- **Platform not supported**: Verify the platform is enabled in extension settings

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

For support or inquiries, please contact <support@catalyst-app.example.com>
