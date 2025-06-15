# Catalyst Whisper Coach - User Acceptance Testing

This directory contains all materials related to User Acceptance Testing (UAT) for the Catalyst Whisper Coach Chrome extension.

## Directory Structure

- **config/**: Configuration files for the UAT process
  - `uat_config.json`: Core settings for testing phases, participants, and success criteria
  - `template_config.json`: Settings for UAT templates and forms
  - `analysis_config.json`: Parameters for data processing and analysis

- **templates/**: Template files for testing materials
  - `PRE_TEST_QUESTIONNAIRE.md`: Collects participant background and expectations
  - `TEST_SCENARIOS.md`: Structured testing scenarios for guided sessions
  - `DAILY_JOURNAL.md`: Template for self-guided testing documentation
  - `PARTICIPANT_TRACKING.md`: Template for tracking participant progress

- **examples/**: Example files showing completed artifacts
  - `PARTICIPANT_EXAMPLE.md`: Example of a completed participant file
  - `SAMPLE_UAT_REPORT.md`: Example of a final UAT report

- **results/**: Directory for storing testing results
  - `pre_test/`: Pre-test questionnaire responses
  - `guided_sessions/`: Results from guided testing sessions
  - `daily_journals/`: Daily journal submissions
  - `focus_groups/`: Focus group notes and findings
  - `post_test/`: Post-test survey responses
  - `issues/`: Issue reports and tracking
  - `feedback_analysis/`: Analysis of collected feedback

- **reports/**: Directory for generated reports
  - `weekly/`: Weekly progress reports
  - `alpha/`: Alpha phase summary reports
  - `beta/`: Beta phase summary reports
  - `final/`: Final UAT reports

## Key Documents

- **TESTING_SCHEDULE.md**: Timeline for all testing activities
- **PARTICIPANT_TRACKING.md**: Tracking document for all participants
- **FACILITATOR_GUIDE.md**: Comprehensive guide for test facilitators
- **CONFIGURATION_GUIDE.md**: Documentation for customizing the UAT process
- **DATA_ANALYSIS_GUIDE.md**: Methodology for analyzing testing data
- **RESULTS_INTERPRETATION_GUIDE.md**: Framework for interpreting testing results
- **ISSUE_TEMPLATE.md**: Template for documenting issues and bugs

## Management Tool

The UAT process is managed using the `manage_uat.sh` script located in the parent directory. This script provides functionality for:

- Setting up the testing environment
- Managing participants
- Collecting and organizing feedback
- Generating reports
- Tracking issues

### Basic Usage

```bash
# Show help information
./manage_uat.sh help

# Set up the testing environment
./manage_uat.sh setup

# Add a new participant
./manage_uat.sh participant add --name "John Doe" --email "john.doe@example.com" --profile "active_dater"

# List all participants
./manage_uat.sh participant list

# Check participant status
./manage_uat.sh participant status --id P001

# Collect feedback from a specific period
./manage_uat.sh feedback collect --start-date 2025-06-22 --end-date 2025-06-29

# Analyze collected feedback
./manage_uat.sh feedback analyze

# Generate a report
./manage_uat.sh report generate --format markdown --output weekly_report_1.md

# Check overall testing status
./manage_uat.sh report status --detailed
```

## UAT Process Overview

### 1. Preparation Phase (June 15-21, 2025)

- Finalize testing materials
- Recruit participants using the recruitment email
- Schedule testing sessions
- Prepare testing environment

### 2. Alpha Testing Phase (June 22 - July 5, 2025)

- Conduct guided testing sessions with 5-8 participants
- Collect and analyze initial feedback
- Identify critical issues for immediate resolution
- Generate alpha phase report

### 3. Beta Testing Phase (July 6 - August 2, 2025)

- Expand testing to 30-50 participants
- Conduct guided sessions, self-guided testing, and focus groups
- Collect comprehensive feedback across all platforms
- Generate weekly progress reports

### 4. Analysis and Reporting (August 3-9, 2025)

- Compile and analyze all feedback
- Generate final UAT report with findings
- Develop implementation recommendations
- Create implementation roadmap

## Contact Information

For questions about the UAT process, contact:

- **UAT Coordinator**: [Name]
- **Email**: [Email address]
- **Phone**: [Phone number]

---

Last Updated: June 15, 2025
