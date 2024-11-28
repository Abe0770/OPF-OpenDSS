from pyomo.environ import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

df=pd.read_csv(r"C:\Users\emily\Desktop\finalyearproject\pvaddedsys\source\Test\ED-Emission.csv", sep=',')

model = AbstractModel()
model.g = RangeSet(len(df))
def bound_P(model,g):
    return (df.loc[g-1,'Pmin'] , df.loc[g-1,'Pmax'])
model.P = Var(model.g, bounds=bound_P,initialize=0, within=Reals)
model.Load = Param(initialize=300,within=Reals)

model.W2 = Param(initialize=0.2,within=Reals, mutable=True )
model.W1 = Param(initialize=0.8,within=Reals, mutable=True )

def rule_balance(model):
    return sum(model.P[g] for g in model.g) >= model.Load
model.c1 = Constraint(rule=rule_balance)

def rule_OF(model):
    return sum(df.loc[g-1,'a']*model.P[g]*model.P[g]+df.loc[g-1,'b']*model.P[g]+df.loc[g-1,'c'] for g in model.g)
model.objective = Objective(rule=rule_OF, sense=minimize)

def rule_OF2(model):
    return sum(df.loc[g-1,'d']*model.P[g]*model.P[g]+df.loc[g-1,'e']*model.P[g]+df.loc[g-1,'f'] for g in model.g)
model.objective2 = Objective(rule=rule_OF2, sense=minimize)

def rule_OFWS(model):
    return model.W1*(sum(df.loc[g-1,'a']*model.P[g]*model.P[g]+df.loc[g-1,'b']*model.P[g]+df.loc[g-1,'c'] for g in model.g)) + model.W2*(sum(df.loc[g-1,'d']*model.P[g]*model.P[g]+df.loc[g-1,'e']*model.P[g]+df.loc[g-1,'f'] for g in model.g))
model.OF = Objective(rule=rule_OFWS, sense=minimize)


opt = SolverFactory('ipopt', executable=r"C:\Users\emily\Desktop\finalyearproject\pvaddedsys\source\Solver\ipopt.exe")
instance = model.create_instance()

instance.objective2.deactivate()
instance.objective.deactivate()
instance.OF.activate()

results = opt.solve(instance) # solves and updates instance
print('OF1=', value(instance.objective))
print('OF2=', value(instance.objective2))
print('OF=', value(instance.OF))
for g in instance.g:
    print("blah")
    print(g ,value(instance.P[g]))
Total= sum(value(instance.P[g]) for g in instance.g )
print(Total)
instance.W=2
results = opt.solve(instance) # solves and updates instance
print('OF1=', value(instance.objective))
print('OF2=', value(instance.objective2))
print('OF=', value(instance.OF))
for g in instance.g:
    print(value(instance.P[g]))
Total= sum(value(instance.P[g]) for g in instance.g )
print(Total)