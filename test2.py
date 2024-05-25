files = ['D:/GuoHB/MyFiles/Code/PyAnsys2MoltenSaltTank/constant/mat_FEM_solid.xml','D:/GuoHB/MyFiles/Code/PyAnsys2MoltenSaltTank/constant/mat_FEM_fluid.xml']
system = GetTemplate(TemplateName="EngData").CreateSystem()
engineeringData = system.GetContainer(ComponentName="Engineering Data")
for file in files:
    engineeringData.Import(Source=file)