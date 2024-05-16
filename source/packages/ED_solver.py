from pyomo.environ import *
from itertools import cycle

def solve(plt, np, pd, os, inspect, dict, df, load, count, filename, Solver):
    model = AbstractModel()
    model.g = RangeSet(len(df))
    def bound_P(model, g):
        return (df.loc[g-1, 'Pmin'], df.loc[g-1, 'Pmax'])
    model.P = Var(model.g, bounds=bound_P,initialize=0, within=Reals)
    model.Load = Param(initialize=load,within=Reals)
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

    opt = SolverFactory('ipopt', executable=Solver)    
    instance = model.create_instance()

    instance.objective2.activate()
    instance.objective.deactivate()
    instance.OF.deactivate()

    results = opt.solve(instance)
    temp = []

    for g in instance.g:
        temp.append(value(instance.P[g]))
    Total= sum(value(instance.P[g]) for g in instance.g )
    dict.update({f'time - {count}': temp})

    current_file_path = inspect.stack()[1].filename
    parent_dir_path = os.path.dirname(current_file_path)
    path = os.path.join(parent_dir_path, "Main_Results", "ED_Results", filename)
    df = pd.DataFrame(dict)
    df.to_csv(path, index=False)