from pyomo.environ import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from pyomo.environ import *

# Sample data
buses = ['bus1', 'bus2']
generators = {'gen1': {'bus': 'bus1', 'cost': 10, 'min': 0, 'max': 100},
              'gen2': {'bus': 'bus2', 'cost': 20, 'min': 0, 'max': 80}}
demand = {'bus1': 50, 'bus2': 70}
transmission_limits = {('bus1', 'bus2'): 30, ('bus2', 'bus1'): 30}

# Initialize model
model = ConcreteModel()

# Sets
model.buses = Set(initialize=buses)
model.generators = Set(initialize=generators.keys())

# Parameters
model.gen_cost = Param(model.generators, initialize={g: generators[g]['cost'] for g in generators})
model.gen_min = Param(model.generators, initialize={g: generators[g]['min'] for g in generators})
model.gen_max = Param(model.generators, initialize={g: generators[g]['max'] for g in generators})
model.demand = Param(model.buses, initialize=demand)
model.transmission_limits = Param(model.buses * model.buses, initialize=transmission_limits, default=0)

# Variables
model.gen_output = Var(model.generators, within=NonNegativeReals)

# Objective: Minimize total generation cost
def objective_rule(model):
    return sum(model.gen_cost[g] * model.gen_output[g] for g in model.generators)
model.obj = Objective(rule=objective_rule, sense=minimize)

# Constraints
# Power balance constraint at each bus
def power_balance_rule(model, b):
    generation = sum(model.gen_output[g] for g in model.generators if generators[g]['bus'] == b)
    inflow = sum(model.transmission_limits[(k, b)] for k in model.buses if (k, b) in model.transmission_limits)
    outflow = sum(model.transmission_limits[(b, k)] for k in model.buses if (b, k) in model.transmission_limits)
    return generation + inflow - outflow == model.demand[b]
model.power_balance = Constraint(model.buses, rule=power_balance_rule)

# Generator capacity constraints
def gen_limits_rule(model, g):
    return model.gen_min[g] <= model.gen_output[g] <= model.gen_max[g]
model.gen_limits = Constraint(model.generators, rule=gen_limits_rule)

# Solve the model
solver = SolverFactory('glpk')  # or use another solver like 'gurobi'
results = solver.solve(model, tee=True)

# Access LMPs from the dual values of the power balance constraints
lmps = {b: model.dual[model.power_balance[b]] for b in model.buses}

# Output results
print("Optimal Generation:")
for g in model.generators:
    print(f"{g}: {model.gen_output[g].value} MW")

print("\nLMPs at each bus:")
for b in model.buses:
    print(f"LMP at {b}: {lmps[b]}")