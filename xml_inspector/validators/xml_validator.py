"""XML validation functionality."""

from typing import List, Union
import logging

from ..core.xml_parser import XmlParser, XPathEvaluationError
from ..types import (
    SettingsDocument, 
    XmlFile, 
    ValidationResult, 
    Setting, 
    SettingValue
)

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails."""
    pass


class XmlValidator:
    """Validates XML files against settings documents."""
    
    def __init__(self) -> None:
        """Initialize the XML validator."""
        self.xml_parser = XmlParser()
    
    def validate_xml_files(
        self, 
        xml_files: List[XmlFile], 
        settings_document: SettingsDocument
    ) -> List[ValidationResult]:
        """
        Validate multiple XML files against a settings document.
        
        Args:
            xml_files: List of XmlFile objects to validate
            settings_document: Settings document containing validation rules
            
        Returns:
            List of ValidationResult objects
        """
        results = []
        
        for xml_file in xml_files:
            for setting in settings_document.settings:
                result = self._validate_setting(xml_file, setting)
                results.append(result)
        
        return results
    
    def _validate_setting(self, xml_file: XmlFile, setting: Setting) -> ValidationResult:
        """
        Validate a single setting against an XML file.
        
        Args:
            xml_file: XML file to validate
            setting: Setting definition to validate against
            
        Returns:
            ValidationResult object
        """
        try:
            actual_value_str = self.xml_parser.evaluate_xpath(
                xml_file.content, 
                setting.xpath
            )
            
            if actual_value_str is None:
                return ValidationResult(
                    setting_name=setting.name,
                    xpath=setting.xpath,
                    expected_value=setting.expected_value,
                    actual_value=None,
                    status="missing",
                    message=f"Setting not found at XPath: {setting.xpath}",
                    file_path=xml_file.path
                )
            
            try:
                actual_value = self._convert_value(actual_value_str, setting.type)
            except ValueError as e:
                return ValidationResult(
                    setting_name=setting.name,
                    xpath=setting.xpath,
                    expected_value=setting.expected_value,
                    actual_value=actual_value_str,
                    status="fail",
                    message=f"Type conversion error: {e}",
                    file_path=xml_file.path
                )
            
            is_valid = self._compare_values(actual_value, setting.expected_value, setting.type)
            
            return ValidationResult(
                setting_name=setting.name,
                xpath=setting.xpath,
                expected_value=setting.expected_value,
                actual_value=actual_value,
                status="pass" if is_valid else "fail",
                message=None if is_valid else f"Expected {setting.expected_value}, got {actual_value}",
                file_path=xml_file.path
            )
            
        except XPathEvaluationError as e:
            return ValidationResult(
                setting_name=setting.name,
                xpath=setting.xpath,
                expected_value=setting.expected_value,
                actual_value=None,
                status="fail",
                message=f"XPath evaluation error: {e}",
                file_path=xml_file.path
            )
        except Exception as e:
            return ValidationResult(
                setting_name=setting.name,
                xpath=setting.xpath,
                expected_value=setting.expected_value,
                actual_value=None,
                status="fail",
                message=f"Validation error: {e}",
                file_path=xml_file.path
            )
    
    def _convert_value(self, value: str, value_type: str) -> SettingValue:
        """
        Convert string value to appropriate type.
        
        Args:
            value: String value to convert
            value_type: Target type ('string', 'number', 'boolean')
            
        Returns:
            Converted value
            
        Raises:
            ValueError: If conversion fails
        """
        value = value.strip()
        
        if value_type == "number":
            try:
                # Try integer first
                if '.' not in value:
                    return int(value)
                else:
                    return float(value)
            except ValueError:
                raise ValueError(f'Cannot convert "{value}" to number')
        
        elif value_type == "boolean":
            lower_value = value.lower()
            if lower_value in ['true', '1', 'yes', 'on']:
                return True
            elif lower_value in ['false', '0', 'no', 'off']:
                return False
            else:
                raise ValueError(f'Cannot convert "{value}" to boolean')
        
        else:  # string or default
            return value
    
    def _compare_values(
        self, 
        actual_value: SettingValue, 
        expected_value: Union[SettingValue, None], 
        value_type: str
    ) -> bool:
        """
        Compare actual and expected values.
        
        Args:
            actual_value: Actual value from XML
            expected_value: Expected value from settings
            value_type: Type of comparison to perform
            
        Returns:
            True if values match or no expected value is specified
        """
        if expected_value is None:
            return True
        
        if value_type == "number":
            # Handle number comparison with type conversion
            try:
                actual_num = float(actual_value) if actual_value is not None else 0
                expected_num = float(expected_value)
                return actual_num == expected_num
            except (ValueError, TypeError):
                return False
        
        elif value_type == "boolean":
            # Handle boolean comparison
            return bool(actual_value) == bool(expected_value)
        
        else:  # string comparison
            return str(actual_value) == str(expected_value)