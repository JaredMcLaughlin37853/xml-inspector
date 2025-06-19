"""Tests for XML parser functionality."""

import pytest
from pathlib import Path
import tempfile
import os

from xml_inspector.core.xml_parser import XmlParser, XmlParseError, XPathEvaluationError


class TestXmlParser:
    """Test cases for XmlParser class."""
    
    @pytest.fixture
    def parser(self):
        """Create XML parser instance."""
        return XmlParser()
    
    @pytest.fixture
    def sample_xml_content(self):
        """Sample XML content for testing."""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<device>
  <settings>
    <network>
      <ip>192.168.1.100</ip>
      <port>8080</port>
      <enabled>true</enabled>
    </network>
    <security>
      <encryption>AES256</encryption>
      <timeout>30</timeout>
    </security>
  </settings>
</device>'''
    
    @pytest.fixture
    def sample_xml_file(self, sample_xml_content):
        """Create a temporary XML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(sample_xml_content)
            temp_file = f.name
        
        yield temp_file
        
        # Cleanup
        os.unlink(temp_file)
    
    def test_parse_xml_file_success(self, parser, sample_xml_file):
        """Test successful XML file parsing."""
        result = parser.parse_xml_file(sample_xml_file)
        
        assert result.path == sample_xml_file
        assert result.content is not None
        assert result.content.tag == 'device'
    
    def test_parse_xml_file_not_found(self, parser):
        """Test parsing non-existent file."""
        with pytest.raises(XmlParseError, match="File not found"):
            parser.parse_xml_file("/non/existent/file.xml")
    
    def test_parse_xml_file_invalid_xml(self, parser):
        """Test parsing invalid XML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write('<invalid><xml></invalid>')
            temp_file = f.name
        
        try:
            with pytest.raises(XmlParseError, match="Invalid XML"):
                parser.parse_xml_file(temp_file)
        finally:
            os.unlink(temp_file)
    
    def test_parse_xml_files_multiple(self, parser, sample_xml_content):
        """Test parsing multiple XML files."""
        # Create two temporary files
        temp_files = []
        for i in range(2):
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                f.write(sample_xml_content)
                temp_files.append(f.name)
        
        try:
            results = parser.parse_xml_files(temp_files)
            
            assert len(results) == 2
            for result in results:
                assert result.content.tag == 'device'
        finally:
            for temp_file in temp_files:
                os.unlink(temp_file)
    
    def test_evaluate_xpath_text_content(self, parser, sample_xml_file):
        """Test XPath evaluation for text content."""
        xml_file = parser.parse_xml_file(sample_xml_file)
        
        ip = parser.evaluate_xpath(xml_file.content, '//network/ip/text()')
        assert ip == '192.168.1.100'
        
        port = parser.evaluate_xpath(xml_file.content, '//network/port/text()')
        assert port == '8080'
        
        enabled = parser.evaluate_xpath(xml_file.content, '//network/enabled/text()')
        assert enabled == 'true'
    
    def test_evaluate_xpath_no_match(self, parser, sample_xml_file):
        """Test XPath evaluation with no matches."""
        xml_file = parser.parse_xml_file(sample_xml_file)
        
        result = parser.evaluate_xpath(xml_file.content, '//nonexistent/text()')
        assert result is None
    
    def test_evaluate_xpath_invalid_expression(self, parser, sample_xml_file):
        """Test XPath evaluation with invalid expression."""
        xml_file = parser.parse_xml_file(sample_xml_file)
        
        with pytest.raises(XPathEvaluationError):
            parser.evaluate_xpath(xml_file.content, '//invalid[xpath')
    
    def test_evaluate_xpath_attribute(self, parser):
        """Test XPath evaluation for attributes."""
        xml_content = '''<?xml version="1.0"?>
<root>
    <item id="test123" name="sample"/>
</root>'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            f.write(xml_content)
            temp_file = f.name
        
        try:
            xml_file = parser.parse_xml_file(temp_file)
            
            item_id = parser.evaluate_xpath(xml_file.content, '//item/@id')
            assert item_id == 'test123'
            
            item_name = parser.evaluate_xpath(xml_file.content, '//item/@name')
            assert item_name == 'sample'
        finally:
            os.unlink(temp_file)