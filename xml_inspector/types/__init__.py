"""Type definitions for XML Inspector."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Literal
from datetime import datetime

SettingType = Literal["string", "number", "boolean"]
ValidationStatus = Literal["pass", "fail", "missing"]


@dataclass
class Setting:
    """Represents a single setting to be validated."""
    
    name: str
    xpath: str
    expected_value: Optional[Union[str, int, float, bool]] = None
    description: Optional[str] = None
    required: bool = True
    type: SettingType = "string"


@dataclass
class SettingsMetadata:
    """Metadata for settings documents."""
    
    version: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None


@dataclass
class SettingsDocument:
    """Represents a complete settings document."""
    
    entity_type: str
    settings: List[Setting]
    metadata: Optional[SettingsMetadata] = None


@dataclass
class ValidationResult:
    """Result of validating a single setting."""
    
    setting_name: str
    xpath: str
    expected_value: Optional[Union[str, int, float, bool]]
    actual_value: Optional[Union[str, int, float, bool]]
    status: ValidationStatus
    message: Optional[str]
    file_path: str


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
    entity_type: str
    xml_files: List[str]
    settings_documents: List[str]


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


# Type aliases for convenience
SettingValue = Union[str, int, float, bool]
ValidationResults = List[ValidationResult]