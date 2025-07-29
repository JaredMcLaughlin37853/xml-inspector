# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

xml-inspector is a quality assurance tool for XML files that validates configuration settings using Python-based validation functions for complex XML inspection scenarios.

**Language**: Python 3.8+
**Architecture**: Object-oriented with dataclasses for type safety

## Core Workflow

### Python-Based Validation
1. **Validation Function Development**: Create Python functions that implement custom validation logic
2. **Settings Configuration**: Create JSON settings documents that specify which validation rules to execute
3. **XML File Processing**: Tool processes XML files using registered Python validation functions
4. **Validation Execution**: Each validation function receives parsed XML content and returns structured results:
   - Custom validation logic using lxml for XML parsing and XPath evaluation
   - Flexible return values with pass/fail status and detailed messages
   - Support for different severity levels (error, warning, info)
5. **Report Generation**: Generate detailed reports with validation results and comprehensive summaries

## Development Commands

- **Install Dependencies**: `pip install -r requirements-dev.txt`
- **Install Package**: `pip install -e .` (development mode)
- **Testing**: `pytest` - Run test suite with pytest
- **Test Coverage**: `pytest --cov=xml_inspector` - Run tests with coverage
- **Code Formatting**: `black xml_inspector tests` - Format code with Black
- **Linting**: `flake8 xml_inspector tests` - Check code style
- **Type Checking**: `mypy xml_inspector` - Run static type checking

## CLI Usage

The tool provides a command-line interface with the following commands:

- **inspect**: Main command to validate XML files against Python validation settings
- **validate-settings**: Validate the structure of settings documents

### CLI Examples:
```bash
# Python-based inspection
xml-inspector inspect -x file.xml -s validation-settings.json

# Multiple XML files with HTML output
xml-inspector inspect -x file1.xml -x file2.xml -s validation-settings.json -o report.html -f html

# Validate settings document structure
xml-inspector validate-settings -f validation-settings.json
```

## Project Structure

- `xml_inspector/` - Main Python package
  - `core/` - Core functionality (XML parsing, inspection engine)
  - `parsers/` - Settings document parsers (JSON)
  - `validators/` - Python-based XML validation logic
  - `reporters/` - Report generation (JSON/HTML)
  - `types/` - Python dataclass type definitions
  - `validation_rules/` - Built-in validation rules
- `tests/` - Test suite using pytest
- `examples/` - Sample XML files, validation functions, and settings documents

## Key Dependencies

- **lxml**: XML parsing and XPath evaluation
- **click**: Command-line interface framework
- **colorama**: Cross-platform colored terminal output
- **jinja2**: HTML report template rendering

## Architecture Components

### Core Components
- **XmlParser**: Handles XML file parsing and XPath evaluation using lxml
- **XmlInspector**: Main orchestrator class that coordinates all components
- **CLI**: Click-based command-line interface with colored output

### Python-Based Validation  
- **PythonSettingsParser**: Processes Python validation settings documents (JSON format)
- **PythonValidator**: Manages registration and execution of Python validation functions
- **ValidationFunction**: Python functions that implement custom validation logic
  - Receive XmlFile objects containing parsed XML content
  - Return Result objects with pass/fail status and detailed messages
  - Support different severity levels (error, warning, info)
- **Custom Validation Rules**: User-defined Python functions for specific validation scenarios

### Reporting
- **ReportGenerator**: Creates JSON and HTML reports using Jinja2 templates with detailed validation results

## Type System

The project uses Python dataclasses for type safety:

### Core Types
- `XmlFile`: Parsed XML file with content and metadata
- `Result`: Result of a validation operation with status, values, and messages
- `Value`: Typed value from XML validation
- `ValidationResult`: Result of a single Python validation rule execution
- `ValidationSummary`: Statistics for validation results
- `InspectionReport`: Complete inspection report with summary and results

### Validation Types
- `PythonValidationRule`: Definition of a Python validation rule with function and metadata
- `ValidationSettings`: Container for validation rule IDs to execute
- `ValidationFunction`: Type alias for validation functions that take XmlFile and return Result

### Metadata Types
- `ReportMetadata`: Metadata for inspection reports including timestamps and file information
- `Severity`: Literal type for validation severity levels (error, warning, info)
- `ValidationStatus`: Literal type for validation status (pass, fail, missing)

## Custom Validation Functions

Custom validation functions should follow this pattern:

```python
from xml_inspector.types import XmlFile, Result, Value

def my_validation_function(xml_file: XmlFile) -> Result:
    # Implement custom validation logic using xml_file.content (lxml element)
    # Return Result with appropriate status and details
    pass
```