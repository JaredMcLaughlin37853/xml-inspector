"""Report generation functionality."""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Literal, Union
import logging

from jinja2 import Template

from ..types import (
    InspectionReport,
    ValidationResult,
    ValidationSummary,
    ReportMetadata
)

logger = logging.getLogger(__name__)

ReportFormat = Literal["json", "html"]


class ReportGenerationError(Exception):
    """Raised when report generation fails."""
    pass


class ReportGenerator:
    """Generates inspection reports in various formats."""
    
    def __init__(self) -> None:
        """Initialize the report generator."""
        pass
    
    def generate_report(
        self,
        results: List[ValidationResult],
        xml_files: List[str],
        validation_rules: List[str]
    ) -> InspectionReport:
        """
        Generate an inspection report from Python validation results.
        
        Args:
            results: List of validation results
            xml_files: List of XML file paths that were validated
            validation_rules: List of validation rule IDs used
            
        Returns:
            InspectionReport object
        """
        summary = self._generate_summary(results)
        metadata = ReportMetadata(
            timestamp=datetime.now().isoformat(),
            xml_files=xml_files,
            validation_rules=validation_rules
        )
        
        return InspectionReport(
            summary=summary,
            results=results,
            metadata=metadata
        )
    
    def save_report_to_file(
        self,
        report: InspectionReport,
        output_path: Union[str, Path],
        format: ReportFormat = "json"
    ) -> None:
        """
        Save report to file in specified format.
        
        Args:
            report: InspectionReport to save
            output_path: Path where to save the report
            format: Output format ('json' or 'html')
            
        Raises:
            ReportGenerationError: If report generation fails
        """
        output_path = Path(output_path)
        
        try:
            # Create directory if it doesn't exist
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if format == "json":
                self._save_json_report(report, output_path)
            elif format == "html":
                self._save_html_report(report, output_path)
            else:
                raise ReportGenerationError(f"Unsupported report format: {format}")
                
        except Exception as e:
            if isinstance(e, ReportGenerationError):
                raise
            raise ReportGenerationError(f"Failed to save report to {output_path}: {e}")
    
    def _generate_summary(self, results: List[ValidationResult]) -> ValidationSummary:
        """Generate summary statistics from validation results."""
        total_checks = len(results)
        passed = sum(1 for r in results if self._extract_status(r.result) == "pass")
        failed = sum(1 for r in results if self._extract_status(r.result) == "fail")
        missing = sum(1 for r in results if self._extract_status(r.result) == "missing")
        
        return ValidationSummary(
            total_checks=total_checks,
            passed=passed,
            failed=failed,
            missing=missing
        )
    
    def _extract_status(self, result) -> str:
        """
        Extract status from result object, supporting various custom formats.
        
        Args:
            result: Result object in any custom format
            
        Returns:
            Status string ("pass", "fail", or "missing")
        """
        # Handle dictionary format with status field
        if isinstance(result, dict):
            if 'status' in result:
                return result['status']
            # Handle legacy formats with overall_status
            elif 'overall_status' in result:
                status = result['overall_status'].lower()
                if status in ['pass', 'passed']:
                    return "pass"
                elif status in ['fail', 'failed', 'error']:
                    return "fail"
                else:
                    return "missing"
        
        # Handle objects with status attribute
        if hasattr(result, 'status'):
            return result.status
        
        # Default to fail if status cannot be determined
        return "fail"
    
    def _extract_message(self, result) -> str:
        """Extract message from result object, supporting various formats."""
        # Handle dictionary format
        if isinstance(result, dict):
            if 'message' in result:
                return result['message']
            elif 'error' in result:
                return result['error']
        
        # Handle objects with message attribute
        if hasattr(result, 'message'):
            return result.message
        
        return "No message available"
    
    def _get_result_display_value(self, result) -> str:
        """Get a display-friendly representation of the result."""
        # Handle dictionary format - look for common value fields
        if isinstance(result, dict):
            # Try common field names
            for field in ['returned_value', 'calculated_points', 'value', 'result']:
                if field in result:
                    return str(result[field])
            # If it's a complex dictionary, show a summary
            return f"Complex result ({len(result)} fields)"
        
        # For other formats, convert to string
        return str(result)
    
    def _save_json_report(self, report: InspectionReport, output_path: Path) -> None:
        """Save report as JSON file."""
        def convert_to_dict(obj):
            """Convert dataclass to dictionary for JSON serialization."""
            if hasattr(obj, '__dict__'):
                return {k: convert_to_dict(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [convert_to_dict(item) for item in obj]
            else:
                return obj
        
        report_dict = convert_to_dict(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)
    
    def _save_html_report(self, report: InspectionReport, output_path: Path) -> None:
        """Save report as HTML file."""
        html_content = self._generate_html_content(report)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _generate_html_content(self, report: InspectionReport) -> str:
        """Generate HTML content for the report."""
        # Separate results by status using flexible status extraction
        passed_results = [r for r in report.results if self._extract_status(r.result) == "pass"]
        failed_results = [r for r in report.results if self._extract_status(r.result) == "fail"]
        missing_results = [r for r in report.results if self._extract_status(r.result) == "missing"]
        
        # Format timestamp for display
        try:
            timestamp = datetime.fromisoformat(report.metadata.timestamp)
            formatted_timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_timestamp = report.metadata.timestamp
        
        html_template = Template('''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XML Inspector Report</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            line-height: 1.6;
        }
        .header { 
            border-bottom: 2px solid #333; 
            padding-bottom: 10px; 
            margin-bottom: 20px; 
        }
        .summary { 
            background-color: #f5f5f5; 
            padding: 15px; 
            border-radius: 5px; 
            margin-bottom: 20px; 
        }
        .summary-item { 
            display: inline-block; 
            margin-right: 20px; 
            font-weight: bold;
        }
        .pass { color: #28a745; }
        .fail { color: #dc3545; }
        .missing { color: #ffc107; }
        .results-section { 
            margin-bottom: 30px; 
        }
        .result-item { 
            border: 1px solid #ddd; 
            padding: 12px; 
            margin: 8px 0; 
            border-radius: 4px; 
            background-color: #fafafa;
        }
        .result-pass { border-left: 4px solid #28a745; }
        .result-fail { border-left: 4px solid #dc3545; }
        .result-missing { border-left: 4px solid #ffc107; }
        .metadata { 
            font-size: 0.9em; 
            color: #666; 
            margin-bottom: 10px;
        }
        .setting-name {
            font-weight: bold;
            font-size: 1.1em;
            margin-bottom: 5px;
        }
        .setting-details {
            margin-left: 10px;
            font-size: 0.9em;
        }
        .file-path {
            color: #666;
            font-style: italic;
        }
        h1 { color: #333; }
        h2 { 
            margin-top: 25px;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>XML Inspector Report</h1>
        <div class="metadata">
            <p><strong>Entity Type:</strong> {{ metadata.entity_type }}</p>
            <p><strong>Generated:</strong> {{ formatted_timestamp }}</p>
            <p><strong>XML Files:</strong> {{ metadata.xml_files | join(', ') }}</p>
            <p><strong>Settings Documents:</strong> {{ metadata.settings_documents | join(', ') }}</p>
        </div>
    </div>

    <div class="summary">
        <h2>Summary</h2>
        <div class="summary-item">Total Checks: {{ summary.total_checks }}</div>
        <div class="summary-item pass">Passed: {{ summary.passed }}</div>
        <div class="summary-item fail">Failed: {{ summary.failed }}</div>
        <div class="summary-item missing">Missing: {{ summary.missing }}</div>
    </div>

    {% if failed_results %}
    <div class="results-section">
        <h2 class="fail">Failed Checks ({{ failed_results|length }})</h2>
        {% for result in failed_results %}
        <div class="result-item result-fail">
            <div class="setting-name">{{ result.rule_description }}</div>
            <div class="setting-details">
                <div class="file-path">{{ result.file_path }}</div>
                <div><strong>Rule ID:</strong> {{ result.rule_id }}</div>
                <div><strong>Result:</strong> {{ get_result_display_value(result.result) }}</div>
                <div><strong>Message:</strong> {{ extract_message(result.result) }}</div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if missing_results %}
    <div class="results-section">
        <h2 class="missing">Missing Settings ({{ missing_results|length }})</h2>
        {% for result in missing_results %}
        <div class="result-item result-missing">
            <div class="setting-name">{{ result.rule_description }}</div>
            <div class="setting-details">
                <div class="file-path">{{ result.file_path }}</div>
                <div><strong>Rule ID:</strong> {{ result.rule_id }}</div>
                <div><strong>Message:</strong> {{ extract_message(result.result) }}</div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}

    {% if passed_results %}
    <div class="results-section">
        <h2 class="pass">Passed Checks ({{ passed_results|length }})</h2>
        {% for result in passed_results %}
        <div class="result-item result-pass">
            <div class="setting-name">{{ result.rule_description }}</div>
            <div class="setting-details">
                <div class="file-path">{{ result.file_path }}</div>
                <div><strong>Rule ID:</strong> {{ result.rule_id }}</div>
                <div><strong>Result:</strong> {{ get_result_display_value(result.result) }}</div>
            </div>
        </div>
        {% endfor %}
    </div>
    {% endif %}

</body>
</html>''')
        
        return html_template.render(
            summary=report.summary,
            metadata=report.metadata,
            formatted_timestamp=formatted_timestamp,
            failed_results=failed_results,
            missing_results=missing_results,
            passed_results=passed_results,
            extract_message=self._extract_message,
            get_result_display_value=self._get_result_display_value
        )