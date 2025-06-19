"""Tests for settings parser functionality."""

import pytest
import tempfile
import os
import json
import yaml

from xml_inspector.parsers.settings_parser import SettingsParser, SettingsParseError
from xml_inspector.types import SettingsDocument


class TestSettingsParser:
    """Test cases for SettingsParser class."""
    
    @pytest.fixture
    def parser(self):
        """Create settings parser instance."""
        return SettingsParser()
    
    @pytest.fixture
    def sample_settings_data(self):
        """Sample settings data for testing."""
        return {
            "entityType": "device-config",
            "settings": [
                {
                    "name": "network-ip",
                    "xpath": "//network/ip/text()",
                    "expectedValue": "192.168.1.100",
                    "description": "Device IP address",
                    "type": "string"
                },
                {
                    "name": "network-port",
                    "xpath": "//network/port/text()",
                    "expectedValue": 8080,
                    "type": "number"
                }
            ],
            "metadata": {
                "version": "1.0",
                "description": "Test settings"
            }
        }
    
    def test_parse_json_settings(self, parser, sample_settings_data):
        """Test parsing JSON settings document."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_settings_data, f)
            temp_file = f.name
        
        try:
            result = parser.parse_settings_document(temp_file)
            
            assert result.entity_type == "device-config"
            assert len(result.settings) == 2
            assert result.settings[0].name == "network-ip"
            assert result.settings[0].xpath == "//network/ip/text()"
            assert result.settings[0].expected_value == "192.168.1.100"
            assert result.metadata is not None
            assert result.metadata.version == "1.0"
        finally:
            os.unlink(temp_file)
    
    def test_parse_yaml_settings(self, parser, sample_settings_data):
        """Test parsing YAML settings document."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(sample_settings_data, f)
            temp_file = f.name
        
        try:
            result = parser.parse_settings_document(temp_file)
            
            assert result.entity_type == "device-config"
            assert len(result.settings) == 2
            assert result.settings[1].name == "network-port"
            assert result.settings[1].expected_value == 8080
        finally:
            os.unlink(temp_file)
    
    def test_parse_unsupported_format(self, parser):
        """Test parsing unsupported file format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("invalid content")
            temp_file = f.name
        
        try:
            with pytest.raises(SettingsParseError, match="Unsupported settings file format"):
                parser.parse_settings_document(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_parse_missing_entity_type(self, parser):
        """Test parsing settings without entity type."""
        invalid_data = {
            "settings": []
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(SettingsParseError, match="valid entityType"):
                parser.parse_settings_document(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_parse_invalid_settings_array(self, parser):
        """Test parsing with invalid settings array."""
        invalid_data = {
            "entityType": "test",
            "settings": "not an array"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_file = f.name
        
        try:
            with pytest.raises(SettingsParseError, match="settings array"):
                parser.parse_settings_document(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_merge_settings_documents(self, parser):
        """Test merging multiple settings documents."""
        doc1 = SettingsDocument(
            entity_type="device-config",
            settings=[
                type('Setting', (), {
                    'name': 'setting1',
                    'xpath': '//test1',
                    'expected_value': 'value1',
                    'required': True,
                    'type': 'string',
                    'description': None
                })()
            ]
        )
        
        doc2 = SettingsDocument(
            entity_type="device-config",
            settings=[
                type('Setting', (), {
                    'name': 'setting2',
                    'xpath': '//test2',
                    'expected_value': 'value2',
                    'required': True,
                    'type': 'string',
                    'description': None
                })()
            ]
        )
        
        result = parser.merge_settings_documents([doc1, doc2])
        
        assert result.entity_type == "device-config"
        assert len(result.settings) == 2
        assert {s.name for s in result.settings} == {'setting1', 'setting2'}
    
    def test_merge_documents_with_override(self, parser):
        """Test merging documents with setting override."""
        from xml_inspector.types import Setting
        
        doc1 = SettingsDocument(
            entity_type="device-config",
            settings=[
                Setting(
                    name='setting1',
                    xpath='//test1',
                    expected_value='value1'
                )
            ]
        )
        
        doc2 = SettingsDocument(
            entity_type="device-config",
            settings=[
                Setting(
                    name='setting1',
                    xpath='//test1',
                    expected_value='value2'
                )
            ]
        )
        
        result = parser.merge_settings_documents([doc1, doc2])
        
        assert len(result.settings) == 1
        assert result.settings[0].expected_value == 'value2'
    
    def test_merge_documents_entity_type_mismatch(self, parser):
        """Test merging documents with mismatched entity types."""
        doc1 = SettingsDocument(
            entity_type="device-config",
            settings=[]
        )
        
        doc2 = SettingsDocument(
            entity_type="server-config",
            settings=[]
        )
        
        with pytest.raises(SettingsParseError, match="Entity type mismatch"):
            parser.merge_settings_documents([doc1, doc2])
    
    def test_parse_snake_case_fields(self, parser):
        """Test parsing with snake_case field names."""
        settings_data = {
            "entity_type": "device-config",  # snake_case instead of camelCase
            "settings": [
                {
                    "name": "test-setting",
                    "xpath": "//test/text()",
                    "expected_value": "test-value",  # snake_case
                    "type": "string"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(settings_data, f)
            temp_file = f.name
        
        try:
            result = parser.parse_settings_document(temp_file)
            
            assert result.entity_type == "device-config"
            assert len(result.settings) == 1
            assert result.settings[0].expected_value == "test-value"
        finally:
            os.unlink(temp_file)