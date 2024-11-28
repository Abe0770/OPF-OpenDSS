from pyomo.environ import *
from itertools import cycle

def solveone(plt, np, pd, os, inspect, dict, df, load, count, filename, Solver):
    model = AbstractModel()
    model.g = RangeSet(len(df))
    
    model.t = RangeSet(len(dfDW))
    dfDW=pd.read_csv('DW.csv', sep=',')

    def bound_P(model,g):
        return (df.loc[g-1,'Pmin'] , df.loc[g-1,'Pmax'])
    model.P = Var(model.g, bounds=bound_P,initialize=0, within=Reals)
    model.Load = Param(initialize=load ,within=Reals)
    def rule_balance(model):
        return sum(model.P[g] for g in model.g) >= model.Load
    model.c1 = Constraint(rule=rule_balance)
    def rule_OF(model):
        return sum(df.loc[g-1,'a']*model.P[g]*model.P[g]+df.loc[g-1,'b']*model.P[g]+df.loc[g-1,'c'] for g in model.g)
    
    def bound_P1(model,g,t):
        return (df.loc[g-1,'Pmin'] , df.loc[g-1,'Pmax'])
    model.P1 = Var(model.g, model.t,bounds=bound_P1,initialize=0, within=Reals)
    def rule_balance1(model,t):
        return sum(model.P1[g,t] for g in model.g) >= model.Load*dfDW.loc[t-1,'D']
    model.c1 = Constraint(model.t, rule=rule_balance1)
    def rule_OF1(model):
        return sum(df.loc[g-1,'a']*model.P1[g,t]*model.P1[g,t]+df.loc[g-1,'b']*model.P1[g,t]+df.loc[g-1,'c'] for g in model.g for t in model.t)
    model.objective = Objective(rule=rule_OF, sense=minimize)
    model.objective1 = Objective(rule=rule_OF1, sense=minimize)


    opt = SolverFactory('ipopt', executable=Solver)
    instance = model.create_instance()
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

    
    # X = list(range(1, 25))
    # color_cycle = None
    # if color_cycle is None:
    #     color_cycle = plt.cm.tab10.colors 
    # colors = cycle(color_cycle)
    # for i in range(0, len(df)):
    #     values_list = df.iloc[i, 6:].tolist()
    #     plt.plot(X, values_list, label=df.iloc[i, 0], marker="o", color=next(colors))

    # plt.xlabel("Time")
    # plt.ylabel("Power Output (MW)")
    # plt.title("ED") 
    # plt.grid(True)
    # plt.legend()

    # plt.tight_layout()

    # plt.show()
    