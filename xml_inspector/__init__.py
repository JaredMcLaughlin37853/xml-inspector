"""
XML Inspector - A Python-based quality assurance tool for XML files.

This package provides functionality to validate XML files using 
Python validation functions and generate comprehensive reports.
"""

from .core.inspector import XmlInspector, InspectionOptions
from .core.xml_parser import XmlParser
from .parsers.python_settings_parser import PythonSettingsParser
from .validators.python_validator import PythonValidator
from .reporters.report_generator import ReportGenerator

__version__ = "1.0.0"
__all__ = [
    "XmlInspector",
    "InspectionOptions",
    "XmlParser", 
    "PythonSettingsParser",
    "PythonValidator",
    "ReportGenerator",
]