"""Tests for DSL parser functionality."""

import pytest
import tempfile
import os
import json

from xml_inspector.parsers.settings_parser import SettingsParser, SettingsParseError
from xml_inspector.types import DslValidationSettings


class TestSettingsParser:
    """Test cases for DSL SettingsParser class."""
    
    @pytest.fixture
    def parser(self):
        """Create DSL parser instance."""
        return SettingsParser()
    
    @pytest.fixture
    def sample_dsl_data(self):
        """Sample DSL data for testing."""
        return {
            "validationSettings": [
                {
                    "id": "test_rule_1",
                    "description": "Test existence rule",
                    "type": "existence",
                    "severity": "error",
                    "expression": {
                        "op": "value",
                        "xpath": "//test/node/text()"
                    }
                },
                {
                    "id": "test_rule_2", 
                    "description": "Test comparison rule",
                    "type": "comparison",
                    "severity": "warning",
                    "expression": {
                        "op": "value",
                        "xpath": "//test/count/text()",
                        "dataType": "integer"
                    },
                    "operator": ">=",
                    "value": 5
                }
            ]
        }
    
    def test_parse_dsl_json_file(self, parser, sample_dsl_data):
        """Test parsing valid DSL JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_dsl_data, f)
            temp_path = f.name
        
        try:
            result = parser.parse_settings_document(temp_path)
            assert isinstance(result, DslValidationSettings)
            assert len(result.validation_settings) == 2
            assert result.validation_settings[0].id == "test_rule_1"
            assert result.validation_settings[0].type == "existence"
            assert result.validation_settings[1].id == "test_rule_2"
            assert result.validation_settings[1].type == "comparison"
        finally:
            os.unlink(temp_path)
    
    def test_parse_invalid_json(self, parser):
        """Test parsing invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')
            temp_path = f.name
        
        try:
            with pytest.raises(SettingsParseError, match="Invalid JSON"):
                parser.parse_settings_document(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_parse_missing_validation_settings(self, parser):
        """Test parsing JSON without validationSettings."""
        invalid_data = {"otherField": "value"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_path = f.name
        
        try:
            with pytest.raises(SettingsParseError, match="must contain 'validationSettings'"):
                parser.parse_settings_document(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_parse_non_json_file(self, parser):
        """Test parsing non-JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write('test: value')
            temp_path = f.name
        
        try:
            with pytest.raises(SettingsParseError, match="Only JSON format is supported"):
                parser.parse_settings_document(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_parse_nonexistent_file(self, parser):
        """Test parsing non-existent file."""
        with pytest.raises(SettingsParseError, match="File not found"):
            parser.parse_settings_document("/nonexistent/file.json")