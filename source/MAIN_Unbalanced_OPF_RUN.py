import os
from pathlib import Path
import py_dss_interface
import pandas as pd 
import numpy as np
from win32com.client import makepy
import pyomo.environ as pyo 
import math

from packages.Extract_OpenDSS_Data import Extract_data_OpenDSS
from OPF_model.MAIN_OpenDSS_to_OPF import OpenDSS_to_OPF

dss = py_dss_interface.DSSDLL()

fileDir = Path(__file__).parents[1]
dss_file = os.path.join(fileDir, "Test_cases", "13Bus", "IEEE13Nodeckt.dss")
OPF_model_path = os.path.join(fileDir, "source", "OPF_model")
Pyomo_data_path = os.path.join(OPF_model_path, "Pyomo_OPF_Data")

dss.text(f"compile [{dss_file}]")
dss.text("solve")

[LineSet, LineDataDSS, BusSet, BusVnom, NodeSet, LoadsSet, LoadPhase, LoadBus, LoadVnom, transformerRating] = Extract_data_OpenDSS(math, np, pd, dss)

for i in [LineSet, LineDataDSS, BusSet, BusVnom, NodeSet, LoadsSet, LoadPhase, LoadBus, LoadVnom, transformerRating]:
    print(i, end = "\n\n\n")

#BusSetNoSlack = np.delete(BusSet, np.where(BusSet == 'sourcebus')[0][0])

OpenDSS_to_OPF(OPF_model_path, Pyomo_data_path, os, np, pd, dss, BusSet, LineSet, LineDataDSS, LoadsSet, LoadPhase, LoadBus, LoadVnom)