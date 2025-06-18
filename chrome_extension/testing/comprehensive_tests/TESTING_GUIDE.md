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
