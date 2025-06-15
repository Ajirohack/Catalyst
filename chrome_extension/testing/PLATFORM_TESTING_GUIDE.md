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
   ```
   cd backend
   python main.py
   ```
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
   - Copy and paste the content of `testing/test_selectors.js`
   - Review the results to verify that all selectors are working

4. **Test Whisper functionality**
   - Send various types of messages
   - Click the extension icon to see if whisper suggestions appear
   - Verify that suggestions are relevant to the conversation

5. **Document your findings**
   - Fill out the test template in `testing/platforms/[platform]_test.md`
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
3. Update the selector in `content_script.js`
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
