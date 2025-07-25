"""Tests for main DSL inspector functionality."""

import pytest
import tempfile
import os
import json

from xml_inspector.core.inspector import XmlInspector, InspectionOptions, InspectionError


class TestXmlInspector:
    """Test cases for DSL XmlInspector class."""
    
    @pytest.fixture
    def inspector(self):
        """Create XML inspector instance."""
        return XmlInspector()
    
    @pytest.fixture
    def sample_xml_file(self):
        """Create sample XML file."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<device>
  <network>
    <ip>192.168.1.100</ip>
    <port>8080</port>
    <enabled>true</enabled>
  </network>
  <count>5</count>
</device>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            return f.name
    
    @pytest.fixture
    def sample_dsl_file(self):
        """Create sample DSL settings file."""
        dsl_content = {
            "validationSettings": [
                {
                    "id": "test_ip_existence",
                    "description": "Check IP address exists",
                    "type": "existence",
                    "severity": "error",
                    "expression": {
                        "op": "value",
                        "xpath": "//network/ip/text()"
                    }
                },
                {
                    "id": "test_port_range",
                    "description": "Check port is in valid range",
                    "type": "range",
                    "severity": "warning",
                    "expression": {
                        "op": "value",
                        "xpath": "//network/port/text()",
                        "dataType": "integer"
                    },
                    "minValue": "1",
                    "maxValue": "65535",
                    "dataType": "integer"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(dsl_content, f)
            return f.name
    
    def test_inspect_with_dsl_settings(self, inspector, sample_xml_file, sample_dsl_file):
        """Test inspection with DSL settings."""
        options = InspectionOptions(
            xml_files=[sample_xml_file],
            dsl_settings_file=sample_dsl_file,
            output_format="json"
        )
        
        report = inspector.inspect(options)
        
        assert report is not None
        assert report.summary.total_checks >= 0
        assert len(report.results) >= 0
        assert len(report.metadata.xml_files) == 1
        assert len(report.metadata.dsl_documents) == 1
        
        # Clean up
        os.unlink(sample_xml_file)
        os.unlink(sample_dsl_file)
    
    def test_validate_dsl_document(self, inspector, sample_dsl_file):
        """Test DSL document validation."""
        result = inspector.validate_settings_document(sample_dsl_file)
        
        assert result is not None
        assert len(result.validation_settings) == 2
        assert result.validation_settings[0].id == "test_ip_existence"
        assert result.validation_settings[1].id == "test_port_range"
        
        # Clean up
        os.unlink(sample_dsl_file)
    
    def test_inspect_with_nonexistent_xml_file(self, inspector, sample_dsl_file):
        """Test inspection with non-existent XML file."""
        options = InspectionOptions(
            xml_files=["/nonexistent/file.xml"],
            dsl_settings_file=sample_dsl_file
        )
        
        with pytest.raises(InspectionError):
            inspector.inspect(options)
        
        # Clean up
        os.unlink(sample_dsl_file)
    
    def test_inspect_with_nonexistent_dsl_file(self, inspector, sample_xml_file):
        """Test inspection with non-existent DSL file."""
        options = InspectionOptions(
            xml_files=[sample_xml_file],
            dsl_settings_file="/nonexistent/dsl.json"
        )
        
        with pytest.raises(InspectionError):
            inspector.inspect(options)
        
        # Clean up
        os.unlink(sample_xml_file)