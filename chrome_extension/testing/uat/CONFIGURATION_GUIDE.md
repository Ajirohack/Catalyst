# Catalyst Whisper Coach - UAT Configuration Guide

## Introduction

This document outlines the configuration settings and customization options for the User Acceptance Testing (UAT) framework for the Catalyst Whisper Coach Chrome extension. Use this guide to adapt the UAT process to specific testing requirements, participant profiles, and organizational needs.

## UAT Framework Components

The UAT framework consists of the following configurable components:

1. Documentation templates
2. Data collection instruments
3. Analysis tools and methodologies
4. Reporting templates
5. Management scripts and tools

## Core Configuration Files

### 1. UAT Settings File

The main configuration file for the UAT process is located at:

```
/chrome_extension/testing/uat/config/uat_config.json
```

This JSON file contains settings for:

- Testing phases and duration
- Participant requirements
- Platform testing priorities
- Success criteria thresholds
- Reporting requirements

Example configuration:

```json
{
  "testing": {
    "alpha_phase": {
      "start_date": "2025-06-22",
      "end_date": "2025-07-05",
      "min_participants": 5,
      "max_participants": 8
    },
    "beta_phase": {
      "start_date": "2025-07-06",
      "end_date": "2025-08-02",
      "min_participants": 30,
      "max_participants": 50
    }
  },
  "participants": {
    "profiles": {
      "relationship_coaches": {
        "percentage": 20,
        "required_platforms": ["WhatsApp", "Messenger"]
      },
      "active_daters": {
        "percentage": 30,
        "required_platforms": ["WhatsApp", "Instagram"]
      },
      "couples": {
        "percentage": 25,
        "required_platforms": ["WhatsApp", "Messenger"]
      },
      "communication_students": {
        "percentage": 15,
        "required_platforms": ["Discord", "Slack"]
      },
      "general_users": {
        "percentage": 10,
        "required_platforms": []
      }
    },
    "technical_proficiency": {
      "beginner": 30,
      "intermediate": 50,
      "advanced": 20
    }
  },
  "platforms": {
    "WhatsApp": {
      "priority": 1,
      "min_testers": 20
    },
    "Messenger": {
      "priority": 2,
      "min_testers": 15
    },
    "Instagram": {
      "priority": 2,
      "min_testers": 15
    },
    "Discord": {
      "priority": 3,
      "min_testers": 10
    },
    "Slack": {
      "priority": 3,
      "min_testers": 10
    },
    "Teams": {
      "priority": 4,
      "min_testers": 5
    },
    "Telegram": {
      "priority": 4,
      "min_testers": 5
    }
  },
  "success_criteria": {
    "sus_score": {
      "threshold": 70,
      "weight": 3
    },
    "nps": {
      "threshold": 30,
      "weight": 2
    },
    "task_completion": {
      "threshold": 85,
      "weight": 3
    },
    "feature_satisfaction": {
      "threshold": 4.0,
      "weight": 2
    },
    "critical_issues": {
      "max_allowed": 5,
      "weight": 4
    }
  },
  "reporting": {
    "formats": ["markdown", "html", "pdf"],
    "weekly_updates": true,
    "executive_summary_length": "2 pages",
    "include_raw_data": false
  }
}
```

### 2. Template Configuration

The template configuration file controls the appearance and content of UAT templates:

```
/chrome_extension/testing/uat/config/template_config.json
```

This file contains settings for:

- Template branding and styling
- Required and optional fields
- Rating scales and formats
- Default text and instructions

Example configuration:

```json
{
  "branding": {
    "logo_path": "/chrome_extension/icons/logo.png",
    "primary_color": "#3e4784",
    "secondary_color": "#f8f9fa",
    "font_family": "Arial, sans-serif"
  },
  "templates": {
    "consent_form": {
      "required_fields": [
        "participant_name",
        "participant_signature",
        "date"
      ],
      "optional_fields": [
        "participant_email",
        "participant_phone"
      ],
      "include_privacy_section": true,
      "include_recording_consent": true
    },
    "pre_test_questionnaire": {
      "demographic_section": true,
      "technical_proficiency_section": true,
      "communication_habits_section": true,
      "expectations_section": true,
      "rating_scale": "1-5"
    },
    "task_completion_form": {
      "track_time": true,
      "track_errors": true,
      "satisfaction_rating": true,
      "open_comments": true,
      "facilitator_observations": true,
      "rating_scale": "1-5"
    },
    "daily_journal": {
      "platforms_used_section": true,
      "suggestion_metrics_section": true,
      "issue_reporting_section": true,
      "time_tracking": true,
      "rating_scale": "1-5"
    },
    "post_test_survey": {
      "include_sus": true,
      "include_nps": true,
      "feature_satisfaction_section": true,
      "open_feedback_section": true,
      "future_recommendations_section": true,
      "rating_scale": "1-5"
    }
  },
  "default_text": {
    "consent_introduction": "Thank you for participating in the User Acceptance Testing of the Catalyst Whisper Coach Chrome extension...",
    "pre_test_introduction": "Before we begin testing, we would like to learn a bit about you and your communication habits...",
    "task_completion_introduction": "This form will guide you through specific tasks to test the Catalyst Whisper Coach extension...",
    "daily_journal_introduction": "Please complete this journal entry for each day you use the extension during the testing period...",
    "post_test_introduction": "Now that you have completed testing the Catalyst Whisper Coach extension, please share your overall experience..."
  }
}
```

### 3. Analysis Configuration

The analysis configuration file defines parameters for data processing and analysis:

```
/chrome_extension/testing/uat/config/analysis_config.json
```

This file contains settings for:

- Data processing methods
- Statistical analysis parameters
- Qualitative coding framework
- Prioritization criteria
- Reporting thresholds

Example configuration:

```json
{
  "quantitative_analysis": {
    "sus": {
      "calculate_subscales": true,
      "include_confidence_intervals": true,
      "comparison_benchmark": 68
    },
    "nps": {
      "promoter_threshold": 9,
      "detractor_threshold": 6,
      "comparison_benchmark": 30
    },
    "task_completion": {
      "success_threshold": 0.85,
      "time_outlier_threshold": 2.0,
      "error_severity_weights": {
        "critical": 3,
        "major": 2,
        "minor": 1
      }
    },
    "satisfaction_ratings": {
      "aggregation_method": "mean",
      "include_standard_deviation": true,
      "minimum_responses": 5
    },
    "segmentation": {
      "user_profiles": true,
      "platforms": true,
      "technical_proficiency": true,
      "demographics": false
    }
  },
  "qualitative_analysis": {
    "coding_framework": {
      "usability": [
        "navigation",
        "learnability",
        "efficiency",
        "memorability",
        "errors",
        "satisfaction"
      ],
      "suggestions": [
        "relevance",
        "timing",
        "quality",
        "usefulness",
        "presentation"
      ],
      "integration": [
        "detection",
        "display",
        "performance",
        "compatibility"
      ],
      "impact": [
        "communication_improvement",
        "relationship_outcomes",
        "learning",
        "confidence"
      ]
    },
    "sentiment_analysis": {
      "enabled": true,
      "categories": [
        "positive",
        "negative",
        "neutral",
        "mixed"
      ]
    },
    "theme_extraction": {
      "minimum_frequency": 3,
      "cross_participant_validation": true
    }
  },
  "prioritization": {
    "impact_levels": {
      "high": {
        "affected_users": 0.3,
        "severity": "blocks_core_functionality"
      },
      "medium": {
        "affected_users": 0.15,
        "severity": "impacts_key_features"
      },
      "low": {
        "affected_users": 0.05,
        "severity": "minor_inconvenience"
      }
    },
    "effort_levels": {
      "high": {
        "development_time": "weeks",
        "complexity": "architectural_change"
      },
      "medium": {
        "development_time": "days",
        "complexity": "feature_modification"
      },
      "low": {
        "development_time": "hours",
        "complexity": "simple_fix"
      }
    }
  },
  "reporting_thresholds": {
    "include_in_strengths": {
      "satisfaction": 4.0,
      "positive_mentions": 5
    },
    "include_in_issues": {
      "affected_users": 0.1,
      "severity": "impacts_experience"
    },
    "include_in_recommendations": {
      "impact": "medium",
      "effort": "medium"
    }
  }
}
```

## UAT Management Script Configuration

The UAT management script (`manage_uat.sh`) can be configured using command-line parameters and environment variables.

### Command-Line Parameters

The script accepts the following parameters:

```
./manage_uat.sh setup [--config PATH_TO_CONFIG]
./manage_uat.sh participant add --name NAME --email EMAIL [--profile PROFILE]
./manage_uat.sh participant list [--status STATUS]
./manage_uat.sh participant status [--id PARTICIPANT_ID]
./manage_uat.sh feedback collect [--start-date DATE] [--end-date DATE]
./manage_uat.sh feedback analyze [--method METHOD]
./manage_uat.sh report generate [--format FORMAT] [--output PATH]
./manage_uat.sh report status [--detailed]
```

### Environment Variables

The script recognizes the following environment variables:

```bash
# Directory Configuration
UAT_ROOT_DIR           # Root directory for UAT files
UAT_RESULTS_DIR        # Directory for test results
UAT_REPORTS_DIR        # Directory for generated reports

# Participant Management
UAT_MAX_PARTICIPANTS   # Maximum number of participants
UAT_REQUIRED_PROFILES  # Comma-separated list of required profiles

# Testing Configuration
UAT_ALPHA_START_DATE   # Start date for alpha testing
UAT_ALPHA_END_DATE     # End date for alpha testing
UAT_BETA_START_DATE    # Start date for beta testing
UAT_BETA_END_DATE      # End date for beta testing

# Reporting Configuration
UAT_REPORT_FORMATS     # Comma-separated list of report formats
UAT_INCLUDE_RAW_DATA   # Whether to include raw data in reports
```

Example usage:

```bash
# Set environment variables
export UAT_ROOT_DIR="/Volumes/Project Disk/Catalyst/chrome_extension/testing/uat"
export UAT_REPORT_FORMATS="markdown,html"

# Run the script
./manage_uat.sh setup
```

## Template Customization

### Modifying Markdown Templates

All templates in the UAT framework are stored as Markdown files in the `/chrome_extension/testing/uat/` directory. To customize a template:

1. Open the template file in a text editor
2. Modify the content while preserving placeholders (text within square brackets)
3. Save the template with the same filename

Important placeholders include:

- `[Participant ID]`: Unique identifier for the participant
- `[Date]`: Current date or testing date
- `[Your Name]`: Participant's name
- `[Facilitator Name]`: Name of the test facilitator
- `[Platform Name]`: Name of the messaging platform being tested

### Adding Custom Sections

To add a new section to a template:

1. Open the template file
2. Add a new heading with appropriate level (e.g., `## New Section`)
3. Add the content for the new section
4. Update the template configuration file to recognize the new section

Example addition to a template:

```markdown
## Technical Environment

### Device Information
- **Device Type**: [Device Type]
- **Operating System**: [Operating System]
- **Browser Version**: [Browser Version]
- **Screen Resolution**: [Screen Resolution]

### Network Information
- **Connection Type**: [Connection Type]
- **Average Speed**: [Average Speed]
```

## Data Collection Customization

### Custom Survey Questions

To add custom questions to the survey instruments:

1. Identify the appropriate template file
2. Add the new questions in the desired format
3. Update the analysis configuration to process the new data points

Example addition to the post-test survey:

```markdown
## Platform-Specific Experience

### WhatsApp Experience
- How would you rate the extension's integration with WhatsApp? [1-5]
- Did you encounter any WhatsApp-specific issues? [Yes/No]
- If yes, please describe: [Text field]

### Instagram Experience
- How would you rate the extension's integration with Instagram? [1-5]
- Did you encounter any Instagram-specific issues? [Yes/No]
- If yes, please describe: [Text field]
```

### Custom Metrics

To track additional metrics during testing:

1. Define the metric in the appropriate template
2. Add calculation methods to the analysis configuration
3. Include the metric in reporting templates

Example metric addition:

```json
"custom_metrics": {
  "suggestion_acceptance_rate": {
    "calculation": "used_suggestions / total_suggestions",
    "display_format": "percentage",
    "target_value": 0.6
  },
  "time_to_first_value": {
    "calculation": "time_to_first_positive_feedback",
    "display_format": "minutes",
    "target_value": 10
  }
}
```

## Analysis Customization

### Custom Analysis Methods

To implement custom analysis methods:

1. Add the method specification to the analysis configuration
2. Create an implementation script in the `/chrome_extension/testing/uat/scripts/` directory
3. Update the UAT management script to call the new analysis method

Example custom analysis method:

```json
"custom_analysis": {
  "platform_comparison": {
    "script": "analyze_platforms.py",
    "input": "all_feedback.csv",
    "output": "platform_comparison.md",
    "parameters": {
      "min_users_per_platform": 5,
      "metrics": ["success_rate", "satisfaction", "issues"]
    }
  }
}
```

### Custom Visualization

To add custom visualizations to reports:

1. Define the visualization in the reporting configuration
2. Create a script to generate the visualization
3. Update report templates to include the visualization

Example visualization configuration:

```json
"visualizations": {
  "platform_comparison_radar": {
    "script": "generate_radar_chart.py",
    "data_source": "platform_metrics.csv",
    "output_format": "png",
    "include_in_reports": ["final"]
  },
  "satisfaction_heatmap": {
    "script": "generate_heatmap.py",
    "data_source": "feature_satisfaction.csv",
    "output_format": "png",
    "include_in_reports": ["final", "executive"]
  }
}
```

## Integration with External Tools

### JIRA Integration

To integrate the UAT framework with JIRA for issue tracking:

1. Configure JIRA API credentials in the configuration file
2. Enable JIRA integration in the UAT management script
3. Define issue mapping for automated ticket creation

Example JIRA configuration:

```json
"jira_integration": {
  "enabled": true,
  "api_url": "https://your-organization.atlassian.net/rest/api/2/",
  "project_key": "CWC",
  "issue_types": {
    "bug": {
      "key": "Bug",
      "priority_mapping": {
        "high": "High",
        "medium": "Medium",
        "low": "Low"
      }
    },
    "improvement": {
      "key": "Improvement",
      "priority_mapping": {
        "high": "High",
        "medium": "Medium",
        "low": "Low"
      }
    }
  },
  "create_issues_automatically": true,
  "issue_template": "UAT Issue: {issue_title}\n\nDescription: {issue_description}\n\nSteps to Reproduce: {steps_to_reproduce}\n\nImpact: {impact}\n\nParticipant ID: {participant_id}"
}
```

### Analytics Integration

To integrate with analytics platforms:

1. Configure analytics API credentials
2. Define data export format and schedule
3. Specify metrics mapping for consistency

Example analytics configuration:

```json
"analytics_integration": {
  "platforms": {
    "google_analytics": {
      "enabled": true,
      "property_id": "UA-12345678-1",
      "metrics_mapping": {
        "page_views": "session_count",
        "events": "feature_usage",
        "conversions": "suggestion_acceptance"
      }
    },
    "mixpanel": {
      "enabled": false,
      "project_token": "",
      "metrics_mapping": {}
    }
  },
  "export_frequency": "daily",
  "include_in_analysis": true
}
```

## Best Practices for Configuration

1. **Maintain Version Control**: Keep all configuration files in version control
2. **Document Changes**: Add comments to configuration files explaining significant changes
3. **Test Before Deployment**: Test configuration changes in a development environment
4. **Use Environment-Specific Configs**: Create separate configurations for development, staging, and production
5. **Regular Backups**: Back up configuration files regularly
6. **Validate JSON**: Ensure all JSON configuration files are valid before deployment
7. **Consistent Naming**: Use consistent naming conventions across all configuration files
8. **Minimize Redundancy**: Avoid duplicating configuration settings across multiple files

## Troubleshooting

### Common Configuration Issues

1. **Invalid JSON Format**
   - Symptom: Script fails with JSON parsing error
   - Solution: Validate JSON syntax using a linter or validator

2. **Missing Required Fields**
   - Symptom: Script fails with "missing required field" error
   - Solution: Check configuration against the required fields list

3. **Path Resolution Issues**
   - Symptom: Script cannot find templates or output directories
   - Solution: Ensure all paths are absolute or properly relative to script location

4. **Permission Issues**
   - Symptom: Script cannot write to output directories
   - Solution: Check directory permissions and ownership

### Configuration Validation

To validate your UAT configuration:

```bash
# Run the validation script
cd /Volumes/Project Disk/Catalyst/chrome_extension
./manage_uat.sh validate-config

# Or validate a specific configuration file
./manage_uat.sh validate-config --file /path/to/config.json
```

## Contact and Support

For questions about UAT configuration, contact:

- **UAT Framework Administrator**: [Name, Email]
- **Technical Support**: [Name, Email]

---

*Last Updated: June 15, 2025*
