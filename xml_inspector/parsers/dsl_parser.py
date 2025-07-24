"""DSL settings document parsing functionality."""

import json
from pathlib import Path
from typing import Any, Dict, List, Union, Optional
import logging

import yaml

from ..types import (
    DslExpression, DslCondition, DslComparison, DslValidationRule, 
    DslValidationSettings, DslValidationType, DslSeverity, DslDataType,
    DslComparisonOperator, DslConditionType
)

logger = logging.getLogger(__name__)


class DslParseError(Exception):
    """Raised when DSL document parsing fails."""
    pass


class DslParser:
    """Handles parsing of DSL validation settings documents."""
    
    def parse_dsl_document(self, file_path: Union[str, Path]) -> DslValidationSettings:
        """
        Parse a DSL validation settings document from JSON or YAML file.
        
        Args:
            file_path: Path to the DSL document
            
        Returns:
            DslValidationSettings object
            
        Raises:
            DslParseError: If parsing fails
        """
        file_path = Path(file_path)
        
        try:
            if not file_path.exists():
                raise DslParseError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            extension = file_path.suffix.lower()
            
            if extension == '.json':
                data = self._parse_json_content(content)
            elif extension in ['.yaml', '.yml']:
                data = self._parse_yaml_content(content)
            else:
                raise DslParseError(f"Unsupported DSL file format: {extension}")
            
            return self._validate_dsl_document(data)
            
        except DslParseError:
            raise
        except Exception as e:
            raise DslParseError(f"Failed to parse DSL document {file_path}: {e}")
    
    def _parse_json_content(self, content: str) -> Dict[str, Any]:
        """Parse JSON content."""
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise DslParseError(f"Invalid JSON: {e}")
    
    def _parse_yaml_content(self, content: str) -> Dict[str, Any]:
        """Parse YAML content."""
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise DslParseError(f"Invalid YAML: {e}")
    
    def _validate_dsl_document(self, data: Dict[str, Any]) -> DslValidationSettings:
        """
        Validate and convert parsed data to DslValidationSettings.
        
        Args:
            data: Parsed DSL data
            
        Returns:
            DslValidationSettings object
            
        Raises:
            DslParseError: If validation fails
        """
        if not isinstance(data, dict):
            raise DslParseError("DSL document must be an object")
        
        # Validate validationSettings array
        validation_settings_data = data.get('validationSettings', [])
        if not isinstance(validation_settings_data, list):
            raise DslParseError("DSL document must have a validationSettings array")
        
        validation_rules = []
        for i, rule_data in enumerate(validation_settings_data):
            try:
                rule = self._parse_validation_rule(rule_data)
                validation_rules.append(rule)
            except Exception as e:
                raise DslParseError(f"Error parsing validation rule at index {i}: {e}")
        
        return DslValidationSettings(validation_settings=validation_rules)
    
    def _parse_validation_rule(self, data: Dict[str, Any]) -> DslValidationRule:
        """Parse a single validation rule."""
        if not isinstance(data, dict):
            raise DslParseError("Validation rule must be an object")
        
        # Required fields
        rule_id = data.get('id')
        if not rule_id or not isinstance(rule_id, str):
            raise DslParseError("Validation rule must have a valid id")
        
        description = data.get('description')
        if not description or not isinstance(description, str):
            raise DslParseError("Validation rule must have a valid description")
        
        rule_type = data.get('type')
        if rule_type not in ['existence', 'pattern', 'range', 'comparison', 'computedComparison']:
            raise DslParseError(f"Invalid validation rule type: {rule_type}")
        
        severity = data.get('severity')
        if severity not in ['error', 'warning', 'info']:
            raise DslParseError(f"Invalid severity: {severity}")
        
        # Optional fields
        conditions = None
        if 'conditions' in data:
            conditions = [self._parse_condition(cond) for cond in data['conditions']]
        
        expression = None
        if 'expression' in data:
            expression = self._parse_expression(data['expression'])
        
        pattern = data.get('pattern')
        min_value = data.get('minValue')
        max_value = data.get('maxValue')
        data_type = data.get('dataType')
        operator = data.get('operator')
        value = data.get('value')
        
        comparison = None
        if 'comparison' in data:
            comparison = self._parse_comparison(data['comparison'])
        
        return DslValidationRule(
            id=rule_id,
            description=description,
            type=rule_type,  # type: ignore
            severity=severity,  # type: ignore
            conditions=conditions,
            expression=expression,
            pattern=pattern,
            min_value=min_value,
            max_value=max_value,
            data_type=data_type,  # type: ignore
            operator=operator,  # type: ignore
            value=value,
            comparison=comparison
        )
    
    def _parse_condition(self, data: Dict[str, Any]) -> DslCondition:
        """Parse a condition object."""
        if not isinstance(data, dict):
            raise DslParseError("Condition must be an object")
        
        condition_type = data.get('type')
        if condition_type not in ['exists', 'attributeEquals']:
            raise DslParseError(f"Invalid condition type: {condition_type}")
        
        xpath = data.get('xpath')
        if not xpath or not isinstance(xpath, str):
            raise DslParseError("Condition must have a valid xpath")
        
        attribute = data.get('attribute')
        value = data.get('value')
        
        return DslCondition(
            type=condition_type,  # type: ignore
            xpath=xpath,
            attribute=attribute,
            value=value
        )
    
    def _parse_comparison(self, data: Dict[str, Any]) -> DslComparison:
        """Parse a comparison object."""
        if not isinstance(data, dict):
            raise DslParseError("Comparison must be an object")
        
        operator = data.get('operator')
        if operator not in ['==', '!=', '>', '<', '>=', '<=', 'between']:
            raise DslParseError(f"Invalid comparison operator: {operator}")
        
        left_expression = None
        if 'leftExpression' in data:
            left_expression = self._parse_expression(data['leftExpression'])
        
        right_expression = None
        if 'rightExpression' in data:
            right_expression = self._parse_expression(data['rightExpression'])
        
        lower_expression = None
        if 'lowerExpression' in data:
            lower_expression = self._parse_expression(data['lowerExpression'])
        
        upper_expression = None
        if 'upperExpression' in data:
            upper_expression = self._parse_expression(data['upperExpression'])
        
        return DslComparison(
            operator=operator,  # type: ignore
            left_expression=left_expression,
            right_expression=right_expression,
            lower_expression=lower_expression,
            upper_expression=upper_expression
        )
    
    def _parse_expression(self, data: Dict[str, Any]) -> DslExpression:
        """Parse an expression object recursively."""
        if not isinstance(data, dict):
            raise DslParseError("Expression must be an object")
        
        op = data.get('op')
        if not op or not isinstance(op, str):
            raise DslParseError("Expression must have a valid op")
        
        # Parse args recursively
        args = None
        if 'args' in data:
            args = []
            for arg in data['args']:
                if isinstance(arg, dict):
                    # Recursive expression
                    args.append(self._parse_expression(arg))
                else:
                    # Literal value
                    args.append(arg)
        
        xpath = data.get('xpath')
        
        xpath_expression = None
        if 'xpathExpression' in data:
            xpath_expression = self._parse_expression(data['xpathExpression'])
        
        expression = None
        if 'expression' in data:
            expression = self._parse_expression(data['expression'])
        
        value = data.get('value')
        data_type = data.get('dataType')
        
        return DslExpression(
            op=op,
            args=args,
            xpath=xpath,
            xpath_expression=xpath_expression,
            expression=expression,
            value=value,
            data_type=data_type  # type: ignore
        )