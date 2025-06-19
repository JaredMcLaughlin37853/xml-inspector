# XML Inspector Examples

This directory contains example files demonstrating how to use the XML Inspector tool.

## Files Overview

### XML Files
- `xml-files/device-config.xml` - Sample device configuration XML file representing a network router

### Settings Documents
- `settings/standard-device-settings.json` - Standard settings that apply to all devices
- `settings/project-specific-settings.yaml` - Additional settings specific to a particular project

## Usage Examples

### Basic Inspection
Inspect a single XML file against standard settings:

```bash
xml-inspector inspect \
  --xml examples/xml-files/device-config.xml \
  --standard examples/settings/standard-device-settings.json \
  --type device-config
```

### Inspection with Project-Specific Settings
Include both standard and project-specific settings:

```bash
xml-inspector inspect \
  --xml examples/xml-files/device-config.xml \
  --standard examples/settings/standard-device-settings.json \
  --project examples/settings/project-specific-settings.yaml \
  --type device-config \
  --output report.json
```

### Generate HTML Report
Create an HTML report for easier viewing:

```bash
xml-inspector inspect \
  --xml examples/xml-files/device-config.xml \
  --standard examples/settings/standard-device-settings.json \
  --project examples/settings/project-specific-settings.yaml \
  --type device-config \
  --output report.html \
  --format html
```

### Validate Settings Document
Verify that a settings document is properly formatted:

```bash
xml-inspector validate-settings \
  --file examples/settings/standard-device-settings.json
```

## Expected Results

When running the example with both standard and project-specific settings, you should see:
- **Passed checks**: Most settings should pass as the example XML is designed to be compliant
- **Any failures**: Will be clearly identified in the report with expected vs actual values
- **Missing settings**: If any required settings are not found in the XML

The generated report will provide a comprehensive overview of all validation results, making it easy to identify configuration issues or compliance gaps.