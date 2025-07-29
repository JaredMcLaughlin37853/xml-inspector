"""Python-based XML validation functionality."""

import logging
from typing import Dict, List

from ..types import (
    XmlFile, ValidationResult, Result, Value, 
    PythonValidationRule, ValidationFunction
)

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation setup fails."""
    pass


class PythonValidator:
    """Validates XML files using Python validation functions."""
    
    def __init__(self):
        """Initialize the Python validator."""
        self.registered_rules: Dict[str, PythonValidationRule] = {}
    
    def register_rule(self, rule: PythonValidationRule) -> None:
        """
        Register a validation rule.
        
        Args:
            rule: The validation rule to register
        """
        self.registered_rules[rule.id] = rule
    
    def register_function(self, rule_id: str, description: str, 
                         validation_function: ValidationFunction, 
                         severity: str = "error") -> None:
        """
        Register a validation function directly.
        
        Args:
            rule_id: Unique identifier for the rule
            description: Human-readable description
            validation_function: Function that takes XmlFile and returns Result
            severity: Severity level (error, warning, info)
        """
        rule = PythonValidationRule(
            id=rule_id,
            description=description,
            validation_function=validation_function,
            severity=severity  # type: ignore
        )
        self.register_rule(rule)
    
    def validate_xml_files(self, xml_files: List[XmlFile], 
                          rule_ids: List[str]) -> List[ValidationResult]:
        """
        Validate XML files using specified validation rules.
        
        Args:
            xml_files: List of parsed XML files
            rule_ids: List of rule IDs to execute
            
        Returns:
            List of validation results
            
        Raises:
            ValidationError: If validation setup fails
        """
        results = []
        
        # Validate that all requested rules are registered
        missing_rules = [rule_id for rule_id in rule_ids 
                        if rule_id not in self.registered_rules]
        if missing_rules:
            raise ValidationError(f"Unregistered validation rules: {missing_rules}")
        
        for xml_file in xml_files:
            for rule_id in rule_ids:
                try:
                    rule = self.registered_rules[rule_id]
                    result = self._validate_rule(xml_file, rule)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to validate rule {rule_id} for file {xml_file.path}: {e}")
                    # Create a failed result for the error
                    error_result = Result(
                        status="fail",
                        returned_value=None,
                        expected_value=None,
                        message=f"Validation error: {e}"
                    )
                    results.append(ValidationResult(
                        rule_id=rule_id,
                        rule_description=self.registered_rules[rule_id].description,
                        result=error_result,
                        file_path=xml_file.path,
                        severity=self.registered_rules[rule_id].severity
                    ))
        
        return results
    
    def _validate_rule(self, xml_file: XmlFile, rule: PythonValidationRule) -> ValidationResult:
        """
        Validate a single rule against an XML file.
        
        Args:
            xml_file: The XML file to validate
            rule: The validation rule
            
        Returns:
            ValidationResult for this rule
        """
        try:
            result = rule.validation_function(xml_file)
            return ValidationResult(
                rule_id=rule.id,
                rule_description=rule.description,
                result=result,
                file_path=xml_file.path,
                severity=rule.severity
            )
        except Exception as e:
            error_result = Result(
                status="fail",
                returned_value=None,
                expected_value=None,
                message=f"Rule validation failed: {e}"
            )
            return ValidationResult(
                rule_id=rule.id,
                rule_description=rule.description,
                result=error_result,
                file_path=xml_file.path,
                severity=rule.severity
            )
    
    def get_registered_rules(self) -> List[str]:
        """
        Get list of registered rule IDs.
        
        Returns:
            List of rule IDs
        """
        return list(self.registered_rules.keys())
    
    def get_rule_description(self, rule_id: str) -> str:
        """
        Get description for a rule.
        
        Args:
            rule_id: The rule ID
            
        Returns:
            Rule description
            
        Raises:
            ValidationError: If rule not found
        """
        if rule_id not in self.registered_rules:
            raise ValidationError(f"Rule not found: {rule_id}")
        return self.registered_rules[rule_id].description