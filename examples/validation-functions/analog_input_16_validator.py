"""
Validation function for Analog Input 16 point count comparison between
DNP DCA application and System Point Database application.

This function calculates the total adjusted points for "Analog Input 16" type
from the DNP DCA configuration and compares it with the corresponding record
in the DCA Configuration List.
"""

from lxml import etree
from typing import Dict, List
from xml_inspector.types import XmlFile


def validate_analog_input_16_points_adapted(xml_file: XmlFile) -> Dict[str, any]:
    """
    Validates Analog Input 16 point counts between DCA Configuration and 
    DCA Configuration List using xml-inspector interface.
    
    Args:
        xml_file: XmlFile object containing parsed XML content
        
    Returns:
        Dictionary with detailed validation results in custom format
    """
    try:
        # Return the detailed dictionary format directly
        # This gives the function designer full control over result presentation
        result = _validate_analog_input_16_points(xml_file.content)
        
        # Add a status field for the report generator to extract
        if result['overall_status'] == 'PASS':
            result['status'] = 'pass'
        elif result['overall_status'] == 'FAIL':
            result['status'] = 'fail'
        else:  # ERROR
            result['status'] = 'fail'
        
        return result
        
    except Exception as e:
        return {
            'validation_type': 'analog_input_16_point_count',
            'overall_status': 'ERROR',
            'status': 'fail',
            'error': f"Validation function error: {str(e)}",
            'details': [],
            'summary': {
                'total_config_records': 0,
                'passed': 0,
                'failed': 0
            }
        }


def _validate_analog_input_16_points(xml_root: etree._Element) -> Dict[str, any]:
    """
    Internal validation function that validates Analog Input 16 point counts between 
    DCA Configuration and DCA Configuration List.
    
    Args:
        xml_root: Root element of the parsed XML document
        
    Returns:
        Dictionary containing validation results with details for each DCA record
    """
    results = {
        'validation_type': 'analog_input_16_point_count',
        'overall_status': 'PASS',
        'details': [],
        'summary': {
            'total_config_records': 0,
            'passed': 0,
            'failed': 0
        }
    }
    
    try:
        # Get all DCA Configuration records
        cfg_table_records = xml_root.xpath("//B023_CFG/Record")
        results['summary']['total_config_records'] = len(cfg_table_records)

        # Get DCA Configuration List records for comparison
        syspt_table_records = xml_root.xpath("//B008_DCA/Record")
        print(f"DCA Table Record Count: {len(syspt_table_records)}")
        if not syspt_table_records:
            results['overall_status'] = 'ERROR'
            results['error'] = 'No B008_DCA node found in XML'
            return results
            
        #dca_list_records = dca_list_records[0].xpath("Record")
        
        for cfg_table_record in cfg_table_records:
            record_result = _process_dca_record(xml_root, cfg_table_record, syspt_table_records)
            results['details'].append(record_result)
            
            if record_result['status'] == 'PASS':
                results['summary']['passed'] += 1
            else:
                results['summary']['failed'] += 1
                results['overall_status'] = 'FAIL'
                
    except Exception as e:
        results['overall_status'] = 'ERROR'
        results['error'] = f'Error processing XML: {str(e)}'
    
    return results


def _process_dca_record(xml_root: etree._Element, dca_record: etree._Element, 
                       dca_list_records: List[etree._Element]) -> Dict[str, any]:
    """
    Process a single DCA Configuration record to calculate and validate 
    Analog Input 16 points.
    
    Args:
        xml_root: Root element of the parsed XML document
        dca_record: Single DCA Configuration record element
        dca_list_records: List of DCA Configuration List records
        
    Returns:
        Dictionary containing validation result for this record
    """
    result = {
        'dca_index': None,
        'calculated_points': 0,
        'expected_points': None,
        'status': 'FAIL',
        'details': []
    }
    
    try:
        # Get DCA index
        dca_index = int(dca_record.get('DCA_x0020_Index', 0))
        result['dca_index'] = dca_index
        
        # Get device mapping information
        first_device_entry = int(dca_record.get('First_x0020_Device_x0020_Entry', 0))
        num_devices = int(dca_record.get('Number_x0020_Of_x0020_Devices', 0))

        # Calculate total Analog Input 16 points
        total_analog_input_16_points = 0
        
        # Process each associated device configuration record
        for device_idx in range(first_device_entry, first_device_entry + num_devices):
            device_records = xml_root.xpath(f"//B023_DEV/Record[position()={device_idx + 1}]")
            
            if not device_records:
                continue
                
            device_record = device_records[0]
            
            device_points = _calculate_device_analog_input_16_points(xml_root, device_record)

            total_analog_input_16_points += device_points
            
            result['details'].append({
                'device_index': device_idx,
                'analog_input_16_points': device_points
            })
        
        result['calculated_points'] = total_analog_input_16_points
        
        # Get expected points from DCA Configuration List
        if dca_index < len(dca_list_records):
            dca_list_record = dca_list_records[dca_index]
            expected_points = int(dca_list_record.get('NumAI', 0))
            result['expected_points'] = expected_points
            
            # Compare calculated vs expected
            if total_analog_input_16_points == expected_points:
                result['status'] = 'PASS'
            else:
                result['status'] = 'FAIL'
                result['error'] = f'Mismatch: calculated {total_analog_input_16_points}, expected {expected_points}'
        else:
            result['status'] = 'ERROR'
            result['error'] = f'DCA index {dca_index} out of range for DCA Configuration List'
            
    except Exception as e:
        result['status'] = 'ERROR'
        result['error'] = f'Error processing DCA record: {str(e)}'
        
    return result


def _calculate_device_analog_input_16_points(xml_root: etree._Element, 
                                           device_record: etree._Element) -> int:
    """
    Calculate Analog Input 16 points for a single device configuration record.
    
    Args:
        xml_root: Root element of the parsed XML document
        device_record: Single device configuration record element
        
    Returns:
        Total adjusted Analog Input 16 points for this device
    """
    total_points = 0
    
    try:

        # Get point mapping information
        device_config = device_record.find('Device_x0020_Configuration')

        if device_config is not None:
            config_record = device_config.find('Record')
            if config_record is not None:
                first_point_record = int(config_record.get('First_x0020_Point_x0020_Record'))
                num_point_records = int(config_record.get('Number_x0020_of_x0020_Point_x0020_Records'))
            else:
                print("No <Record> found inside <Device_x0020_Configuration")
        else:
            print("No <Device_x0020_Configuration> found")

        # Process each associated device point map record
        for point_idx in range(first_point_record, first_point_record + num_point_records):
            # Note: The XPath in the requirements has a typo (BO23_PNT instead of B023_PNT)
            # Using the correct B023_PNT based on the pattern
            point_records = xml_root.xpath(f"//B023_PNT/Record[position()={point_idx + 1}]")

            if not point_records:
                continue
                
            point_record = point_records[0]
            object_type = point_record.get('DCA_x0020_Object_x0020_Type', '')
            
            # Only count Analog Input 16 points
            if object_type == 'Analog Input 16':
                device_points = int(point_record.get('Number_x0020_Of_x0020_Device_x0020_Points', 0))
                
                # Apply adjustment rules for device configuration
                # For Analog Input 16 in device configuration: add 5 to the total count
                adjusted_points = device_points + 5
                total_points += adjusted_points
                
    except Exception as e:
        # Log error but don't fail the entire calculation
        pass
        
    return total_points


# Legacy interface for backwards compatibility and standalone usage
def validate_analog_input_16_points(xml_root: etree._Element) -> Dict[str, any]:
    """
    Legacy function interface for backwards compatibility.
    
    Args:
        xml_root: Root element of the parsed XML document
        
    Returns:
        Dictionary containing validation results with details for each DCA record
    """
    return _validate_analog_input_16_points(xml_root)


def main():
    """
    Example usage of the validation function.
    """
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python analog_input_16_validator.py <xml_file_path>")
        sys.exit(1)
        
    xml_file_path = sys.argv[1]
    
    try:
        # Parse XML file
        parser = etree.XMLParser()
        tree = etree.parse(xml_file_path, parser)
        root = tree.getroot()
        
        # Run validation
        results = validate_analog_input_16_points(root)
        
        # Print results
        print(f"Validation Status: {results['overall_status']}")
        print(f"Total DCA Records: {results['summary']['total_dca_records']}")
        print(f"Passed: {results['summary']['passed']}")
        print(f"Failed: {results['summary']['failed']}")
        
        if results['overall_status'] == 'ERROR':
            print(f"Error: {results.get('error', 'Unknown error')}")
        
        for detail in results['details']:
            print(f"\nDCA Index {detail['dca_index']}: {detail['status']}")
            print(f"  Calculated Points: {detail['calculated_points']}")
            print(f"  Expected Points: {detail['expected_points']}")
            if detail['status'] != 'PASS':
                print(f"  Error: {detail.get('error', 'Unknown error')}")
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()