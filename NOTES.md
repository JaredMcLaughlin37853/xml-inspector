DNP V3.00 DCA @APPLICATION
	-> DCA CONFIGURATION @TABLE
		FOR EACH @RECORD
			-> DCA_x0020_INDEX @ATTRIBUTE
				GET VALUE
			-> DCA_x0020_Address @ATTRIBUTE
				GET VALUE
			-> First_x0020_Device_x0020_Entry @ATTRIBUTE
				GET VALUE
			-> Number_x0020_Of_x0020_Devices @ATTRIBUTE
				GET VALUE
			-> DEVICE CONFIGURATION @TABLE
				FOR EACH @RECORD IN RANGE (First_x0020_Device_x0020_Entry:(First_x0020_Device_x0020 + Number_x0020_Of_x0020_Devices))
                    -> First_x0020_Point_x0020_Record @ATTRIBUTE
                        GET VALUE
                    -> Number_x0020_of_x0020_Point_x0020_Records
                        GET VALUE
                    -> DEVICE POINT MAP @TABLE
                        FOR EACH @RECORD IN RANGE (First_x0020_Point_x0020_Record: (First_x0020_Point_x0020_Record + Number_x0020_of_x0020_Point_x0020_Records))
                            -> DCA_x0020_Object_x0020_Type
                                GET VALUE
                            -> Number_x0020_Of_x0020_Device_x0020_Points
                                GET VALUE ***This is the value that will be counted and then eventually compared to Sys Pt Db
