template_geo = GetTemplate(TemplateName="Geometry")
template_fluid = GetTemplate(TemplateName="Fluid Flow")

"""系统创建"""
sys_geo_all = template_geo.CreateSystem()
geo_all_comp = sys_geo_all.GetComponent(Name="Geometry")
# 流热分析系统
system_fluid = template_fluid.CreateSystem(
    ComponentsToShare=[geo_all_comp], Position="Right", RelativeTo=sys_geo_all)
geo_all = sys_geo_all.GetContainer(ComponentName="Geometry")
"""导入几何模型"""
geo_all.SetFile(FilePath=r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\geometry\HM_Static.agdb")



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
# # 1. 启动
# core_nums = 12
# setupComponent_fluent = system_fluent.GetComponent(Name="Setup")
# setupComponent_fluent.Refresh()
# setup_fluent = system_fluent.GetContainer(ComponentName="Setup")
# fluentLauncherSettings = setup_fluent.GetFluentLauncherSettings()
# fluentLauncherSettings.SetEntityProperties(Properties=Set(EnvPath={}, RunParallel=True, NumberOfProcessorsMeshing=core_nums, NumberOfProcessors=core_nums))
# setup_fluent.Edit(Interactive=True)
# # 2. 运行计算
# fluent_tui_file = r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\scripts\fluent\script\Fluent_tui_command.jou"
# jou_command = '/file/read-journal \"{}\" yes yes'.format(fluent_tui_file)
# setup_fluent.SendCommand(Command='/file/set-tui-version "21.2"')
# setup_fluent.SendCommand(Command=jou_command)
