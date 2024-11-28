def has_column(df, column_name):
    return column_name in df.columns

def Extract_DSSmonitors_data(glob, re, pd, np, BusSetNoSource):
    DSSMon_Bus_Vmag = np.zeros([BusSetNoSource.size,3])
    DSSMon_Bus_Vdeg = np.zeros([BusSetNoSource.size,3])
    Demand_Data = {}
    DSSMon_P_line = {}
    DSSMon_Q_line = {}
    DSSMon_Imag_line = {}
    Demand_Data = {}
    getLoadFiles = f"*loadv*.csv"
    LoadFiles = glob.glob(getLoadFiles)
    getLineFiles = f"*line*.csv"
    LineFiles = glob.glob(getLineFiles)
    getLviFiles = f"*lvi*.csv"
    LviFiles = glob.glob(getLviFiles)
    LoadPower = f"*loadp*.csv"
    getLoadpowerFiles = glob.glob(LoadPower)

    for file in getLoadpowerFiles:
        df = pd.read_csv(file)
        busName = re.search(r"loadp_(?P<substring>[^_]+)_power", file)
        if busName:
            name = busName.group(1)
            if has_column(df, " P1 (kW)"):
                Demand_Data[f"{name}_p1"] = df[" P1 (kW)"].tolist()
            if has_column(df, " P2 (kW)"):
                Demand_Data[f"{name}_p2"] = df[" P2 (kW)"].tolist()
            if has_column(df, " P3 (kW)"):
                Demand_Data[f"{name}_p3"] = df[" P3 (kW)"].tolist() 

            if has_column(df, " Q1 (kvar)"):
                Demand_Data[f"{name}_q1"] = df[" Q1 (kvar)"].tolist()
            if has_column(df, " Q2 (kvar)"):
                Demand_Data[f"{name}_q2"] = df[" Q2 (kvar)"].tolist()
            if has_column(df, " Q3 (kvar)"):
                Demand_Data[f"{name}_q3"] = df[" Q3 (kvar)"].tolist()
    count = 0
    # for file in LviFiles:
    #     df = pd.read_csv(file)
    #     busName = re.search(r"lvi_(?P<substring>[^_]+)_vi", file)
    #     if busName:
    #         name = busName.group(1)
    #         print(name)
    #         if has_column(df, " V1"):
    #             DSSMon_Bus_Vmag[count][0] = df[" V1"].iloc[0]
    #         if has_column(df, " V2"):
    #             DSSMon_Bus_Vmag[count][1] = df[" V2"].iloc[0]
    #         if has_column(df, " V3"):
    #             DSSMon_Bus_Vmag[count][2] = df[" V3"].iloc[0]

    #         if has_column(df, " VAngle1"):
    #             DSSMon_Bus_Vdeg[count][0] = df[" VAngle1"].iloc[0]
    #         if has_column(df, " VAngle2"):
    #             DSSMon_Bus_Vdeg[count][1] = df[" VAngle2"].iloc[0]
    #         if has_column(df, " VAngle3"):
    #             DSSMon_Bus_Vdeg[count][2] = df[" VAngle3"].iloc[0]
        # count = count + 1
    # for file in LoadFiles:
    #     df = pd.read_csv(file)
    #     busName = re.search(r"load_(?P<substring>[^_]+)_voltage", file)
    #     if busName:
    #         name = busName.group(1)
    #         if has_column(df, " V1"):
    #             DSSMon_Bus_Vmag[f"{name}_v1"] = df[" V1"].tolist()
    #         if has_column(df, " V2"):
    #             DSSMon_Bus_Vmag[f"{name}_v2"] = df[" V2"].tolist()
    #         if has_column(df, " V3"):
    #             DSSMon_Bus_Vmag[f"{name}_v3"] = df[" V3"].tolist()

    #         if has_column(df, " VAngle1"):
    #             DSSMon_Bus_Vdeg[f"{name}_va1"] = df[" VAngle1"].tolist()
    #         if has_column(df, " VAngle2"):
    #             DSSMon_Bus_Vdeg[f"{name}_va2"] = df[" VAngle2"].tolist()
    #         if has_column(df, " VAngle3"):
    #             DSSMon_Bus_Vdeg[f"{name}_va3"] = df[" VAngle3"].tolist()
    
    for file in LineFiles:
        df = pd.read_csv(file)
        LineName = re.search(r"line_(\d+)_1", file)
        if LineName:
            name = LineName.group(1)
            if has_column(df, " P1 (kW)"):
                DSSMon_P_line[f"{name}_p1"] = df[" P1 (kW)"].tolist()
            if has_column(df, " P2 (kW)"):
                DSSMon_P_line[f"{name}_p2"] = df[" P2 (kW)"].tolist()
            if has_column(df, " P3 (kW)"):
                DSSMon_P_line[f"{name}_p3"] = df[" P3 (kW)"].tolist()

            if has_column(df, " Q1 (kvar)"):
                DSSMon_Q_line[f"{name}_q1"] = df[" Q1 (kvar)"].tolist()
            if has_column(df, " Q2 (kvar)"):
                DSSMon_Q_line[f"{name}_q2"] = df[" Q2 (kvar)"].tolist()
            if has_column(df, " Q3 (kvar)"):
                DSSMon_Q_line[f"{name}_q3"] = df[" Q3 (kvar)"].tolist()

    for file in LviFiles:
        df = pd.read_csv(file)
        LineName = re.search(r"lvi_(\d+)_vi", file)
        if LineName:
            name = LineName.group(1)
            if has_column(df, " I1"):
                DSSMon_Imag_line[f"{name}_i1"] = df[" I1"].tolist()
            if has_column(df, " I2"):
                DSSMon_Imag_line[f"{name}_i2"] = df[" I2"].tolist()
            if has_column(df, " I3"):
                DSSMon_Imag_line[f"{name}_i3"] = df[" I3"].tolist()

    return [DSSMon_Imag_line, DSSMon_P_line, DSSMon_Q_line, Demand_Data]