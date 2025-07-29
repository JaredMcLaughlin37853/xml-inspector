"""
Example of how to create and register custom validation rules.

This file demonstrates how to:
1. Write custom Python validation functions
2. Register them with the validator
3. Use them in a validation settings JSON file
"""

from xml_inspector import XmlInspector
from xml_inspector.core.inspector import InspectionOptions
from xml_inspector.types import XmlFile, Result, Value
# No built-in validation rules to import


def check_required_elements(xml_file: XmlFile) -> Result:
    """
    Custom rule: Check that required XML elements are present.
    """
    try:
        root = xml_file.content
        
        # Define required elements for this validation
        required_elements = [
            "//Configuration",
            "//Device", 
            "//Points"
        ]
        
        missing_elements = []
        for xpath in required_elements:
            elements = root.xpath(xpath)
            if not elements:
                missing_elements.append(xpath.replace("//", ""))
        
        if missing_elements:
            return Result(
                status="fail",
                returned_value=Value(type="list", value=missing_elements),
                expected_value=Value(type="string", value="All required elements present"),
                message=f"Missing required elements: {', '.join(missing_elements)}"
            )
        else:
            return Result(
                status="pass",
                returned_value=Value(type="string", value="All required elements found"),
                expected_value=Value(type="string", value="All required elements present"),
                message="All required elements are present"
            )
            
    except Exception as e:
        return Result(
            status="fail",
            returned_value=None,
            expected_value=None,
            message=f"Validation error: {e}"
        )


def validate_numeric_ranges(xml_file: XmlFile) -> Result:
    """
    Custom rule: Check that numeric values fall within expected ranges.
    """
    try:
        root = xml_file.content
        
        # Check various numeric ranges
        validation_errors = []
        
        # Example: Check that all port numbers are valid (1-65535)
        port_elements = root.xpath("//Port/text()")
        for port_text in port_elements:
            try:
                port = int(port_text)
                if port < 1 or port > 65535:
                    validation_errors.append(f"Invalid port number: {port} (must be 1-65535)")
            except ValueError:
                validation_errors.append(f"Non-numeric port value: {port_text}")
        
        # Example: Check that percentages are 0-100
        percentage_elements = root.xpath("//Percentage/text()")
        for pct_text in percentage_elements:
            try:
                pct = float(pct_text)
                if pct < 0 or pct > 100:
                    validation_errors.append(f"Invalid percentage: {pct} (must be 0-100)")
            except ValueError:
                validation_errors.append(f"Non-numeric percentage value: {pct_text}")
        
        if validation_errors:
            return Result(
                status="fail",
                returned_value=Value(type="list", value=validation_errors),
                expected_value=Value(type="string", value="All numeric values in valid ranges"),
                message=f"Found {len(validation_errors)} numeric range violations"
            )
        else:
            return Result(
                status="pass",
                returned_value=Value(type="string", value="All numeric values valid"),
                expected_value=Value(type="string", value="All numeric values in valid ranges"),
                message="All numeric values are within expected ranges"
            )
            
    except Exception as e:
        return Result(
            status="fail",
            returned_value=None,
            expected_value=None,
            message=f"Validation error: {e}"
        )


def check_attribute_consistency(xml_file: XmlFile) -> Result:
    """
    Custom rule: Verify that related attributes have consistent values.
    """
    try:
        root = xml_file.content
        
        # Example: Check that device count matches actual device elements
        config_elements = root.xpath("//Configuration")
        consistency_errors = []
        
        for config in config_elements:
            device_count_attr = config.get("deviceCount")
            if device_count_attr:
                try:
                    expected_count = int(device_count_attr)
                    actual_devices = len(config.xpath(".//Device"))
                    
                    if expected_count != actual_devices:
                        consistency_errors.append(
                            f"Device count mismatch: attribute says {expected_count}, "
                            f"but found {actual_devices} devices"
                        )
                except ValueError:
                    consistency_errors.append(f"Invalid deviceCount attribute: {device_count_attr}")
        
        if consistency_errors:
            return Result(
                status="fail",
                returned_value=Value(type="list", value=consistency_errors),
                expected_value=Value(type="string", value="All attributes consistent"),
                message=f"Found {len(consistency_errors)} consistency issues"
            )
        else:
            return Result(
                status="pass",
                returned_value=Value(type="string", value="All attributes consistent"),
                expected_value=Value(type="string", value="All attributes consistent"),
                message="All related attributes are consistent"
            )
            
    except Exception as e:
        return Result(
            status="fail",
            returned_value=None,
            expected_value=None,
            message=f"Validation error: {e}"
        )


def main():
    """
    Example of how to use custom validation rules.
    """
    # Create inspector instance
    inspector = XmlInspector()
    validator = inspector.get_validator()
    
    # No built-in rules to register
    
    # Register custom rules
    validator.register_function(
        rule_id="check_required_elements",
        description="Validates that required XML elements are present",
        validation_function=check_required_elements,
        severity="error"
    )
    
    validator.register_function(
        rule_id="validate_numeric_ranges", 
        description="Checks that numeric values fall within expected ranges",
        validation_function=validate_numeric_ranges,
        severity="warning"
    )
    
    validator.register_function(
        rule_id="check_attribute_consistency",
        description="Verifies that related attributes have consistent values", 
        validation_function=check_attribute_consistency,
        severity="error"
    )
    
    # Now you can use the custom-validation-rules.json settings file
    options = InspectionOptions(
        xml_files=["examples/xml-files/sample-data.xml"],
        settings_file="examples/settings/custom-validation-rules.json",
        output_path="custom_validation_report.json",
        output_format="json"
    )
    
    # Perform inspection
    try:
        report = inspector.inspect(options)
        print(f"Validation completed!")
        print(f"Total checks: {report.summary.total_checks}")
        print(f"Passed: {report.summary.passed}")
        print(f"Failed: {report.summary.failed}")
        print(f"Missing: {report.summary.missing}")
    except Exception as e:
        print(f"Validation failed: {e}")


if __name__ == "__main__":
    main()