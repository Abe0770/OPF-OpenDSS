def Extract_data_OpenDSS(math, np, pd, dss):
    NodeSet = dss.circuit_all_node_names()
    transformerRating = dss.transformers_read_kva()

    # Get BUSES NOMINAL VOLTAGE
    BusSet = np.array(dss.circuit_all_bus_names())
    BusVnom = pd.DataFrame(0,index = BusSet, columns = ['Vnom_pp','Vnom_pn'])
    for iBus in BusSet:
        dss.circuit_set_active_bus(iBus)
        BusVnom.loc[iBus,'Vnom_pp'] = dss.bus_kv_base() * 1000 * math.sqrt(3)
        BusVnom.loc[iBus,'Vnom_pn'] = dss.bus_kv_base() * 1000

    # Get LINE DATA
    LineSet = dss.lines_all_names()
    LineDataDSS = pd.DataFrame(index = LineSet, columns = ['Sending bus','Receiving bus','Cable code'])
    for iLine in LineSet:
        LineDataDSS.loc[iLine,'Sending bus'] = dss.lines_read_bus1()
        LineDataDSS.loc[iLine, 'Receiving bus'] = dss.lines_read_bus2()
        LineDataDSS.loc[iLine,'Cable code'] = dss.lines_read_linecode()

    # Get LOAD DATA
    LoadsSet = dss.loads_all_names()
    LoadPhase = pd.DataFrame(0,index = LoadsSet, columns=["phase"]) 
    LoadBus = pd.DataFrame(index = LoadsSet, columns=["Bus"])
    LoadVnom = pd.DataFrame(index = LoadsSet, columns=["Vnom [V]"])

    for iLoad in LoadsSet:
        dss.circuit_set_active_element("Load,"+iLoad)
        dss.loads_write_name = iLoad
        
        BusNames = dss.bus_name()
        bus1 = BusNames[0]
        LoadBus.loc[iLoad]["Bus"] = bus1.partition(".")[0]
        Phases_name = bus1.partition(".")[2]
        LoadPhase.loc[iLoad]["phase"] = Phases_name
        LoadVnom.loc[iLoad]["Vnom [V]"] = dss.loads_read_kv() * 1000
    return [LineSet, LineDataDSS, BusSet, BusVnom, NodeSet, LoadsSet, LoadPhase, LoadBus, LoadVnom, transformerRating]