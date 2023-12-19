def GetAdmittanceMatrix(dss, OPF_model_path, os):
    dss.text("set datapath=" + OPF_model_path + '/AuxData')

    file1 = dss.text('Export YPrims')
    file2 = dss.text('Export Y')
    os.replace(file1, "LV_Network_EXP_YPRIM.CSV")
    os.replace(file2, "LV_Network_EXP_Y.CSV")