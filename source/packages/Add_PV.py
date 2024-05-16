def addPV(dss, busName, bus, phase, load, voltage, pv_factor, pv_file, flag):
    if flag == 0:
        pv_file.write("New XYCurve.MyPvsT npts=4  xarray=[0  25  75  100]  yarray=[1.2 1.0 0.8  0.6] \n")
        pv_file.write("New XYCurve.MyEff npts=4  xarray=[.1  .2  .4  1.0]  yarray=[.86  .9  .93  .97] \n")
        pv_file.write("New loadshape.MyIrrad npts=24 interval=1\n")
        pv_file.write("mult=[0 0 0 0 0 0 0.1 0.2 0.3 0.5 0.8 0.9 1.0 1.0 0.99 0.9 0.7 0.4 0.1 0 0 0 0 0]\n")
        pv_file.write("New Tshape.Mytemp npts=24 interval=1\n")
        pv_file.write("temp=[25 25 25 25 25 25 25 25 35 40 45 50 60 60 55 40 35 30 25 25 25 25 25 25]\n")

    pv_pmpp = load * pv_factor
    pv_file.write(f"New PVSystem.PV{busName} phases={phase} bus1={bus} kv={voltage} irrad=0.98 pmpp={pv_pmpp} temperature=25 pf=1\n")
    pv_file.write("%cutin=0 %cutout=2 effcurve=MyEff P-tCurve=MyPvsT Daily=MyIrrad Tdaily=Mytemp\n\n\n")

    # pv_file.write(f"New Transformer.genpvup{count} phases=3 xhl=5.750000")
    # pv_file.write(f"wdg=1 bus=trafo_pv{count} kV=0.48 kVA={pv_pmpp} conn=wye")  
    # pv_file.write(f"wdg=2 bus={bus} kv=4.16 kVA={pv_pmpp} conn=wye")