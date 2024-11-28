from pyomo.environ import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os

print(os.getcwd())

df=pd.read_csv('C:/Users/emily/Desktop/finalyearproject/pvaddedsys/source/Test/DED/DED/ED1.csv', sep=',')
dfDW=pd.read_csv('C:/Users/emily/Desktop/finalyearproject/pvaddedsys/source/Test/DED/DED/DW.csv', sep=',')
model = AbstractModel()
model.g = RangeSet(len(df))
model.t = RangeSet(len(dfDW))
def bound_P(model,g,t):
    return (df.loc[g-1,'Pmin'] , df.loc[g-1,'Pmax'])
model.P = Var(model.g, model.t,bounds=bound_P,initialize=0, within=Reals)
model.Load = Param(initialize=300,within=Reals)
def rule_balance(model,t):
    return sum(model.P[g,t] for g in model.g) >= model.Load*dfDW.loc[t-1,'D']
model.c1 = Constraint(model.t, rule=rule_balance)
def rule_OF(model):
    return sum(df.loc[g-1,'a']*model.P[g,t]*model.P[g,t]+df.loc[g-1,'b']*model.P[g,t]+df.loc[g-1,'c'] for g in model.g for t in model.t)
model.objective = Objective(rule=rule_OF, sense=minimize)

opt = SolverFactory('ipopt', executable = "C:/Users/emily/Desktop/finalyearproject/pvaddedsys/source/Solver/ipopt.exe")
instance = model.create_instance()
results = opt.solve(instance)
results.write()
#for t in instance.t:
   # for g in instance.g:
    # print(t,g,value(instance.P[g,t]))
#Total= sum(value(instance.P[g,t]) for g in instance.g )
#print(Total)

#print(model.objective)
plt.figure(figsize=(8,8))
for g in instance.g:
    Y = [value(instance.P[g,t]) for t in instance.t]
    X = [t for t in instance.t]
    plt.scatter(X,Y,s=40, label=str(g))
XL=[str(t) for t in instance.t]
plt.xticks(X,XL)
plt.xlabel('Time')
plt.ylabel('Power Output (MW)')
plt.grid()
plt.legend()
plt.show()

