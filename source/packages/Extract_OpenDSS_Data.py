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
        dss.circuit_set_active_element(iLine)
        LineDataDSS.loc[iLine,'Sending bus'] = dss.lines_read_bus1()
        LineDataDSS.loc[iLine, 'Receiving bus'] = dss.lines_read_bus2()
        LineDataDSS.loc[iLine,'Cable code'] = dss.lines_read_linecode()

    # Get LOAD DATA
    LoadsSet = dss.loads_all_names()
    LoadPhase = pd.DataFrame(0,index = LoadsSet, columns=["phase"]) 
    LoadBus = pd.DataFrame(index = LoadsSet, columns=["Bus"])
    LoadVnom = pd.DataFrame(index = LoadsSet, columns=["Vnom [V]"])

    dss.loads_first()
    for iLoad in LoadsSet:
        for string in BusSet:
            if string in iLoad:
                bus1 = string
                if string != iLoad:
                    Phases_name = ord(iLoad[3]) - 96
                else:
                    Phases_name = 1
                break
        
        LoadBus.loc[iLoad]["Bus"] = bus1.partition(".")[0]
        LoadPhase.loc[iLoad]["phase"] = Phases_name
        LoadVnom.loc[iLoad]["Vnom [V]"] = dss.loads_read_kv() * 1000
        dss.loads_next()

    CableData = pd.DataFrame(index = LineSet, columns = ['Cable name', 'type', 'R1 [ohms]', 'X1 [ohms]', 'C1 [uF]', 'R0 [ohms]', 'X0 [ohms]', 'C0 [uF]', 'phases', 'Current rating [A]'])
    
    n = dss.linecodes_count()
    dss.linecodes_first()
    for cable in range (0, n):
        CableData.loc[cable, 'type'] = ['cab']
        CableData.loc[cable, 'R1 [ohms]'] = dss.linecodes_read_r1()
        CableData.loc[cable, 'X1 [ohms]'] = dss.linecodes_read_x1()
        CableData.loc[cable, 'C1 [ohms]'] = dss.linecodes_read_c1()
        CableData.loc[cable, 'R0 [ohms]'] = dss.linecodes_read_r0()
        CableData.loc[cable, 'X0 [ohms]'] = dss.linecodes_read_x0()
        CableData.loc[cable, 'C0 [ohms]'] = dss.linecodes_read_c0()
        CableData.loc[cable, 'phases'] = dss.linecodes_read_phases()
        CableData.loc[cable, 'Cable name'] = dss.linecodes_read_name()
        CableData.loc[cable, 'Current rating [A]'] = dss.linecodes_read_emerg_amps()
        dss.linecodes_next()
    
        

    return [LineSet, LineDataDSS, BusSet, BusVnom, NodeSet, LoadsSet, LoadPhase, LoadBus, LoadVnom, transformerRating, CableData]