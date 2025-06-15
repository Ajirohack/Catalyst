# Catalyst Whisper Coach - Testing Documentation

This directory contains tools, scripts, and documentation for testing the Catalyst Whisper Coach Chrome extension.

## Testing Structure

- **`platforms/`**: Platform-specific test files and reports
- **`results/`**: Test results and logs
- **`test_ui.html`**: Interactive test UI for simulating messaging platforms
- **`test_selectors.js`**: Script to verify DOM selectors on real platforms
- **`PLATFORM_TESTING_GUIDE.md`**: Comprehensive guide for platform testing
- **`PLATFORM_TESTING_SUMMARY.md`**: Template for summarizing test results
- **`ISSUE_TEMPLATE.md`**: Template for reporting issues

## Testing Workflow

### 1. Setup Testing Environment

Before testing, ensure you have:

- Google Chrome installed
- The Catalyst backend server running
- The extension loaded in Chrome

### 2. Available Testing Tasks

The following VS Code tasks are available for testing:

- **Run Chrome with Extension**: Opens Chrome with the extension loaded
- **Open Whisper Coach Test UI**: Opens the test UI for simulated testing
- **Run Platform Testing**: Runs the platform testing script
- **Test Catalyst Whisper Extension**: Runs basic extension verification tests

### 3. Testing Approaches

#### Simulated Testing

Use the Test UI (`test_ui.html`) to simulate different messaging platforms and test extension functionality without requiring accounts on each platform.

To run simulated testing:

1. Run the "Open Whisper Coach Test UI" task
2. Select a platform from the dropdown
3. Load a test scenario
4. Test extension functionality
5. Document your findings

#### Real Platform Testing

Test on actual messaging platforms to verify DOM selectors and real-world functionality.

To run real platform testing:

1. Run the "Run Chrome with Extension" task
2. Navigate to the actual messaging platform
3. Log in with a test account
4. Open the browser console and paste the content of `test_selectors.js`
5. Verify that DOM selectors are working correctly
6. Document your findings in the platform-specific test file

### 4. Reporting Issues

When you encounter issues during testing:

1. Create a new file in the `platforms` directory using the ISSUE_TEMPLATE.md template
2. Fill out all relevant information
3. Include screenshots or videos if possible
4. Suggest solutions if you have ideas

### 5. Updating DOM Selectors

If you find that DOM selectors need to be updated:

1. Open `content_script.js`
2. Locate the PLATFORM_SELECTORS object
3. Update the selector for the specific platform
4. Test the updated selector using the test_selectors.js script
5. Document the changes in your issue report

## Test Coverage Goals

Ensure testing covers:

1. **Basic Functionality**
   - Extension loads without errors
   - DOM selectors work correctly
   - Messages are properly extracted
   - Whisper suggestions are displayed

2. **User Experience**
   - Suggestions are helpful and contextually relevant
   - UI is intuitive and responsive
   - Performance impact is minimal

3. **Edge Cases**
   - Long conversations
   - Messages in different languages
   - Different browser window sizes
   - Various platform themes/layouts

## Generating Test Reports

After completing testing:

1. Compile your findings in the PLATFORM_TESTING_SUMMARY.md file
2. Include success rates for each platform
3. List any issues found
4. Provide recommendations for improvements

## Contact

If you have questions about the testing process, contact the development team at [dev@catalyst.example.com](mailto:dev@catalyst.example.com).
