## Lib imports
import os
from pathlib import Path
import py_dss_interface
import pandas as pd
import numpy as np
import glob
import re
import matplotlib.pyplot as plt
import inspect
from copy import deepcopy


## FUNCTIONS
from packages.Extract_OpenDSS_Data import Extract_load_data
from packages.Add_PV import addPV
from packages.Generation_Data import Get_Generation_Data
from packages.solveone import solveone
from packages.ED_solver import solve
from packages.Add_Storage import addStorage
from packages.compare import compare
# from OPF_model.MAIN_OpenDSS_to_OPF import OpenDSS_to_OPF
# from packages.Extract_DSSmon itors_Data import Extract_DSSmonitors_data
# from packages.Voltage_initialization import Voltage_initialization
# from packages.Extract_Load_Power import Extract_LoadAndPV_Data
# from packages.OPF_model_creator_v01 import OPF_model_creator
# from packages.plots import plot
# from packages.phasors import phasor


#------------------------- OPF Creator Constraints -------------------------
def range1(start, end, step):
    return range(start, end+1, step)
Time_sim_interval = 1
Time_unit = 'h'
Time_start = 1
Time_end = 24
Time_sim = np.array(range1(Time_start,Time_end,Time_sim_interval))
V_statutory_lim = [0.9,1.1]
min_Cosphi = 0.95
Inverter_S_oversized = 1.1
security_margin_current= 0.9
security_margin_Transformer_S= 0.9
pv_installation_cost = 1720
bess_installation_cost = 1590
pv_factor = 1.5
storage_factor = pv_factor * 0.3
storage_kwh_factor = 4
initial_soc = 50
#---------------------------------------------------------------------------


#------------------------------------ PATHS --------------------------------
fileDir = Path(__file__).parents[1]
dss_file_path = os.path.join(fileDir, "TestCases", "13Bus")
dss_file = os.path.join(dss_file_path, "IEEE13Nodeckt.dss")
OPF_model_path = os.path.join(fileDir, "source", "OPF_model")
Pyomo_data_path = os.path.join(OPF_model_path, "Pyomo_OPF_Data")
Main_path = os.path.join(fileDir, "source")
Result_path = os.path.join(Main_path, "Main_results")
Storage_data_path = os.path.join(Result_path, "Storage_Data")
ED_Results_path = os.path.join(Result_path, "ED_Results")
Export_path = os.path.join(Result_path, "OpenDSS_Exports")
Network_path = os.path.join(Main_path, "Network_data")
Network_profiles_path = os.path.join(Network_path, "profiles")
Network_pv_profiles_path = os.path.join(Network_profiles_path, "PV_profiles")
Solver_path = os.path.join(Main_path, "Solver", "ipopt.exe")
#----------------------------------------------------------------------------


# INIT LIB AND COMPILE FILE
dss = py_dss_interface.DSSDLL()
dss.text("Clear")
dss.text(f"compile [{dss_file}]")


# GET THE LOAD DATA AND TOTAL LOAD
Load_data, Total_load = Extract_load_data(dss_file)


# Solve the circuit
dss.text('solve') 


# ADD LOSSES TO THE TOTAL LOAD
mat = dss.circuit_losses()
load_plus_loss = (mat[0]/1000) + Total_load


#------------------------ GENERATE PV RATING CSV -------------------------
temp_dict = {}
for bus, data in Load_data.items():
    temp_dict[f"pv_{bus}"] = data['kw'] * 0.5
df = pd.DataFrame.from_dict(temp_dict, orient='index', columns=['value'])
filepath = os.path.join(Network_pv_profiles_path, "PV_rating.csv")
df.to_csv(filepath, header=False)
#-------------------------------------------------------------------------


# TIME SERIES MODE STARTS HERE
dss.text(f'New LoadShape.loads_loadshape interval=1 npts=24 csvfile =[{dss_file_path}\LoadShape1.csv]')
dss.text('BatchEdit Load..* daily=loads_loadshape')


# GET THE LOAD SHAPE AS A LIST
df = pd.read_csv(f"{dss_file_path}/LoadShape1.csv", header=None)
Load_shape = df.iloc[:, 0].tolist()


# INITIALIZE TRANSFORMER MONITORS
for i in dss.transformers_all_Names():
    dss.text(f"New monitor.transformer_{i}_power element=Transformer.{i} terminal=1 mode=1 ppolar=no")


# SOLVE THE CIRCUIT
dss.text('set mode=daily')
dss.text(f'set stepsize={Time_sim_interval}{Time_unit}')
dss.text(f'set number={Time_end}')
dss.text('solve')
dss.text(f"Set datapath = {Export_path}") # Set Export path


# MONITOR OUTPUT
for i in dss.monitors_all_names():
    dss.text(f"Export monitors {i}")


# CHECK IF THE PASSED DATAFRAME HAS A PARTICULAR COLUMN
def has_column(df, column_name):
    return column_name in df.columns


# -------------------------------------- GET THE TRANSFORMER POWER --------------------------------------
total_kw_transformer = []
getTFFiles = f"{Export_path}/*transformer_sub*.csv"
TFFiles = glob.glob(getTFFiles)
for file in TFFiles:
    TFname = re.search(r"transformer_(?P<substring>[^_]+)_power", file)
    if TFname:
        df = pd.read_csv(file)
        name = TFname.group(1)
        P1 = []
        P2 = []
        P3 = []
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
            total_kw_transformer.append(a + b + c)
# ----------------------------------------------------------------------------------------------------------


# ADD PV TO THE SYSTEM

flag = 0
f_path = os.path.join(dss_file_path, "pvsystems.dss")
if os.path.exists(f_path):
    os.remove(f_path)
with open(f_path, "a") as pv_file:
    for bus, data in Load_data.items():
        addPV(dss, bus, data["bus1"], data["phases"], data["kw"], data["kv"], pv_factor, pv_file, flag)
        flag = 1

dss.text(f"Redirect {f_path}")



# Initialize PV SYSTEM MONITORS
for i in dss.pvsystems_all_names():
    dss.text(f"New monitor.pvsystems_{i}_Power element=PVSystem.{i} terminal=1 mode=1 ppolar=no")
    dss.text(f"New monitor.pvsystems_{i}_variables element=PVSystem.{i} terminal=1 mode=3")

# SOLVE THE CIRCUIT
dss.text('set mode=daily')
dss.text(f'set stepsize={Time_sim_interval}{Time_unit}')
dss.text(f'set number={Time_end}')
dss.text('solve')


# MONITOR OUTPUT 
for i in dss.monitors_all_names():
    dss.text(f"Export monitors {i}")


# GET GENERATION DATA
pv_actual_power = {}
pv_actual_power["PV_Name"] = []
for i in range(0, 24):
    pv_actual_power["PV_Name"].append(f'time_{i}')
pv_load_temp = Get_Generation_Data(pd, Export_path, glob, re)
pv_actual_power.update(pv_load_temp)


# CREATE THE PV RESULTS CSV FILE
dff = pd.DataFrame(pv_actual_power)
dff = dff.T
df = df.rename(columns=df.iloc[0], inplace=True)
dff.to_csv(os.path.join(Main_path, "Main_Results", "PV_Files", "PV_Actual_Power.csv"), header = False)


# GET PV COST
def pv_cost(Prated, Tpv, n):
    return ((pv_installation_cost * Prated) / (n * Tpv * 365)) + ((19 * Prated) / (365 * Tpv))


# GET BESS COST
def bess_cost(Prated, Tbess, n):
    return (bess_installation_cost * Prated) / (n * Tbess * 365)

def add_generator(name, a1, b1, c1, d1, e1, f1, Pmin1, Pmax1, gen_name, a, b, c, d, e, f, Pmin, Pmax):
    gen_name.append(name)
    Pmin.append(Pmin1)
    Pmax.append(Pmax1)
    a.append(a1)
    b.append(b1)
    c.append(c1)
    d.append(d1)
    e.append(e1)
    f.append(f1)


# CREATE INITIAL CSV FILE WITH GENERATORS AND ITS CORRESPONDING PARAMETERS
gen_name = []
a = []
b = []
c = []
d = []
e = []
f = []
Pmin = []
Pmax = []
for bus, data in Load_data.items():
    gen_name.append(f'PV_bus_{bus}')
    a.append(0)
    b.append(0)
    c.append(pv_cost(data["kw"] * pv_factor, Time_end, 20))
    d.append(0)
    e.append(0)
    f.append(0)
    Pmin.append(0)
    Pmax.append(data["kw"] * pv_factor)


add_generator('G1', 4.05, 18.07, 98.87, 2, 15, 34.6, 0, load_plus_loss * 1.2, gen_name, a, b, c, d, e, f, Pmin, Pmax)
add_generator('G2', 3, 20, 100, 2, 7, 35, 0, load_plus_loss * 1.2, gen_name, a, b, c, d, e, f, Pmin, Pmax)
add_generator('G3', 4.05, 15.55, 104.26, 0.95, 10, 36.49, 0, load_plus_loss * 1.2, gen_name, a, b, c, d, e, f, Pmin, Pmax)



#------------------------------------ RUN ED WITH STORAGE VALUES ----------------------------------------------
flag = 0
storage_val = {}
for bus, data in Load_data.items():
    addStorage(dss, bus, data["kw"], data["kv"], data["phases"], data["bus1"], Storage_data_path, pd, os, np, Load_shape, flag, 0, 1, storage_factor, initial_soc, dss_file, storage_kwh_factor)
    gen_name.append(f'Storage_{bus}')
    storage_val[f"Storage_{bus}"] = data["kw"] * storage_factor
    a.append(0)
    b.append(0)
    c.append(bess_cost(data["kw"] * storage_factor, Time_end, 20))
    d.append(0)
    e.append(0)
    f.append(0)
    Pmin.append(0)
    Pmax.append(data["kw"] * storage_factor)
    flag = 1
ed_dict = {'name': gen_name, 'a': a, 'b': b, 'c': c, 'd': d, 'e': e, 'f': f, 'Pmin': Pmin, 'Pmax': Pmax}
df = pd.DataFrame(ed_dict)
print(df)
df.to_csv(os.path.join(ED_Results_path, "ED_Results.csv"), index = False)

storage_df = pd.DataFrame(ed_dict)
temp_list = []
temp1 = []
count = 0
for key in pv_actual_power:
    del pv_actual_power[key]
    break


for i in range(0, Time_end):
    for bus, power in pv_actual_power.items():
        temp_list.append(power[count])
    temp_list.append(load_plus_loss * 1.2) # for generator
    temp_list.append(load_plus_loss * 1.2)
    temp_list.append(load_plus_loss * 1.2)
    for storage_name, power in storage_val.items():
        temp_list.append(power)
    ed_dict['Pmax'] = temp_list
    new_df = pd.DataFrame(ed_dict)
    solve(plt, np, pd, os, inspect, ed_dict, new_df, total_kw_transformer[count], count, "ED_Results.csv", Solver_path)
    temp_list.clear()
    count += 1


#-------------------------------------------------------------------------------------------------------------


# ED FINAL RESULTS
power_cart = {}
power_cart = compare(ED_Results_path, f"{ED_Results_path}/ED_Results.csv", f"{Main_path}/Main_Results/PV_Files/PV_Actual_Power.csv", f"{Result_path}/Storage_Data/Storage_Data.csv", Load_data, pd, "hours", Load_shape, deepcopy)

print(dss.circuit_line_losses())
dss.text(line)

#-------------------------- GET STORAGE CURVE ---------------------------
df = pd.read_csv(f"{ED_Results_path}/ED_Final.csv", index_col = 0)
Storage_SOC = {}
Storage_Curve = {}
storage_list = []
storage_soc_list = []
soc_index = 1
storage_index = 2
index_size = len(df)

pv_ed = {}

while (storage_index <= index_size):
    row_data = df.iloc[storage_index]
    storage_list = row_data.tolist()
    row_data = df.iloc[soc_index]
    storage_soc_list = row_data.tolist()
    row_name = df.index[soc_index]
    parts = row_name.split("_")
    bus_name = parts[-1]
    storage_index += 4
    soc_index += 4
    kw_rated = Load_data[bus_name]["kw"] * storage_factor
    Current_SOC = initial_soc
    Storage_Curve[row_name] = []
    Storage_SOC[row_name] = storage_soc_list
    row_dat = df.iloc[soc_index - 1]
    pv_ed_data = row_dat.tolist()
    row_nam = df.index[soc_index - 1]
    pv_ed[row_nam] = pv_ed_data

    for power, soc in zip(storage_list, storage_soc_list):
        if soc < Current_SOC:
            Storage_Curve[row_name].append(power / kw_rated)
        elif soc > Current_SOC:
            Storage_Curve[row_name].append((((soc - Current_SOC) / 100.0) * 4.0) * -1)
        else:
            Storage_Curve[row_name].append(0)
        Current_SOC = soc
#-------------------------------------------------------------------------

# PLOT THE SOC OF ALL STORAGES AT ALL TIMES
for i in Storage_SOC:
    plt.plot(Storage_SOC[i], label = f"{i}")

plt.grid()
plt.xlabel("Time (Hours)")
plt.ylabel("SOC (%)")
plt.title("Storage SOC")
plt.legend()
plt.show()

for i in pv_actual_power:
    plt.plot(pv_actual_power[i], label = f"{i}")

plt.grid()
plt.xlabel("Time (Hours)")
plt.ylabel("POWER (kW)")
plt.title("PV ACTUAL POWER")
plt.legend()
plt.show()

for i in pv_ed:
    plt.plot(pv_ed[i], label = f"{i}")

plt.grid()
plt.xlabel("Time (Hours)")
plt.ylabel("POWER (kW)")
plt.title("PV FINAL POWER")
plt.legend()
plt.show()

for i in Storage_Curve:
    plt.plot(Storage_Curve[i], label = f"{i}")

plt.grid()
plt.xlabel("Time (Hours)")
plt.ylabel("Charge/Discharge")
plt.title("Storage Curve")
plt.legend()
plt.show()

# ADD STORAGE WITH NEW STORAGE CURVE TO DSS
f_path = os.path.join(dss_file_path, "storages.dss")
if os.path.exists(f_path):
    os.remove(f_path)
with open(f_path, "a") as storage_file:
    for bus, data in Load_data.items():
        addStorage(dss, bus, data["kw"], data["kv"], data["phases"], data["bus1"], Storage_data_path, pd, os, np, Load_shape, flag, 1, Storage_Curve[f"Storage_SOC_{bus}"], storage_factor, initial_soc, storage_file, storage_kwh_factor)
        f2 = 1
dss.text(f"Redirect {f_path}")


# GET THE STORAGE NAMES
dss.circuit_set_active_class("Storage")
storage_name = dss.active_class_all_names()

# Initialize Monitors for all storages
for i in storage_name:
    dss.text(f"New monitor.{i}_power element=Storage.{i} terminal=1 mode=1 ppolar=no")
    dss.text(f"New monitor.{i}_variables element=Storage.{i} terminal=1 mode=3")



# Solve the Circuit
dss.text('set mode=daily')
dss.text(f'set stepsize={Time_sim_interval}{Time_unit}')
dss.text(f'set number={Time_end}')
dss.text('solve')

# MONITOR OUTPUT
for i in dss.monitors_all_names():
    dss.text(f"Export monitors {i}")

def has_column(df, column_name):
    return column_name in df.columns

# Load_shape.clear()
# for i in range(0, 23):
#     Load_shape.append(1)


# ss_ed = {'name': 'G1', 'a': 0, 'b': 103.8, 'c': 0, 'Pmin': 0, 'Pmax': load_plus_loss}

# df1 = pd.DataFrame(ss_ed)
# for i in total_kw_transformer:
#     solve(plt, np, pd, os, inspect, ss_ed, df1, Load_shape, Time_sim_interval, "ed_tf.csv", i)


'''
# DSSMon_Bus_Vdeg = np.zeros([Bus_set.size,3])
# df = pd.read_csv(f"{dss_file_path}/IEEE13Nodeckt_EXP_VOLTAGES.csv")
# Vmag = df[[df.columns[3], df.columns[7], df.columns[11]]]
# Vdeg = df[[df.columns[4], df.columns[8], df.columns[12]]]
# Y = df[df.columns[0]]
# X = ["V1", "V2", "V3"]
# XX = ["Angle 1", "Angle 2", "Angle 3"]

# YY = Y.to_numpy()
# DSSMon_Bus_Vmag = Vmag.to_numpy()
# DSSMon_Bus_Vdeg = Vdeg.to_numpy()

# OpenDSS_to_OPF(OPF_model_path, Pyomo_data_path, os, np, pd, dss, Bus_set, Lines_set, Line_data_DSS, Loads_Set, Load_phase, Load_bus, Load_Vnom)

# #---------------------------------- Monitor Initializations ----------------------------------
# for i in dss.lines_all_names():
#     dss.text(f"New monitor.Line_{i} element=Line.{i} terminal=1 mode=1 ppolar=no")
#     dss.text(f"New monitor.Lvi_{i}_vi element=Line.{i} terminal=1 mode=0")

# for i in dss.transformers_all_Names():
#     dss.text(f"New monitor.Transformer_{i}_power element=Transformer.{i} terminal=1 mode=1 ppolar=no")

# for i in dss.loads_all_names():
#     dss.text(f"New monitor.Loadv_{i}_voltage element=Load.{i} terminal=1 mode=0")
#     dss.text(f"New monitor.Loadp_{i}_power element=Load.{i} terminal=1 mode=1 ppolar=no")

# for i in dss.pvsystems_all_names():
#     dss.text(f"New monitor.pvsystems_{i}_Power element=PVSystem.{i} terminal=1 mode=1 ppolar=no")
#     dss.text(f"New monitor.pvsystems_{i}_variables element=PVSystem.{i} terminal=1 mode=3 ")
# #----------------------------------------------------------------------------------------------
    
# dss.text('set mode=daily')
# dss.text('set stepsize=1h')
# dss.text('set number=24')
# dss.text('solve')

# def range1(start, end, step):
#     return range(start, end+1, step)

# #------------------------- OPF Creator Constraints -------------------------
# Time_sim_interval = 1
# Time_start = 1
# Time_end = 24
# Time_sim = np.array(range1(Time_start,Time_end,Time_sim_interval))
# V_statutory_lim = [0.9,1.1]
# min_Cosphi = 0.95 
# Inverter_S_oversized = 1.1
# security_margin_current= 0.9 
# security_margin_Transformer_S= 0.9
# #---------------------------------------------------------------------------

# Bus_setNoSource = np.delete(Bus_set, np.where(Bus_set == 'sourcebus')[0][0])
# [DSSMon_Imag_line, DSSMon_P_line, DSSMon_Q_line, Demand_Data] = Extract_DSSmonitors_data(glob, re, pd, np, Bus_setNoSource)

# Bus_setNoSource = np.delete(Bus_set, np.where(Bus_set == 'sourcebus')[0][0])

# V_init_pu = Voltage_initialization(math, pd, np, Bus_set, Bus_setNoSource, dss, DSSMon_Bus_Vmag, DSSMon_Bus_Vdeg)

# Demand_Data, PV_Set, PV_Gen_Data, Transformer_Outputs = Extract_LoadAndPV_Data(glob, re, pd, Time_end, dss, Main_path, plt, os, np)

# OPF_model = OPF_model_creator(pd, pyo, math, Time_sim, V_init_pu, Demand_Data, PV_Set, PV_Gen_Data, Bus_Vnom, V_statutory_lim, min_Cosphi, Inverter_S_oversized, CableData, Transformer_rating, security_margin_current, security_margin_Transformer_S)

# solve(plt, np, pd, dss, total_load_kw, Bus_set, Loads_kva, Loads_kva)

# dss.text(f"Set datapath = {Export_path}")
'''


#### USELESS CODE

# ED SOLVER 
# solve(plt, np, pd, os, inspect, dict, df, Load_shape, Time_sim_interval, "ED_Results_Rated.csv", total_load)