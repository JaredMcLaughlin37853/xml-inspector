"""Main XML inspection engine."""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Union
import logging

from .xml_parser import XmlParser
from ..parsers.settings_parser import SettingsParser
from ..validators.xml_validator import XmlValidator
from ..reporters.report_generator import ReportGenerator, ReportFormat
from ..types import InspectionReport, SettingsDocument

logger = logging.getLogger(__name__)


@dataclass
class InspectionOptions:
    """Options for XML inspection."""
    
    xml_files: List[Union[str, Path]]
    standard_settings_file: Union[str, Path]
    project_settings_file: Optional[Union[str, Path]] = None
    entity_type: str = ""
    output_path: Optional[Union[str, Path]] = None
    output_format: ReportFormat = "json"


class InspectionError(Exception):
    """Raised when inspection fails."""
    pass


class XmlInspector:
    """Main class for XML inspection and validation."""
    
    def __init__(self) -> None:
        """Initialize the XML inspector."""
        self.xml_parser = XmlParser()
        self.settings_parser = SettingsParser()
        self.validator = XmlValidator()
        self.report_generator = ReportGenerator()
    
    def inspect(self, options: InspectionOptions) -> InspectionReport:
        """
        Perform XML inspection based on provided options.
        
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
            
            # Parse settings documents
            settings_documents: List[SettingsDocument] = []
            settings_documents.append(
                self.settings_parser.parse_settings_document(options.standard_settings_file)
            )
            
            if options.project_settings_file:
                settings_documents.append(
                    self.settings_parser.parse_settings_document(options.project_settings_file)
                )
            
            # Merge settings if multiple documents
            if len(settings_documents) > 1:
                merged_settings = self.settings_parser.merge_settings_documents(settings_documents)
            else:
                merged_settings = settings_documents[0]
            
            # Validate entity type if specified
            if options.entity_type and merged_settings.entity_type != options.entity_type:
                raise InspectionError(
                    f"Entity type mismatch: expected {options.entity_type}, "
                    f"got {merged_settings.entity_type}"
                )
            
            # Perform validation
            validation_results = self.validator.validate_xml_files(xml_files, merged_settings)
            
            # Generate report
            settings_file_paths = [str(options.standard_settings_file)]
            if options.project_settings_file:
                settings_file_paths.append(str(options.project_settings_file))
            
            report = self.report_generator.generate_report(
                validation_results,
                [str(path) for path in options.xml_files],
                settings_file_paths,
                merged_settings.entity_type
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
            raise InspectionError(f"Inspection failed: {e}")
    
    def validate_settings_document(self, file_path: Union[str, Path]) -> SettingsDocument:
        """
        Validate a settings document structure.
        
        Args:
            file_path: Path to the settings document
            
        Returns:
            Parsed and validated SettingsDocument
            
        Raises:
            InspectionError: If validation fails
        """
        try:
            return self.settings_parser.parse_settings_document(file_path)
        except Exception as e:
            raise InspectionError(f"Settings document validation failed: {e}")