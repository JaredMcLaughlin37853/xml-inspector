# XML Inspector

A comprehensive quality assurance tool for XML files that validates configuration settings using Python-based validation functions. XML Inspector executes custom Python validation logic against XML content to identify compliance issues and generate detailed reports.

## Features

- ✅ **XML Validation**: Parse and validate XML files using XPath expressions
- 🐍 **Python-Based Validation**: Write custom validation logic in Python functions for maximum flexibility
- 🔧 **Built-in DNP Rules**: Pre-built validation rules for DNP3 protocol configurations
- 📊 **Rich Reporting**: Generate detailed reports in JSON and HTML formats
- 🎯 **Modular Rule System**: Register and manage validation rules with unique identifiers
- 🔍 **Advanced Logic**: Implement complex validation scenarios with full Python capabilities
- 🐍 **Python Library**: Use programmatically in your Python applications
- 💻 **CLI Interface**: Easy-to-use command-line tool with colored output
- 🧪 **Comprehensive Testing**: Full test suite with extensive validation coverage

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
  --xml examples/test-data.xml \
  --settings examples/validation-rules.json
```

### 2. Generate HTML Report

```bash
xml-inspector inspect \
  --xml examples/test-data.xml \
  --settings examples/validation-rules.json \
  --output report.html \
  --format html
```

### 3. Validate Settings Document

```bash
xml-inspector validate-settings \
  --file examples/validation-rules.json
```

## Usage

### Command Line Interface

The `xml-inspector` CLI provides two main commands:

#### `inspect` - Validate XML files

```bash
xml-inspector inspect [OPTIONS]

Options:
  -x, --xml <files...>     XML files to inspect (multiple allowed)
  -s, --settings <file>    Validation settings document (JSON format)
  -o, --output <file>      Output file path for report
  -f, --format <format>    Output format: json|html (default: json)
  -v, --verbose            Enable verbose output
  --help                   Show help message
```

#### `validate-settings` - Validate settings documents

```bash
xml-inspector validate-settings [OPTIONS]

Options:
  -f, --file <file>    Validation settings document to validate (JSON format)
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
    settings_file="path/to/validation-rules.json",
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

### Validation Settings Document Structure

XML Inspector uses a simple JSON format that references Python validation functions:

```json
{
  "validationRules": [
    "validate_required_elements",
    "validate_numeric_ranges",
    "custom_validation_rule"
  ]
}
```

### Writing Custom Python Validation Functions

Create Python functions that take an `XmlFile` and return a `Result`:

```python
from xml_inspector.types import XmlFile, Result, Value

def validate_custom_rule(xml_file: XmlFile) -> Result:
    """Custom validation logic."""
    try:
        root = xml_file.content
        
        # Your validation logic using XPath, calculations, etc.
        items = root.xpath("//Item")
        
        if len(items) > 0:
            return Result(
                status="pass",
                returned_value=Value(type="count", value=len(items)),
                expected_value=Value(type="string", value="Items should exist"),
                message=f"Found {len(items)} items"
            )
        else:
            return Result(
                status="fail",
                returned_value=Value(type="count", value=0),
                expected_value=Value(type="string", value="Items should exist"),
                message="No items found"
            )
            
    except Exception as e:
        return Result(
            status="fail",
            returned_value=None,
            expected_value=None,
            message=f"Validation error: {e}"
        )

# Register the function
validator.register_function(
    rule_id="custom_validation_rule",
    description="Check that items exist in XML",
    validation_function=validate_custom_rule,
    severity="error"
)
```

### Custom Validation Rules

XML Inspector uses a pure Python-based validation system where all validation logic is implemented as custom Python functions. There are no built-in validation rules - users implement their own validation functions tailored to their specific XML validation needs.

### Creating and Using Custom Validation Functions

#### Step 1: Write Your Custom Validation Function

Create a Python file with your validation logic:

```python
# custom_validators.py
from xml_inspector.types import XmlFile, Result, Value

def validate_required_attributes(xml_file: XmlFile) -> Result:
    """Check that all Device elements have required attributes."""
    try:
        root = xml_file.content
        devices = root.xpath("//Device")
        
        required_attrs = ["id", "name", "type"]
        missing_attrs = []
        
        for i, device in enumerate(devices):
            for attr in required_attrs:
                if not device.get(attr):
                    missing_attrs.append(f"Device {i}: missing '{attr}' attribute")
        
        if missing_attrs:
            return Result(
                status="fail",
                returned_value=Value(type="list", value=missing_attrs),
                expected_value=Value(type="string", value="All required attributes present"),
                message=f"Found {len(missing_attrs)} missing attributes"
            )
        else:
            return Result(
                status="pass",
                returned_value=Value(type="string", value="All attributes present"),
                expected_value=Value(type="string", value="All required attributes present"),
                message="All devices have required attributes"
            )
            
    except Exception as e:
        return Result(
            status="fail",
            returned_value=None,
            expected_value=None,
            message=f"Validation error: {e}"
        )

def validate_numeric_ranges(xml_file: XmlFile) -> Result:
    """Check that Port values are within valid range (1-65535)."""
    try:
        root = xml_file.content
        ports = root.xpath("//Port/text()")
        invalid_ports = []
        
        for port_text in ports:
            try:
                port = int(port_text)
                if port < 1 or port > 65535:
                    invalid_ports.append(f"Port {port} out of range")
            except ValueError:
                invalid_ports.append(f"Invalid port value: {port_text}")
        
        if invalid_ports:
            return Result(
                status="fail",
                returned_value=Value(type="list", value=invalid_ports),
                expected_value=Value(type="string", value="All ports in range 1-65535"),
                message=f"Found {len(invalid_ports)} invalid ports"
            )
        else:
            return Result(
                status="pass",
                returned_value=Value(type="string", value="All ports valid"),
                expected_value=Value(type="string", value="All ports in range 1-65535"),
                message="All port values are valid"
            )
            
    except Exception as e:
        return Result(
            status="fail",
            returned_value=None,
            expected_value=None,
            message=f"Validation error: {e}"
        )
```

#### Step 2: Create Your Settings JSON

Reference your custom rules by ID:

```json
{
  "validationRules": [
    "validate_required_attributes",
    "validate_numeric_ranges"
  ]
}
```

#### Step 3: Register and Use Your Custom Functions

```python
from xml_inspector import XmlInspector
from xml_inspector.core.inspector import InspectionOptions
from custom_validators import validate_required_attributes, validate_numeric_ranges

# Create inspector and get validator
inspector = XmlInspector()
validator = inspector.get_validator()

# Register your custom rules
validator.register_function(
    rule_id="validate_required_attributes",
    description="Check that all Device elements have required attributes",
    validation_function=validate_required_attributes,
    severity="error"
)

validator.register_function(
    rule_id="validate_numeric_ranges", 
    description="Check that Port values are within valid range",
    validation_function=validate_numeric_ranges,
    severity="warning"
)

# Run inspection with custom rules
options = InspectionOptions(
    xml_files=["config.xml"],
    settings_file="custom-validation.json",
    output_path="report.html",
    output_format="html"
)

report = inspector.inspect(options)
print(f"Validation completed: {report.summary.passed}/{report.summary.total_checks} passed")
```

#### Step 4: Complete CLI Usage Example

Since validation rules must be registered before the CLI can use them, you need to create a registration script:

**Create `register_and_run.py`:**
```python
#!/usr/bin/env python3
"""Register custom rules and run CLI inspection."""

from xml_inspector import XmlInspector
from xml_inspector.core.inspector import InspectionOptions
from custom_validators import validate_required_attributes, validate_numeric_ranges

def register_rules_and_inspect():
    """Register rules and run inspection."""
    # Create inspector and register rules
    inspector = XmlInspector()
    validator = inspector.get_validator()
    
    validator.register_function(
        rule_id="validate_required_attributes",
        description="Check required attributes",
        validation_function=validate_required_attributes,
        severity="error"
    )
    
    validator.register_function(
        rule_id="validate_numeric_ranges",
        description="Check numeric ranges", 
        validation_function=validate_numeric_ranges,
        severity="warning"
    )
    
    # Run inspection
    options = InspectionOptions(
        xml_files=["config.xml"],
        settings_file="custom-validation.json",
        output_path="report.html",
        output_format="html"
    )
    
    report = inspector.inspect(options)
    print(f"Validation completed: {report.summary.passed}/{report.summary.total_checks} passed")

if __name__ == "__main__":
    register_rules_and_inspect()
```

**Run the complete workflow:**
```bash
# Run the registration and inspection script
python register_and_run.py
```

**Alternative: Use pure CLI after registering rules in a separate script**
```bash
# Step 1: Create and run a registration script (one-time setup)
python setup_rules.py  # Contains only validator.register_function() calls

# Step 2: Use CLI commands directly
xml-inspector inspect -x config.xml -s custom-validation.json -o report.html -f html
xml-inspector validate-settings -f custom-validation.json
```

**Note**: The CLI can only use rules that have been registered in the current Python session. For persistent rule registration, consider creating a package with your custom rules that can be imported and registered automatically.

#### Validation Function Guidelines

- **Function Signature**: Must take `XmlFile` parameter and return `Result`
- **Exception Handling**: Always wrap logic in try/catch and return appropriate `Result`
- **Return Values**: Use `Value` objects to wrap returned data with type information
- **Status Values**: Return "pass", "fail", or "missing" status
- **Messages**: Provide clear, descriptive messages for both success and failure cases

### XPath Examples

- `//element/text()` - Get text content of an element
- `//element/@attribute` - Get attribute value
- `//parent/child[@id='value']/text()` - Get text from element with specific attribute
- `//element[1]/text()` - Get text from first element
- `//element[contains(@class, 'value')]` - Partial attribute matching

## Examples

The `examples/` directory contains:

- **XML Files**: Sample XML data for testing and demonstration
- **Validation Settings**: JSON files referencing Python validation rules
- **Usage Examples**: Demonstrations of various validation scenarios

### Key Example Files

- `examples/validation-rules.json` - Sample validation settings with rule references
- `examples/test-data.xml` - Sample XML data for testing validation functions

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
│   │   ├── inspector.py        # Main inspection engine
│   │   └── xml_parser.py       # XML parsing utilities
│   ├── parsers/           # Document parsers
│   │   └── python_settings_parser.py  # Settings document parser
│   ├── validators/        # XML validation logic
│   │   └── python_validator.py    # Python-based validation
│   ├── validation_rules/  # Built-in validation rules
│   │   ├── dnp_validation.py   # DNP protocol validation rules
│   │   └── __init__.py         # Rule registration
│   ├── reporters/         # Report generation
│   ├── types/             # Type definitions for validation
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