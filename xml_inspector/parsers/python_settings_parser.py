"""Python validation settings parsing functionality."""

import json
from pathlib import Path
from typing import Union
import logging

import yaml

from ..types import ValidationSettings

logger = logging.getLogger(__name__)


class SettingsParseError(Exception):
    """Raised when settings parsing fails."""
    pass


class PythonSettingsParser:
    """Handles parsing of Python validation settings documents."""
    
    def parse_settings_document(self, file_path: Union[str, Path]) -> ValidationSettings:
        """
        Parse a Python validation settings document from JSON or YAML file.
        
        Args:
            file_path: Path to the settings document
            
        Returns:
            ValidationSettings object
            
        Raises:
            SettingsParseError: If parsing fails
        """
        file_path = Path(file_path)
        
        try:
            if not file_path.exists():
                raise SettingsParseError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            extension = file_path.suffix.lower()
            
            if extension == '.json':
                data = self._parse_json_content(content)
            elif extension in ['.yaml', '.yml']:
                data = self._parse_yaml_content(content)
            else:
                raise SettingsParseError(f"Unsupported settings file format: {extension}")
            
            return self._validate_settings_document(data)
            
        except SettingsParseError:
            raise
        except Exception as e:
            raise SettingsParseError(f"Failed to parse settings document {file_path}: {e}")
    
    def _parse_json_content(self, content: str) -> dict:
        """Parse JSON content."""
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise SettingsParseError(f"Invalid JSON: {e}")
    
    def _parse_yaml_content(self, content: str) -> dict:
        """Parse YAML content."""
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise SettingsParseError(f"Invalid YAML: {e}")
    
    def _validate_settings_document(self, data: dict) -> ValidationSettings:
        """
        Validate and convert parsed data to ValidationSettings.
        
        Args:
            data: Parsed settings data
            
        Returns:
            ValidationSettings object
            
        Raises:
            SettingsParseError: If validation fails
        """
        if not isinstance(data, dict):
            raise SettingsParseError("Settings document must be an object")
        
        # Validate validationRules array
        validation_rules_data = data.get('validationRules', [])
        if not isinstance(validation_rules_data, list):
            raise SettingsParseError("Settings document must have a validationRules array")
        
        # Validate that all entries are strings (rule IDs)
        for i, rule_id in enumerate(validation_rules_data):
            if not isinstance(rule_id, str):
                raise SettingsParseError(f"Validation rule at index {i} must be a string (rule ID)")
        
        return ValidationSettings(validation_rules=validation_rules_data)