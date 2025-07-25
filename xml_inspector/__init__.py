"""
XML Inspector - A DSL-based quality assurance tool for XML files.

This package provides functionality to validate XML files using 
DSL (Domain Specific Language) expressions and generate comprehensive reports.
"""

from .core.inspector import XmlInspector, InspectionOptions
from .core.xml_parser import XmlParser
from .parsers.settings_parser import SettingsParser
from .validators.dsl_validator import DslValidator
from .reporters.report_generator import ReportGenerator

__version__ = "1.0.0"
__all__ = [
    "XmlInspector",
    "InspectionOptions",
    "XmlParser", 
    "SettingsParser",
    "DslValidator",
    "ReportGenerator",
]