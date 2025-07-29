"""Main XML inspection engine for Python validation."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union
import logging

from .xml_parser import XmlParser
from ..parsers.python_settings_parser import PythonSettingsParser
from ..validators.python_validator import PythonValidator
from ..reporters.report_generator import ReportGenerator, ReportFormat
from ..types import InspectionReport, ValidationSettings

logger = logging.getLogger(__name__)


@dataclass
class InspectionOptions:
    """Options for Python-based XML inspection."""
    
    xml_files: List[Union[str, Path]]
    settings_file: Union[str, Path]
    output_path: Optional[Union[str, Path]] = None
    output_format: ReportFormat = "json"


class InspectionError(Exception):
    """Raised when inspection fails."""
    pass


class XmlInspector:
    """Main class for Python-based XML inspection and validation."""
    
    def __init__(self) -> None:
        """Initialize the XML inspector."""
        self.xml_parser = XmlParser()
        self.settings_parser = PythonSettingsParser()
        self.validator = PythonValidator()
        self.report_generator = ReportGenerator()
    
    def inspect(self, options: InspectionOptions) -> InspectionReport:
        """
        Perform Python-based XML inspection.
        
        Args:
            options: InspectionOptions containing all inspection parameters
            
        Returns:
            InspectionReport containing validation results
            
        Raises:
            InspectionError: If inspection fails
        """
        try:
            # Parse XML files
            xml_files = self.xml_parser.parse_xml_files(options.xml_files)
            
            # Parse settings document
            settings = self.settings_parser.parse_settings_document(options.settings_file)
            
            # Perform Python validation
            validation_results = self.validator.validate_xml_files(xml_files, settings.validation_rules)
            
            # Generate report
            report = self.report_generator.generate_report(
                validation_results,
                [str(path) for path in options.xml_files],
                settings.validation_rules
            )
            
            # Save report if output path specified
            if options.output_path:
                self.report_generator.save_report_to_file(
                    report, 
                    options.output_path, 
                    options.output_format
                )
            
            return report
            
        except Exception as e:
            if isinstance(e, InspectionError):
                raise
            raise InspectionError(f"Python-based inspection failed: {e}")
    
    def validate_settings_document(self, file_path: Union[str, Path]) -> ValidationSettings:
        """
        Validate a settings document structure.
        
        Args:
            file_path: Path to the settings document
            
        Returns:
            Parsed and validated ValidationSettings
            
        Raises:
            InspectionError: If validation fails
        """
        try:
            return self.settings_parser.parse_settings_document(file_path)
        except Exception as e:
            raise InspectionError(f"Settings document validation failed: {e}")
    
    def get_validator(self) -> PythonValidator:
        """
        Get the validator instance for registering rules.
        
        Returns:
            PythonValidator instance
        """
        return self.validator