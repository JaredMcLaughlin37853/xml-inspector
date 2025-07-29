DNP V3.00 DCA @APPLICATION
	-> DCA CONFIGURATION @TABLE (xpath: //B023_CFG)
		FOR EACH @RECORD (xpath: //B023_CFG/Record)
			-> DCA_x0020_INDEX @ATTRIBUTE (xpath: //B023_CFG/Record/@DCA_x0020_Index)
				GET VALUE 
			-> First_x0020_Device_x0020_Entry @ATTRIBUTE (xpath: //B023_CFG/Record/@First_x0020_Device_x0020_Entry)
				GET VALUE
			-> Number_x0020_Of_x0020_Devices @ATTRIBUTE (xpath: //B023_CFG/Record/@Number_x0020_Of_x0020_Devices)
				GET VALUE
			-> DEVICE CONFIGURATION @TABLE (xpath: //B023_DEV)
				FOR EACH @RECORD IN RANGE (First_x0020_Device_x0020_Entry:(First_x0020_Device_x0020 + Number_x0020_Of_x0020_Devices))
                    -> First_x0020_Point_x0020_Record @ATTRIBUTE
                        GET VALUE
                    -> Number_x0020_of_x0020_Point_x0020_Records
                        GET VALUE
                    -> DEVICE POINT MAP @TABLE (xpath: //B023_PNT)
                        FOR EACH @RECORD IN RANGE (First_x0020_Point_x0020_Record: (First_x0020_Point_x0020_Record + Number_x0020_of_x0020_Point_x0020_Records)) (xpath: //BO23_PNT/Record)
                            -> DCA_x0020_Object_x0020_Type
                                GET VALUE
                            -> Number_x0020_Of_x0020_Device_x0020_Points
                                GET VALUE ***This is the value that will be counted and then eventually compared to Sys Pt Db


The XML contains the following nodes for identifying number of points in the DNP DCA application:

DCA CONFIGURATION @XPATH: //B023_CFG
DEVICE CONFIGURATION @XPATH: //B023_DEV
DEVICE POINT MAP @XPATH: //B023_PNT

Each node has children nodes that represent records:

DCA CONFIGURATION records @XPATH: //B023_CFG/Record
DEVICE CONFIGURATION records @XPATH: //B023_DEV/Record
DEVICE POINT MAP records @XPATH: //BO23_PNT/Record

For each DCA CONFIGURATION record there are the following attributes:

DCA_x0020_Index @XPATH: //B023_CFG/Record/@DCA_x0020_Index
First_x0020_Device_x0020_Entry @XPATH: //B023_CFG/Record/@First_x0020_Device_x0020_Entry
Number_x0020_Of_x0020_Devices @XPATH //B023_CFG/Record/@Number_x0020_Of_x0020_Devices

For each DEVICE CONFIGURATION record there are the following attributes:

First_x0020_Point_x0020_Record @XPATH: //B023_DEV/Record/@First_x0020_Point_x0020_Record
Number_x0020_of_x0020_Point_x0020_Records @XPATH: //B023_DEV/Record/@Number_x0020_of_x0020_Point_x0020_Records

For each DEVICE POINT MAP record there are the following attributes:

DCA_x0020_Object_x0020_Type @XPATH: //BO23_PNT/Record/@DCA_x0020_Object_x0020_Type
Number_x0020_Of_x0020_Device_x0020_Points @XPATH: //BO23_PNT/Record/@Number_x0020_Of_x0020_Device_x0020_Points

Mapping within the B023_CFG node:

For each record under the DCA CONFIGURATION node there are associated records from the DEVICE CONFIGURATION and DEVICE POINT MAP nodes. To map from DCA CONFIGURATION to DEVICE CONFIGURATION, you use the attributes First_x0020_Device_x0020_Entry and Number_x0020_Of_x0020_Devices attributes, where First_x0020_Device_x0020_Entry is the starting record under the DEVICE CONFIGURATION node and Number_x0020_Of_x0020_Devices is the total number of records to include in the range. To map from DEVICE CONFIGURATION to DEVICE POINT MAP, you use the attributes First_x0020_Point_x0020_Record and Number_x0020_of_x0020_Point_x0020_Records, where First_x0020_Point_x0020_Record is the starting record under the DEVICE POINT MAP node and Number_x0020_of_x0020_Point_x0020_Records is the total number records to include in the range.

For each record under DCA CONFIGURATION node, the point count needs to be adjusted as follows:

If DCA_x0020_Object_x0020_Type is equal to Binary Input, then add 3 to the total count.
If DCA_x0020_Object_x0020_Type is equal to Binary Output, then add 9 to the total count.

For each record udner the DEVICE CONFIGURATION node, the point count needs to be adjusted as follows:

If DCA_x0020_Object_x0020_Type is equal to Binary Input, then add 16 to the total count.
If DCA_x0020_Object_x0020_Type is equal to Binary Output, then add 9 to the total count.
If DCA_x0020_Object_x0020_Type is equal to Analog Input 16, then add 5 to the total count.

The XML also contains the following node for identifying the number of points provisioned in the System Point Database application:

DCA Configuration List @XPATH: //B008_DCA

This node has children nodes that represent records. Each record has the following attributes:

NumDI
NumDO
NumAI

Mapping between the B023_CFG node and the B008_DCA node:

For each record under the DCA CONFIGURATION there is an attribute called DCA_x0020_Index. This attribute corresponds to a record under the DCA Configuration List. It uses zero based indexing. For example, when the DCA_x0020_Index is 1, this is the second record listed under the DCA Configuration List node. The number of points of each type, represented by the DCA_x0020_Object_x0020_Type attribute, corresponds to attributes for each record under the DCA Configuartion List node accourding to the following map:

Analog Input 16 -> NumAI
Binary Input -> NumDI
Binary Output -> NumDO

DSL Expression Request:

I need a DSL complient expression that will, for each DCA CONFIGURATION record, determine the total number of points of type "Analog Input 16", adjusted according to rules mentioned above. The type is determined by DCA_x0020_Object_x0020_Type and the count for that particular instance is Number_x0020_Of_x0020_Device_x0020_Points. It then needs to compare the adjusted point count to the corresponding record under the DCA Configuration List, per the mapping mentioned.

Here is an example:

Record 0 under the DCA CONFIGURATION node, has 1 associated record under the DEVICE CONFIGURATION node, and 1 records under the DEVICE POINT MAP node. The DCA_x0020_Object_x0020_Type type for the is Binary Input and the value for Number_x0020_Of_x0020_Device_x0020_Points is 5. This would result in a total count of Record 0 of the DCA CONFIGURATION node, of 24. The DCA_x0020_Index for the DCA CONFIGURATION record 0 is 3. This corresponds to the 4th record under the DCA Configuration List. The adjusted point count, 24, needs to be compared to the value of NumAI udner the 4th record of the DCA Configuration List.

# Thought
What if instead of creating a DSL, I just used Python as my language.

@dataclass
class Value:
    type: str
    value: Any

@dataclass  
class Result:
    status: str  # "Pass" or "Fail"
    returned_value: Value
    expected_value: Value
    
# Interpretation: Result represents the result of a validation
# performed on an XML file. status represents whether or not the validation passed,
# returned_value is the value(s) retrieved, and expected_value represents the expected value(s)

def validate(xml_file) -> Result:
    """
    Takes an XML file.
    Performs a validation.
    Returns a Result
    """
    pass