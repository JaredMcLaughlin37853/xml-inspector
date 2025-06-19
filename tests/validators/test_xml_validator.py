"""Tests for XML validator functionality."""

import pytest
from lxml import etree

from xml_inspector.validators.xml_validator import XmlValidator
from xml_inspector.types import XmlFile, SettingsDocument, Setting


class TestXmlValidator:
    """Test cases for XmlValidator class."""
    
    @pytest.fixture
    def validator(self):
        """Create XML validator instance."""
        return XmlValidator()
    
    @pytest.fixture
    def sample_xml_file(self):
        """Create sample XML file for testing."""
        xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<device>
  <settings>
    <network>
      <ip>192.168.1.100</ip>
      <port>8080</port>
      <enabled>true</enabled>
    </network>
    <security>
      <timeout>30</timeout>
    </security>
  </settings>
</device>'''
        
        document = etree.fromstring(xml_content.encode('utf-8'))
        return XmlFile(path='/test/sample.xml', content=document)
    
    def test_validate_exact_string_match(self, validator, sample_xml_file):
        """Test validation with exact string matches."""
        settings_doc = SettingsDocument(
            entity_type="device-config",
            settings=[
                Setting(
                    name="network-ip",
                    xpath="//network/ip/text()",
                    expected_value="192.168.1.100",
                    type="string"
                )
            ]
        )
        
        results = validator.validate_xml_files([sample_xml_file], settings_doc)
        
        assert len(results) == 1
        assert results[0].status == "pass"
        assert results[0].setting_name == "network-ip"
        assert results[0].actual_value == "192.168.1.100"
    
    def test_validate_number_conversion(self, validator, sample_xml_file):
        """Test validation with number type conversion."""
        settings_doc = SettingsDocument(
            entity_type="device-config",
            settings=[
                Setting(
                    name="network-port",
                    xpath="//network/port/text()",
                    expected_value=8080,
                    type="number"
                ),
                Setting(
                    name="security-timeout",
                    xpath="//security/timeout/text()",
                    expected_value=30,
                    type="number"
                )
            ]
        )
        
        results = validator.validate_xml_files([sample_xml_file], settings_doc)
        
        assert len(results) == 2
        assert all(r.status == "pass" for r in results)
        assert results[0].actual_value == 8080
        assert results[1].actual_value == 30
    
    def test_validate_boolean_conversion(self, validator, sample_xml_file):
        """Test validation with boolean type conversion."""
        settings_doc = SettingsDocument(
            entity_type="device-config",
            settings=[
                Setting(
                    name="network-enabled",
                    xpath="//network/enabled/text()",
                    expected_value=True,
                    type="boolean"
                )
            ]
        )
        
        results = validator.validate_xml_files([sample_xml_file], settings_doc)
        
        assert len(results) == 1
        assert results[0].status == "pass"
        assert results[0].actual_value is True
    
    def test_validate_value_mismatch(self, validator, sample_xml_file):
        """Test validation with mismatched values."""
        settings_doc = SettingsDocument(
            entity_type="device-config",
            settings=[
                Setting(
                    name="network-ip",
                    xpath="//network/ip/text()",
                    expected_value="192.168.1.200",  # Different value
                    type="string"
                )
            ]
        )
        
        results = validator.validate_xml_files([sample_xml_file], settings_doc)
        
        assert len(results) == 1
        assert results[0].status == "fail"
        assert results[0].actual_value == "192.168.1.100"
        assert results[0].expected_value == "192.168.1.200"
        assert "Expected 192.168.1.200, got 192.168.1.100" in results[0].message
    
    def test_validate_missing_setting(self, validator, sample_xml_file):
        """Test validation with missing settings."""
        settings_doc = SettingsDocument(
            entity_type="device-config",
            settings=[
                Setting(
                    name="missing-setting",
                    xpath="//nonexistent/text()",
                    expected_value="some-value",
                    type="string"
                )
            ]
        )
        
        results = validator.validate_xml_files([sample_xml_file], settings_doc)
        
        assert len(results) == 1
        assert results[0].status == "missing"
        assert results[0].actual_value is None
        assert "Setting not found at XPath" in results[0].message
    
    def test_validate_no_expected_value(self, validator, sample_xml_file):
        """Test validation when no expected value is provided."""
        settings_doc = SettingsDocument(
            entity_type="device-config",
            settings=[
                Setting(
                    name="network-ip",
                    xpath="//network/ip/text()",
                    expected_value=None,  # No expected value
                    type="string"
                )
            ]
        )
        
        results = validator.validate_xml_files([sample_xml_file], settings_doc)
        
        assert len(results) == 1
        assert results[0].status == "pass"  # Should pass when no expected value
        assert results[0].actual_value == "192.168.1.100"
    
    def test_validate_invalid_xpath(self, validator, sample_xml_file):
        """Test validation with invalid XPath expression."""
        settings_doc = SettingsDocument(
            entity_type="device-config",
            settings=[
                Setting(
                    name="invalid-xpath",
                    xpath="//invalid[xpath",  # Invalid XPath
                    expected_value="value",
                    type="string"
                )
            ]
        )
        
        results = validator.validate_xml_files([sample_xml_file], settings_doc)
        
        assert len(results) == 1
        assert results[0].status == "fail"
        assert "XPath evaluation error" in results[0].message
    
    def test_validate_type_conversion_error(self, validator, sample_xml_file):
        """Test validation with type conversion errors."""
        settings_doc = SettingsDocument(
            entity_type="device-config",
            settings=[
                Setting(
                    name="network-ip-as-number",
                    xpath="//network/ip/text()",  # Contains IP string
                    expected_value=123,
                    type="number"  # Try to convert IP to number
                )
            ]
        )
        
        results = validator.validate_xml_files([sample_xml_file], settings_doc)
        
        assert len(results) == 1
        assert results[0].status == "fail"
        assert "Type conversion error" in results[0].message
    
    def test_boolean_conversion_variants(self, validator):
        """Test various boolean conversion scenarios."""
        xml_content = '''<?xml version="1.0"?>
<root>
    <flag1>true</flag1>
    <flag2>false</flag2>
    <flag3>1</flag3>
    <flag4>0</flag4>
    <flag5>yes</flag5>
    <flag6>no</flag6>
</root>'''
        
        document = etree.fromstring(xml_content.encode('utf-8'))
        xml_file = XmlFile(path='/test/bool.xml', content=document)
        
        # Test various boolean values
        test_cases = [
            ("flag1", "//flag1/text()", True),
            ("flag2", "//flag2/text()", False),
            ("flag3", "//flag3/text()", True),
            ("flag4", "//flag4/text()", False),
            ("flag5", "//flag5/text()", True),
            ("flag6", "//flag6/text()", False),
        ]
        
        for name, xpath, expected in test_cases:
            settings_doc = SettingsDocument(
                entity_type="test",
                settings=[
                    Setting(
                        name=name,
                        xpath=xpath,
                        expected_value=expected,
                        type="boolean"
                    )
                ]
            )
            
            results = validator.validate_xml_files([xml_file], settings_doc)
            assert len(results) == 1
            assert results[0].status == "pass", f"Failed for {name}"
            assert results[0].actual_value == expected