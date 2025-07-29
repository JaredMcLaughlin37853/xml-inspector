"""Type definitions for XML Inspector Python validation."""

from dataclasses import dataclass
from typing import List, Optional, Union, Any, Literal, Callable

ValidationStatus = Literal["pass", "fail", "missing"]
Severity = Literal["error", "warning", "info"]

@dataclass
class ValidationResult:
    """Result of validating a Python validation rule."""
    
    rule_id: str
    rule_description: str
    result: Any  # Custom result format determined by validation function
    file_path: str
    severity: Severity = "error"


@dataclass
class ValidationSummary:
    """Summary statistics for validation results."""
    
    total_checks: int
    passed: int
    failed: int
    missing: int


@dataclass
class ReportMetadata:
    """Metadata for inspection reports."""
    
    timestamp: str
    xml_files: List[str]
    validation_rules: List[str]


@dataclass
class InspectionReport:
    """Complete inspection report."""
    
    summary: ValidationSummary
    results: List[ValidationResult]
    metadata: ReportMetadata


@dataclass
class XmlFile:
    """Represents a parsed XML file."""
    
    path: str
    content: Any  # lxml.etree._Element


@dataclass
class PythonValidationRule:
    """Represents a Python validation rule."""
    
    id: str
    description: str
    validation_function: Callable[[XmlFile], Any]  # Function can return any format
    severity: Severity = "error"


@dataclass
class ValidationSettings:
    """Container for Python validation settings."""
    
    validation_rules: List[str]  # List of rule IDs to execute


# Type aliases for convenience
ValidationResults = List[ValidationResult]
ValidationFunction = Callable[[XmlFile], Any]  # Function can return any format