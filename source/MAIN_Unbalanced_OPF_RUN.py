import os
from pathlib import Path
import py_dss_interface
import pandas as pd 
import numpy as np
import pyomo.environ as pyo 
import math
import glob
import re
import win32com.client
from win32com.client import makepy
import matplotlib.pyplot as plt

from packages.Extract_OpenDSS_Data import Extract_data_OpenDSS
from OPF_model.MAIN_OpenDSS_to_OPF import OpenDSS_to_OPF
from packages.Extract_DSSmonitors_Data import Extract_DSSmonitors_data
from packages.Voltage_initialization import Voltage_initialization
from packages.Extract_Load_Power import Extract_LoadAndPV_Data
from packages.OPF_model_creator_v01 import OPF_model_creator
from packages.plots import plot

dss = py_dss_interface.DSSDLL()

fileDir = Path(__file__).parents[1]
dss_file_path = os.path.join(fileDir, "Test_cases", "13Bus2")
dss_file = os.path.join(dss_file_path, "IEEE13Nodeckt.dss")
OPF_model_path = os.path.join(fileDir, "source", "OPF_model")
Pyomo_data_path = os.path.join(OPF_model_path, "Pyomo_OPF_Data")
Main_path = os.path.join(fileDir, "source")

dssObj = win32com.client.Dispatch("OpenDSSEngine.DSS")
dssText = dssObj.Text # to excecute OpenDSS text commands
dssCircuit = dssObj.ActiveCircuit # Use it to access the elements in the circuit (e.g., capacitors, buses, etc.)
dssSolution = dssCircuit.Solution
dssElem = dssCircuit.ActiveCktElement
dssBus = dssCircuit.ActiveBus 

dss.text(f"compile [{dss_file}]")
dss.text("solve")

dss.text("Export Voltages")

[Lines_set, Line_data_DSS, Bus_set, Bus_Vnom, Nodes_set, Loads_Set, Load_phase, Load_bus, Load_Vnom, Transformer_rating, CableData] = Extract_data_OpenDSS(math, np, pd, dss)

DSSMon_Bus_Vdeg = np.zeros([Bus_set.size,3])
df = pd.read_csv(f"{dss_file_path}/IEEE13Nodeckt_EXP_VOLTAGES.csv")
Vmag = df[[df.columns[3], df.columns[7], df.columns[11]]]
Vdeg = df[[df.columns[4], df.columns[8], df.columns[12]]]

DSSMon_Bus_Vmag = Vmag.to_numpy()
DSSMon_Bus_Vdeg = Vdeg.to_numpy()

# for i in [Lines_set, Line_data_DSS, Bus_set, Bus_Vnom, Nodes_set, Loads_Set, Load_phase, Load_bus, Load_Vnom, Transformer_rating]:
#     print(i, end = "\n\n\n")

OpenDSS_to_OPF(OPF_model_path, Pyomo_data_path, os, np, pd, dss, Bus_set, Lines_set, Line_data_DSS, Loads_Set, Load_phase, Load_bus, Load_Vnom)

# dss.text(f'New LoadShape.loads_loadshape interval=1 npts=24 csvfile =[{dss_file_path}/LoadShape1.csv]')
# dss.text('BatchEdit Load..* daily=loads_loadshape')

for i in dss.lines_all_names():
    dss.text(f"New monitor.Line_{i} element=Line.{i} terminal=1 mode=1 ppolar=no")
    dss.text(f"New monitor.Lvi_{i}_vi element=Line.{i} terminal=1 mode=0")

for i in dss.transformers_all_Names():
    dss.text(f"New monitor.Transformer_{i}_power element=Transformer.{i} terminal=1 mode=1 ppolar=no")

for i in dss.loads_all_names():
    dss.text(f"New monitor.Loadv_{i}_voltage element=Load.{i} terminal=1 mode=0")
    dss.text(f"New monitor.Loadp_{i}_power element=Load.{i} terminal=1 mode=1 ppolar=no")

for i in dss.pvsystems_all_names():
    dss.text(f"New monitor.pvsystems_{i}_Power element=PVSystem.{i} terminal=1 mode=1 ppolar=no")

dss.text('set mode=daily')
dss.text('set stepsize=1h')
dss.text('set number=24')
dss.text('solve')

def range1(start, end, step):
    return range(start, end+1, step)

# OPF Creator Constraints
Time_sim_interval = 1
Time_start = 1
Time_end = 24
Time_sim = np.array(range1(Time_start,Time_end,Time_sim_interval))
V_statutory_lim = [0.9,1.1]
min_Cosphi = 0.95 
Inverter_S_oversized = 1.1
security_margin_current= 0.9 
security_margin_Transformer_S= 0.9

dssMonitors=dssCircuit.Monitors
Bus_setNoSource = np.delete(Bus_set, np.where(Bus_set == 'sourcebus')[0][0])
[DSSMon_Imag_line, DSSMon_P_line, DSSMon_Q_line, Demand_Data] = Extract_DSSmonitors_data(glob, re, pd, np, Bus_setNoSource)

Bus_setNoSource = np.delete(Bus_set, np.where(Bus_set == 'sourcebus')[0][0])

for i in dss.monitors_all_names():
    dss.text(f"Export monitors {i}")

V_init_pu = Voltage_initialization(math, pd, np, Bus_set, Bus_setNoSource, dss, DSSMon_Bus_Vmag, DSSMon_Bus_Vdeg)

Demand_Data, PV_Set, PV_Gen_Data = Extract_LoadAndPV_Data(glob, re, pd, Time_end, dss, Main_path, plt)

OPF_model = OPF_model_creator(pd, pyo, math, Time_sim, V_init_pu, Demand_Data, PV_Set, PV_Gen_Data, Bus_Vnom, V_statutory_lim, min_Cosphi, Inverter_S_oversized, CableData, Transformer_rating, security_margin_current, security_margin_Transformer_S)

# print('Initializing OPF model...')
# os.chdir(Pyomo_data_path)
# instance = OPF_model.create_instance(f"{Pyomo_data_path}/Model_data.dat")
# os.chdir(Main_path)