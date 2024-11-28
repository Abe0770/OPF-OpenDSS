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

def get_bess_power(pd, Export_path, glob, re):
    bess_load = {}
    getBessFiles = f"{Export_path}/*storage*.csv"
    BessFiles = glob.glob(getBessFiles)
    for file in BessFiles:
        BessName = re.search(r"storage_(?P<substring>[^_]+)_power", file)
        if BessName:
            temp = []
            df = pd.read_csv(file)
            name = BessName.group(1)
            P1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            P2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            P3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
            if has_column(df, " P1 (kW)"):
                column_name = " P1 (kW)"
                P1 = df[column_name].tolist()
            if has_column(df, " P2 (kW)"):
                column_name = " P2 (kW)"
                P2 = df[column_name].tolist()
            if has_column(df, " P3 (kW)"):
                column_name = " P3 (kW)"
                P3 = df[column_name].tolist()

            for a, b, c in zip(P1, P2, P3):
                temp.append(a + b + c)
            bess_load[name] = temp

    return bess_load