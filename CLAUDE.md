# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

xml-inspector is a quality assurance tool for XML files that validates configuration settings against standardized requirements. The tool compares XML content with reference documents to identify compliance issues.

**Language**: Python 3.8+
**Architecture**: Object-oriented with dataclasses for type safety

## Core Workflow

1. **Entity Type Selection**: User selects the type of entity (e.g., device settings, configurations)
2. **XML File Upload**: Upload one or multiple XML files for inspection
3. **Standard Settings Document**: Upload reference document containing:
   - Standard setting values
   - XPath locations for each setting
4. **Project-Specific Settings**: Upload additional document with project-specific requirements
5. **XML Inspection**: Tool extracts values from XML files using XPath expressions
6. **Validation**: Compare extracted values against both standard and project-specific requirements
7. **Report Generation**: Generate comprehensive report showing passed and failed checks

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

- **inspect**: Main command to validate XML files against settings documents
- **validate-settings**: Validate the structure of settings documents

### CLI Examples:
```bash
# Basic inspection
xml-inspector inspect -x file.xml -s settings.json -t device-config

# With project settings and HTML output
xml-inspector inspect -x file.xml -s standard.json -p project.yaml -t device-config -o report.html -f html

# Validate settings document
xml-inspector validate-settings -f settings.json
```

## Project Structure

- `xml_inspector/` - Main Python package
  - `core/` - Core functionality (XML parsing, inspection engine)
  - `parsers/` - Settings document parsers (JSON/YAML)
  - `validators/` - XML validation logic
  - `reporters/` - Report generation (JSON/HTML)
  - `types/` - Python dataclass type definitions
- `tests/` - Test suite using pytest
- `examples/` - Sample XML files and settings documents

## Key Dependencies

- **lxml**: XML parsing and XPath evaluation
- **PyYAML**: YAML settings document parsing
- **click**: Command-line interface framework
- **colorama**: Cross-platform colored terminal output
- **jinja2**: HTML report template rendering

## Architecture Components

- **XmlParser**: Handles XML file parsing and XPath evaluation using lxml
- **SettingsParser**: Processes JSON/YAML settings documents with validation
- **XmlValidator**: Compares extracted XML values against expected values with type conversion
- **ReportGenerator**: Creates JSON and HTML reports using Jinja2 templates
- **XmlInspector**: Main orchestrator class that coordinates all components
- **CLI**: Click-based command-line interface with colored output

## Type System

The project uses Python dataclasses for type safety:
- `Setting`: Individual setting definition
- `SettingsDocument`: Complete settings document
- `ValidationResult`: Result of a single validation check
- `InspectionReport`: Complete inspection report with summary and results