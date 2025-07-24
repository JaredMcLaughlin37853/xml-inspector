# XML Inspector

A comprehensive quality assurance tool for XML files that validates configuration settings against standardized requirements. XML Inspector compares XML content with reference documents to identify compliance issues and generate detailed reports.

## Features

- ✅ **XML Validation**: Parse and validate XML files using XPath expressions
- 🚀 **DSL (Domain Specific Language)**: Powerful expression-based validation with dynamic XPath, map operations, and complex computations
- 🔍 **Type-Aware Validation**: Automatic conversion and validation of strings, numbers, booleans, and dates
- 📊 **Rich Reporting**: Generate detailed reports in JSON and HTML formats
- 🎯 **Project-Specific Rules**: Merge standard and project-specific validation requirements
- 🧮 **Advanced Operations**: Count, sum, average, arithmetic, logical operations, and iterative processing
- 🐍 **Python Library**: Use programmatically in your Python applications
- 💻 **CLI Interface**: Easy-to-use command-line tool with colored output
- 🧪 **Comprehensive Testing**: Full test suite with extensive DSL validation coverage

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
  --standard examples/dsl-example.json
```

### 2. Generate HTML Report

```bash
xml-inspector inspect \
  --xml examples/test-data.xml \
  --standard examples/dsl-example.json \
  --output report.html \
  --format html
```

### 3. Validate Settings Document

```bash
xml-inspector validate-settings \
  --file examples/dsl-example.json
```

## Usage

### Command Line Interface

The `xml-inspector` CLI provides two main commands:

#### `inspect` - Validate XML files

```bash
xml-inspector inspect [OPTIONS]

Options:
  -x, --xml <files...>     XML files to inspect (multiple allowed)
  -s, --standard <file>    Standard DSL validation document (JSON/YAML)
  -p, --project <file>     Project-specific DSL validation document (optional)
  -t, --type <entityType>  Entity type for validation (optional)
  -o, --output <file>      Output file path for report
  -f, --format <format>    Output format: json|html (default: json)
  -v, --verbose            Enable verbose output
  --help                   Show help message
```

#### `validate-settings` - Validate settings documents

```bash
xml-inspector validate-settings [OPTIONS]

Options:
  -f, --file <file>    DSL validation document to validate
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
    standard_settings_file="path/to/dsl-validation.json",
    project_settings_file="path/to/project-validation.yaml",  # Optional
    entity_type="",  # Optional for DSL
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

### DSL Validation Document Structure

XML Inspector uses a powerful DSL format for defining validation rules with advanced operations:

```json
{
  "validationSettings": [
    {
      "id": "count_items",
      "description": "Count total number of items",
      "type": "existence",
      "severity": "error",
      "expression": {
        "op": "count",
        "xpath": "//Item"
      }
    },
    {
      "id": "sum_prices",
      "description": "Sum all item prices should be greater than 100",
      "type": "comparison", 
      "severity": "warning",
      "expression": {
        "op": "sum",
        "xpath": "//Item/@price",
        "dataType": "decimal"
      },
      "operator": ">",
      "value": 100
    },
    {
      "id": "map_calculation",
      "description": "Calculate total value using map (quantity * price)",
      "type": "computedComparison",
      "severity": "error",
      "comparison": {
        "operator": ">",
        "leftExpression": {
          "op": "sum",
          "args": [
            {
              "op": "map",
              "xpath": "//Item",
              "expression": {
                "op": "multiply",
                "args": [
                  { "op": "value", "xpath": "@quantity", "dataType": "decimal" },
                  { "op": "value", "xpath": "@price", "dataType": "decimal" }
                ]
              }
            }
          ]
        },
        "rightExpression": {
          "op": "literal",
          "value": 500
        }
      }
    }
  ]
}
```

#### DSL Validation Rule Types

- **existence**: Check if expression result exists/is truthy
- **pattern**: Match expression result against regex pattern  
- **range**: Validate expression result is within min/max range
- **comparison**: Compare expression result with fixed value
- **computedComparison**: Compare two expressions or use between operator

#### DSL Expression Operations

- **Basic**: `count`, `sum`, `average`, `value`, `literal`
- **Arithmetic**: `add`, `subtract`, `multiply`, `divide`
- **Logic**: `if`, `and`, `or`, `not`
- **Comparison**: `==`, `!=`, `>`, `<`, `>=`, `<=`
- **String**: `concat`
- **Advanced**: `map` (iterate over nodes and apply expression per node)

#### DSL Features

- **Dynamic XPath**: Use `xpathExpression` instead of `xpath` to compute XPath strings dynamically
- **Conditional Rules**: Add `conditions` array to control when rules apply
- **Type Conversion**: Automatic handling of `string`, `integer`, `decimal`, `date` types
- **Nested Expressions**: Build complex validation logic with recursive expression trees

### XPath Examples

- `//element/text()` - Get text content of an element
- `//element/@attribute` - Get attribute value
- `//parent/child[@id='value']/text()` - Get text from element with specific attribute
- `//element[1]/text()` - Get text from first element
- `//element[contains(@class, 'value')]` - Partial attribute matching

## Examples

The `examples/` directory contains:

- **XML Files**: Sample XML data for testing and demonstration
- **DSL Documents**: JSON and YAML validation rules with advanced expressions
- **Usage Examples**: Demonstrations of various DSL features

### Key Example Files

- `examples/dsl-example.json` - DSL validation rules with count, sum, and map operations
- `examples/test-data.xml` - Sample XML data for testing DSL functionality

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
│   ├── core/              # Core functionality (parsing, inspection, DSL evaluation)
│   │   ├── dsl_evaluator.py    # DSL expression evaluator
│   │   ├── inspector.py        # Main inspection engine
│   │   └── xml_parser.py       # XML parsing utilities
│   ├── parsers/           # Document parsers
│   │   ├── dsl_parser.py       # DSL format parser
│   │   └── settings_parser.py  # Settings document parser with auto-detection
│   ├── validators/        # XML validation logic
│   │   ├── dsl_validator.py    # DSL-based validation
│   │   └── xml_validator.py    # XML validation utilities
│   ├── reporters/         # Report generation
│   ├── types/             # Type definitions for DSL and validation
│   └── cli.py             # Command-line interface
├── tests/                 # Test suite
├── examples/              # Example files and documentation
├── spec/                  # DSL specification and JSON schema
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