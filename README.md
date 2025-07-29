# XML Inspector

A comprehensive quality assurance tool for XML files that validates configuration settings using Python-based validation functions. XML Inspector provides a flexible framework for executing custom Python validation logic against XML content to identify compliance issues and generate detailed reports.

## ✨ Features

- 🐍 **Python-Based Validation**: Write custom validation logic in Python functions with full access to lxml and XPath
- 🔧 **Custom Function Registration**: Register validation functions via configuration files with auto-discovery
- 📊 **Rich Reporting**: Generate detailed reports in JSON and HTML formats with comprehensive validation results
- 💻 **Enhanced CLI**: Command-line interface with custom function support and verbose loading options
- 🎯 **Flexible Configuration**: JSON-based settings with support for multiple validation rules
- 🔍 **Advanced XML Processing**: Complex validation scenarios using XPath, node mapping, and conditional logic
- 🐍 **Python Library**: Use programmatically in your Python applications with full API access
- 🧪 **Type Safety**: Built with Python dataclasses and comprehensive type annotations
- 📁 **Auto-Discovery**: Automatic discovery of configuration files in standard locations

## 🚀 Installation

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

## 🏃 Quick Start

### 1. Basic XML Inspection

```bash
xml-inspector inspect -x data.xml -s validation-settings.json
```

### 2. With Custom Validation Functions

```bash
# Auto-discovers xml-inspector.config.json
xml-inspector inspect -x data.xml -s validation-settings.json --verbose-loading

# Explicit configuration file
xml-inspector inspect -x data.xml -s validation-settings.json -c my-config.json
```

### 3. Generate HTML Report

```bash
xml-inspector inspect -x data.xml -s validation-settings.json -o report.html -f html
```

### 4. Validate Settings Document

```bash
xml-inspector validate-settings -f validation-settings.json
```

## 📖 Usage

### Command Line Interface

#### `inspect` - Validate XML files with custom function support

```bash
xml-inspector inspect [OPTIONS]

Options:
  -x, --xml TEXT               XML files to inspect (can be specified multiple times) [required]
  -s, --settings TEXT          Validation settings document (JSON format) [required]
  -o, --output TEXT            Output file path for the report
  -f, --format [json|html]     Output format for the report (default: json)
  -c, --functions-config TEXT  Configuration file for custom validation functions
  --verbose-loading            Show detailed function loading information
  -v, --verbose                Enable verbose output
  --help                       Show help message
```

#### `validate-settings` - Validate settings documents

```bash
xml-inspector validate-settings [OPTIONS]

Options:
  -f, --file TEXT              Validation settings document to validate (JSON format) [required]
  -c, --functions-config TEXT  Configuration file for custom validation functions
  --help                       Show help message
```

### Python Library

Use XML Inspector programmatically in your Python applications:

```python
from xml_inspector import XmlInspector
from xml_inspector.core.inspector import InspectionOptions

# Create inspector instance
inspector = XmlInspector()

# Register custom validation functions (optional)
validator = inspector.get_validator()
validator.register_function(
    rule_id="my_custom_rule",
    description="My custom validation logic",
    validation_function=my_validation_function,
    severity="error"
)

# Configure inspection
options = InspectionOptions(
    xml_files=["path/to/config.xml"],
    settings_file="path/to/validation-settings.json",
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

## ⚙️ Configuration

### Custom Function Registration

XML Inspector automatically discovers and loads custom validation functions from configuration files.

#### Configuration File Locations (searched in order):
1. `./xml-inspector.config.json` (project root)
2. `~/.xml-inspector/config.json` (user config)
3. `~/.config/xml-inspector/config.json` (XDG config)

#### Configuration File Format

```json
{
  "validation_functions": [
    {
      "id": "analog_input_16_validation",
      "module": "examples.validation-functions.my_validator",
      "function": "validate_analog_input_16_points",
      "description": "Validates Analog Input 16 point counts between DCA Configuration and DCA Configuration List",
      "severity": "error"
    },
    {
      "id": "custom_range_check",
      "module": "/absolute/path/to/validators.py",
      "function": "check_value_ranges",
      "description": "Validates that numeric values fall within expected ranges",
      "severity": "warning"
    }
  ],
  "function_paths": [
    "examples/validation-functions",
    "custom/validation/modules"
  ]
}
```

#### Configuration Options

- **`validation_functions`**: Array of custom validation function definitions
  - **`id`**: Unique identifier for the validation rule
  - **`module`**: Python module path (dotted notation or file path)
  - **`function`**: Name of the validation function within the module
  - **`description`**: Human-readable description of the validation
  - **`severity`**: Severity level (`error`, `warning`, `info`)

- **`function_paths`**: Additional paths to add to Python module search path

### Validation Settings Document

The validation settings document specifies which validation rules to execute:

```json
{
  "validationRules": [
    "analog_input_16_validation",
    "custom_range_check",
    "validate_required_elements"
  ]
}
```

### Writing Custom Validation Functions

Create Python functions that take an `XmlFile` and return any custom format you prefer:

```python
from xml_inspector.types import XmlFile
from typing import Dict, Any

def my_validation_function(xml_file: XmlFile) -> Dict[str, Any]:
    """
    Custom validation function with flexible result format.
    
    Args:
        xml_file: XmlFile object containing parsed XML content
        
    Returns:
        Custom result format - you have complete control over the structure
    """
    # Access the parsed XML content
    xml_root = xml_file.content
    
    # Perform validation using XPath, Python logic, etc.
    elements = xml_root.xpath("//important/element")
    
    # Return whatever format makes sense for your validation
    if len(elements) == 0:
        return {
            "status": "fail",  # Required for report generation
            "validation_type": "element_presence_check",
            "found_elements": len(elements),
            "required_elements": 1,
            "missing_elements": ["important/element"],
            "message": "Required element 'important/element' not found",
            "details": {
                "xpath_used": "//important/element",
                "search_performed_at": "2024-01-15T10:30:00Z"
            }
        }
    
    return {
        "status": "pass",  # Required for report generation
        "validation_type": "element_presence_check", 
        "found_elements": len(elements),
        "elements_found": [elem.tag for elem in elements],
        "message": "All required elements found",
        "performance_stats": {
            "xpath_execution_time": "0.002s",
            "elements_processed": len(elements)
        }
    }
```

#### Alternative Simple Format

You can also return simple dictionary formats for straightforward validations:

```python
from xml_inspector.types import XmlFile

def simple_validation_function(xml_file: XmlFile) -> dict:
    """Simple validation with basic dictionary format."""
    xml_root = xml_file.content
    elements = xml_root.xpath("//important/element")
    
    if len(elements) == 0:
        return {
            "status": "fail",
            "found_count": len(elements),
            "expected_count": 1,
            "message": "Required element not found"
        }
    
    return {
        "status": "pass",
        "found_count": len(elements),
        "expected_count": 1,
        "message": "Validation passed"
    }
```

#### Validation Function Requirements

- **Function signature**: `(xml_file: XmlFile) -> Any` (return any format you want)
- **Access XML content**: via `xml_file.content` (lxml.etree._Element)
- **Status field**: Include a `status` field in your result for report generation
- **Status values**: `"pass"`, `"fail"`, or `"missing"`
- **Complete control**: Design your result format to best represent your validation data

## 📁 Example: DNP DCA Point Validation

Here's a real-world example of validating DNP3 DCA configurations:

### XML Structure
```xml
<CCE:Device>
  <!-- DCA Configuration -->
  <B023_CFG>
    <Record DCA_x0020_Index="3" 
            First_x0020_Device_x0020_Entry="0" 
            Number_x0020_Of_x0020_Devices="3"/>
  </B023_CFG>
  
  <!-- Device Configuration -->
  <B023_DEV>
    <Record First_x0020_Point_x0020_Record="0" 
            Number_x0020_of_x0020_Point_x0020_Records="1"/>
  </B023_DEV>
  
  <!-- Device Point Map -->
  <B023_PNT>
    <Record DCA_x0020_Object_x0020_Type="Analog Input 16" 
            Number_x0020_Of_x0020_Device_x0020_Points="5"/>
  </B023_PNT>
  
  <!-- DCA Configuration List -->
  <B008_DCA>
    <Record NumAI="10" NumDI="24" NumDO="18"/>
  </B008_DCA>
</CCE:Device>
```

### Configuration File
```json
{
  "validation_functions": [
    {
      "id": "dnp_analog_input_16_validation",
      "module": "examples.validation-functions.dnp_validator",
      "function": "validate_analog_input_16_points",
      "description": "Validates Analog Input 16 point counts with adjustment rules",
      "severity": "error"
    }
  ],
  "function_paths": ["examples/validation-functions"]
}
```

### Validation Settings
```json
{
  "validationRules": [
    "dnp_analog_input_16_validation"
  ]
}
```

### Usage
```bash
xml-inspector inspect -x device-config.xml -s dnp-validation.json --verbose-loading
```

## 📊 Report Formats

### JSON Report
```json
{
  "summary": {
    "total_checks": 1,
    "passed": 0,
    "failed": 1,
    "missing": 0
  },
  "results": [
    {
      "rule_id": "dnp_analog_input_16_validation",
      "rule_description": "Validates Analog Input 16 point counts",
      "result": {
        "status": "fail",
        "returned_value": {"type": "count", "value": 10},
        "expected_value": {"type": "count", "value": 15},
        "message": "Point count mismatch: calculated 10, expected 15"
      },
      "file_path": "device-config.xml",
      "severity": "error"
    }
  ],
  "metadata": {
    "timestamp": "2024-01-15T10:30:00Z",
    "xml_files": ["device-config.xml"],
    "validation_rules": ["dnp_analog_input_16_validation"]
  }
}
```

### HTML Report
Rich, interactive HTML reports with:
- Executive summary with pass/fail statistics
- Detailed validation results with syntax highlighting
- Expandable error details and recommendations
- Print-friendly formatting

## 🛠️ Development

### Project Structure
```
xml-inspector/
├── xml_inspector/           # Main Python package
│   ├── config/             # Configuration and function loading
│   │   ├── __init__.py
│   │   └── function_loader.py
│   ├── core/               # Core functionality
│   │   ├── inspector.py    # Main inspection engine
│   │   └── xml_parser.py   # XML parsing utilities
│   ├── parsers/            # Settings document parsers
│   ├── validators/         # Validation logic
│   ├── reporters/          # Report generation
│   ├── types/              # Type definitions
│   └── cli.py              # Command-line interface
├── examples/               # Example files and validation functions
├── tests/                  # Test suite
└── requirements.txt        # Dependencies
```

### Running Tests
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run test suite
pytest

# Run with coverage
pytest --cov=xml_inspector

# Code formatting
black xml_inspector tests

# Type checking
mypy xml_inspector

# Linting
flake8 xml_inspector tests
```

### Creating New Validation Functions

1. **Write the validation function**:
   ```python
   def my_validation(xml_file: XmlFile) -> Result:
       # Your validation logic here
       pass
   ```

2. **Create configuration file**:
   ```json
   {
     "validation_functions": [
       {
         "id": "my_validation",
         "module": "path.to.module",
         "function": "my_validation",
         "description": "My custom validation",
         "severity": "error"
       }
     ]
   }
   ```

3. **Test your function**:
   ```bash
   xml-inspector inspect -x test.xml -s settings.json --verbose-loading
   ```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- [lxml](https://lxml.de/) - XML processing library
- [click](https://click.palletsprojects.com/) - Command line interface creation
- [jinja2](https://jinja.palletsprojects.com/) - Template engine for reports

## 📞 Support

If you encounter any issues or have questions:

1. Check the existing issues on GitHub
2. Create a new issue with detailed information
3. Include sample XML files and configuration when possible

---

**XML Inspector** - Comprehensive XML validation with Python flexibility 🐍✨