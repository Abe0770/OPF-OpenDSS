from packages.plots import plot

def has_column(df, column_name):
    return column_name in df.columns

def compute_power(Time_end, df):
    complex_power1 = [0] * Time_end
    complex_power2 = [0] * Time_end
    complex_power3 = [1] * Time_end

    if has_column(df, " P1 (kW)"):
        p1 = df[" P1 (kW)"]
        q1 = df[" Q1 (kvar)"]
        complex_power1 = p1 + 1j * q1
    if has_column(df, " P2 (kW)"):
        p2 = df[" P2 (kW)"]
        q2 = df[" Q2 (kvar)"]
        complex_power2 = p2 + 1j * q2
    if has_column(df, " P3 (kW)"):
        p3 = df[" P3 (kW)"]
        q3 = df[" Q3 (kvar)"]
        complex_power3 = p3 + 1j * q3

    total_complex_power = [sum(item) for item in zip(complex_power1, complex_power2, complex_power3)]
    total_active_power = [element.real for element in total_complex_power]
    total_reactive_power = [element.imag for element in total_complex_power]

    return [total_complex_power, total_active_power, total_reactive_power]

def Extract_LoadAndPV_Data(glob, re, pd, Time_end, dss, Main_path, plt):
    store = Main_path + "/Main_Results"
    Demand_Data = {}
    PV_Set = dss.pvsystems_all_names()
    PV_Gen_data = {}
    PVPower = f"*pvsystems*.csv"
    getPVsetFiles = glob.glob(PVPower)
    LoadPower = f"*loadp*.csv"
    getLoadpowerFiles = glob.glob(LoadPower)
    TransformerPower = f"*transformer*.csv"
    getTransformerFiles = glob.glob(TransformerPower)
    count = 0
    dss.pvsystems_first()
    for file in getPVsetFiles:
        df = pd.read_csv(file)
        PVName = re.search(r"pvsystems_(?P<substring>[^_]+)_power", file)
        pv_rating_data = dss.pvsystems_read_kva_rated()
        total_active_power = []
        total_reactive_power = []
        if PVName:
            name = PVName.group(1)

            [total_complex_power, total_active_power, total_reactive_power] = compute_power(Time_end, df)

            plot(total_active_power, "Time [Hrs]", "Active Power [kW]", f"{name}_active_power", f"{store}/PV_Plots/{name}_active_power.png", plt)
            
            PV_Gen_data[name, "Profile"] = pd.Series(total_active_power, index=range(1, len(total_active_power) + 1))
            PV_Gen_data[PV_Set[count], 'Rating'] = pv_rating_data
            dss.pvsystems_next()
            count = count + 1

    total_active_power = []
    for file in getLoadpowerFiles:
        df = pd.read_csv(file)
        busName = re.search(r"loadp_(?P<substring>[^_]+)_power", file)

        if busName:
            name = busName.group(1)
            
            [total_complex_power, total_active_power, total_reactive_power] = compute_power(Time_end, df)

            plot(total_active_power, "Time [Hrs]", "Active Power [kW]", f"{name}_active_power", f"{store}/Load_Power_Plots/{name}_active_power.png", plt)
            plot(total_active_power, "Time [Hrs]", "Reactive Power [kvar]", f"{name}_reactive_power", f"{store}/Load_Power_Plots/{name}_reactive_power.png", plt)
            Demand_Data[name, "P_Profile"] = pd.Series(total_active_power, index=range(1, len(total_active_power) + 1))
            Demand_Data[name, "Q_Profile"] = pd.Series(total_reactive_power, index=range(1, len(total_reactive_power) + 1))

    for file in getTransformerFiles:
        df = pd.read_csv(file)
        busName = re.search(r"transformer_(?P<substring>[^_]+)_power", file)

        if busName:
            name = busName.group(1)
            
            [total_complex_power, total_active_power, total_reactive_power] = compute_power(Time_end, df)

            plot(total_active_power, "Time [Hrs]", "Active Power [kW]", f"{name}_active_power", f"{store}/Transformer_Power_Plots/{name}_active_power.png", plt)
            plot(total_active_power, "Time [Hrs]", "Reactive Power [kvar]", f"{name}_reactive_power", f"{store}/Transformer_Power_Plots/{name}_reactive_power.png", plt)

    return [Demand_Data, PV_Set, PV_Gen_data]