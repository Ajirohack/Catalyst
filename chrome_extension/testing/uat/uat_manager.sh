#!/bin/bash
# Catalyst Whisper Coach - UAT Management Script

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Directories
UAT_DIR="./testing/uat"
RESULTS_DIR="$UAT_DIR/results"
PARTICIPANT_DIR="$UAT_DIR/participants"

# Create necessary directories
mkdir -p $RESULTS_DIR
mkdir -p $PARTICIPANT_DIR

# Main menu
show_menu() {
    clear
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${BLUE}  Catalyst Whisper Coach - UAT Manager   ${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    echo -e "1. ${GREEN}Setup UAT Environment${NC}"
    echo -e "2. ${GREEN}Manage Participants${NC}"
    echo -e "3. ${GREEN}Generate Participant Materials${NC}"
    echo -e "4. ${GREEN}Process Feedback Data${NC}"
    echo -e "5. ${GREEN}Generate Reports${NC}"
    echo -e "6. ${GREEN}View UAT Status${NC}"
    echo -e "7. ${YELLOW}Exit${NC}"
    echo
    echo -n "Please select an option: "
    read -r option
    
    case $option in
        1) setup_environment ;;
        2) manage_participants ;;
        3) generate_materials ;;
        4) process_feedback ;;
        5) generate_reports ;;
        6) view_status ;;
        7) exit 0 ;;
        *) 
            echo -e "${RED}Invalid option${NC}"
            sleep 2
            show_menu
            ;;
    esac
}

# Setup environment
setup_environment() {
    clear
    echo -e "${BLUE}Setting up UAT Environment${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    # Check if all required files exist
    missing_files=0
    required_files=(
        "$UAT_DIR/UAT_PLAN.md"
        "$UAT_DIR/RECRUITMENT_EMAIL.md"
        "$UAT_DIR/CONSENT_FORM.md"
        "$UAT_DIR/PRE_TEST_QUESTIONNAIRE.md"
        "$UAT_DIR/TASK_COMPLETION_FORM.md"
        "$UAT_DIR/DAILY_JOURNAL.md"
        "$UAT_DIR/POST_TEST_SURVEY.md"
        "$UAT_DIR/FOCUS_GROUP_GUIDE.md"
        "$UAT_DIR/FEEDBACK_IMPLEMENTATION_TRACKER.md"
        "$UAT_DIR/UAT_REPORT_TEMPLATE.md"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            echo -e "${RED}Missing required file: $file${NC}"
            missing_files=$((missing_files + 1))
        fi
    done
    
    if [ $missing_files -gt 0 ]; then
        echo -e "${RED}$missing_files required files are missing. Please create them before proceeding.${NC}"
    else
        echo -e "${GREEN}All required files are present.${NC}"
    fi
    
    # Create participant tracking file if it doesn't exist
    if [ ! -f "$UAT_DIR/participants.csv" ]; then
        echo "id,name,email,phone,profile,platforms,status,start_date,end_date,materials_sent,consent_signed,pre_test_completed,daily_journals,post_test_completed,focus_group" > "$UAT_DIR/participants.csv"
        echo -e "${GREEN}Created participant tracking file.${NC}"
    else
        echo -e "${YELLOW}Participant tracking file already exists.${NC}"
    fi
    
    # Create feedback tracking file if it doesn't exist
    if [ ! -f "$UAT_DIR/feedback.csv" ]; then
        echo "id,participant_id,date,source,category,description,priority,status,assigned_to,target_release" > "$UAT_DIR/feedback.csv"
        echo -e "${GREEN}Created feedback tracking file.${NC}"
    else
        echo -e "${YELLOW}Feedback tracking file already exists.${NC}"
    fi
    
    echo
    echo -e "${GREEN}Environment setup complete.${NC}"
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    show_menu
}

# Manage participants
manage_participants() {
    clear
    echo -e "${BLUE}Manage Participants${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    echo -e "1. ${GREEN}Add New Participant${NC}"
    echo -e "2. ${GREEN}View All Participants${NC}"
    echo -e "3. ${GREEN}Update Participant Status${NC}"
    echo -e "4. ${GREEN}Generate Participant Report${NC}"
    echo -e "5. ${GREEN}Back to Main Menu${NC}"
    echo
    echo -n "Please select an option: "
    read -r option
    
    case $option in
        1) add_participant ;;
        2) view_participants ;;
        3) update_participant ;;
        4) participant_report ;;
        5) show_menu ;;
        *) 
            echo -e "${RED}Invalid option${NC}"
            sleep 2
            manage_participants
            ;;
    esac
}

# Add new participant
add_participant() {
    clear
    echo -e "${BLUE}Add New Participant${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    # Generate ID
    id=$(date +%Y%m%d%H%M%S)
    
    echo -n "Enter participant name: "
    read -r name
    
    echo -n "Enter participant email: "
    read -r email
    
    echo -n "Enter participant phone: "
    read -r phone
    
    echo "Select participant profile:"
    echo "1. Relationship Coach"
    echo "2. Active Dater"
    echo "3. Couple"
    echo "4. Communication Student"
    echo "5. Other"
    echo -n "Enter profile number: "
    read -r profile_num
    
    case $profile_num in
        1) profile="Relationship Coach" ;;
        2) profile="Active Dater" ;;
        3) profile="Couple" ;;
        4) profile="Communication Student" ;;
        5) profile="Other" ;;
        *) profile="Unknown" ;;
    esac
    
    echo -n "Enter platforms to test (comma-separated): "
    read -r platforms
    
    # Add participant to CSV
    echo "$id,$name,$email,$phone,$profile,$platforms,Invited,$(date +%Y-%m-%d),,No,No,No,0,No,No" >> "$UAT_DIR/participants.csv"
    
    # Create participant directory
    mkdir -p "$PARTICIPANT_DIR/$id"
    
    echo -e "${GREEN}Participant added successfully with ID: $id${NC}"
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    manage_participants
}

# View all participants
view_participants() {
    clear
    echo -e "${BLUE}All Participants${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    if [ -f "$UAT_DIR/participants.csv" ]; then
        # Skip header and format output
        tail -n +2 "$UAT_DIR/participants.csv" | while IFS=',' read -r id name email profile platforms status start rest; do
            echo -e "${YELLOW}ID:${NC} $id"
            echo -e "${YELLOW}Name:${NC} $name"
            echo -e "${YELLOW}Email:${NC} $email"
            echo -e "${YELLOW}Profile:${NC} $profile"
            echo -e "${YELLOW}Platforms:${NC} $platforms"
            echo -e "${YELLOW}Status:${NC} $status"
            echo -e "${YELLOW}Start Date:${NC} $start"
            echo -e "${BLUE}------------------------------------------${NC}"
        done
    else
        echo -e "${RED}No participants found.${NC}"
    fi
    
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    manage_participants
}

# Update participant status
update_participant() {
    clear
    echo -e "${BLUE}Update Participant Status${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    echo -n "Enter participant ID: "
    read -r participant_id
    
    if [ -f "$UAT_DIR/participants.csv" ]; then
        # Check if participant exists
        if grep -q "^$participant_id," "$UAT_DIR/participants.csv"; then
            echo "Select new status:"
            echo "1. Invited"
            echo "2. Active"
            echo "3. Completed"
            echo "4. Withdrawn"
            echo -n "Enter status number: "
            read -r status_num
            
            case $status_num in
                1) status="Invited" ;;
                2) status="Active" ;;
                3) status="Completed" ;;
                4) status="Withdrawn" ;;
                *) status="Unknown" ;;
            esac
            
            # Update status in CSV
            tmp_file=$(mktemp)
            awk -F, -v id="$participant_id" -v stat="$status" 'BEGIN {OFS=","} $1==id {$7=stat} {print}' "$UAT_DIR/participants.csv" > "$tmp_file"
            mv "$tmp_file" "$UAT_DIR/participants.csv"
            
            echo -e "${GREEN}Participant status updated successfully.${NC}"
        else
            echo -e "${RED}Participant not found.${NC}"
        fi
    else
        echo -e "${RED}No participants found.${NC}"
    fi
    
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    manage_participants
}

# Generate participant report
participant_report() {
    clear
    echo -e "${BLUE}Generate Participant Report${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    if [ -f "$UAT_DIR/participants.csv" ]; then
        # Count participants by status
        total=$(tail -n +2 "$UAT_DIR/participants.csv" | wc -l)
        invited=$(grep -c ",Invited," "$UAT_DIR/participants.csv")
        active=$(grep -c ",Active," "$UAT_DIR/participants.csv")
        completed=$(grep -c ",Completed," "$UAT_DIR/participants.csv")
        withdrawn=$(grep -c ",Withdrawn," "$UAT_DIR/participants.csv")
        
        # Count participants by profile
        coaches=$(grep -c ",Relationship Coach," "$UAT_DIR/participants.csv")
        daters=$(grep -c ",Active Dater," "$UAT_DIR/participants.csv")
        couples=$(grep -c ",Couple," "$UAT_DIR/participants.csv")
        students=$(grep -c ",Communication Student," "$UAT_DIR/participants.csv")
        others=$(grep -c ",Other," "$UAT_DIR/participants.csv")
        
        echo -e "${YELLOW}Total Participants:${NC} $total"
        echo
        echo -e "${YELLOW}Status Breakdown:${NC}"
        echo -e "  Invited: $invited"
        echo -e "  Active: $active"
        echo -e "  Completed: $completed"
        echo -e "  Withdrawn: $withdrawn"
        echo
        echo -e "${YELLOW}Profile Breakdown:${NC}"
        echo -e "  Relationship Coaches: $coaches"
        echo -e "  Active Daters: $daters"
        echo -e "  Couples: $couples"
        echo -e "  Communication Students: $students"
        echo -e "  Others: $others"
        
        # Generate report file
        report_file="$RESULTS_DIR/participant_report_$(date +%Y%m%d).md"
        
        echo "# Catalyst Whisper Coach - UAT Participant Report" > "$report_file"
        echo >> "$report_file"
        echo "**Generated on:** $(date +"%Y-%m-%d")" >> "$report_file"
        echo >> "$report_file"
        echo "## Participant Summary" >> "$report_file"
        echo >> "$report_file"
        echo "**Total Participants:** $total" >> "$report_file"
        echo >> "$report_file"
        echo "### Status Breakdown" >> "$report_file"
        echo >> "$report_file"
        echo "- **Invited:** $invited" >> "$report_file"
        echo "- **Active:** $active" >> "$report_file"
        echo "- **Completed:** $completed" >> "$report_file"
        echo "- **Withdrawn:** $withdrawn" >> "$report_file"
        echo >> "$report_file"
        echo "### Profile Breakdown" >> "$report_file"
        echo >> "$report_file"
        echo "- **Relationship Coaches:** $coaches" >> "$report_file"
        echo "- **Active Daters:** $daters" >> "$report_file"
        echo "- **Couples:** $couples" >> "$report_file"
        echo "- **Communication Students:** $students" >> "$report_file"
        echo "- **Others:** $others" >> "$report_file"
        echo >> "$report_file"
        echo "## Participant Details" >> "$report_file"
        echo >> "$report_file"
        
        # Add participant details
        echo "| ID | Name | Profile | Platforms | Status | Start Date |" >> "$report_file"
        echo "|---|---|---|---|---|---|" >> "$report_file"
        
        tail -n +2 "$UAT_DIR/participants.csv" | while IFS=',' read -r id name email profile platforms status start rest; do
            echo "| $id | $name | $profile | $platforms | $status | $start |" >> "$report_file"
        done
        
        echo -e "${GREEN}Report generated: $report_file${NC}"
    else
        echo -e "${RED}No participants found.${NC}"
    fi
    
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    manage_participants
}

# Generate materials
generate_materials() {
    clear
    echo -e "${BLUE}Generate Participant Materials${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    echo -n "Enter participant ID: "
    read -r participant_id
    
    if [ -f "$UAT_DIR/participants.csv" ]; then
        # Check if participant exists
        if grep -q "^$participant_id," "$UAT_DIR/participants.csv"; then
            # Extract participant details
            participant_data=$(grep "^$participant_id," "$UAT_DIR/participants.csv")
            participant_name=$(echo "$participant_data" | cut -d',' -f2)
            participant_email=$(echo "$participant_data" | cut -d',' -f3)
            participant_profile=$(echo "$participant_data" | cut -d',' -f5)
            participant_platforms=$(echo "$participant_data" | cut -d',' -f6)
            
            # Create materials directory
            materials_dir="$PARTICIPANT_DIR/$participant_id/materials"
            mkdir -p "$materials_dir"
            
            # Copy and personalize materials
            cp "$UAT_DIR/RECRUITMENT_EMAIL.md" "$materials_dir/recruitment_email.md"
            cp "$UAT_DIR/CONSENT_FORM.md" "$materials_dir/consent_form.md"
            cp "$UAT_DIR/PRE_TEST_QUESTIONNAIRE.md" "$materials_dir/pre_test_questionnaire.md"
            cp "$UAT_DIR/TASK_COMPLETION_FORM.md" "$materials_dir/task_completion_form.md"
            cp "$UAT_DIR/DAILY_JOURNAL.md" "$materials_dir/daily_journal.md"
            cp "$UAT_DIR/POST_TEST_SURVEY.md" "$materials_dir/post_test_survey.md"
            
            # Personalize recruitment email
            sed -i "" "s/\[Participant Name\]/$participant_name/g" "$materials_dir/recruitment_email.md"
            
            # Add participant ID to forms
            sed -i "" "s/_________________/$participant_id/g" "$materials_dir/pre_test_questionnaire.md"
            sed -i "" "s/_________________/$participant_id/g" "$materials_dir/task_completion_form.md"
            sed -i "" "s/_________________/$participant_id/g" "$materials_dir/daily_journal.md"
            sed -i "" "s/_________________/$participant_id/g" "$materials_dir/post_test_survey.md"
            
            # Update tracking file
            tmp_file=$(mktemp)
            awk -F, -v id="$participant_id" -v mat="Yes" 'BEGIN {OFS=","} $1==id {$10=mat} {print}' "$UAT_DIR/participants.csv" > "$tmp_file"
            mv "$tmp_file" "$UAT_DIR/participants.csv"
            
            echo -e "${GREEN}Materials generated for $participant_name (ID: $participant_id)${NC}"
            echo -e "${GREEN}Materials saved to: $materials_dir${NC}"
        else
            echo -e "${RED}Participant not found.${NC}"
        fi
    else
        echo -e "${RED}No participants found.${NC}"
    fi
    
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    show_menu
}

# Process feedback
process_feedback() {
    clear
    echo -e "${BLUE}Process Feedback Data${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    echo -e "1. ${GREEN}Add New Feedback${NC}"
    echo -e "2. ${GREEN}View All Feedback${NC}"
    echo -e "3. ${GREEN}Update Feedback Status${NC}"
    echo -e "4. ${GREEN}Generate Feedback Report${NC}"
    echo -e "5. ${GREEN}Back to Main Menu${NC}"
    echo
    echo -n "Please select an option: "
    read -r option
    
    case $option in
        1) add_feedback ;;
        2) view_feedback ;;
        3) update_feedback ;;
        4) feedback_report ;;
        5) show_menu ;;
        *) 
            echo -e "${RED}Invalid option${NC}"
            sleep 2
            process_feedback
            ;;
    esac
}

# Add new feedback
add_feedback() {
    clear
    echo -e "${BLUE}Add New Feedback${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    # Generate ID
    id="F$(date +%Y%m%d%H%M%S)"
    
    echo -n "Enter participant ID: "
    read -r participant_id
    
    echo "Select feedback source:"
    echo "1. Pre-test Questionnaire"
    echo "2. Task Completion"
    echo "3. Daily Journal"
    echo "4. Post-test Survey"
    echo "5. Focus Group"
    echo "6. Other"
    echo -n "Enter source number: "
    read -r source_num
    
    case $source_num in
        1) source="Pre-test Questionnaire" ;;
        2) source="Task Completion" ;;
        3) source="Daily Journal" ;;
        4) source="Post-test Survey" ;;
        5) source="Focus Group" ;;
        6) source="Other" ;;
        *) source="Unknown" ;;
    esac
    
    echo "Select feedback category:"
    echo "1. User Interface"
    echo "2. Suggestion Quality"
    echo "3. Platform Integration"
    echo "4. Performance"
    echo "5. Feature Request"
    echo "6. Bug Report"
    echo "7. Other"
    echo -n "Enter category number: "
    read -r category_num
    
    case $category_num in
        1) category="User Interface" ;;
        2) category="Suggestion Quality" ;;
        3) category="Platform Integration" ;;
        4) category="Performance" ;;
        5) category="Feature Request" ;;
        6) category="Bug Report" ;;
        7) category="Other" ;;
        *) category="Unknown" ;;
    esac
    
    echo -n "Enter feedback description: "
    read -r description
    
    echo "Select priority:"
    echo "1. P0 - Critical"
    echo "2. P1 - High"
    echo "3. P2 - Medium"
    echo "4. P3 - Low"
    echo "5. P4 - Consideration"
    echo -n "Enter priority number: "
    read -r priority_num
    
    case $priority_num in
        1) priority="P0 - Critical" ;;
        2) priority="P1 - High" ;;
        3) priority="P2 - Medium" ;;
        4) priority="P3 - Low" ;;
        5) priority="P4 - Consideration" ;;
        *) priority="Unknown" ;;
    esac
    
    # Add feedback to CSV
    echo "$id,$participant_id,$(date +%Y-%m-%d),$source,$category,\"$description\",$priority,New,Unassigned,TBD" >> "$UAT_DIR/feedback.csv"
    
    echo -e "${GREEN}Feedback added successfully with ID: $id${NC}"
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    process_feedback
}

# View all feedback
view_feedback() {
    clear
    echo -e "${BLUE}All Feedback${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    if [ -f "$UAT_DIR/feedback.csv" ]; then
        # Skip header and format output
        tail -n +2 "$UAT_DIR/feedback.csv" | while IFS=',' read -r id participant_id date source category description priority status assigned target; do
            echo -e "${YELLOW}ID:${NC} $id"
            echo -e "${YELLOW}Participant:${NC} $participant_id"
            echo -e "${YELLOW}Date:${NC} $date"
            echo -e "${YELLOW}Source:${NC} $source"
            echo -e "${YELLOW}Category:${NC} $category"
            echo -e "${YELLOW}Description:${NC} $description"
            echo -e "${YELLOW}Priority:${NC} $priority"
            echo -e "${YELLOW}Status:${NC} $status"
            echo -e "${BLUE}------------------------------------------${NC}"
        done
    else
        echo -e "${RED}No feedback found.${NC}"
    fi
    
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    process_feedback
}

# Update feedback status
update_feedback() {
    clear
    echo -e "${BLUE}Update Feedback Status${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    echo -n "Enter feedback ID: "
    read -r feedback_id
    
    if [ -f "$UAT_DIR/feedback.csv" ]; then
        # Check if feedback exists
        if grep -q "^$feedback_id," "$UAT_DIR/feedback.csv"; then
            echo "Select new status:"
            echo "1. New"
            echo "2. Evaluated"
            echo "3. Planned"
            echo "4. In Progress"
            echo "5. Testing"
            echo "6. Completed"
            echo "7. Deferred"
            echo "8. Won't Fix"
            echo -n "Enter status number: "
            read -r status_num
            
            case $status_num in
                1) status="New" ;;
                2) status="Evaluated" ;;
                3) status="Planned" ;;
                4) status="In Progress" ;;
                5) status="Testing" ;;
                6) status="Completed" ;;
                7) status="Deferred" ;;
                8) status="Won't Fix" ;;
                *) status="Unknown" ;;
            esac
            
            # Update status in CSV
            tmp_file=$(mktemp)
            awk -F, -v id="$feedback_id" -v stat="$status" 'BEGIN {OFS=","} $1==id {$8=stat} {print}' "$UAT_DIR/feedback.csv" > "$tmp_file"
            mv "$tmp_file" "$UAT_DIR/feedback.csv"
            
            echo -e "${GREEN}Feedback status updated successfully.${NC}"
        else
            echo -e "${RED}Feedback not found.${NC}"
        fi
    else
        echo -e "${RED}No feedback found.${NC}"
    fi
    
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    process_feedback
}

# Generate feedback report
feedback_report() {
    clear
    echo -e "${BLUE}Generate Feedback Report${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    if [ -f "$UAT_DIR/feedback.csv" ]; then
        # Count feedback by category
        total=$(tail -n +2 "$UAT_DIR/feedback.csv" | wc -l)
        ui=$(grep -c ",User Interface," "$UAT_DIR/feedback.csv")
        suggestions=$(grep -c ",Suggestion Quality," "$UAT_DIR/feedback.csv")
        integration=$(grep -c ",Platform Integration," "$UAT_DIR/feedback.csv")
        performance=$(grep -c ",Performance," "$UAT_DIR/feedback.csv")
        features=$(grep -c ",Feature Request," "$UAT_DIR/feedback.csv")
        bugs=$(grep -c ",Bug Report," "$UAT_DIR/feedback.csv")
        
        # Count feedback by priority
        p0=$(grep -c ",P0 - Critical," "$UAT_DIR/feedback.csv")
        p1=$(grep -c ",P1 - High," "$UAT_DIR/feedback.csv")
        p2=$(grep -c ",P2 - Medium," "$UAT_DIR/feedback.csv")
        p3=$(grep -c ",P3 - Low," "$UAT_DIR/feedback.csv")
        p4=$(grep -c ",P4 - Consideration," "$UAT_DIR/feedback.csv")
        
        # Count feedback by status
        new=$(grep -c ",New," "$UAT_DIR/feedback.csv")
        evaluated=$(grep -c ",Evaluated," "$UAT_DIR/feedback.csv")
        planned=$(grep -c ",Planned," "$UAT_DIR/feedback.csv")
        in_progress=$(grep -c ",In Progress," "$UAT_DIR/feedback.csv")
        testing=$(grep -c ",Testing," "$UAT_DIR/feedback.csv")
        completed=$(grep -c ",Completed," "$UAT_DIR/feedback.csv")
        deferred=$(grep -c ",Deferred," "$UAT_DIR/feedback.csv")
        wont_fix=$(grep -c ",Won't Fix," "$UAT_DIR/feedback.csv")
        
        echo -e "${YELLOW}Total Feedback Items:${NC} $total"
        echo
        echo -e "${YELLOW}Category Breakdown:${NC}"
        echo -e "  User Interface: $ui"
        echo -e "  Suggestion Quality: $suggestions"
        echo -e "  Platform Integration: $integration"
        echo -e "  Performance: $performance"
        echo -e "  Feature Requests: $features"
        echo -e "  Bug Reports: $bugs"
        echo
        echo -e "${YELLOW}Priority Breakdown:${NC}"
        echo -e "  P0 - Critical: $p0"
        echo -e "  P1 - High: $p1"
        echo -e "  P2 - Medium: $p2"
        echo -e "  P3 - Low: $p3"
        echo -e "  P4 - Consideration: $p4"
        echo
        echo -e "${YELLOW}Status Breakdown:${NC}"
        echo -e "  New: $new"
        echo -e "  Evaluated: $evaluated"
        echo -e "  Planned: $planned"
        echo -e "  In Progress: $in_progress"
        echo -e "  Testing: $testing"
        echo -e "  Completed: $completed"
        echo -e "  Deferred: $deferred"
        echo -e "  Won't Fix: $wont_fix"
        
        # Generate report file
        report_file="$RESULTS_DIR/feedback_report_$(date +%Y%m%d).md"
        
        echo "# Catalyst Whisper Coach - UAT Feedback Report" > "$report_file"
        echo >> "$report_file"
        echo "**Generated on:** $(date +"%Y-%m-%d")" >> "$report_file"
        echo >> "$report_file"
        echo "## Feedback Summary" >> "$report_file"
        echo >> "$report_file"
        echo "**Total Feedback Items:** $total" >> "$report_file"
        echo >> "$report_file"
        echo "### Category Breakdown" >> "$report_file"
        echo >> "$report_file"
        echo "- **User Interface:** $ui" >> "$report_file"
        echo "- **Suggestion Quality:** $suggestions" >> "$report_file"
        echo "- **Platform Integration:** $integration" >> "$report_file"
        echo "- **Performance:** $performance" >> "$report_file"
        echo "- **Feature Requests:** $features" >> "$report_file"
        echo "- **Bug Reports:** $bugs" >> "$report_file"
        echo >> "$report_file"
        echo "### Priority Breakdown" >> "$report_file"
        echo >> "$report_file"
        echo "- **P0 - Critical:** $p0" >> "$report_file"
        echo "- **P1 - High:** $p1" >> "$report_file"
        echo "- **P2 - Medium:** $p2" >> "$report_file"
        echo "- **P3 - Low:** $p3" >> "$report_file"
        echo "- **P4 - Consideration:** $p4" >> "$report_file"
        echo >> "$report_file"
        echo "### Status Breakdown" >> "$report_file"
        echo >> "$report_file"
        echo "- **New:** $new" >> "$report_file"
        echo "- **Evaluated:** $evaluated" >> "$report_file"
        echo "- **Planned:** $planned" >> "$report_file"
        echo "- **In Progress:** $in_progress" >> "$report_file"
        echo "- **Testing:** $testing" >> "$report_file"
        echo "- **Completed:** $completed" >> "$report_file"
        echo "- **Deferred:** $deferred" >> "$report_file"
        echo "- **Won't Fix:** $wont_fix" >> "$report_file"
        echo >> "$report_file"
        echo "## High Priority Items" >> "$report_file"
        echo >> "$report_file"
        echo "| ID | Category | Description | Status |" >> "$report_file"
        echo "|---|---|---|---|" >> "$report_file"
        
        # Add high priority items
        grep ",P0 - Critical,\|,P1 - High," "$UAT_DIR/feedback.csv" | while IFS=',' read -r id participant_id date source category description priority status rest; do
            echo "| $id | $category | $description | $status |" >> "$report_file"
        done
        
        echo >> "$report_file"
        echo "## Implementation Progress" >> "$report_file"
        echo >> "$report_file"
        echo "### Implementation Rate" >> "$report_file"
        echo >> "$report_file"
        
        # Calculate implementation rate
        implementation_rate=$((completed * 100 / total))
        echo "**Implementation Rate:** $implementation_rate%" >> "$report_file"
        
        echo -e "${GREEN}Report generated: $report_file${NC}"
    else
        echo -e "${RED}No feedback found.${NC}"
    fi
    
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    process_feedback
}

# Generate reports
generate_reports() {
    clear
    echo -e "${BLUE}Generate Reports${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    echo -e "1. ${GREEN}Generate UAT Summary Report${NC}"
    echo -e "2. ${GREEN}Generate Detailed Feedback Report${NC}"
    echo -e "3. ${GREEN}Generate Implementation Plan${NC}"
    echo -e "4. ${GREEN}Back to Main Menu${NC}"
    echo
    echo -n "Please select an option: "
    read -r option
    
    case $option in
        1) uat_summary_report ;;
        2) detailed_feedback_report ;;
        3) implementation_plan ;;
        4) show_menu ;;
        *) 
            echo -e "${RED}Invalid option${NC}"
            sleep 2
            generate_reports
            ;;
    esac
}

# Generate UAT summary report
uat_summary_report() {
    clear
    echo -e "${BLUE}Generate UAT Summary Report${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    report_file="$RESULTS_DIR/uat_summary_report_$(date +%Y%m%d).md"
    
    # Copy template
    cp "$UAT_DIR/UAT_REPORT_TEMPLATE.md" "$report_file"
    
    echo -e "${GREEN}UAT Summary Report template copied to: $report_file${NC}"
    echo -e "${YELLOW}Please edit this file to complete the report.${NC}"
    
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    generate_reports
}

# Generate detailed feedback report
detailed_feedback_report() {
    # Similar to feedback_report but more detailed
    # Implementation omitted for brevity
    echo -e "${YELLOW}This feature is not yet implemented.${NC}"
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    generate_reports
}

# Generate implementation plan
implementation_plan() {
    # Generate implementation plan based on feedback
    # Implementation omitted for brevity
    echo -e "${YELLOW}This feature is not yet implemented.${NC}"
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    generate_reports
}

# View UAT status
view_status() {
    clear
    echo -e "${BLUE}UAT Status Overview${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
    
    echo -e "${YELLOW}UAT Phase:${NC} In Progress"
    echo -e "${YELLOW}Start Date:${NC} 2025-06-15"
    echo -e "${YELLOW}End Date:${NC} 2025-07-15"
    echo
    
    if [ -f "$UAT_DIR/participants.csv" ]; then
        total_participants=$(tail -n +2 "$UAT_DIR/participants.csv" | wc -l)
        active_participants=$(grep -c ",Active," "$UAT_DIR/participants.csv")
        completed_participants=$(grep -c ",Completed," "$UAT_DIR/participants.csv")
        echo -e "${YELLOW}Participants:${NC}"
        echo -e "  Total: $total_participants"
        echo -e "  Active: $active_participants"
        echo -e "  Completed: $completed_participants"
    else
        echo -e "${YELLOW}Participants:${NC} No data available"
    fi
    
    echo
    
    if [ -f "$UAT_DIR/feedback.csv" ]; then
        total_feedback=$(tail -n +2 "$UAT_DIR/feedback.csv" | wc -l)
        implemented_feedback=$(grep -c ",Completed," "$UAT_DIR/feedback.csv")
        critical_issues=$(grep -c ",P0 - Critical," "$UAT_DIR/feedback.csv")
        high_issues=$(grep -c ",P1 - High," "$UAT_DIR/feedback.csv")
        echo -e "${YELLOW}Feedback:${NC}"
        echo -e "  Total Items: $total_feedback"
        echo -e "  Implemented: $implemented_feedback"
        echo -e "  Critical Issues: $critical_issues"
        echo -e "  High Priority Issues: $high_issues"
    else
        echo -e "${YELLOW}Feedback:${NC} No data available"
    fi
    
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo -e "  1. Complete participant recruitment"
    echo -e "  2. Conduct guided testing sessions"
    echo -e "  3. Analyze initial feedback"
    echo -e "  4. Begin implementing high-priority changes"
    
    echo
    read -n 1 -s -r -p "Press any key to continue..."
    show_menu
}

# Start the script
show_menu
