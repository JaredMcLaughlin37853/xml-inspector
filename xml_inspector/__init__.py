"""
XML Inspector - A quality assurance tool for XML files.

This package provides functionality to validate XML files against 
standardized requirements and generate comprehensive reports.
"""

from .core.inspector import XmlInspector
from .core.xml_parser import XmlParser
from .parsers.settings_parser import SettingsParser
from .validators.xml_validator import XmlValidator
from .reporters.report_generator import ReportGenerator

__version__ = "1.0.0"
__all__ = [
    "XmlInspector",
    "XmlParser", 
    "SettingsParser",
    "XmlValidator",
    "ReportGenerator",
]