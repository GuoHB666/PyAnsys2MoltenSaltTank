
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
setupComp_mechanical = system_mechanical.GetComponent(Name="Setup")
setupComp_external.TransferData(TargetComponent=setupComp_mechanical)
setup_external = system_external.GetContainer(ComponentName="Setup")
sys_geo_all.DisplayText = "Fluid and solid zone"
sys_geo_solid.DisplayText = "Only solid zone"


"""建立几何模型"""
geo_all.SetFile(FilePath=r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\geometry\HM_Static.agdb")
geo_solid = sys_geo_solid.GetContainer(ComponentName="Geometry")
geo_solid.SetFile(FilePath=r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\geometry\HM_Static.agdb")











"""FLUENT 网格划分 """

# 1. refresh Fluent system
meshComponent_fluent = system_fluid.GetComponent(Name="Mesh")
meshComponent_fluent.Refresh()

# 2. Fluent mesh generation
mesh_fluent_path = r"D:\\GuoHB\\MyFiles\\Code\\PyAnsysWorkbench\\software\\scripts\\HM Static\\CFD_meshing_content.py"
command_content = 'WB.AppletList.Applet("DSApplet").App.Script.doToolsRunMacro("%s")' % mesh_fluent_path

mesh_fluent = system_fluid.GetContainer(ComponentName="Mesh")
mesh_fluent.Edit(Interactive=False)
mesh_fluent.SendCommand(Command=command_content)
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
fluent_tui_file = r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\scripts\HM Static\fluent_tui_command.jou"
jou_command = '/file/read-journal \"{}\" yes yes'.format(fluent_tui_file)
setup_fluent.SendCommand(Command='/file/set-tui-version "21.2"')
setup_fluent.SendCommand(Command=jou_command)





# 通过如下命令，获取到FLUENT文件夹
import os
prj_files = GetAllFiles()
setup_comp_fluent = system_fluid.GetComponent(Name="Setup")
cfd_file = setup_comp_fluent.DirectoryName
cfd_file = cfd_file.replace(" ", "-")
for file in prj_files:
    if "wbpj" in file:
        directory = os.path.dirname(file)
        wbpj_name = os.path.basename(file).split(".")[0]
        fluent_folder = "{}\\{}_files\\dp0\\{}\\Fluent".format(directory, wbpj_name, cfd_file)
        break
print(fluent_folder)