"""Type definitions for XML Inspector."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any, Literal
from datetime import datetime

SettingType = Literal["string", "number", "boolean"]
ValidationStatus = Literal["pass", "fail", "missing"]
DslValidationType = Literal["existence", "pattern", "range", "comparison", "computedComparison"]
DslSeverity = Literal["error", "warning", "info"]
DslDataType = Literal["string", "integer", "decimal", "date"]
DslComparisonOperator = Literal["==", "!=", ">", "<", ">=", "<=", "between"]
DslConditionType = Literal["exists", "attributeEquals"]


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


# DSL Types
@dataclass
class DslExpression:
    """Represents a DSL expression node."""
    
    op: str
    args: Optional[List[Union['DslExpression', str, int, float, bool]]] = None
    xpath: Optional[str] = None
    xpath_expression: Optional['DslExpression'] = None
    expression: Optional['DslExpression'] = None
    value: Optional[Union[str, int, float, bool]] = None
    data_type: Optional[DslDataType] = None


@dataclass
class DslCondition:
    """Represents a condition that controls when a rule applies."""
    
    type: DslConditionType
    xpath: str
    attribute: Optional[str] = None
    value: Optional[str] = None


@dataclass
class DslComparison:
    """Represents a comparison operation between two expressions."""
    
    operator: DslComparisonOperator
    left_expression: Optional[DslExpression] = None
    right_expression: Optional[DslExpression] = None
    lower_expression: Optional[DslExpression] = None
    upper_expression: Optional[DslExpression] = None


@dataclass
class DslValidationRule:
    """Represents a DSL validation rule."""
    
    id: str
    description: str
    type: DslValidationType
    severity: DslSeverity
    conditions: Optional[List[DslCondition]] = None
    expression: Optional[DslExpression] = None
    pattern: Optional[str] = None
    min_value: Optional[str] = None
    max_value: Optional[str] = None
    data_type: Optional[DslDataType] = None
    operator: Optional[DslComparisonOperator] = None
    value: Optional[Union[str, int, float]] = None
    comparison: Optional[DslComparison] = None


@dataclass
class DslValidationSettings:
    """Container for DSL validation settings."""
    
    validation_settings: List[DslValidationRule]