# XML Inspector DSL Examples

This directory contains example files demonstrating how to use the XML Inspector tool with DSL (Domain Specific Language) validation.

## Files Overview

### XML Files
- `xml-files/device-config.xml` - Sample device configuration XML file representing a network router
- `xml-files/sample-d20me.xml` - Sample D20ME XML file for complex validation scenarios
- `xml-files/FLANDERH.xml` - Another sample XML file for testing
- `xml-files/sample-d20me-xpath-discovery.xml` - XML for XPath discovery examples

### DSL Documents
- `settings/d20me-settings.json` - DSL validation document with complex node validation rules
- `dsl-example.json` - Simple DSL validation example

## Installation

First, install the Python package:

```bash
# Install in development mode
pip install -e .

# Or install from requirements
pip install -r requirements.txt
```

## Usage Examples

### Basic DSL Inspection
Inspect XML files using DSL validation rules:

```bash
xml-inspector inspect \
  --xml examples/xml-files/sample-d20me.xml \
  --dsl examples/settings/d20me-settings.json
```

### Multiple XML Files with HTML Output
Inspect multiple XML files and generate HTML report:

```bash
xml-inspector inspect \
  --xml examples/xml-files/sample-d20me.xml \
  --xml examples/xml-files/device-config.xml \
  --dsl examples/settings/d20me-settings.json \
  --output report.html \
  --format html
```

### Validate DSL Document
Verify that a DSL validation document is properly formatted:

```bash
xml-inspector validate-settings \
  --file examples/settings/d20me-settings.json
```

### Using as Python Library

You can also use XML Inspector as a Python library:

```python
from xml_inspector import XmlInspector, InspectionOptions

inspector = XmlInspector()

options = InspectionOptions(
    xml_files=["examples/xml-files/sample-d20me.xml"],
    dsl_settings_file="examples/settings/d20me-settings.json",
    output_path="report.json",
    output_format="json"
)

report = inspector.inspect(options)
print(f"Total checks: {report.summary.total_checks}")
print(f"Passed: {report.summary.passed}")
print(f"Failed: {report.summary.failed}")
```

## DSL Features Demonstrated

### Node Validation
The example DSL documents demonstrate:
- **Per-node validation**: Validate each node individually with detailed results
- **Complex mapping**: Map between related XML nodes using dynamic XPath construction
- **Aggregation**: Sum, count, and other operations across multiple nodes
- **Conditional logic**: Complex expressions with calculations and comparisons

### Expression Types
- **existence**: Check if expressions evaluate to truthy values
- **pattern**: Match expression results against regular expressions
- **range**: Validate expression results fall within specified bounds
- **comparison**: Compare expression results with fixed values
- **computedComparison**: Compare two expressions or use between operations
- **nodeValidation**: Validate multiple nodes individually with per-node PASS/FAIL results

## Development

### Running Tests
```bash
pytest
```

### Code Formatting
```bash
black xml_inspector tests
```

### Type Checking
```bash
mypy xml_inspector
```

## Expected Results

When running the DSL examples, you should see:
- **Rule-based validation**: Each DSL rule will be evaluated independently
- **Per-node results**: For nodeValidation rules, you'll get individual results for each node
- **Complex calculations**: The tool will evaluate sophisticated expressions and aggregations
- **Detailed reporting**: Comprehensive reports showing which rules passed/failed and why

The generated report will provide detailed validation results for each DSL rule, making it easy to identify XML structure issues or data inconsistencies.