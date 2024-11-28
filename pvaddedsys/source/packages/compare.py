def generator(gen_bus_line_loss, bus):
    gen = 'G1'
    min = 99999999999
    for key, val in gen_bus_line_loss.items():
        if key == bus:
            for key1, val1 in val.items():
                if val1 < min:
                    min = val1
                    gen = key1
    return gen


def compare(ED_Results_path, PVed, PVactual, BESSstatus, Load_data, pd, sim_time, Load_shape, deepcopy, gen_bus_line_loss):
    col_name = []
    for i in range(0, 24):
        col_name.append(f"time - {i}")
    power_cart = {}
    df_ed = pd.read_csv(PVed, index_col=None)
    df_pvact = pd.read_csv(PVactual)
    df_bess = pd.read_csv(BESSstatus, header = None)
    dict = {}
    gen_dict = {}
    dict["Element"] = col_name
    for i in df_ed[df_ed.columns[0]]:
        if i.startswith('G'):
            gen_dict[i] = df_ed.loc[df_ed[df_ed.columns[0]] == i].iloc[0][9:].tolist()

    bess_dict = {}


    for index, row in df_bess.iterrows():
        key = row[0]
        value_list = list(row[1:])
        bess_dict[key] = value_list


    for bus, data in Load_data.items():
        pv_element = f"PV_bus_{bus}"
        storage_element = f"Storage_{bus}"
        pv_actual = f"pv{bus}"

        PV = df_ed.loc[df_ed[df_ed.columns[0]] == pv_element]
        Storage = df_ed.loc[df_ed[df_ed.columns[0]] == storage_element]
        pvact = df_pvact.loc[df_pvact[df_pvact.columns[0]] == pv_actual]
    
        PVed_list = PV.iloc[0][6:].tolist()
        Storage_list = Storage.iloc[0][6:].tolist()
        PVact_list = pvact.iloc[0][1:].tolist()

        list1_pv = []
        list4_soc = []
        list2_storage = []
        time = 0
        for pved, pvact, bess in zip(PVed_list, PVact_list, Storage_list):
            soc = float(bess_dict[f"storage_{bus}"][5])  
            current_kwh = float(bess_dict[f"storage_{bus}"][4])
            kwh_rated = float(bess_dict[f"storage_{bus}"][3])

            # CHECK IF PVED == 0
            if pved == 0:
                list1_pv.append(0)
                temp_kwh = current_kwh - bess
                # IF SOC AFTER DISCHARGING > 20, DISCHARGE 
                if ((temp_kwh/kwh_rated) * 100) > 20:
                    current_kwh = temp_kwh
                    soc = (temp_kwh/kwh_rated) * 100
                    list4_soc.append(soc)
                    list2_storage.append(bess)
                    bess_dict[f"storage_{bus}"][5] = soc
                    bess_dict[f"storage_{bus}"][4] = current_kwh

                # ELSE IF SOC > 20, DISCHARGE TILL SOC BECOMES 20%
                elif soc > 20:
                    storage_power = (current_kwh) - (0.2 * kwh_rated)
                    list2_storage.append(storage_power)
                    current_kwh -= storage_power
                    soc = (current_kwh/kwh_rated) * 100
                    bess_dict[f"storage_{bus}"][5] = soc
                    bess_dict[f"storage_{bus}"][4] = current_kwh
                    list4_soc.append(soc)
                    gen_dict[generator(gen_bus_line_loss, bus)][time] += (bess - storage_power)
                    # list3_g1[time] += (bess - storage_power)
                
                # ELSE IF SOC <= 20 TAKE THE POWER FROM GENERATOR
                else:
                    list2_storage.append(0)
                    gen_dict[generator(gen_bus_line_loss, bus)][time] += bess
                    # list3_g1[time] += bess
                    list4_soc.append(soc)
                    
            else:
                # CASE - 1
                if (pvact - pved) >= bess:
                    list1_pv.append(pved + bess)
                    list2_storage.append(0)

                    bal_pv_power = (pvact - (pved + bess))

                    # IF THE SOC IS LESS THAN 90 CHARGE 
                    if (((bal_pv_power + current_kwh) / kwh_rated) * 100) < 90:
                        current_kwh += bal_pv_power
                        soc = (current_kwh/kwh_rated) * 100
                        bess_dict[f"storage_{bus}"][5] = soc
                        bess_dict[f"storage_{bus}"][4] = current_kwh
                        list4_soc.append(soc)

                    elif soc < 90:
                        cart = bal_pv_power - (kwh_rated - current_kwh)
                        current_kwh = 0.9 * kwh_rated
                        soc = 90
                        bess_dict[f"storage_{bus}"][5] = soc
                        bess_dict[f"storage_{bus}"][4] = current_kwh
                        list4_soc.append(soc)
                        power_cart[f"time_{time}_pv_{bus}"] = cart
                    
                    # IF SOC >= 90
                    else:
                        power_cart[f"time_{time}_pv_{bus}"] = bal_pv_power
                        list4_soc.append(soc)

                # CASE - 2
                else:
                    list1_pv.append(pvact)
                    temp_kwh = current_kwh - bess

                    if ((temp_kwh / kwh_rated) * 100) > 20:
                        current_kwh = temp_kwh
                        soc = (temp_kwh/kwh_rated) * 100
                        list4_soc.append(soc)
                        list2_storage.append(bess)
                        bess_dict[f"storage_{bus}"][5] = soc
                        bess_dict[f"storage_{bus}"][4] = current_kwh


                    elif soc > 20:
                        storage_power = (current_kwh) - (0.2 * kwh_rated)
                        list2_storage.append(storage_power)
                        current_kwh -= storage_power
                        soc = (current_kwh/kwh_rated) * 100
                        bess_dict[f"storage_{bus}"][5] = soc
                        bess_dict[f"storage_{bus}"][4] = current_kwh
                        list4_soc.append(soc)
                        gen_dict[generator(gen_bus_line_loss, bus)][time] += (bess - storage_power)
                        # list3_g1[time] += (bess - storage_power)

                    else:
                        list2_storage.append(0)
                        gen_dict[generator(gen_bus_line_loss, bus)][time] += bess
                        # list3_g1[time] += bess
                        list4_soc.append(soc)
            time += 1

        dict[f"PV_{bus}"] = list1_pv
        dict[f"Storage_SOC_{bus}"] = list4_soc
        dict[f"Storage_{bus}"] = list2_storage
        load_temp = deepcopy(Load_shape)
        for i in range(len(load_temp)):
            load_temp[i] *= data["kw"]
        
        dict[f"Load_{bus}"] = load_temp


    # dict["G1"] = list3_g1
    for key1, val1 in gen_dict.items():
        dict[key1] = val1
    tempdf = pd.DataFrame(dict)
    tempdf = tempdf.T
    tempdf.to_csv(f"{ED_Results_path}/ED_Final.csv", header = False)
    return power_cart