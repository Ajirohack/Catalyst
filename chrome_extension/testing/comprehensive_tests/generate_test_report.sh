#!/bin/bash
# Script to generate a consolidated test report

# Directory containing test results
TEST_DIR=$(dirname "$0")
PLATFORMS_DIR="$TEST_DIR/platforms"
SCREENSHOTS_DIR="$TEST_DIR/screenshots"

# Output file
REPORT_FILE="$TEST_DIR/consolidated_report.md"

echo "Generating consolidated test report..."

# Create report header
cat > "$REPORT_FILE" << HEADER
# Catalyst Whisper Coach - Consolidated Test Report

**Generated on:** $(date)

## Test Environment
- **Chrome Version:** $(grep -m 1 "Chrome Version" $PLATFORMS_DIR/*.md | head -n 1 | cut -d':' -f2 | xargs)
- **Extension Version:** $(grep -m 1 "Extension Version" $PLATFORMS_DIR/*.md | head -n 1 | cut -d':' -f2 | xargs)

## Summary

| Platform | Message Detection | Whisper Functionality | Status |
|----------|-------------------|----------------------|--------|
HEADER

# Process each platform test file
for test_file in "$PLATFORMS_DIR"/*.md; do
    platform=$(basename "$test_file" _test.md)
    
    # Extract test results
    message_detection=$(grep -c "\[x\]" <<< "$(grep "Extension detects" "$test_file")")
    message_detection_total=$(grep -c "Extension detects" "$test_file")
    
    whisper_functionality=$(grep -c "\[x\]" <<< "$(grep "Whisper" "$test_file")")
    whisper_functionality_total=$(grep -c "Whisper" "$test_file")
    
    # Determine status
    if [ "$message_detection" -eq "$message_detection_total" ] && [ "$whisper_functionality" -eq "$whisper_functionality_total" ]; then
        status="✅ Pass"
    elif [ "$message_detection" -eq 0 ] || [ "$whisper_functionality" -eq 0 ]; then
        status="❌ Fail"
    else
        status="⚠️ Partial"
    fi
    
    # Add to report
    echo "| $platform | $message_detection/$message_detection_total | $whisper_functionality/$whisper_functionality_total | $status |" >> "$REPORT_FILE"
done

# Add issues section
cat >> "$REPORT_FILE" << ISSUES

## Issues Found

ISSUES

# Extract issues from test files
for test_file in "$PLATFORMS_DIR"/*.md; do
    platform=$(basename "$test_file" _test.md)
    notes=$(sed -n '/## Notes:/,/## Screenshots:/p' "$test_file" | grep -v "## Notes:" | grep -v "## Screenshots:" | grep -v "<!--")
    
    if [ -n "$notes" ]; then
        echo "### $platform" >> "$REPORT_FILE"
        echo "$notes" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
    fi
done

# Add recommendations section
cat >> "$REPORT_FILE" << RECOMMENDATIONS

## Recommendations

- Review all platforms marked as "Fail" or "Partial"
- Prioritize fixing DOM selectors for platforms with message detection issues
- Test the extension on additional accounts for each platform
- Consider adding automated testing for critical platforms

## Next Steps

1. Address critical issues identified in this report
2. Retest platforms with issues after fixes are implemented
3. Expand testing to include more edge cases
4. Prepare for user acceptance testing (UAT)
RECOMMENDATIONS

echo "Report generated at: $REPORT_FILE"
