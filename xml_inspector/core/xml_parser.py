"""XML parsing and XPath evaluation functionality."""

from typing import List, Optional, Union
from pathlib import Path
import logging

from lxml import etree

from ..types import XmlFile

logger = logging.getLogger(__name__)


class XmlParseError(Exception):
    """Raised when XML parsing fails."""
    pass


class XPathEvaluationError(Exception):
    """Raised when XPath evaluation fails."""
    pass


class XmlParser:
    """Handles XML file parsing and XPath evaluation."""
    
    def __init__(self) -> None:
        """Initialize the XML parser."""
        self.parser = etree.XMLParser(recover=False, strip_cdata=False)
    
    def parse_xml_file(self, file_path: Union[str, Path]) -> XmlFile:
        """
        Parse a single XML file.
        
        Args:
            file_path: Path to the XML file
            
        Returns:
            XmlFile object containing the parsed content
            
        Raises:
            XmlParseError: If the file cannot be parsed
        """
        file_path = Path(file_path)
        
        try:
            if not file_path.exists():
                raise XmlParseError(f"File not found: {file_path}")
            
            if not file_path.is_file():
                raise XmlParseError(f"Path is not a file: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            try:
                document = etree.fromstring(xml_content.encode('utf-8'), self.parser)
            except etree.XMLSyntaxError as e:
                raise XmlParseError(f"Invalid XML in file {file_path}: {e}")
            
            return XmlFile(path=str(file_path), content=document)
            
        except Exception as e:
            if isinstance(e, XmlParseError):
                raise
            raise XmlParseError(f"Failed to parse XML file {file_path}: {e}")
    
    def parse_xml_files(self, file_paths: List[Union[str, Path]]) -> List[XmlFile]:
        """
        Parse multiple XML files.
        
        Args:
            file_paths: List of paths to XML files
            
        Returns:
            List of XmlFile objects
        """
        return [self.parse_xml_file(file_path) for file_path in file_paths]
    
    def evaluate_xpath(self, document: etree._Element, xpath_expression: str) -> Optional[str]:
        """
        Evaluate an XPath expression against an XML document.
        
        Args:
            document: The XML document (lxml Element)
            xpath_expression: XPath expression to evaluate
            
        Returns:
            String result of the XPath evaluation, or None if no match
            
        Raises:
            XPathEvaluationError: If XPath evaluation fails
        """
        try:
            result = document.xpath(xpath_expression)
            
            if not result:
                return None
            
            # Handle different types of XPath results
            if isinstance(result, list) and len(result) > 0:
                first_result = result[0]
                
                # Text node
                if isinstance(first_result, str):
                    return first_result.strip()
                
                # Element node - get text content
                if hasattr(first_result, 'text') and first_result.text is not None:
                    return first_result.text.strip()
                
                # Attribute node
                if hasattr(first_result, 'strip'):
                    return first_result.strip()
                
                # Element node with no direct text - get all text content
                if hasattr(first_result, 'itertext'):
                    text_content = ''.join(first_result.itertext()).strip()
                    return text_content if text_content else None
            
            return None
            
        except etree.XPathEvalError as e:
            raise XPathEvaluationError(f'XPath evaluation failed for expression "{xpath_expression}": {e}')
        except Exception as e:
            raise XPathEvaluationError(f'Unexpected error evaluating XPath "{xpath_expression}": {e}')