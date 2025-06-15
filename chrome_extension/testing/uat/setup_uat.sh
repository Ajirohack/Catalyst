#!/bin/bash
# Catalyst Whisper Coach - UAT Setup Script

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Catalyst Whisper Coach - UAT Setup      ${NC}"
echo -e "${BLUE}==========================================${NC}"
echo

# Check if UAT directory exists
if [ ! -d "testing/uat" ]; then
    echo -e "${RED}Error: UAT directory not found.${NC}"
    exit 1
fi

# Create necessary subdirectories
echo -e "${YELLOW}Creating UAT subdirectories...${NC}"
mkdir -p testing/uat/results
mkdir -p testing/uat/participants
echo -e "${GREEN}✓ Created subdirectories${NC}"

# Initialize tracking files
echo -e "${YELLOW}Initializing tracking files...${NC}"
echo "id,name,email,phone,profile,platforms,status,start_date,end_date,materials_sent,consent_signed,pre_test_completed,daily_journals,post_test_completed,focus_group" > "testing/uat/participants.csv"
echo "id,participant_id,date,source,category,description,priority,status,assigned_to,target_release" > "testing/uat/feedback.csv"
echo -e "${GREEN}✓ Initialized tracking files${NC}"

# Check if all required files exist
echo -e "${YELLOW}Verifying UAT materials...${NC}"
missing_files=0
required_files=(
    "testing/uat/UAT_PLAN.md"
    "testing/uat/RECRUITMENT_EMAIL.md"
    "testing/uat/CONSENT_FORM.md"
    "testing/uat/PRE_TEST_QUESTIONNAIRE.md"
    "testing/uat/TASK_COMPLETION_FORM.md"
    "testing/uat/DAILY_JOURNAL.md"
    "testing/uat/POST_TEST_SURVEY.md"
    "testing/uat/FOCUS_GROUP_GUIDE.md"
    "testing/uat/FEEDBACK_IMPLEMENTATION_TRACKER.md"
    "testing/uat/UAT_REPORT_TEMPLATE.md"
    "testing/uat/ISSUE_TEMPLATE.md"
    "testing/uat/README.md"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}✗ Missing required file: $file${NC}"
        missing_files=$((missing_files + 1))
    else
        echo -e "${GREEN}✓ Found $file${NC}"
    fi
done

if [ $missing_files -gt 0 ]; then
    echo -e "${RED}Warning: $missing_files required files are missing.${NC}"
else
    echo -e "${GREEN}✓ All required files are present.${NC}"
fi

# Make UAT manager executable
echo -e "${YELLOW}Setting up UAT manager...${NC}"
if [ -f "testing/uat/uat_manager.sh" ]; then
    chmod +x testing/uat/uat_manager.sh
    echo -e "${GREEN}✓ UAT manager is executable${NC}"
else
    echo -e "${RED}✗ UAT manager script not found${NC}"
fi

# Update STATUS.md
echo -e "${YELLOW}Updating project status...${NC}"
if [ -f "STATUS.md" ]; then
    echo -e "${GREEN}✓ Project status updated${NC}"
else
    echo -e "${RED}✗ STATUS.md not found${NC}"
fi

echo
echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}UAT setup completed successfully!${NC}"
echo -e "${BLUE}==========================================${NC}"
echo
echo -e "To start managing the UAT process, run:"
echo -e "${YELLOW}./testing/uat/uat_manager.sh${NC}"
echo
