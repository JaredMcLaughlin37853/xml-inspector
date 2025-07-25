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


The XML contains the following nodes:

DCA CONFIGURATION @XPATH: //B023_CFG
DEVICE CONFIGURATION @XPATH: //B023_DEV
DEVICE POINT MAP @XPATH: //B023_PNT

Each node has children nodes that represent records:

DCA CONFIGURATION records @XPATH: //B023_CFG/Record
DEVICE CONFIGURATION records @XPATH: //B023_DEV/Record
DEVICE POINT MAP records @XPATH: //BO23_PNT/Record

For each DCA CONFIGURATION record there are the following attributes:

First_x0020_Device_x0020_Entry @XPATH: //B023_CFG/Record/@First_x0020_Device_x0020_Entry
Number_x0020_Of_x0020_Devices @XPATH //B023_CFG/Record/@Number_x0020_Of_x0020_Devices

For each DEVICE CONFIGURATION record there are the following attributes:

First_x0020_Point_x0020_Record @XPATH: //B023_DEV/Record/@First_x0020_Point_x0020_Record
Number_x0020_of_x0020_Point_x0020_Records @XPATH: //B023_DEV/Record/@Number_x0020_of_x0020_Point_x0020_Records

For each DEVICE POINT MAP record there are the following attributes:

DCA_x0020_Object_x0020_Type @XPATH: //BO23_PNT/Record/@DCA_x0020_Object_x0020_Type
Number_x0020_Of_x0020_Device_x0020_Points @XPATH: //BO23_PNT/Record/@Number_x0020_Of_x0020_Device_x0020_Points

Mapping:

For each record under the DCA CONFIGURATION node there are associated records from the DEVICE CONFIGURATION and DEVICE POINT MAP nodes. To map from DCA CONFIGURATION to DEVICE CONFIGURATION, you use the attributes First_x0020_Device_x0020_Entry and Number_x0020_Of_x0020_Devices attributes, where First_x0020_Device_x0020_Entry is the starting record under the DEVICE CONFIGURATION node and Number_x0020_Of_x0020_Devices is the total number of records to include in the range. To map from DEVICE CONFIGURATION to DEVICE POINT MAP, you use the attributes First_x0020_Point_x0020_Record and Number_x0020_of_x0020_Point_x0020_Records, where First_x0020_Point_x0020_Record is the starting record under the DEVICE POINT MAP node and Number_x0020_of_x0020_Point_x0020_Records is the total number records to include in the range.

DSL Expression Request:

I need a DSL complient expression that will, for each DCA CONFIGURATION record, determine the total number of points of type "Analog Input 16". The type is determined by DCA_x0020_Object_x0020_Type and the count for that particular instance is Number_x0020_Of_x0020_Device_x0020_Points.


