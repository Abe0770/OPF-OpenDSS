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
from packages.Generation_Data import Get_Generation_Data, get_bess_power
from packages.solveone import solveone
from packages.ED_solver import solve
from packages.Add_Storage import addStorage
from packages.compare import compare
from packages.dfs import adj_list


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
Generator_profiles_path = os.path.join(Network_profiles_path, "Generators")
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
dss.text(f'New LoadShape.loads_loadshape interval=1 npts=24 csvfile =[{dss_file_path}/LoadShape1.csv]')
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

x = range(len(total_kw_transformer))  

plt.plot(x, total_kw_transformer)

plt.xlabel("Time (hours)")
plt.ylabel("Transformer Power (kW)")
plt.title("Sub Transformer Power")

plt.grid(True)

plt.show()

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


# GET PV GENERATION DATA
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

def add_generator(gen_profile, gen_name, a, b, c, d, e, f, Pmin, Pmax):
    gen_name.append(gen_profile[0])
    Pmin.append(gen_profile[8])
    Pmax.append(gen_profile[7])
    a.append(gen_profile[1])
    b.append(gen_profile[2])
    c.append(gen_profile[3])    
    d.append(gen_profile[4])
    e.append(gen_profile[5])
    f.append(gen_profile[6])


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


gen_file_path  = os.path.join(Generator_profiles_path, "Generator_Profiles.csv")
gen_df = pd.read_csv(gen_file_path)

for i in gen_df.values.tolist():
    add_generator(i, gen_name, a, b, c, d, e, f, Pmin, Pmax)


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
df.to_csv(os.path.join(ED_Results_path, "ED_Results.csv"), index = False)

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

dss.text("show losses")

for root, dirs, files in os.walk(Export_path):
    for file in files:
        if file.endswith("Losses.Txt"):
            losses_file_name = file
            break
    break

Bus_set = dss.circuit_all_bus_names()
Bus_set.remove('sourcebus')
Bus_set.remove('rg60')

loss_file = os.path.join(Export_path, losses_file_name)
gen_bus_line_loss = {}
gen_bus_line_loss = adj_list(loss_file, Bus_set, gen_file_path, pd)


# ED FINAL RESULTS
power_cart = {}
power_cart = compare(ED_Results_path, f"{ED_Results_path}/ED_Results.csv", f"{Main_path}/Main_Results/PV_Files/PV_Actual_Power.csv", f"{Result_path}/Storage_Data/Storage_Data.csv", Load_data, pd, "hours", Load_shape, deepcopy, gen_bus_line_loss)



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
bess_ed = {}
generator_dict = {}
while (storage_index <= index_size):
    row_data = df.iloc[storage_index]
    storage_list = row_data.tolist()
    row_data = df.iloc[soc_index]
    storage_soc_list = row_data.tolist()
    row_name = df.index[soc_index]
    parts = row_name.split("_")
    bus_name = parts[-1]
    if bus_name.startswith('G'):
        break
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

# Get the bess actual power
bess_load_temp = get_bess_power(pd, Export_path, glob, re)

# PLOT THE SOC OF ALL STORAGES AT ALL TIMES
for i in Storage_SOC:
    if i == 'Storage_SOC_634c' or i == 'Storage_SOC_675c' or i == 'Storage_SOC_692' or i == 'Storage_SOC_646':
        plt.plot(Storage_SOC[i], label = f"{i}")

plt.grid()
plt.xlabel("Time (Hours)")
plt.ylabel("SOC (%)")
plt.title("Storage SOC")
plt.legend()
plt.show()

for i in pv_actual_power:
    if i == 'pv634c' or i == 'pv675c' or i == 'pv692' or i == 'pv646':
        plt.plot(pv_actual_power[i], label = f"{i}")

plt.grid()
plt.xlabel("Time (Hours)")
plt.ylabel("POWER (kW)")
plt.title("PV ACTUAL POWER")
plt.legend()
plt.show()

for i in bess_load_temp:
    if i == '634c' or i == '675c' or i == '692' or i == '646':
        plt.plot(bess_load_temp[i], label = f"{i}")



plt.grid()
plt.xlabel("Time (Hours)")
plt.ylabel("POWER (kW)")
plt.title("BESS ACTUAL POWER")
plt.legend()
plt.show()

for i in pv_ed:
    if i == 'PV_634c' or i == 'PV_675c' or i == 'PV_692' or i == 'PV_646':
        plt.plot(pv_ed[i], label = f"{i}")

plt.grid()
plt.xlabel("Time (Hours)")
plt.ylabel("POWER (kW)")
plt.title("PV ED POWER")
plt.legend()
plt.show()

for i in Storage_Curve:
    if i == 'Storage_SOC_634c' or i == 'Storage_SOC_675c' or i == 'Storage_SOC_692' or i == 'Storage_SOC_646':
        plt.plot(Storage_Curve[i], label = f"{i}")

plt.grid()
plt.xlabel("Time (Hours)")
plt.ylabel("Charge/Discharge")
plt.title("Storage Curve")
plt.legend()
plt.show()


# Data points
x = list(range(24))  # Time from 0 to 23
G1 = [450.9226646718991,420.58312642034616,407.23352728243975,418.73677549770514,829.5890339373769,1092.1193860649075,1104.724884690565,1042.1074284775495,944.7127777280193,119.05517401802804,37.349999999999994,37.349999999999994,59.48229999999995,53.6893172531025,59.00474478329773,47.290381503499106,55.5718184866712,159.30879360435728,618.3596266876432,773.9015615325882,886.6628475424288,894.6187288147081,827.8368169142216,822.907481930132]
G2 = [586.2094640734687,546.7680643464498,529.4135854671714,544.3678081470164,679.9827441185894,755.6102018843794,771.9973500977342,690.5946570208141,563.9816110464249,37.78172622343292,0.0,0.0,0.0,0.0,0.0,0.0,0.0,142.08726037253638,740.0215985594045,943.9571976969378,1010.8451034904019,952.2343474591204,865.4178619884877,803.3020471876671]
G3 = [478.9698248996247,446.77276389797663,432.60584236387183,444.8133710821127,905.566175956866,1200.6673659697558,1214.0446298173924,1147.593451795417,1044.235863244895,165.37371236898514,134.1,134.1,134.1,86.96325497758465,89.06282645725418,75.30211553953089,83.32291550579825,193.98239377405451,681.3790530062616,852.6565849110603,819.5884384992826,764.9268725613813,694.0562721771913,713.0543814858335]

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(x, G1, label='G1')
plt.plot(x, G2, label='G2')
plt.plot(x, G3, label='G3')

# Labeling
plt.xlabel('Time')
plt.ylabel('Generator Power')
plt.title('Generator Power')
plt.legend()

# Displaying the plot
plt.grid(True)
plt.show()


# Data
x = list(range(24))  # Time from 0 to 23
g1 = [450.9226646718991,420.58312642034616,407.23352728243975,418.73677549770514,439.9790339373766,442.7693860649074,455.3748846905649,392.75742847754964,295.3627777280193,29.055174018028058,0.0,0.0,0.0,0.0,0.0,0.0,0.0,109.29020028656718,569.239691199542,719.2260742535875,645.5267428715766,594.0187288147081,527.2368169142215,479.4554209135902]
g2 = [586.2094640734687,546.7680643464498,529.4135854671714,544.3678081470164,571.9827441185894,575.6102018843794,591.9973500977342,510.59465702081417,383.9816110464248,37.78172622343292,0.0,0.0,0.0,0.0,0.0,0.0,0.0,142.08726037253638,740.0215985594045,935.0038965296633,839.1947657330494,772.2343474591204,685.4178619884877,623.3020471876671]
g3 = [478.9698248996247,446.77276389797663,432.60584236387183,444.8133710821127,467.3561759568661,470.31736596975594,483.69462981739247,417.243451795417,313.88586324489506,31.273712368985155,0.0,0.0,0.0,0.0,0.0,0.0,0.0,116.42108718457838,604.5307510105928,763.6999738434572,685.4884384992826,630.8268725613813,559.9562721771913,509.2494845846847]

# Plot
plt.figure(figsize=(10, 6))
plt.plot(x, g1, label='G1')
plt.plot(x, g2, label='G2')
plt.plot(x, g3, label='G3')

# Labels and title
plt.xlabel('Time (hours)')
plt.ylabel('Generator Power')
plt.title('Generator Power after Reducing Losses')
plt.legend()

# Show plot
plt.grid(True)
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

# PLOT FROM TRANSFORMER SUB
