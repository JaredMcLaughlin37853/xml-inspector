"""Type definitions for XML Inspector DSL validation."""

from dataclasses import dataclass
from typing import List, Optional, Union, Any, Literal

ValidationStatus = Literal["pass", "fail", "missing"]
DslValidationType = Literal["existence", "pattern", "range", "comparison", "computedComparison", "nodeValidation"]
DslSeverity = Literal["error", "warning", "info"]
DslDataType = Literal["string", "integer", "decimal", "date"]
DslComparisonOperator = Literal["==", "!=", ">", "<", ">=", "<=", "between"]
DslConditionType = Literal["exists", "attributeEquals"]


@dataclass
class NodeValidationResult:
    """Result of validating a single node in a node validation rule."""
    
    node_index: int
    node_xpath: str
    actual_value: Any
    expected_value: Any
    status: ValidationStatus
    message: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of validating a DSL rule."""
    
    rule_id: str
    rule_description: str
    xpath: str
    expected_value: Optional[Union[str, int, float, bool]]
    actual_value: Optional[Union[str, int, float, bool]]
    status: ValidationStatus
    message: Optional[str]
    file_path: str
    # For nodeValidation type rules - contains per-node results
    node_results: Optional[List[NodeValidationResult]] = None


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
    dsl_documents: List[str]


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
    # Fields for nodeValidation type
    nodes_xpath: Optional[str] = None  # XPath to select the nodes to validate
    node_value_expression: Optional[DslExpression] = None  # Expression to extract value from each node
    expected_value_expression: Optional[DslExpression] = None  # Expression to get expected value for each node


@dataclass
class DslValidationSettings:
    """Container for DSL validation settings."""
    
    validation_settings: List[DslValidationRule]