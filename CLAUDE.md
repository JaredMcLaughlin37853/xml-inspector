# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

xml-inspector is a quality assurance tool for XML files that validates configuration settings against standardized requirements. The tool supports both simple settings-based validation and advanced DSL (Domain Specific Language) expression-based validation for complex XML inspection scenarios.

**Language**: Python 3.8+
**Architecture**: Object-oriented with dataclasses for type safety

## Core Workflow

The tool supports two validation approaches:

### Simple Settings-Based Validation
1. **Entity Type Selection**: User selects the type of entity (e.g., device settings, configurations)
2. **XML File Upload**: Upload one or multiple XML files for inspection
3. **Standard Settings Document**: Upload reference document containing:
   - Standard setting values
   - XPath locations for each setting
4. **Project-Specific Settings**: Upload additional document with project-specific requirements
5. **XML Inspection**: Tool extracts values from XML files using XPath expressions
6. **Validation**: Compare extracted values against both standard and project-specific requirements
7. **Report Generation**: Generate comprehensive report showing passed and failed checks

### Advanced DSL Expression-Based Validation
1. **DSL Document Creation**: Create JSON documents with complex validation rules using the DSL syntax
2. **XML File Upload**: Upload XML files for inspection
3. **Expression Evaluation**: Tool evaluates sophisticated expressions including:
   - Dynamic XPath construction
   - Complex calculations and aggregations
   - Conditional logic and mapping between related XML nodes
   - Per-node individual validation with detailed results
4. **Validation Types**: Supports multiple validation approaches:
   - `existence`: Check if expressions evaluate to truthy values
   - `pattern`: Match expression results against regular expressions
   - `range`: Validate expression results fall within specified bounds
   - `comparison`: Compare expression results with fixed values
   - `computedComparison`: Compare two expressions or use between operations
   - `nodeValidation`: Validate multiple nodes individually with per-node PASS/FAIL results
5. **Report Generation**: Generate detailed reports with individual node results and comprehensive validation summaries

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
# Basic settings-based inspection
xml-inspector inspect -x file.xml -s settings.json -t device-config

# With project settings and HTML output
xml-inspector inspect -x file.xml -s standard.json -p project.yaml -t device-config -o report.html -f html

# DSL-based inspection with complex expressions
xml-inspector inspect -x config.xml -s dsl-validation.json -t device-config

# Validate settings document structure
xml-inspector validate-settings -f settings.json
```

## Project Structure

- `xml_inspector/` - Main Python package
  - `core/` - Core functionality (XML parsing, inspection engine, DSL evaluator)
  - `parsers/` - Settings document parsers (JSON/YAML, DSL parser)
  - `validators/` - XML validation logic (settings-based and DSL-based)
  - `reporters/` - Report generation (JSON/HTML)
  - `types/` - Python dataclass type definitions
- `tests/` - Test suite using pytest
- `examples/` - Sample XML files and settings documents
- `spec/` - DSL specification and JSON schema files

## Key Dependencies

- **lxml**: XML parsing and XPath evaluation
- **PyYAML**: YAML settings document parsing
- **click**: Command-line interface framework
- **colorama**: Cross-platform colored terminal output
- **jinja2**: HTML report template rendering

## Architecture Components

### Core Components
- **XmlParser**: Handles XML file parsing and XPath evaluation using lxml
- **XmlInspector**: Main orchestrator class that coordinates all components
- **CLI**: Click-based command-line interface with colored output

### Settings-Based Validation
- **SettingsParser**: Processes JSON/YAML settings documents with validation
- **XmlValidator**: Compares extracted XML values against expected values with type conversion

### DSL Expression-Based Validation  
- **DslParser**: Parses DSL validation documents with complex expression trees
- **DslEvaluator**: Evaluates DSL expressions including:
  - Arithmetic and logical operations
  - Dynamic XPath construction with `xpathExpression`
  - Map operations for iterating over nodes
  - Conditional logic with if/then/else
- **DslValidator**: Validates XML files using DSL rules with support for:
  - Multiple validation types (existence, pattern, range, comparison, computedComparison, nodeValidation)
  - Per-node validation with individual PASS/FAIL results
  - Complex mapping between related XML nodes

### Reporting
- **ReportGenerator**: Creates JSON and HTML reports using Jinja2 templates with support for both simple and detailed per-node results

## Type System

The project uses Python dataclasses for type safety:

### Settings-Based Types
- `Setting`: Individual setting definition
- `SettingsDocument`: Complete settings document

### DSL Expression Types
- `DslExpression`: Recursive expression tree node with operations, arguments, and XPath
- `DslValidationRule`: Complete DSL validation rule with type, expressions, and conditions
- `DslValidationSettings`: Container for multiple DSL validation rules
- `DslCondition`: Precondition that controls when a rule applies
- `DslComparison`: Comparison between two expressions

### Result Types
- `ValidationResult`: Result of a single validation check (supports both simple and per-node results)
- `NodeValidationResult`: Individual node result for nodeValidation rules
- `InspectionReport`: Complete inspection report with summary and results

### Utility Types
- `XmlFile`: Parsed XML file with content and metadata
- `ValidationSummary`: Statistics for validation results
- `ReportMetadata`: Metadata for inspection reports

## DSL Documentation

For detailed DSL syntax and capabilities, see:
- `spec/dsl-spec.md` - Complete DSL specification with examples
- `spec/json-schema.json` - JSON schema for DSL document validation
- `DSL_TRAINING_MANUAL.md` - Comprehensive training manual with examples