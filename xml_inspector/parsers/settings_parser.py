"""DSL document parsing functionality."""

import json
from pathlib import Path
from typing import Union
import logging

from ..types import DslValidationSettings
from .dsl_parser import DslParser

logger = logging.getLogger(__name__)


class SettingsParseError(Exception):
    """Raised when DSL document parsing fails."""
    pass


class SettingsParser:
    """Handles parsing of DSL validation documents in JSON format."""
    
    def __init__(self):
        """Initialize the DSL parser."""
        self.dsl_parser = DslParser()
    
    def parse_settings_document(self, file_path: Union[str, Path]) -> DslValidationSettings:
        """
        Parse a DSL validation document from JSON file.
        
        Args:
            file_path: Path to the DSL document
            
        Returns:
            DslValidationSettings object
            
        Raises:
            SettingsParseError: If parsing fails
        """
        file_path = Path(file_path)
        
        try:
            if not file_path.exists():
                raise SettingsParseError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if file_path.suffix.lower() != '.json':
                raise SettingsParseError(f"Only JSON format is supported for DSL documents: {file_path.suffix}")
            
            data = json.loads(content)
            
            # Validate DSL format
            if 'validationSettings' not in data:
                raise SettingsParseError("DSL document must contain 'validationSettings' array")
            
            return self.dsl_parser._validate_dsl_document(data)
            
        except SettingsParseError:
            raise
        except json.JSONDecodeError as e:
            raise SettingsParseError(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            raise SettingsParseError(f"Failed to parse DSL document {file_path}: {e}")