# Catalyst Whisper Coach - UAT Configuration

This directory contains configuration files for the User Acceptance Testing (UAT) framework.

## Configuration Files

### 1. uat_config.json

Contains core settings for the UAT process including:

- Testing phases and schedules
- Participant requirements
- Platform testing priorities
- Success criteria thresholds
- Reporting requirements

### 2. template_config.json

Defines settings for UAT templates including:

- Template branding and styling
- Required and optional fields
- Rating scales and formats
- Default text and instructions

### 3. analysis_config.json

Specifies parameters for data processing and analysis:

- Quantitative analysis methods
- Qualitative coding framework
- Prioritization criteria
- Reporting thresholds

## Usage

These configuration files are used by the UAT management script and analysis tools. To modify UAT behavior, edit these files rather than changing the scripts directly.

## Best Practices

1. **Back up configurations** before making significant changes
2. **Validate JSON** after editing to ensure proper syntax
3. **Document changes** in commit messages or comments
4. **Test changes** in a development environment before using in production

## Customization

For detailed information on customizing these configurations, refer to the [CONFIGURATION_GUIDE.md](/Volumes/Project Disk/Catalyst/chrome_extension/testing/uat/CONFIGURATION_GUIDE.md) document.

## Dependencies

The UAT framework scripts and tools rely on these configuration files having the correct structure. Do not remove required fields or change the overall structure without updating the corresponding scripts.

---

*Last Updated: June 15, 2025*
