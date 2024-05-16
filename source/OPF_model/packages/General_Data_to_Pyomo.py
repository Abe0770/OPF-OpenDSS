def Sets_and_others(pd,Bus_set,Pyomo_data_path,Lines_set,Line_data_DSS,Loads_set,Load_phase,Load_bus,Load_Vnom):
    Buses = Bus_set
    
    ## Phases set
    open(Pyomo_data_path + '/Phases_Pyomo.csv', 'w').close()
    with open(Pyomo_data_path + '/Phases_Pyomo.csv', 'a') as open_file:
        Headers= 'Phases_abc'
        open_file.write(Headers + '\n')
        for phase in ['1','2','3']:
            open_file.write(phase + '\n')
    
    ## Bus set
    open(Pyomo_data_path + '/Buses_Pyomo.csv', 'w').close()
    with open(Pyomo_data_path + '/Buses_Pyomo.csv', 'a') as open_file:
        Headers= 'Buses'
        open_file.write(Headers + '\n')
        for bus in Buses:
            open_file.write(bus + '\n')
                
    ## Lines data   
    Lines_set = pd.DataFrame(columns=['Lines'])     
    Lines_buses = pd.DataFrame(columns=['Lines','Lines_k','Lines_i','Lines_cable'])
    Lines_buses['Lines'] = Line_data_DSS.index
    Lines_buses[['Lines_k','Lines_i','Lines_cable']] = Line_data_DSS[['Sending bus','Receiving bus','Cable code']].values
    Lines_set['Lines'] = Line_data_DSS.index
    Lines_set.to_csv(Pyomo_data_path + '/Lines_Pyomo.csv',index=False)
    Lines_buses.to_csv(Pyomo_data_path + '/Lines_data_Pyomo.csv',index=False)    

    ## Loads data
    Loads_set = pd.DataFrame(columns=['Loads'])
    Loads_data = pd.DataFrame(columns=['Loads','Load_bus_conn','Load_phase_conn','Load_Vnom'])
    Loads_set['Loads'] = Load_bus.index
    Loads_data['Loads'] = Load_bus.index
    Loads_data['Load_bus_conn'] = Load_bus['Bus'].values
    Loads_data['Load_phase_conn'] = Load_phase['phase'].values
    Loads_data['Load_Vnom'] = Load_Vnom['Vnom [V]'].values   
    Loads_set.to_csv(Pyomo_data_path + '/Loads_Pyomo.csv',index=False)
    Loads_data.to_csv(Pyomo_data_path + '/Loads_data_Pyomo.csv',index=False)