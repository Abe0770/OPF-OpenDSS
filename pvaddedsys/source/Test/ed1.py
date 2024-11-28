from pyomo.environ import *
import  pyomo.environ as pyo
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df=pd.read_csv(r"C:\Users\emily\Desktop\finalyearproject\pvaddedsys\source\Test\ED-Emission.csv", sep=',')

model = AbstractModel()
model.a= pyo.Set(dimen=1)
model.g = RangeSet(len(df))
model.Buses = pyo.Set(dimen=1)

def bound_P(model,g):
    return (df.loc[g-1,'Pmin'] , df.loc[g-1,'Pmax'])

model.P = Var(model.g, bounds=bound_P, initialize=0, within=Reals)

model.Load = Param(initialize=300,within=Reals)
def rule_balance(model):
    return sum(model.P[g] for g in model.g) >= model.Load
model.c1 = Constraint(rule=rule_balance)

def rule_OF(model):
    return sum((df.loc[g-1,'a'] * model.P[g] * model.P[g]) + (df.loc[g-1,'b'] * model.P[g]) + (df.loc[g-1,'c']) for g in model.g)
model.objective = Objective(rule=rule_OF, sense=minimize)

def rule_OF2(model):
    return sum((df.loc[g-1,'d'] * model.P[g] * model.P[g]) + (df.loc[g-1,'e'] * model.P[g]) + (df.loc[g-1,'f']) for g in model.g)
model.objective2 = Objective(rule=rule_OF2, sense=minimize)

opt = SolverFactory('ipopt', executable=r"C:\Users\emily\Desktop\finalyearproject\pvaddedsys\source\Solver\ipopt.exe")
instance = model.create_instance()


instance.objective2.deactivate()
results = opt.solve(instance) # solves and updates instance
print('OF1=', value(instance.objective))
print('OF2=', value(instance.objective2))
for g in instance.g:
    print(g ,value(instance.P[g]))
Total= sum(value(instance.P[g]) for g in instance.g )
print(Total)
instance.objective.deactivate()
instance.objective2.activate()

results = opt.solve(instance) # solves and updates instance
print('OF1=', value(instance.objective))
print('OF2=', value(instance.objective2))
for g in instance.g:
    print(g ,value(instance.P[g]))
Total= sum(value(instance.P[g]) for g in instance.g )
print(Total)
print('Buses=', [Buses for Buses in instance.Buses])