def Extract_load_data(dssFile):
    with open(dssFile, 'r') as file:
        lines = file.readlines()
    data = {}
    totalLoad = 0
    for line in lines:
        if line.lower().startswith("new load"):
            parts = line.strip().split()

            load_value = None
            bus1_value = None
            phases_value = None
            kw_value = None
            kv_value = None

            for part in parts:
                if part.lower().startswith("load"):
                    key, value = part.split(".")
                    if key == "Load":
                        load_value = value
                elif part.lower().startswith(tuple(["bus1", "phases", "kw", "kv"])):
                    key, value = part.split("=")
                    if key.lower() == "bus1":
                        bus1_value = value
                    elif key.lower() == "phases":
                        phases_value = int(value)
                    elif key.lower() == "kw":
                        kw_value = int(value)
                        totalLoad += kw_value
                    elif key.lower() == "kv":
                        kv_value = float(value)

            # Create dictionaries if all required values are found
            if load_value and bus1_value and phases_value and kw_value and kv_value:
                data[load_value] = {
                    "bus1": bus1_value,
                    "phases": phases_value,
                    "kw": kw_value,
                    "kv": kv_value,
                }
    return data, totalLoad