#!/bin/bash

# Catalyst Whisper Coach - Comprehensive Platform Testing Script
# This script guides testers through testing all supported platforms

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Test results directory
TEST_DIR="./test_results"
mkdir -p $TEST_DIR

# Generate timestamp for this test run
TIMESTAMP=$(date +%Y%m%d%H%M%S)
LOG_FILE="$TEST_DIR/comprehensive_test_$TIMESTAMP.log"

# Log function
log() {
  echo -e "$1" | tee -a $LOG_FILE
}

# Header function
header() {
  log "\n${BLUE}==============================================${NC}"
  log "${BLUE}  $1${NC}"
  log "${BLUE}==============================================${NC}"
}

# Step function
step() {
  log "\n${CYAN}🔹 $1${NC}"
}

# Success function
success() {
  log "${GREEN}✅ $1${NC}"
}

# Warning function
warning() {
  log "${YELLOW}⚠️  $1${NC}"
}

# Error function
error() {
  log "${RED}❌ $1${NC}"
}

# Function to test a platform
test_platform() {
  local platform=$1
  local url=$2
  
  header "Testing Platform: $platform"
  log "URL: $url"
  log "Date: $(date)"
  
  step "Preparing test for $platform"
  log "Please follow these steps to test $platform:"
  
  step "1. Open Chrome with the extension installed"
  log "   You can use the 'Run Chrome with Extension' task in VS Code"
  
  step "2. Navigate to $url"
  log "   Wait for the page to fully load"
  
  step "3. Verify the extension recognizes the platform"
  log "   Click the extension icon in Chrome toolbar"
  log "   Confirm the platform name appears in the popup"
  read -p "   Does the extension recognize the platform? (y/n): " platform_recognized
  if [[ $platform_recognized == "y" ]]; then
    success "Platform recognition successful"
  else
    error "Platform recognition failed"
  fi
  
  step "4. Test message detection"
  log "   Send a test message on the platform"
  log "   Wait a few seconds for processing"
  read -p "   Were messages detected correctly? (y/n): " messages_detected
  if [[ $messages_detected == "y" ]]; then
    success "Message detection successful"
  else
    error "Message detection failed"
  fi
  
  step "5. Test whisper suggestions"
  log "   Send a message with emotional content like:"
  log "   'I'm feeling really frustrated about what happened yesterday'"
  log "   Wait for whisper suggestions to appear"
  read -p "   Did whisper suggestions appear? (y/n): " whispers_appeared
  if [[ $whispers_appeared == "y" ]]; then
    success "Whisper suggestions successful"
  else
    error "Whisper suggestions failed"
  fi
  
  step "6. Test UI appearance"
  log "   Check that whisper widget appears properly"
  log "   Verify styling and positioning is correct"
  read -p "   Is the UI appearance correct? (y/n): " ui_correct
  if [[ $ui_correct == "y" ]]; then
    success "UI appearance correct"
  else
    error "UI appearance issues detected"
  fi
  
  step "7. Test performance"
  log "   Monitor for any lag or performance issues"
  log "   Check CPU usage in Task Manager"
  read -p "   Is performance acceptable? (y/n): " performance_ok
  if [[ $performance_ok == "y" ]]; then
    success "Performance acceptable"
  else
    error "Performance issues detected"
  fi
  
  # Optional notes
  log "\nAdditional Notes:"
  read -p "Enter any additional observations or issues (press enter to skip): " notes
  if [[ -n $notes ]]; then
    log "Notes: $notes"
  fi
  
  # Calculate success rate
  local tests_passed=0
  local total_tests=5
  
  [[ $platform_recognized == "y" ]] && ((tests_passed++))
  [[ $messages_detected == "y" ]] && ((tests_passed++))
  [[ $whispers_appeared == "y" ]] && ((tests_passed++))
  [[ $ui_correct == "y" ]] && ((tests_passed++))
  [[ $performance_ok == "y" ]] && ((tests_passed++))
  
  local success_rate=$((tests_passed * 100 / total_tests))
  
  if [[ $success_rate -eq 100 ]]; then
    success "Platform Test Complete - All tests passed (100%)"
  elif [[ $success_rate -ge 80 ]]; then
    warning "Platform Test Complete - $success_rate% tests passed"
  else
    error "Platform Test Complete - $success_rate% tests passed"
  fi
  
  # Record test results
  cat >> $TEST_DIR/platform_results.csv << EOL
$TIMESTAMP,$platform,$platform_recognized,$messages_detected,$whispers_appeared,$ui_correct,$performance_ok,$success_rate%,"$notes"
EOL
  
  log "\nPress enter to continue to next platform..."
  read
}

# Initialize CSV if it doesn't exist
if [[ ! -f $TEST_DIR/platform_results.csv ]]; then
  echo "Timestamp,Platform,Recognition,Messages,Whispers,UI,Performance,Success Rate,Notes" > $TEST_DIR/platform_results.csv
fi

# Display welcome message
header "Catalyst Comprehensive Platform Testing"
log "This script will guide you through testing the Catalyst extension on all supported platforms."
log "Test results will be saved to: $LOG_FILE"
log "Date: $(date)"

# Ask which platforms to test
log "\nSupported Platforms:"
log "1. WhatsApp Web"
log "2. Facebook Messenger"
log "3. Instagram DMs"
log "4. Discord"
log "5. Slack"
log "6. Microsoft Teams"
log "7. Telegram Web"
log "8. Google Meet"
log "9. Zoom"
log "10. ChatGPT"
log "11. Gmail"
log "12. LinkedIn Messaging"
log "13. Twitter/X DMs"
log "14. Outlook"
log "15. Reddit Chat"
log "16. Skype Web"
log "0. All platforms"

read -p "Enter platform number(s) to test (comma-separated) or 0 for all: " platforms_input

# Define all platforms with their URLs
declare -A platform_urls=(
  ["WhatsApp Web"]="https://web.whatsapp.com"
  ["Facebook Messenger"]="https://www.messenger.com"
  ["Instagram DMs"]="https://www.instagram.com/direct/inbox"
  ["Discord"]="https://discord.com/channels/@me"
  ["Slack"]="https://slack.com"
  ["Microsoft Teams"]="https://teams.microsoft.com"
  ["Telegram Web"]="https://web.telegram.org"
  ["Google Meet"]="https://meet.google.com"
  ["Zoom"]="https://zoom.us"
  ["ChatGPT"]="https://chat.openai.com"
  ["Gmail"]="https://mail.google.com"
  ["LinkedIn Messaging"]="https://www.linkedin.com/messaging"
  ["Twitter/X DMs"]="https://twitter.com"
  ["Outlook"]="https://outlook.live.com"
  ["Reddit Chat"]="https://www.reddit.com"
  ["Skype Web"]="https://web.skype.com"
)

# Convert platform numbers to names
if [[ $platforms_input == "0" ]]; then
  # Test all platforms
  platforms_to_test=("${!platform_urls[@]}")
else
  # Parse comma-separated input
  IFS=',' read -ra platform_numbers <<< "$platforms_input"
  platforms_to_test=()
  
  for number in "${platform_numbers[@]}"; do
    case $number in
      1) platforms_to_test+=("WhatsApp Web") ;;
      2) platforms_to_test+=("Facebook Messenger") ;;
      3) platforms_to_test+=("Instagram DMs") ;;
      4) platforms_to_test+=("Discord") ;;
      5) platforms_to_test+=("Slack") ;;
      6) platforms_to_test+=("Microsoft Teams") ;;
      7) platforms_to_test+=("Telegram Web") ;;
      8) platforms_to_test+=("Google Meet") ;;
      9) platforms_to_test+=("Zoom") ;;
      10) platforms_to_test+=("ChatGPT") ;;
      11) platforms_to_test+=("Gmail") ;;
      12) platforms_to_test+=("LinkedIn Messaging") ;;
      13) platforms_to_test+=("Twitter/X DMs") ;;
      14) platforms_to_test+=("Outlook") ;;
      15) platforms_to_test+=("Reddit Chat") ;;
      16) platforms_to_test+=("Skype Web") ;;
      *) warning "Invalid platform number: $number" ;;
    esac
  done
fi

# Confirm test plan
total_platforms=${#platforms_to_test[@]}
log "\n${YELLOW}Planning to test $total_platforms platforms:${NC}"
for platform in "${platforms_to_test[@]}"; do
  log "- $platform (${platform_urls[$platform]})"
done

read -p "Press enter to begin testing or Ctrl+C to cancel..."

# Run tests for selected platforms
for platform in "${platforms_to_test[@]}"; do
  test_platform "$platform" "${platform_urls[$platform]}"
done

# Generate test report
header "Testing Summary"
log "Testing completed on $(date)"
log "Tested $total_platforms platforms"

# Analyze results from CSV
if [[ -f $TEST_DIR/platform_results.csv ]]; then
  passed_count=0
  partial_count=0
  failed_count=0
  
  # Skip header line
  while IFS=, read -r timestamp platform recognition messages whispers ui performance success_rate notes; do
    # Skip header
    [[ $timestamp == "Timestamp" ]] && continue
    
    # Only process entries from this test run
    [[ $timestamp == $TIMESTAMP* ]] || continue
    
    # Extract success rate percentage
    success_rate=${success_rate%\%}
    
    if [[ $success_rate -eq 100 ]]; then
      ((passed_count++))
    elif [[ $success_rate -ge 80 ]]; then
      ((partial_count++))
    else
      ((failed_count++))
    fi
  done < $TEST_DIR/platform_results.csv
  
  log "Results:"
  success "✅ Fully passed: $passed_count"
  warning "⚠️ Partial issues: $partial_count"
  error "❌ Failed: $failed_count"
  
  # Calculate overall success rate
  if [[ $total_platforms -gt 0 ]]; then
    overall_rate=$(( (passed_count * 100 + partial_count * 75) / total_platforms ))
    log "\nOverall success rate: ${YELLOW}$overall_rate%${NC}"
    
    if [[ $overall_rate -ge 90 ]]; then
      success "✅ Testing successful! The extension is working well across platforms."
    elif [[ $overall_rate -ge 70 ]]; then
      warning "⚠️ Testing partially successful. Some platforms need attention."
    else
      error "❌ Testing revealed significant issues across platforms."
    fi
  fi
fi

log "\nDetailed test results saved to:"
log "- Log file: $LOG_FILE"
log "- Results CSV: $TEST_DIR/platform_results.csv"

# Generate HTML report
HTML_REPORT="$TEST_DIR/report_$TIMESTAMP.html"
cat > $HTML_REPORT << EOL
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Catalyst Platform Testing Report</title>
  <style>
    body { font-family: system-ui, -apple-system, sans-serif; line-height: 1.5; margin: 20px; max-width: 1200px; margin: 0 auto; padding: 20px; }
    h1 { color: #2563eb; }
    h2 { color: #4b5563; margin-top: 30px; }
    table { border-collapse: collapse; width: 100%; margin: 20px 0; }
    th, td { border: 1px solid #d1d5db; padding: 8px 12px; text-align: left; }
    th { background-color: #f3f4f6; }
    tr:nth-child(even) { background-color: #f9fafb; }
    .pass { color: #059669; }
    .partial { color: #d97706; }
    .fail { color: #dc2626; }
    .summary { display: flex; gap: 20px; margin: 20px 0; }
    .summary-card { flex: 1; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .big-number { font-size: 36px; font-weight: bold; margin: 10px 0; }
    .progress-bar { height: 20px; background-color: #e5e7eb; border-radius: 10px; overflow: hidden; margin-top: 20px; }
    .progress-fill { height: 100%; background-color: #2563eb; }
  </style>
</head>
<body>
  <h1>Catalyst Platform Testing Report</h1>
  <p>Generated: $(date)</p>
  
  <div class="summary">
    <div class="summary-card">
      <h3>Platforms Tested</h3>
      <div class="big-number">$total_platforms</div>
    </div>
    <div class="summary-card">
      <h3>Pass Rate</h3>
      <div class="big-number">$overall_rate%</div>
      <div class="progress-bar">
        <div class="progress-fill" style="width: $overall_rate%;"></div>
      </div>
    </div>
    <div class="summary-card">
      <h3>Results</h3>
      <p><span class="pass">✅ Pass: $passed_count</span></p>
      <p><span class="partial">⚠️ Partial: $partial_count</span></p>
      <p><span class="fail">❌ Fail: $failed_count</span></p>
    </div>
  </div>
  
  <h2>Detailed Results</h2>
  <table>
    <tr>
      <th>Platform</th>
      <th>Recognition</th>
      <th>Messages</th>
      <th>Whispers</th>
      <th>UI</th>
      <th>Performance</th>
      <th>Success Rate</th>
      <th>Notes</th>
    </tr>
EOL

# Add results to HTML table
if [[ -f $TEST_DIR/platform_results.csv ]]; then
  while IFS=, read -r timestamp platform recognition messages whispers ui performance success_rate notes; do
    # Skip header
    [[ $timestamp == "Timestamp" ]] && continue
    
    # Only process entries from this test run
    [[ $timestamp == $TIMESTAMP* ]] || continue
    
    # Format yes/no as checkmarks/X
    [[ $recognition == "y" ]] && recognition="✅" || recognition="❌"
    [[ $messages == "y" ]] && messages="✅" || messages="❌"
    [[ $whispers == "y" ]] && whispers="✅" || whispers="❌"
    [[ $ui == "y" ]] && ui="✅" || ui="❌"
    [[ $performance == "y" ]] && performance="✅" || performance="❌"
    
    # Remove quotes from notes
    notes="${notes//\"}"
    
    # Determine row class based on success rate
    success_rate_num=${success_rate%\%}
    if [[ $success_rate_num -eq 100 ]]; then
      row_class="class=\"pass\""
    elif [[ $success_rate_num -ge 80 ]]; then
      row_class="class=\"partial\""
    else
      row_class="class=\"fail\""
    fi
    
    # Add to HTML table
    cat >> $HTML_REPORT << EOL
    <tr $row_class>
      <td>$platform</td>
      <td>$recognition</td>
      <td>$messages</td>
      <td>$whispers</td>
      <td>$ui</td>
      <td>$performance</td>
      <td>$success_rate</td>
      <td>$notes</td>
    </tr>
EOL
  done < $TEST_DIR/platform_results.csv
fi

# Close HTML file
cat >> $HTML_REPORT << EOL
  </table>
  
  <h2>Recommendations</h2>
  <p>Based on the test results, consider the following actions:</p>
  <ul>
EOL

# Add recommendations based on results
if [[ $failed_count -gt 0 ]]; then
  cat >> $HTML_REPORT << EOL
    <li class="fail">Address failed platform issues as a priority</li>
EOL
fi

if [[ $partial_count -gt 0 ]]; then
  cat >> $HTML_REPORT << EOL
    <li class="partial">Review partially working platforms for specific issues</li>
EOL
fi

if [[ $passed_count -eq $total_platforms ]]; then
  cat >> $HTML_REPORT << EOL
    <li class="pass">All platforms are working well! Consider expanding to additional platforms</li>
EOL
fi

# Finish HTML file
cat >> $HTML_REPORT << EOL
    <li>Schedule regular platform testing as part of the release cycle</li>
    <li>Monitor for platform UI changes that might break selectors</li>
  </ul>
  
  <p><small>Report generated by Catalyst Platform Testing Tool</small></p>
</body>
</html>
EOL

log "\nHTML report generated: $HTML_REPORT"
log "Open this file in a browser to view the formatted report"

# Wrap up
header "Testing Complete"
log "Thank you for conducting comprehensive platform testing!"
log "Your results will help improve the Catalyst extension for all users."
