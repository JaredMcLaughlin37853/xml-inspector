# XML Inspector

A comprehensive quality assurance tool for XML files that validates configuration settings against standardized requirements. XML Inspector compares XML content with reference documents to identify compliance issues and generate detailed reports.

## Features

- ✅ **XML Validation**: Parse and validate XML files using XPath expressions
- 📋 **Settings Documents**: Support for JSON and YAML configuration files
- 🔍 **Type-Aware Validation**: Automatic conversion and validation of strings, numbers, and booleans
- 📊 **Rich Reporting**: Generate detailed reports in JSON and HTML formats
- 🎯 **Project-Specific Rules**: Merge standard and project-specific validation requirements
- 🐍 **Python Library**: Use programmatically in your Python applications
- 💻 **CLI Interface**: Easy-to-use command-line tool with colored output
- 🧪 **Comprehensive Testing**: Full test suite with 73% code coverage

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from Source

```bash
# Clone the repository
git clone <repository-url>
cd xml-inspector

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install the package in development mode
pip install -e .
```

## Quick Start

### 1. Basic XML Inspection

```bash
xml-inspector inspect \
  --xml examples/xml-files/device-config.xml \
  --standard examples/settings/standard-device-settings.json \
  --type device-config
```

### 2. Generate HTML Report

```bash
xml-inspector inspect \
  --xml examples/xml-files/device-config.xml \
  --standard examples/settings/standard-device-settings.json \
  --type device-config \
  --output report.html \
  --format html
```

### 3. Validate Settings Document

```bash
xml-inspector validate-settings \
  --file examples/settings/standard-device-settings.json
```

## Usage

### Command Line Interface

The `xml-inspector` CLI provides two main commands:

#### `inspect` - Validate XML files

```bash
xml-inspector inspect [OPTIONS]

Options:
  -x, --xml <files...>     XML files to inspect (multiple allowed)
  -s, --standard <file>    Standard settings document (JSON/YAML)
  -p, --project <file>     Project-specific settings document (optional)
  -t, --type <entityType>  Entity type for validation
  -o, --output <file>      Output file path for report
  -f, --format <format>    Output format: json|html (default: json)
  -v, --verbose            Enable verbose output
  --help                   Show help message
```

#### `validate-settings` - Validate settings documents

```bash
xml-inspector validate-settings [OPTIONS]

Options:
  -f, --file <file>    Settings document to validate
  --help               Show help message
```

### Python Library

Use XML Inspector programmatically in your Python applications:

```python
from xml_inspector import XmlInspector
from xml_inspector.core.inspector import InspectionOptions

# Create inspector instance
inspector = XmlInspector()

# Configure inspection
options = InspectionOptions(
    xml_files=["path/to/config.xml"],
    standard_settings_file="path/to/standard-settings.json",
    project_settings_file="path/to/project-settings.yaml",  # Optional
    entity_type="device-config",
    output_path="report.json",
    output_format="json"
)

# Perform inspection
report = inspector.inspect(options)

# Access results
print(f"Total checks: {report.summary.total_checks}")
print(f"Passed: {report.summary.passed}")
print(f"Failed: {report.summary.failed}")
print(f"Missing: {report.summary.missing}")
```

## Configuration

### Settings Document Structure

Settings documents define validation rules using JSON or YAML format:

```json
{
  "entityType": "device-config",
  "metadata": {
    "version": "1.0.0",
    "description": "Standard device configuration settings",
    "author": "IT Operations Team"
  },
  "settings": [
    {
      "name": "device-type",
      "xpath": "//device/@type",
      "expectedValue": "router",
      "description": "Device type classification",
      "type": "string",
      "required": true
    },
    {
      "name": "network-port",
      "xpath": "//network/port/text()",
      "expectedValue": 8080,
      "description": "Network port number",
      "type": "number",
      "required": true
    },
    {
      "name": "interface-enabled",
      "xpath": "//interface[@id='eth0']/enabled/text()",
      "expectedValue": true,
      "description": "Primary interface must be enabled",
      "type": "boolean",
      "required": true
    }
  ]
}
```

### Setting Properties

- **name**: Unique identifier for the setting
- **xpath**: XPath expression to locate the value in XML
- **expectedValue**: Expected value (optional - if omitted, only checks presence)
- **description**: Human-readable description
- **type**: Data type (`string`, `number`, `boolean`)
- **required**: Whether the setting must be present (default: `true`)

### XPath Examples

- `//element/text()` - Get text content of an element
- `//element/@attribute` - Get attribute value
- `//parent/child[@id='value']/text()` - Get text from element with specific attribute
- `//element[1]/text()` - Get text from first element
- `//element[contains(@class, 'value')]` - Partial attribute matching

## Examples

The `examples/` directory contains:

- **XML Files**: Sample device configuration files
- **Settings Documents**: JSON and YAML validation rules
- **Usage Examples**: Demonstrations of various features

See [examples/README.md](examples/README.md) for detailed usage examples.

## Development

### Setup Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks (optional)
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=xml_inspector

# Run specific test file
pytest tests/core/test_xml_parser.py
```

### Code Quality

```bash
# Format code
black xml_inspector tests

# Check code style
flake8 xml_inspector tests

# Type checking
mypy xml_inspector
```

### Project Structure

```
xml-inspector/
├── xml_inspector/          # Main Python package
│   ├── core/              # Core functionality (parsing, inspection)
│   ├── parsers/           # Settings document parsers
│   ├── validators/        # XML validation logic
│   ├── reporters/         # Report generation
│   ├── types/             # Type definitions
│   └── cli.py             # Command-line interface
├── tests/                 # Test suite
├── examples/              # Example files and documentation
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── setup.py              # Package configuration
└── pyproject.toml        # Build system configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests and ensure they pass: `pytest`
5. Format code: `black xml_inspector tests`
6. Commit your changes: `git commit -m "Add feature"`
7. Push to the branch: `git push origin feature-name`
8. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Dependencies

### Runtime Dependencies

- **lxml**: XML parsing and XPath evaluation
- **PyYAML**: YAML document parsing
- **click**: Command-line interface framework
- **colorama**: Cross-platform colored terminal output
- **jinja2**: Template engine for HTML reports

### Development Dependencies

- **pytest**: Testing framework
- **pytest-cov**: Test coverage reporting
- **black**: Code formatting
- **flake8**: Code linting
- **mypy**: Static type checking

## Support

For questions, issues, or contributions:

1. Check the [examples](examples/) for usage guidance
2. Review existing [issues](../../issues) 
3. Create a new issue with detailed information
4. Consider contributing improvements via pull requests

---

Built with ❤️ using Python and modern development practices.