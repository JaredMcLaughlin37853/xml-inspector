# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

xml-inspector is a quality assurance tool for XML files that validates configuration settings using DSL (Domain Specific Language) expression-based validation for complex XML inspection scenarios.

**Language**: Python 3.8+
**Architecture**: Object-oriented with dataclasses for type safety

## Core Workflow

### DSL Expression-Based Validation
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
# DSL-based inspection
xml-inspector inspect -x file.xml -d dsl-validation.json

# Multiple XML files with HTML output
xml-inspector inspect -x file1.xml -x file2.xml -d dsl-validation.json -o report.html -f html

# Validate DSL document structure
xml-inspector validate-settings -f dsl-validation.json
```

## Project Structure

- `xml_inspector/` - Main Python package
  - `core/` - Core functionality (XML parsing, inspection engine, DSL evaluator)
  - `parsers/` - DSL document parsers (JSON)
  - `validators/` - DSL-based XML validation logic
  - `reporters/` - Report generation (JSON/HTML)
  - `types/` - Python dataclass type definitions
- `tests/` - Test suite using pytest
- `examples/` - Sample XML files and DSL documents
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

### DSL Expression-Based Validation  
- **SettingsParser**: Processes DSL validation documents (JSON format)
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
- **ReportGenerator**: Creates JSON and HTML reports using Jinja2 templates with support for detailed per-node results

## Type System

The project uses Python dataclasses for type safety:

### DSL Expression Types
- `DslExpression`: Recursive expression tree node with operations, arguments, and XPath
- `DslValidationRule`: Complete DSL validation rule with type, expressions, and conditions
- `DslValidationSettings`: Container for multiple DSL validation rules
- `DslCondition`: Precondition that controls when a rule applies
- `DslComparison`: Comparison between two expressions

### Result Types
- `ValidationResult`: Result of a single DSL validation check (supports per-node results)
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