def has_column(df, column_name):
    return column_name in df.columns

def Get_Generation_Data(pd, Export_path, glob, re):
    pv_load = {}
    getPVFiles = f"{Export_path}/*pv*.csv"
    PVFiles = glob.glob(getPVFiles)
    for file in PVFiles:
        PVname = re.search(r"pvsystems_(?P<substring>[^_]+)_variable", file)
        if PVname:
            df = pd.read_csv(file)
            name = PVname.group(1)
            if has_column(df, "kW_out_desired"):
                column_name = "kW_out_desired" 
                values = df[column_name].tolist()
                pv_load[name] = values
    #             column_values.extend(values)
    # grouped_values = [column_values[i::len(PVFiles)] for i in range(len(PVFiles))]
    return pv_load