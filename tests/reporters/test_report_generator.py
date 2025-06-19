"""Tests for report generator functionality."""

import pytest
import tempfile
import os
import json
from pathlib import Path

from xml_inspector.reporters.report_generator import ReportGenerator, ReportGenerationError
from xml_inspector.types import ValidationResult, InspectionReport


class TestReportGenerator:
    """Test cases for ReportGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create report generator instance."""
        return ReportGenerator()
    
    @pytest.fixture
    def sample_validation_results(self):
        """Sample validation results for testing."""
        return [
            ValidationResult(
                setting_name="network-ip",
                xpath="//network/ip/text()",
                expected_value="192.168.1.100",
                actual_value="192.168.1.100",
                status="pass",
                message=None,
                file_path="/test/sample.xml"
            ),
            ValidationResult(
                setting_name="network-port",
                xpath="//network/port/text()",
                expected_value=8080,
                actual_value=9090,
                status="fail",
                message="Expected 8080, got 9090",
                file_path="/test/sample.xml"
            ),
            ValidationResult(
                setting_name="missing-setting",
                xpath="//missing/text()",
                expected_value="value",
                actual_value=None,
                status="missing",
                message="Setting not found",
                file_path="/test/sample.xml"
            )
        ]
    
    def test_generate_report(self, generator, sample_validation_results):
        """Test basic report generation."""
        report = generator.generate_report(
            sample_validation_results,
            ["/test/sample.xml"],
            ["/test/settings.json"],
            "device-config"
        )
        
        assert report.summary.total_checks == 3
        assert report.summary.passed == 1
        assert report.summary.failed == 1
        assert report.summary.missing == 1
        assert report.results == sample_validation_results
        assert report.metadata.entity_type == "device-config"
        assert report.metadata.xml_files == ["/test/sample.xml"]
        assert report.metadata.settings_documents == ["/test/settings.json"]
        assert report.metadata.timestamp is not None
    
    def test_save_json_report(self, generator, sample_validation_results):
        """Test saving JSON report."""
        report = generator.generate_report(
            sample_validation_results,
            ["/test/sample.xml"],
            ["/test/settings.json"],
            "test-config"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            generator.save_report_to_file(report, output_path, "json")
            
            assert os.path.exists(output_path)
            
            # Verify content
            with open(output_path, 'r') as f:
                saved_data = json.load(f)
            
            assert saved_data["summary"]["total_checks"] == 3
            assert saved_data["summary"]["passed"] == 1
            assert len(saved_data["results"]) == 3
            assert saved_data["metadata"]["entity_type"] == "test-config"
        finally:
            os.unlink(output_path)
    
    def test_save_html_report(self, generator, sample_validation_results):
        """Test saving HTML report."""
        report = generator.generate_report(
            sample_validation_results,
            ["/test/sample.xml"],
            ["/test/settings.json"],
            "test-config"
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            generator.save_report_to_file(report, output_path, "html")
            
            assert os.path.exists(output_path)
            
            # Verify HTML content
            with open(output_path, 'r') as f:
                html_content = f.read()
            
            assert "<!DOCTYPE html>" in html_content
            assert "XML Inspector Report" in html_content
            assert "network-ip" in html_content
            assert "Failed Checks" in html_content
            assert "Missing Settings" in html_content
            assert "Passed Checks" in html_content
        finally:
            os.unlink(output_path)
    
    def test_save_report_creates_directory(self, generator, sample_validation_results):
        """Test that saving report creates directories if they don't exist."""
        report = generator.generate_report(
            sample_validation_results,
            [],
            [],
            "test-config"
        )
        
        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "path" / "report.json"
            
            generator.save_report_to_file(report, nested_path, "json")
            
            assert nested_path.exists()
            
            # Verify content
            with open(nested_path, 'r') as f:
                saved_data = json.load(f)
            assert saved_data["summary"]["total_checks"] == 3
    
    def test_save_report_unsupported_format(self, generator, sample_validation_results):
        """Test saving report with unsupported format."""
        report = generator.generate_report(
            sample_validation_results,
            [],
            [],
            "test-config"
        )
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            output_path = f.name
        
        try:
            with pytest.raises(ReportGenerationError, match="Unsupported report format"):
                generator.save_report_to_file(report, output_path, "xml")  # type: ignore
        finally:
            os.unlink(output_path)
    
    def test_generate_summary_all_passed(self, generator):
        """Test summary generation with all passed results."""
        results = [
            ValidationResult(
                setting_name="test1",
                xpath="//test1",
                expected_value="value1",
                actual_value="value1",
                status="pass",
                message=None,
                file_path="/test.xml"
            ),
            ValidationResult(
                setting_name="test2",
                xpath="//test2",
                expected_value="value2",
                actual_value="value2",
                status="pass",
                message=None,
                file_path="/test.xml"
            )
        ]
        
        summary = generator._generate_summary(results)
        
        assert summary.total_checks == 2
        assert summary.passed == 2
        assert summary.failed == 0
        assert summary.missing == 0
    
    def test_generate_summary_empty_results(self, generator):
        """Test summary generation with empty results."""
        summary = generator._generate_summary([])
        
        assert summary.total_checks == 0
        assert summary.passed == 0
        assert summary.failed == 0
        assert summary.missing == 0
    
    def test_html_report_contains_all_sections(self, generator):
        """Test that HTML report contains all expected sections."""
        results = [
            ValidationResult("pass1", "//pass1", "val", "val", "pass", None, "/test.xml"),
            ValidationResult("fail1", "//fail1", "val1", "val2", "fail", "Mismatch", "/test.xml"),
            ValidationResult("miss1", "//miss1", "val", None, "missing", "Not found", "/test.xml"),
        ]
        
        report = generator.generate_report(results, ["/test.xml"], ["/settings.json"], "test")
        html_content = generator._generate_html_content(report)
        
        # Check that all sections are present
        assert "Summary" in html_content
        assert "Failed Checks (1)" in html_content
        assert "Missing Settings (1)" in html_content
        assert "Passed Checks (1)" in html_content
        
        # Check that specific results are included
        assert "pass1" in html_content
        assert "fail1" in html_content
        assert "miss1" in html_content