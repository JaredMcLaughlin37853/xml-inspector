"""Settings document parsing functionality."""

import json
from pathlib import Path
from typing import Any, Dict, List, Union
import logging

import yaml

from ..types import Setting, SettingsDocument, SettingsMetadata

logger = logging.getLogger(__name__)


class SettingsParseError(Exception):
    """Raised when settings document parsing fails."""
    pass


class SettingsParser:
    """Handles parsing of settings documents in JSON and YAML formats."""
    
    def parse_settings_document(self, file_path: Union[str, Path]) -> SettingsDocument:
        """
        Parse a settings document from JSON or YAML file.
        
        Args:
            file_path: Path to the settings document
            
        Returns:
            SettingsDocument object
            
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
                data = self._parse_json_settings(content)
            elif extension in ['.yaml', '.yml']:
                data = self._parse_yaml_settings(content)
            else:
                raise SettingsParseError(f"Unsupported settings file format: {extension}")
            
            return self._validate_settings_document(data)
            
        except SettingsParseError:
            raise
        except Exception as e:
            raise SettingsParseError(f"Failed to parse settings document {file_path}: {e}")
    
    def parse_multiple_settings_documents(self, file_paths: List[Union[str, Path]]) -> List[SettingsDocument]:
        """
        Parse multiple settings documents.
        
        Args:
            file_paths: List of paths to settings documents
            
        Returns:
            List of SettingsDocument objects
        """
        return [self.parse_settings_document(file_path) for file_path in file_paths]
    
    def merge_settings_documents(self, documents: List[SettingsDocument]) -> SettingsDocument:
        """
        Merge multiple settings documents into one.
        
        Args:
            documents: List of SettingsDocument objects to merge
            
        Returns:
            Merged SettingsDocument
            
        Raises:
            SettingsParseError: If documents cannot be merged
        """
        if not documents:
            raise SettingsParseError("No settings documents provided for merging")
        
        base_document = documents[0]
        merged_settings: List[Setting] = list(base_document.settings)
        
        for i in range(1, len(documents)):
            current_doc = documents[i]
            
            if current_doc.entity_type != base_document.entity_type:
                raise SettingsParseError(
                    f"Entity type mismatch: {base_document.entity_type} vs {current_doc.entity_type}"
                )
            
            for setting in current_doc.settings:
                # Find existing setting with same name
                existing_index = None
                for j, existing_setting in enumerate(merged_settings):
                    if existing_setting.name == setting.name:
                        existing_index = j
                        break
                
                if existing_index is not None:
                    # Override existing setting
                    merged_settings[existing_index] = setting
                else:
                    # Add new setting
                    merged_settings.append(setting)
        
        # Create merged metadata
        merged_metadata = SettingsMetadata(
            version=base_document.metadata.version if base_document.metadata else None,
            description="Merged settings document",
            author=base_document.metadata.author if base_document.metadata else None
        )
        
        return SettingsDocument(
            entity_type=base_document.entity_type,
            settings=merged_settings,
            metadata=merged_metadata
        )
    
    def _parse_json_settings(self, content: str) -> Dict[str, Any]:
        """Parse JSON settings content."""
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            raise SettingsParseError(f"Invalid JSON: {e}")
    
    def _parse_yaml_settings(self, content: str) -> Dict[str, Any]:
        """Parse YAML settings content."""
        try:
            return yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise SettingsParseError(f"Invalid YAML: {e}")
    
    def _validate_settings_document(self, data: Dict[str, Any]) -> SettingsDocument:
        """
        Validate and convert parsed data to SettingsDocument.
        
        Args:
            data: Parsed settings data
            
        Returns:
            SettingsDocument object
            
        Raises:
            SettingsParseError: If validation fails
        """
        if not isinstance(data, dict):
            raise SettingsParseError("Settings document must be an object")
        
        # Validate entity_type
        entity_type = data.get('entityType') or data.get('entity_type')
        if not entity_type or not isinstance(entity_type, str):
            raise SettingsParseError("Settings document must have a valid entityType or entity_type")
        
        # Validate settings array
        settings_data = data.get('settings', [])
        if not isinstance(settings_data, list):
            raise SettingsParseError("Settings document must have a settings array")
        
        settings = []
        for i, setting_data in enumerate(settings_data):
            if not isinstance(setting_data, dict):
                raise SettingsParseError(f"Setting at index {i} must be an object")
            
            # Validate required fields
            name = setting_data.get('name')
            if not name or not isinstance(name, str):
                raise SettingsParseError(f"Setting at index {i} must have a valid name")
            
            xpath = setting_data.get('xpath')
            if not xpath or not isinstance(xpath, str):
                raise SettingsParseError(f"Setting at index {i} must have a valid xpath")
            
            # Extract and validate optional fields
            expected_value = setting_data.get('expectedValue') or setting_data.get('expected_value')
            description = setting_data.get('description')
            required = setting_data.get('required', True)
            setting_type = setting_data.get('type', 'string')
            
            if setting_type not in ['string', 'number', 'boolean']:
                setting_type = 'string'
            
            settings.append(Setting(
                name=name,
                xpath=xpath,
                expected_value=expected_value,
                description=description,
                required=required,
                type=setting_type  # type: ignore
            ))
        
        # Parse metadata
        metadata_data = data.get('metadata', {})
        metadata = None
        if metadata_data:
            metadata = SettingsMetadata(
                version=metadata_data.get('version'),
                description=metadata_data.get('description'),
                author=metadata_data.get('author')
            )
        
        return SettingsDocument(
            entity_type=entity_type,
            settings=settings,
            metadata=metadata
        )