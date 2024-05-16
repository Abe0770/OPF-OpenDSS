def OpenDSS_to_OPF(OPF_model_path, Pyomo_data_path, os, np, pd, dss, BusSet, LineSet, LineDataDSS, LoadsSet, LoadPhase, LoadBus, LoadVnom):
    from OPF_model.packages.Export_admittance_matrix import GetAdmittanceMatrix
    from OPF_model.packages.Y_Bus import Export_Y_bus
    from OPF_model.packages.General_Data_to_Pyomo import Sets_and_others


    GetAdmittanceMatrix(dss, OPF_model_path, os)
    dss.text(f"set datapath={OPF_model_path}")

    Export_Y_bus(np, pd, OPF_model_path, Pyomo_data_path, BusSet)
    dss.text(f"set datapath={OPF_model_path}")

    Sets_and_others(pd,BusSet,Pyomo_data_path,LineSet,LineDataDSS,LoadsSet,LoadPhase,LoadBus,LoadVnom)
    dss.text(f"set datapath={OPF_model_path}")

    os.remove(OPF_model_path + '/AuxData/LV_Network_EXP_Y.CSV')
    os.remove(OPF_model_path + '/AuxData/LV_Network_EXP_YPRIM.CSV')