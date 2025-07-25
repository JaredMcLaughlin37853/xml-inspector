"""DSL-based XML validation functionality."""

import re
from typing import List, Any, Union
from datetime import datetime
import logging

from lxml import etree
from ..types import (
    DslValidationSettings, DslValidationRule, DslExpression, DslComparison,
    ValidationResult, ValidationStatus, XmlFile, NodeValidationResult
)
from ..core.dsl_evaluator import DslEvaluator, DslEvaluationError

logger = logging.getLogger(__name__)


class DslValidationError(Exception):
    """Raised when DSL validation fails."""
    pass


class DslValidator:
    """Validates XML files using DSL validation rules."""
    
    def __init__(self):
        """Initialize the DSL validator."""
        self.evaluator = DslEvaluator()
    
    def validate_xml_files(self, xml_files: List[XmlFile], 
                          dsl_settings: DslValidationSettings) -> List[ValidationResult]:
        """
        Validate XML files against DSL validation rules.
        
        Args:
            xml_files: List of parsed XML files
            dsl_settings: DSL validation settings
            
        Returns:
            List of validation results
            
        Raises:
            DslValidationError: If validation setup fails
        """
        results = []
        
        for xml_file in xml_files:
            for rule in dsl_settings.validation_settings:
                try:
                    result = self._validate_rule(xml_file, rule)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to validate rule {rule.id} for file {xml_file.path}: {e}")
                    # Create a failed result for the error
                    results.append(ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath="N/A",
                        expected_value=None,
                        actual_value=None,
                        status="fail",
                        message=f"Validation error: {e}",
                        file_path=xml_file.path
                    ))
        
        return results
    
    def _validate_rule(self, xml_file: XmlFile, rule: DslValidationRule) -> ValidationResult:
        """
        Validate a single rule against an XML file.
        
        Args:
            xml_file: The XML file to validate
            rule: The DSL validation rule
            
        Returns:
            ValidationResult for this rule
        """
        # Check conditions first
        if rule.conditions:
            if not self.evaluator.evaluate_conditions(rule.conditions, xml_file.content):
                # Conditions not met, skip this rule
                return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath="N/A",
                    expected_value=None,
                    actual_value=None,
                    status="pass",  # Skip is considered pass
                    message="Rule conditions not met, skipped",
                    file_path=xml_file.path
                )
        
        try:
            if rule.type == "existence":
                return self._validate_existence(xml_file, rule)
            elif rule.type == "pattern":
                return self._validate_pattern(xml_file, rule)
            elif rule.type == "range":
                return self._validate_range(xml_file, rule)
            elif rule.type == "comparison":
                return self._validate_comparison(xml_file, rule)
            elif rule.type == "computedComparison":
                return self._validate_computed_comparison(xml_file, rule)
            elif rule.type == "nodeValidation":
                return self._validate_node_validation(xml_file, rule)
            else:
                raise DslValidationError(f"Unknown rule type: {rule.type}")
                
        except Exception as e:
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath="N/A",
                expected_value=None,
                actual_value=None,
                status="fail",
                message=f"Rule validation failed: {e}",
                file_path=xml_file.path
            )
    
    def _validate_existence(self, xml_file: XmlFile, rule: DslValidationRule) -> ValidationResult:
        """Validate existence rule."""
        if not rule.expression:
            raise DslValidationError("Existence rule must have an expression")
        
        try:
            result = self.evaluator.evaluate_expression(rule.expression, xml_file.content)
            
            # For existence, we expect a truthy result (count > 0, value exists, etc.)
            exists = bool(result) and (not isinstance(result, (int, float)) or result > 0)
            
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=self._get_expression_xpath(rule.expression),
                expected_value="exists",
                actual_value=str(result),
                status="pass" if exists else "fail",
                message=rule.description if exists else f"Failed: {rule.description}",
                file_path=xml_file.path
            )
            
        except DslEvaluationError as e:
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=self._get_expression_xpath(rule.expression),
                expected_value="exists",
                actual_value=None,
                status="fail",
                message=f"Evaluation failed: {e}",
                file_path=xml_file.path
            )
    
    def _validate_pattern(self, xml_file: XmlFile, rule: DslValidationRule) -> ValidationResult:
        """Validate pattern rule."""
        if not rule.expression or not rule.pattern:
            raise DslValidationError("Pattern rule must have expression and pattern")
        
        try:
            result = self.evaluator.evaluate_expression(rule.expression, xml_file.content)
            result_str = str(result) if result is not None else ""
            
            pattern_match = re.match(rule.pattern, result_str) is not None
            
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=self._get_expression_xpath(rule.expression),
                expected_value=f"matches pattern: {rule.pattern}",
                actual_value=result_str,
                status="pass" if pattern_match else "fail",
                message=rule.description if pattern_match else f"Failed: {rule.description}",
                file_path=xml_file.path
            )
            
        except DslEvaluationError as e:
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=self._get_expression_xpath(rule.expression),
                expected_value=f"matches pattern: {rule.pattern}",
                actual_value=None,
                status="fail",
                message=f"Evaluation failed: {e}",
                file_path=xml_file.path
            )
    
    def _validate_range(self, xml_file: XmlFile, rule: DslValidationRule) -> ValidationResult:
        """Validate range rule."""
        if not rule.expression or not rule.min_value or not rule.max_value:
            raise DslValidationError("Range rule must have expression, minValue, and maxValue")
        
        try:
            result = self.evaluator.evaluate_expression(rule.expression, xml_file.content)
            
            # Convert to appropriate type based on dataType
            if rule.data_type == "integer":
                actual_val = int(float(str(result)))
                min_val = int(float(rule.min_value))
                max_val = int(float(rule.max_value))
            elif rule.data_type == "decimal":
                actual_val = float(str(result))
                min_val = float(rule.min_value)
                max_val = float(rule.max_value)
            elif rule.data_type == "date":
                actual_val = datetime.fromisoformat(str(result).replace('Z', '+00:00'))
                min_val = datetime.fromisoformat(rule.min_value.replace('Z', '+00:00'))
                max_val = datetime.fromisoformat(rule.max_value.replace('Z', '+00:00'))
            else:  # string
                actual_val = str(result)
                min_val = rule.min_value
                max_val = rule.max_value
            
            in_range = min_val <= actual_val <= max_val
            
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=self._get_expression_xpath(rule.expression),
                expected_value=f"between {rule.min_value} and {rule.max_value}",
                actual_value=str(result),
                status="pass" if in_range else "fail",
                message=rule.description if in_range else f"Failed: {rule.description}",
                file_path=xml_file.path
            )
            
        except (DslEvaluationError, ValueError, TypeError) as e:
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=self._get_expression_xpath(rule.expression),
                expected_value=f"between {rule.min_value} and {rule.max_value}",
                actual_value=None,
                status="fail",
                message=f"Evaluation failed: {e}",
                file_path=xml_file.path
            )
    
    def _validate_comparison(self, xml_file: XmlFile, rule: DslValidationRule) -> ValidationResult:
        """Validate comparison rule."""
        if not rule.expression or not rule.operator or rule.value is None:
            raise DslValidationError("Comparison rule must have expression, operator, and value")
        
        try:
            result = self.evaluator.evaluate_expression(rule.expression, xml_file.content)
            expected = rule.value
            
            # Perform comparison based on operator
            if rule.operator == "==":
                passes = result == expected
            elif rule.operator == "!=":
                passes = result != expected
            elif rule.operator == ">":
                passes = float(result) > float(expected)
            elif rule.operator == "<":
                passes = float(result) < float(expected)
            elif rule.operator == ">=":
                passes = float(result) >= float(expected)
            elif rule.operator == "<=":
                passes = float(result) <= float(expected)
            else:
                raise DslValidationError(f"Unknown comparison operator: {rule.operator}")
            
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=self._get_expression_xpath(rule.expression),
                expected_value=f"{rule.operator} {expected}",
                actual_value=str(result),
                status="pass" if passes else "fail",
                message=rule.description if passes else f"Failed: {rule.description}",
                file_path=xml_file.path
            )
            
        except (DslEvaluationError, ValueError, TypeError) as e:
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=self._get_expression_xpath(rule.expression),
                expected_value=f"{rule.operator} {rule.value}",
                actual_value=None,
                status="fail",
                message=f"Evaluation failed: {e}",
                file_path=xml_file.path
            )
    
    def _validate_computed_comparison(self, xml_file: XmlFile, rule: DslValidationRule) -> ValidationResult:
        """Validate computed comparison rule."""
        if not rule.comparison:
            raise DslValidationError("Computed comparison rule must have comparison")
        
        comparison = rule.comparison
        
        try:
            if comparison.operator == "between":
                if not comparison.lower_expression or not comparison.upper_expression:
                    raise DslValidationError("Between comparison requires lowerExpression and upperExpression")
                
                # For between, we need a target expression (could be leftExpression)
                if not comparison.left_expression:
                    raise DslValidationError("Between comparison requires leftExpression as target")
                
                actual = self.evaluator.evaluate_expression(comparison.left_expression, xml_file.content)
                lower = self.evaluator.evaluate_expression(comparison.lower_expression, xml_file.content)
                upper = self.evaluator.evaluate_expression(comparison.upper_expression, xml_file.content)
                
                passes = float(lower) <= float(actual) <= float(upper)
                expected_desc = f"between {lower} and {upper}"
                
            else:
                if not comparison.left_expression or not comparison.right_expression:
                    raise DslValidationError("Comparison requires leftExpression and rightExpression")
                
                left_result = self.evaluator.evaluate_expression(comparison.left_expression, xml_file.content)
                right_result = self.evaluator.evaluate_expression(comparison.right_expression, xml_file.content)
                
                # Perform comparison
                if comparison.operator == "==":
                    passes = left_result == right_result
                elif comparison.operator == "!=":
                    passes = left_result != right_result
                elif comparison.operator == ">":
                    passes = float(left_result) > float(right_result)
                elif comparison.operator == "<":
                    passes = float(left_result) < float(right_result)
                elif comparison.operator == ">=":
                    passes = float(left_result) >= float(right_result)
                elif comparison.operator == "<=":
                    passes = float(left_result) <= float(right_result)
                else:
                    raise DslValidationError(f"Unknown comparison operator: {comparison.operator}")
                
                actual = left_result
                expected_desc = f"{comparison.operator} {right_result}"
            
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=self._get_comparison_xpath(comparison),
                expected_value=expected_desc,
                actual_value=str(actual),
                status="pass" if passes else "fail",
                message=rule.description if passes else f"Failed: {rule.description}",
                file_path=xml_file.path
            )
            
        except (DslEvaluationError, ValueError, TypeError) as e:
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=self._get_comparison_xpath(comparison),
                expected_value="computed comparison",
                actual_value=None,
                status="fail",
                message=f"Evaluation failed: {e}",
                file_path=xml_file.path
            )
    
    def _get_expression_xpath(self, expression: DslExpression) -> str:
        """Extract XPath from expression for reporting."""
        if expression.xpath:
            return expression.xpath
        elif expression.xpath_expression:
            return "dynamic XPath"
        else:
            return f"expression({expression.op})"
    
    def _get_comparison_xpath(self, comparison: DslComparison) -> str:
        """Extract XPath from comparison for reporting."""
        if comparison.left_expression:
            return self._get_expression_xpath(comparison.left_expression)
        elif comparison.lower_expression:
            return self._get_expression_xpath(comparison.lower_expression)
        else:
            return "computed comparison"
    
    def _validate_node_validation(self, xml_file: XmlFile, rule: DslValidationRule) -> ValidationResult:
        """
        Validate multiple nodes individually and return per-node results.
        
        This validation type iterates through nodes matching an XPath and validates 
        each one individually, producing a PASS/FAIL result for each node.
        """
        if not rule.nodes_xpath:
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath="N/A",
                expected_value=None,
                actual_value=None,
                status="fail",
                message="nodeValidation requires nodesXpath field",
                file_path=xml_file.path
            )
        
        if not rule.node_value_expression:
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=rule.nodes_xpath,
                expected_value=None,
                actual_value=None,
                status="fail",
                message="nodeValidation requires nodeValueExpression field",
                file_path=xml_file.path
            )
        
        # Get nodes to validate
        try:
            nodes = xml_file.content.xpath(rule.nodes_xpath)
        except Exception as e:
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=rule.nodes_xpath,
                expected_value=None,
                actual_value=None,
                status="fail",
                message=f"XPath error: {e}",
                file_path=xml_file.path
            )
        
        if not nodes:
            return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=rule.nodes_xpath,
                expected_value=None,
                actual_value=None,
                status="missing",
                message="No nodes found matching XPath",
                file_path=xml_file.path
            )
        
        node_results = []
        overall_status = "pass"
        
        for i, node in enumerate(nodes):
            try:
                # Get actual value from node
                actual_value = self.evaluator.evaluate_expression(
                    rule.node_value_expression, xml_file.content, node
                )
                
                # Get expected value
                if rule.expected_value_expression:
                    expected_value = self.evaluator.evaluate_expression(
                        rule.expected_value_expression, xml_file.content, node
                    )
                elif rule.value is not None:
                    expected_value = rule.value
                else:
                    expected_value = None
                
                # Perform comparison
                if expected_value is not None:
                    if rule.operator:
                        node_status = self._compare_values(actual_value, expected_value, rule.operator)
                    else:
                        # Default to equality comparison
                        node_status = "pass" if actual_value == expected_value else "fail"
                else:
                    # If no expected value, just check existence
                    node_status = "pass" if actual_value is not None else "fail"
                
                # Build node XPath for reporting
                node_xpath = f"{rule.nodes_xpath}[{i+1}]"
                
                node_result = NodeValidationResult(
                    node_index=i,
                    node_xpath=node_xpath,
                    actual_value=actual_value,
                    expected_value=expected_value,
                    status=node_status,
                    message=f"Node {i+1}: {node_status.upper()}"
                )
                
                node_results.append(node_result)
                
                # Track overall status
                if node_status == "fail":
                    overall_status = "fail"
                
            except Exception as e:
                node_result = NodeValidationResult(
                    node_index=i,
                    node_xpath=f"{rule.nodes_xpath}[{i+1}]",
                    actual_value=None,
                    expected_value=None,
                    status="fail",
                    message=f"Node {i+1}: Error - {e}"
                )
                node_results.append(node_result)
                overall_status = "fail"
        
        # Create summary message
        pass_count = sum(1 for r in node_results if r.status == "pass")
        fail_count = sum(1 for r in node_results if r.status == "fail")
        summary_msg = f"Node validation: {pass_count} passed, {fail_count} failed"
        
        return ValidationResult(
                        rule_id=rule.id,
                        rule_description=rule.description,
                        xpath=rule.nodes_xpath,
            expected_value=f"All nodes should pass validation",
            actual_value=f"{pass_count}/{len(node_results)} nodes passed",
            status=overall_status,
            message=summary_msg,
            file_path=xml_file.path,
            node_results=node_results
        )
    
    def _compare_values(self, actual: Any, expected: Any, operator: str) -> str:
        """Compare two values using the specified operator."""
        try:
            if operator == "==":
                return "pass" if actual == expected else "fail"
            elif operator == "!=":
                return "pass" if actual != expected else "fail"
            elif operator == ">":
                return "pass" if float(actual) > float(expected) else "fail"
            elif operator == "<":
                return "pass" if float(actual) < float(expected) else "fail"
            elif operator == ">=":
                return "pass" if float(actual) >= float(expected) else "fail"
            elif operator == "<=":
                return "pass" if float(actual) <= float(expected) else "fail"
            else:
                return "fail"
        except (ValueError, TypeError):
            return "fail"