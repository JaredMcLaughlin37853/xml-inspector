"""Main XML inspection engine for DSL validation."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union
import logging

from .xml_parser import XmlParser
from ..parsers.settings_parser import SettingsParser
from ..validators.dsl_validator import DslValidator
from ..reporters.report_generator import ReportGenerator, ReportFormat
from ..types import InspectionReport, DslValidationSettings

logger = logging.getLogger(__name__)


@dataclass
class InspectionOptions:
    """Options for DSL-based XML inspection."""
    
    xml_files: List[Union[str, Path]]
    dsl_settings_file: Union[str, Path]
    output_path: Optional[Union[str, Path]] = None
    output_format: ReportFormat = "json"


class InspectionError(Exception):
    """Raised when inspection fails."""
    pass


class XmlInspector:
    """Main class for DSL-based XML inspection and validation."""
    
    def __init__(self) -> None:
        """Initialize the XML inspector."""
        self.xml_parser = XmlParser()
        self.settings_parser = SettingsParser()
        self.dsl_validator = DslValidator()
        self.report_generator = ReportGenerator()
    
    def inspect(self, options: InspectionOptions) -> InspectionReport:
        """
        Perform DSL-based XML inspection.
        
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
            
            # Parse DSL settings document
            dsl_settings = self.settings_parser.parse_settings_document(options.dsl_settings_file)
            
            # Perform DSL validation
            validation_results = self.dsl_validator.validate_xml_files(xml_files, dsl_settings)
            
            # Generate report
            report = self.report_generator.generate_report(
                validation_results,
                [str(path) for path in options.xml_files],
                [str(options.dsl_settings_file)]
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
            raise InspectionError(f"DSL-based inspection failed: {e}")
    
    def validate_settings_document(self, file_path: Union[str, Path]) -> DslValidationSettings:
        """
        Validate a DSL document structure.
        
        Args:
            file_path: Path to the DSL document
            
        Returns:
            Parsed and validated DslValidationSettings
            
        Raises:
            InspectionError: If validation fails
        """
        try:
            return self.settings_parser.parse_settings_document(file_path)
        except Exception as e:
            raise InspectionError(f"DSL document validation failed: {e}")