import os
from pathlib import Path
import py_dss_interface
import pandas as pd 
import numpy as np
from win32com.client import makepy
import math

from packages.Extract_OpenDSS_Data import Extract_data_OpenDSS
from OPF_model.MAIN_OpenDSS_to_OPF import OpenDSS_to_OPF

dss = py_dss_interface.DSSDLL()

fileDir = Path(__file__).parents[1]
dss_file = os.path.join(fileDir, "Test_cases", "13Bus", "IEEE13Nodeckt.dss")
OPF_model_path = os.path.join(fileDir, "source", "OPF_model")

dss.text(f"compile [{dss_file}]")
dss.text("solve")

# def GetAdmittanceMatrix():
#     dss.text("set datapath=" + OPF_model_path + '/AuxData')
#     filename = "LV_Network_EXP_Y.CSV"
#     # opening the file with w+ mode truncates the file
#     f = open(filename, "w+")
#     f.close()
#     filename = "LV_Network_EXP_YPRIM.CSV"
#     # opening the file with w+ mode truncates the file
#     f = open(filename, "w+")
#     f.close()

#     dss.text('Export YPrims')
#     dss.text('Export Y')
    
    
    
    # AdmittanceMatrix = dss.cktelement_y_prim()
    # filename = "ymatrix.csv"
    # lineSet = dss.lines_all_names()
    
    # for line in lineSet:
    #     dss.circuit_set_active_element(line)
    #     print(dss.lines_read_yprim())
        #print(dss.cktelement_y_prim())
    # for i in range
    # with open(filename, "w") as f:
    #     for i in range(len(AdmittanceMatrix)):
    #         for j in range(len(AdmittanceMatrix[i])):
    #             f.write(str(AdmittanceMatrix[i][j]) + ",")
    #         f.write("\n")

# GetAdmittanceMatrix()



