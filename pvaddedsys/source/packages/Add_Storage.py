import math

def addStorage(dss, bus, loadVal, Bus_kV, phase, bus1, Storage_data_path, pd, os, np, Load_shape, flag, flag2, storage_curve, storage_factor, initial_soc, storage_file, storage_kwh_factor):
    
    storage_kw = loadVal * storage_factor
    if flag2 == 0:
        csv_file = os.path.join(Storage_data_path, "Storage_Data.csv")
        new_df = pd.DataFrame()
        if flag == 0:
            column_names = ["Storage Name", "Bus", "kV", "kW rated", "kWh Rated", "Current kWh", "SOC"]
            empty_df = pd.DataFrame(columns=column_names)
            empty_df.to_csv(csv_file, index=False)

        existing_df = pd.read_csv(csv_file)
        row_val = [f"storage_{bus}", f"{bus}", f"{Bus_kV}", f"{storage_kw}", f"{storage_kw * 8}", (initial_soc/100)*(storage_kw * 8), initial_soc]
        new_df = pd.concat([existing_df, pd.DataFrame([row_val], columns=existing_df.columns)], ignore_index=True)
        new_df.to_csv(csv_file, index=False)
        
        Load_list = [loadConst * loadVal for loadConst in Load_shape]
        
    else:
        storage_file.write(f"New LoadShape.storageCurve{bus} npts=24 interval=1\n")
        # curve = np.squeeze(np.array(storage_curve))
        curve = "["
        for i in storage_curve:
            curve = curve + f"{i} "
        curve = curve + "]"

        storage_file.write(f"~ mult={curve}\n")
        storage_file.write(f"New Storage.storage_{bus} phases={phase} Bus1={bus1} kv={Bus_kV} kwrated={storage_kw} kwhrated={storage_kw * storage_kwh_factor} dispmode=follow daily=storageCurve{bus}\n\n\n")