def getValues(parts, totalLoad):
    load_value = None
    bus1_value = None
    phases_value = None
    kw_value = None
    kv_value = None

    for part in parts: # Iterate through the parts of the line
        if part.lower().startswith("load"): # Check if the part contains the load name, e.g. "Load.671"
            key, value = part.split(".") # Split the part into key and value. Key = "Load", Value = "671"
            if key == "Load": # Check if the key is "Load"
                load_value = value # Store the load value
        elif part.lower().startswith(tuple(["bus1", "phases", "kw", "kv"])): # Check if the part contains the bus1, phases, kw, or kv values
            key, value = part.split("=") # Split the part into key and value
            if key.lower() == "bus1": # Check if the key is "bus1"
                bus1_value = value # Store the bus1 value
            elif key.lower() == "phases": # Check if the key is "phases"
                phases_value = int(value) # Store the phases value
            elif key.lower() == "kw": # Check if the key is "kw"
                kw_value = int(value) # Store the kw value
                totalLoad += kw_value # Add the kw value to the total load
            elif key.lower() == "kv": # Check if the key is "kv"
                kv_value = float(value) # Store the kv value
    return load_value, bus1_value, phases_value, kw_value, kv_value, totalLoad

def Extract_load_data(dssFile):
    with open(dssFile, 'r') as file: # Open the DSS file
        lines = file.readlines() # Read the lines of the file
    data = {} # Create an empty dictionary to store the data
    totalLoad = 0 # Create a variable to store the total load

    
    # EXAMPLE LINE - New Load.671 Bus1=671.1.2.3  Phases=3 Conn=Delta Model=1 kV=4.16   kW=1155 kvar=660 
    for line in lines: # Iterate through the lines of the file
        if line.lower().startswith("new load"): # Check if the line starts with "new load"
            parts = line.strip().split() # Split the line into parts

            # Initialize variables
            load_value = None
            bus1_value = None
            phases_value = None
            kw_value = None
            kv_value = None

            load_value, bus1_value, phases_value, kw_value, kv_value, totalLoad = getValues(parts, totalLoad)

            # Create dictionaries if all required values are found
            if load_value and bus1_value and phases_value and kw_value and kv_value: # Check if all required values are found
                data[load_value] = { # Store the load data in the dictionary
                    "bus1": bus1_value,
                    "phases": phases_value,
                    "kw": kw_value,
                    "kv": kv_value,
                }
    return data, totalLoad 
    # Return the data dictionary as list in format data = {load_value : {bus1, phases, kw, kv}, ...} and the total load