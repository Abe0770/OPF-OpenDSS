# Remove the output files from the previous run
import os

parent_path = os.getcwd()
plots = f"{parent_path}/source/Main_Results"
csv_files = f"{parent_path}/source/OPF_model"

for root, dirs, files in os.walk(plots):
    for file in files:
        if file.endswith(".png") or file.endswith(".csv") or file.endswith(".CSV"):
            os.remove(os.path.join(root, file))
for filename in os.listdir(csv_files):
    if filename.endswith(".csv"):
        os.remove(os.path.join(csv_files, filename))

for filename in os.listdir(os.path.join(csv_files, "Pyomo_OPF_data")):
    if filename.endswith(".csv"):
        os.remove(os.path.join(csv_files, "Pyomo_OPF_data", filename))