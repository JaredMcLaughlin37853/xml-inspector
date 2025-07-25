"""DSL Expression Evaluator for XML Inspector."""

import re
from typing import Any, List, Union, Optional
from datetime import datetime
from decimal import Decimal
import logging

from lxml import etree
from ..types import DslExpression, DslValidationRule, DslCondition

logger = logging.getLogger(__name__)


class DslEvaluationError(Exception):
    """Raised when DSL expression evaluation fails."""
    pass


class DslEvaluator:
    """Evaluates DSL expressions against XML documents."""
    
    def __init__(self):
        """Initialize the DSL evaluator."""
        self.operations = {
            'count': self._op_count,
            'sum': self._op_sum,
            'average': self._op_average,
            'value': self._op_value,
            'literal': self._op_literal,
            'add': self._op_add,
            'subtract': self._op_subtract,
            'multiply': self._op_multiply,
            'divide': self._op_divide,
            'if': self._op_if,
            'and': self._op_and,
            'or': self._op_or,
            'not': self._op_not,
            'concat': self._op_concat,
            'map': self._op_map,
            '==': self._op_eq,
            '!=': self._op_ne,
            '>': self._op_gt,
            '<': self._op_lt,
            '>=': self._op_gte,
            '<=': self._op_lte,
        }
    
    def evaluate_expression(self, expression: DslExpression, xml_root: etree._Element, 
                          context_node: Optional[etree._Element] = None) -> Any:
        """
        Evaluate a DSL expression against an XML document.
        
        Args:
            expression: The DSL expression to evaluate
            xml_root: The root XML element
            context_node: Optional context node for relative XPath queries
            
        Returns:
            The result of the expression evaluation
            
        Raises:
            DslEvaluationError: If evaluation fails
        """
        try:
            if expression.op not in self.operations:
                raise DslEvaluationError(f"Unknown operation: {expression.op}")
            
            operation = self.operations[expression.op]
            return operation(expression, xml_root, context_node)
            
        except Exception as e:
            if isinstance(e, DslEvaluationError):
                raise
            raise DslEvaluationError(f"Failed to evaluate expression {expression.op}: {e}")
    
    def evaluate_conditions(self, conditions: List[DslCondition], 
                          xml_root: etree._Element) -> bool:
        """
        Evaluate all conditions and return True if all pass.
        
        Args:
            conditions: List of conditions to evaluate
            xml_root: The root XML element
            
        Returns:
            True if all conditions pass, False otherwise
        """
        for condition in conditions:
            if not self._evaluate_condition(condition, xml_root):
                return False
        return True
    
    def _evaluate_condition(self, condition: DslCondition, xml_root: etree._Element) -> bool:
        """Evaluate a single condition."""
        try:
            if condition.type == "exists":
                nodes = xml_root.xpath(condition.xpath)
                return len(nodes) > 0
            
            elif condition.type == "attributeEquals":
                nodes = xml_root.xpath(condition.xpath)
                if not nodes:
                    return False
                
                node = nodes[0]
                if not hasattr(node, 'get'):
                    return False
                
                attr_value = node.get(condition.attribute)
                return attr_value == condition.value
            
            return False
            
        except Exception as e:
            logger.warning(f"Condition evaluation failed: {e}")
            return False
    
    def _get_xpath_expression(self, expression: DslExpression, xml_root: etree._Element,
                            context_node: Optional[etree._Element] = None) -> str:
        """Get XPath string from either xpath or xpathExpression field."""
        if expression.xpath:
            return expression.xpath
        elif expression.xpath_expression:
            try:
                result = self.evaluate_expression(expression.xpath_expression, xml_root, context_node)
                xpath_str = str(result)
                
                # Validate that the result looks like a reasonable XPath
                if not xpath_str or xpath_str.isspace():
                    raise DslEvaluationError("Dynamic XPath expression evaluated to empty string")
                    
                logger.debug(f"Dynamic XPath evaluated to: {xpath_str}")
                return xpath_str
            except Exception as e:
                raise DslEvaluationError(f"Failed to evaluate dynamic XPath expression: {e}")
        else:
            raise DslEvaluationError("Expression must have either xpath or xpathExpression")
    
    def _convert_value(self, value: Any, data_type: Optional[str] = None) -> Any:
        """Convert value to specified data type."""
        if data_type == "integer":
            return int(float(str(value)))
        elif data_type == "decimal":
            return float(str(value))
        elif data_type == "date":
            if isinstance(value, str):
                return datetime.fromisoformat(value.replace('Z', '+00:00'))
            return value
        else:  # string or no type specified
            return str(value)
    
    # Operation implementations
    def _op_count(self, expr: DslExpression, xml_root: etree._Element, 
                  context_node: Optional[etree._Element] = None) -> int:
        """Count nodes matching XPath."""
        xpath = self._get_xpath_expression(expr, xml_root, context_node)
        search_root = context_node if context_node is not None else xml_root
        nodes = search_root.xpath(xpath)
        return len(nodes)
    
    def _op_sum(self, expr: DslExpression, xml_root: etree._Element, 
                context_node: Optional[etree._Element] = None) -> float:
        """Sum numeric values."""
        if expr.args:
            values = []
            for arg in expr.args:
                if isinstance(arg, DslExpression):
                    result = self.evaluate_expression(arg, xml_root, context_node)
                    if isinstance(result, list):
                        values.extend(result)
                    else:
                        values.append(result)
                else:
                    values.append(arg)
        else:
            xpath = self._get_xpath_expression(expr, xml_root, context_node)
            search_root = context_node if context_node is not None else xml_root
            nodes = search_root.xpath(xpath)
            values = []
            for node in nodes:
                if hasattr(node, 'text') and node.text:
                    values.append(float(node.text))
                elif isinstance(node, str):
                    values.append(float(node))
                elif isinstance(node, (int, float)):
                    values.append(float(node))
                else:
                    values.append(0)
        
        return sum(float(v) for v in values)
    
    def _op_average(self, expr: DslExpression, xml_root: etree._Element, 
                    context_node: Optional[etree._Element] = None) -> float:
        """Calculate average of numeric values."""
        total = self._op_sum(expr, xml_root, context_node)
        count = len(expr.args) if expr.args else self._op_count(expr, xml_root, context_node)
        return total / count if count > 0 else 0
    
    def _op_value(self, expr: DslExpression, xml_root: etree._Element, 
                  context_node: Optional[etree._Element] = None) -> Any:
        """Get scalar node value."""
        xpath = self._get_xpath_expression(expr, xml_root, context_node)
        search_root = context_node if context_node is not None else xml_root
        nodes = search_root.xpath(xpath)
        
        if not nodes:
            return None
        
        node = nodes[0]
        if hasattr(node, 'text') and node.text:
            value = node.text
        elif isinstance(node, (str, int, float)):
            value = node
        else:
            value = str(node)
        
        return self._convert_value(value, expr.data_type)
    
    def _op_literal(self, expr: DslExpression, xml_root: etree._Element, 
                    context_node: Optional[etree._Element] = None) -> Any:
        """Return literal value."""
        return self._convert_value(expr.value, expr.data_type)
    
    def _op_add(self, expr: DslExpression, xml_root: etree._Element, 
                context_node: Optional[etree._Element] = None) -> float:
        """Add arguments."""
        if not expr.args:
            return 0
        
        result = 0
        for arg in expr.args:
            if isinstance(arg, DslExpression):
                value = self.evaluate_expression(arg, xml_root, context_node)
            else:
                value = arg
            result += float(value)
        
        return result
    
    def _op_subtract(self, expr: DslExpression, xml_root: etree._Element, 
                     context_node: Optional[etree._Element] = None) -> float:
        """Subtract arguments."""
        if not expr.args or len(expr.args) < 2:
            return 0
        
        first_arg = expr.args[0]
        if isinstance(first_arg, DslExpression):
            result = float(self.evaluate_expression(first_arg, xml_root, context_node))
        else:
            result = float(first_arg)
        
        for arg in expr.args[1:]:
            if isinstance(arg, DslExpression):
                value = self.evaluate_expression(arg, xml_root, context_node)
            else:
                value = arg
            result -= float(value)
        
        return result
    
    def _op_multiply(self, expr: DslExpression, xml_root: etree._Element, 
                     context_node: Optional[etree._Element] = None) -> float:
        """Multiply arguments."""
        if not expr.args:
            return 1
        
        result = 1
        for arg in expr.args:
            if isinstance(arg, DslExpression):
                value = self.evaluate_expression(arg, xml_root, context_node)
            else:
                value = arg
            result *= float(value)
        
        return result
    
    def _op_divide(self, expr: DslExpression, xml_root: etree._Element, 
                   context_node: Optional[etree._Element] = None) -> float:
        """Divide arguments."""
        if not expr.args or len(expr.args) < 2:
            return 0
        
        first_arg = expr.args[0]
        if isinstance(first_arg, DslExpression):
            result = float(self.evaluate_expression(first_arg, xml_root, context_node))
        else:
            result = float(first_arg)
        
        for arg in expr.args[1:]:
            if isinstance(arg, DslExpression):
                value = self.evaluate_expression(arg, xml_root, context_node)
            else:
                value = arg
            divisor = float(value)
            if divisor == 0:
                raise DslEvaluationError("Division by zero")
            result /= divisor
        
        return result
    
    def _op_if(self, expr: DslExpression, xml_root: etree._Element, 
               context_node: Optional[etree._Element] = None) -> Any:
        """Conditional operation."""
        if not expr.args or len(expr.args) < 3:
            raise DslEvaluationError("if operation requires 3 arguments")
        
        condition = expr.args[0]
        then_expr = expr.args[1]
        else_expr = expr.args[2]
        
        if isinstance(condition, DslExpression):
            condition_result = self.evaluate_expression(condition, xml_root, context_node)
        else:
            condition_result = condition
        
        if condition_result:
            if isinstance(then_expr, DslExpression):
                return self.evaluate_expression(then_expr, xml_root, context_node)
            else:
                return then_expr
        else:
            if isinstance(else_expr, DslExpression):
                return self.evaluate_expression(else_expr, xml_root, context_node)
            else:
                return else_expr
    
    def _op_and(self, expr: DslExpression, xml_root: etree._Element, 
                context_node: Optional[etree._Element] = None) -> bool:
        """Logical AND."""
        if not expr.args:
            return True
        
        for arg in expr.args:
            if isinstance(arg, DslExpression):
                result = self.evaluate_expression(arg, xml_root, context_node)
            else:
                result = arg
            if not result:
                return False
        
        return True
    
    def _op_or(self, expr: DslExpression, xml_root: etree._Element, 
               context_node: Optional[etree._Element] = None) -> bool:
        """Logical OR."""
        if not expr.args:
            return False
        
        for arg in expr.args:
            if isinstance(arg, DslExpression):
                result = self.evaluate_expression(arg, xml_root, context_node)
            else:
                result = arg
            if result:
                return True
        
        return False
    
    def _op_not(self, expr: DslExpression, xml_root: etree._Element, 
                context_node: Optional[etree._Element] = None) -> bool:
        """Logical NOT."""
        if not expr.args or len(expr.args) != 1:
            raise DslEvaluationError("not operation requires exactly 1 argument")
        
        arg = expr.args[0]
        if isinstance(arg, DslExpression):
            result = self.evaluate_expression(arg, xml_root, context_node)
        else:
            result = arg
        
        return not result
    
    def _op_concat(self, expr: DslExpression, xml_root: etree._Element, 
                   context_node: Optional[etree._Element] = None) -> str:
        """String concatenation."""
        if not expr.args:
            return ""
        
        result = ""
        for arg in expr.args:
            if isinstance(arg, DslExpression):
                value = self.evaluate_expression(arg, xml_root, context_node)
            else:
                value = arg
            result += str(value)
        
        return result
    
    def _op_map(self, expr: DslExpression, xml_root: etree._Element, 
                context_node: Optional[etree._Element] = None) -> List[Any]:
        """Map operation - iterate over nodes and evaluate expression per node."""
        if not expr.expression:
            raise DslEvaluationError("map operation requires expression")
        
        # Get XPath either from static xpath or dynamic xpath_expression
        try:
            xpath_str = self._get_xpath_expression(expr, xml_root, context_node)
        except Exception as e:
            raise DslEvaluationError(f"Failed to get XPath for map operation: {e}")
        
        search_root = context_node if context_node is not None else xml_root
        
        try:
            nodes = search_root.xpath(xpath_str)
        except Exception as e:
            logger.warning(f"XPath evaluation failed in map operation: {xpath_str} - {e}")
            return []
        
        results = []
        for node in nodes:
            try:
                result = self.evaluate_expression(expr.expression, xml_root, node)
                results.append(result)
            except Exception as e:
                logger.warning(f"Map evaluation failed for node: {e}")
                continue
        
        return results
    
    def _op_eq(self, expr: DslExpression, xml_root: etree._Element, 
               context_node: Optional[etree._Element] = None) -> bool:
        """Equality comparison."""
        if not expr.args or len(expr.args) != 2:
            raise DslEvaluationError("== operation requires exactly 2 arguments")
        
        left = expr.args[0]
        right = expr.args[1]
        
        if isinstance(left, DslExpression):
            left_val = self.evaluate_expression(left, xml_root, context_node)
        else:
            left_val = left
        
        if isinstance(right, DslExpression):
            right_val = self.evaluate_expression(right, xml_root, context_node)
        else:
            right_val = right
        
        return left_val == right_val
    
    def _op_ne(self, expr: DslExpression, xml_root: etree._Element, 
               context_node: Optional[etree._Element] = None) -> bool:
        """Inequality comparison."""
        return not self._op_eq(expr, xml_root, context_node)
    
    def _op_gt(self, expr: DslExpression, xml_root: etree._Element, 
               context_node: Optional[etree._Element] = None) -> bool:
        """Greater than comparison."""
        if not expr.args or len(expr.args) != 2:
            raise DslEvaluationError("> operation requires exactly 2 arguments")
        
        left = expr.args[0]
        right = expr.args[1]
        
        if isinstance(left, DslExpression):
            left_val = self.evaluate_expression(left, xml_root, context_node)
        else:
            left_val = left
        
        if isinstance(right, DslExpression):
            right_val = self.evaluate_expression(right, xml_root, context_node)
        else:
            right_val = right
        
        return float(left_val) > float(right_val)
    
    def _op_lt(self, expr: DslExpression, xml_root: etree._Element, 
               context_node: Optional[etree._Element] = None) -> bool:
        """Less than comparison."""
        if not expr.args or len(expr.args) != 2:
            raise DslEvaluationError("< operation requires exactly 2 arguments")
        
        left = expr.args[0]
        right = expr.args[1]
        
        if isinstance(left, DslExpression):
            left_val = self.evaluate_expression(left, xml_root, context_node)
        else:
            left_val = left
        
        if isinstance(right, DslExpression):
            right_val = self.evaluate_expression(right, xml_root, context_node)
        else:
            right_val = right
        
        return float(left_val) < float(right_val)
    
    def _op_gte(self, expr: DslExpression, xml_root: etree._Element, 
                context_node: Optional[etree._Element] = None) -> bool:
        """Greater than or equal comparison."""
        if not expr.args or len(expr.args) != 2:
            raise DslEvaluationError(">= operation requires exactly 2 arguments")
        
        left = expr.args[0]
        right = expr.args[1]
        
        if isinstance(left, DslExpression):
            left_val = self.evaluate_expression(left, xml_root, context_node)
        else:
            left_val = left
        
        if isinstance(right, DslExpression):
            right_val = self.evaluate_expression(right, xml_root, context_node)
        else:
            right_val = right
        
        return float(left_val) >= float(right_val)
    
    def _op_lte(self, expr: DslExpression, xml_root: etree._Element, 
                context_node: Optional[etree._Element] = None) -> bool:
        """Less than or equal comparison."""
        if not expr.args or len(expr.args) != 2:
            raise DslEvaluationError("<= operation requires exactly 2 arguments")
        
        left = expr.args[0]
        right = expr.args[1]
        
        if isinstance(left, DslExpression):
            left_val = self.evaluate_expression(left, xml_root, context_node)
        else:
            left_val = left
        
        if isinstance(right, DslExpression):
            right_val = self.evaluate_expression(right, xml_root, context_node)
        else:
            right_val = right
        
        return float(left_val) <= float(right_val)