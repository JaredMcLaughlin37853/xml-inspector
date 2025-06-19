"""Tests for main inspector functionality."""

import pytest
import tempfile
import os
import json

from xml_inspector.core.inspector import XmlInspector, InspectionOptions, InspectionError


class TestXmlInspector:
    """Test cases for XmlInspector class."""
    
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
  </network>
</device>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        yield temp_file
        os.unlink(temp_file)
    
    @pytest.fixture
    def sample_settings_file(self):
        """Create sample settings file."""
        settings_data = {
            "entityType": "device-config",
            "settings": [
                {
                    "name": "network-ip",
                    "xpath": "//network/ip/text()",
                    "expectedValue": "192.168.1.100",
                    "type": "string"
                },
                {
                    "name": "network-port",
                    "xpath": "//network/port/text()",
                    "expectedValue": 8080,
                    "type": "number"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(settings_data, f)
            temp_file = f.name
        
        yield temp_file
        os.unlink(temp_file)
    
    def test_inspect_basic_success(self, inspector, sample_xml_file, sample_settings_file):
        """Test basic successful inspection."""
        options = InspectionOptions(
            xml_files=[sample_xml_file],
            standard_settings_file=sample_settings_file,
            entity_type="device-config"
        )
        
        report = inspector.inspect(options)
        
        assert report.summary.total_checks == 2
        assert report.summary.passed == 2
        assert report.summary.failed == 0
        assert report.summary.missing == 0
        assert report.metadata.entity_type == "device-config"
        assert len(report.results) == 2
    
    def test_inspect_with_project_settings(self, inspector, sample_xml_file, sample_settings_file):
        """Test inspection with project-specific settings."""
        # Create project settings file
        project_settings = {
            "entityType": "device-config",
            "settings": [
                {
                    "name": "additional-setting",
                    "xpath": "//network/ip/text()",
                    "expectedValue": "192.168.1.100",
                    "type": "string"
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(project_settings, f)
            project_file = f.name
        
        try:
            options = InspectionOptions(
                xml_files=[sample_xml_file],
                standard_settings_file=sample_settings_file,
                project_settings_file=project_file,
                entity_type="device-config"
            )
            
            report = inspector.inspect(options)
            
            # Should have settings from both documents
            assert report.summary.total_checks == 3  # 2 standard + 1 project
            assert len(report.results) == 3
        finally:
            os.unlink(project_file)
    
    def test_inspect_entity_type_mismatch(self, inspector, sample_xml_file, sample_settings_file):
        """Test inspection with mismatched entity type."""
        options = InspectionOptions(
            xml_files=[sample_xml_file],
            standard_settings_file=sample_settings_file,
            entity_type="wrong-type"  # Different from settings file
        )
        
        with pytest.raises(InspectionError, match="Entity type mismatch"):
            inspector.inspect(options)
    
    def test_inspect_with_output_file(self, inspector, sample_xml_file, sample_settings_file):
        """Test inspection with output file generation."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            output_file = f.name
        
        try:
            options = InspectionOptions(
                xml_files=[sample_xml_file],
                standard_settings_file=sample_settings_file,
                entity_type="device-config",
                output_path=output_file,
                output_format="json"
            )
            
            report = inspector.inspect(options)
            
            assert os.path.exists(output_file)
            
            # Verify output file content
            with open(output_file, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["summary"]["total_checks"] == 2
            assert saved_data["metadata"]["entity_type"] == "device-config"
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)
    
    def test_inspect_invalid_xml_file(self, inspector, sample_settings_file):
        """Test inspection with invalid XML file."""
        options = InspectionOptions(
            xml_files=["/nonexistent/file.xml"],
            standard_settings_file=sample_settings_file,
            entity_type="device-config"
        )
        
        with pytest.raises(InspectionError):
            inspector.inspect(options)
    
    def test_inspect_invalid_settings_file(self, inspector, sample_xml_file):
        """Test inspection with invalid settings file."""
        options = InspectionOptions(
            xml_files=[sample_xml_file],
            standard_settings_file="/nonexistent/settings.json",
            entity_type="device-config"
        )
        
        with pytest.raises(InspectionError):
            inspector.inspect(options)
    
    def test_validate_settings_document_success(self, inspector, sample_settings_file):
        """Test successful settings document validation."""
        result = inspector.validate_settings_document(sample_settings_file)
        
        assert result.entity_type == "device-config"
        assert len(result.settings) == 2
        assert result.settings[0].name == "network-ip"
    
    def test_validate_settings_document_invalid(self, inspector):
        """Test settings document validation with invalid file."""
        with pytest.raises(InspectionError):
            inspector.validate_settings_document("/nonexistent/settings.json")
    
    def test_inspect_multiple_xml_files(self, inspector, sample_settings_file):
        """Test inspection with multiple XML files."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<device>
  <network>
    <ip>192.168.1.100</ip>
    <port>8080</port>
  </network>
</device>'''
        
        # Create two XML files
        temp_files = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(xml_content)
                temp_files.append(f.name)
        
        try:
            options = InspectionOptions(
                xml_files=temp_files,
                standard_settings_file=sample_settings_file,
                entity_type="device-config"
            )
            
            report = inspector.inspect(options)
            
            # Should have results for both files (2 settings × 2 files = 4 results)
            assert report.summary.total_checks == 4
            assert len(report.results) == 4
            
            # Check that both file paths are represented
            file_paths = {result.file_path for result in report.results}
            assert len(file_paths) == 2
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)