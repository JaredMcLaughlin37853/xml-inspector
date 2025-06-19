# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

xml-inspector is a quality assurance tool for XML files that validates configuration settings against standardized requirements. The tool compares XML content with reference documents to identify compliance issues.

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

## Architecture Components

The system will likely include:
- XML parsing and XPath evaluation engine
- Document processing for standards and project-specific settings
- Validation engine for comparing extracted vs expected values
- Report generation system
- File upload and management interface
- Entity type configuration system

## Development Commands

- **Build**: `npm run build` - Compile TypeScript to JavaScript
- **Development**: `npm run dev` - Watch mode compilation
- **Testing**: `npm test` - Run test suite with Jest
- **Test Watch**: `npm run test:watch` - Run tests in watch mode
- **Linting**: `npm run lint` - Check code style with ESLint
- **Type Check**: `npm run typecheck` - Run TypeScript type checking
- **Install Dependencies**: `npm install`

## CLI Usage

The tool provides a command-line interface with the following commands:

- **inspect**: Main command to validate XML files against settings documents
- **validate-settings**: Validate the structure of settings documents

## Project Structure

- `src/core/` - Core functionality (XML parsing, inspection engine)
- `src/parsers/` - Settings document parsers (JSON/YAML)
- `src/validators/` - XML validation logic
- `src/reporters/` - Report generation (JSON/HTML)
- `src/types/` - TypeScript type definitions
- `examples/` - Sample XML files and settings documents