
SetScriptVersion(Version="21.2.209")

"""使用到的模拟系统模板"""
template_geo = GetTemplate(TemplateName="Geometry")
template_fluid = GetTemplate(TemplateName="Fluid Flow")
template_mechanical = GetTemplate(TemplateName="Static Structural", Solver="ANSYS")
template_external = GetTemplate(TemplateName="External Data")

"""系统创建"""
sys_geo_all = template_geo.CreateSystem()
geo_all_comp = sys_geo_all.GetComponent(Name="Geometry")
# 流热分析系统
system_fluid = template_fluid.CreateSystem(
    ComponentsToShare=[geo_all_comp], Position="Right", RelativeTo=sys_geo_all)
geo_all = sys_geo_all.GetContainer(ComponentName="Geometry")
# 热力学分析系统
sys_geo_solid = template_geo.CreateSystem(Position="Right", RelativeTo=system_fluid)
geo_solid_comp = sys_geo_solid.GetComponent(Name="Geometry")
system_mechanical = template_mechanical.CreateSystem(
    ComponentsToShare=[geo_solid_comp],Position="Right", RelativeTo=sys_geo_solid)
# 数据传递系统
system_external = template_external.CreateSystem(Position="Left", RelativeTo=system_mechanical)
setupComp_external = system_external.GetComponent(Name="Setup")
setup_comp_mechanical = system_mechanical.GetComponent(Name="Setup")
setupComp_external.TransferData(TargetComponent=setup_comp_mechanical)
setup_external = system_external.GetContainer(ComponentName="Setup")
sys_geo_all.DisplayText = "Fluid and solid zone"
sys_geo_solid.DisplayText = "Only solid zone"


"""导入几何模型"""
geo_all.SetFile(FilePath=r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\geometry\HM_Static.agdb")
geo_solid = sys_geo_solid.GetContainer(ComponentName="Geometry")
geo_solid.SetFile(FilePath=r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\geometry\HM_Static.agdb")











"""导入温度温度载荷"""
cfdSolidTemp = setup_external.AddDataFile(FilePath="D:/GuoHB/MyFiles/Simulation/MoltenSaltTank2021-v3/Data/CFD result/h13_solid_temp")
cfdSolidTempProperty = cfdSolidTemp.GetDataProperty()
cfdSolidTempProperty.FileIdentifier = "h13" # 改名字
# 温度载荷坐标变换：fluent是以x轴为对称轴。需要把结果数据转为y轴为对称轴
cfdSolidTempProperty.SetDimensionType(Dimensions="Dimension2D")
cfdSolidTemp.SetStartImportAtLine(FileDataProperty=cfdSolidTempProperty, LineNumber=2)
cfdSolidTempProperty.SetLengthUnit(Unit="m")
cfdSolidTempProperty.ThetaXYUnit = "degree"
cfdSolidTempProperty.ThetaYZUnit = "degree"
cfdSolidTempProperty.ThetaXY = 90
cfdSolidTempProperty.ThetaYZ = 180
# 温度载荷坐标定义
externalLoadColumnData = cfdSolidTempProperty.GetColumnData(Name="ExternalLoadColumnData")
cfdSolidTempProperty.SetColumnDataType(ColumnData=externalLoadColumnData, DataType="Node ID")
externalLoadColumnData2 = cfdSolidTempProperty.GetColumnData(Name="ExternalLoadColumnData 1")
cfdSolidTempProperty.SetColumnDataType(ColumnData=externalLoadColumnData2, DataType="X Coordinate")
externalLoadColumnData3 = cfdSolidTempProperty.GetColumnData(Name="ExternalLoadColumnData 2")
cfdSolidTempProperty.SetColumnDataType(ColumnData=externalLoadColumnData3, DataType="Y Coordinate")
externalLoadColumnData4 = cfdSolidTempProperty.GetColumnData(Name="ExternalLoadColumnData 3")
cfdSolidTempProperty.SetColumnDataType(ColumnData=externalLoadColumnData4, DataType="Temperature")
externalLoadColumnData4.Unit = "K"
setupComp_external.Update(AllDependencies=True)




"""FLUENT 网格划分 """

# 1. refresh Fluent system
meshComponent_fluent = system_fluid.GetComponent(Name="Mesh")
meshComponent_fluent.Refresh()

# 2. Fluent mesh generation
mesh_fluent_path = r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\scripts\HM Static\CFD_meshing_content.py"
mesh_fluent_content = open(mesh_fluent_path, 'r').read()
mesh_fluent = system_fluid.GetContainer(ComponentName="Mesh")
mesh_fluent.Edit(Interactive=False)
mesh_fluent.SendCommand(Language="Python", Command=mesh_fluent_content)
mesh_fluent.Exit()


# 3. transfer mesh file to Fluent
meshComponent_fluent.Update(AllDependencies=True)

"""FLUENT 求解计算"""
# 1. 启动
core_nums = 12
setupComponent_fluent = system_fluent.GetComponent(Name="Setup")
setupComponent_fluent.Refresh()
setup_fluent = system_fluent.GetContainer(ComponentName="Setup")
fluentLauncherSettings = setup_fluent.GetFluentLauncherSettings()
fluentLauncherSettings.SetEntityProperties(Properties=Set(Precision="Double",
      EnvPath={}, RunParallel=True, NumberOfProcessorsMeshing=core_nums, NumberOfProcessors=core_nums))
setup_fluent.Edit(Interactive=False)
# 2. 运行计算
#fluent_tui_file = r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\scripts\fluent\script\Fluent_tui_command.jou"
fluent_tui_file = r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\scripts\HM Static\CFD_calculation_content.jou"
jou_command = '/file/read-journal \"{}\" yes yes'.format(fluent_tui_file)
setup_fluent.SendCommand(Command='/file/set-tui-version "21.2"')
setup_fluent.SendCommand(Command=jou_command)



