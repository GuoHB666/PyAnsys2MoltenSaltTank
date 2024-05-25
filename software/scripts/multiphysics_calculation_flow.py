# encoding: utf-8
# 2021 R2
file_mat_FEM =  r"D:\GuoHB\MyFiles\Code\PyAnsys2MoltenSaltTank\constant\mat_FEM_solid.xml"
script_path = {'geo_content': 'D:\\GuoHB\\MyFiles\\Code\\PyAnsys2MoltenSaltTank\\software\\scripts\\geo_content.py', 'fluent_content': 'D:\\GuoHB\\MyFiles\\Code\\PyAnsys2MoltenSaltTank\\software\\scripts\\fluent_content.jou', 'mechanical_content': 'D:\\GuoHB\\MyFiles\\Code\\PyAnsys2MoltenSaltTank\\software\\scripts\\mechanical_content.py', 'fluent_meshing_content': 'D:\\GuoHB\\MyFiles\\Code\\PyAnsys2MoltenSaltTank\\software\\scripts\\fluent_meshing_content.py', 'multiphysics_calculation_flow': 'D:\\GuoHB\\MyFiles\\Code\\PyAnsys2MoltenSaltTank\\software\\scripts\\multiphysics_calculation_flow.py'}

"""系统创建"""
SetScriptVersion(Version="21.2.209")
system_CFD = GetTemplate(TemplateName="Fluid Flow").CreateSystem()
geoComp = system_CFD.GetComponent(Name="Geometry")
system_FEM = GetTemplate(TemplateName="Static Structural", Solver="ANSYS").CreateSystem(
    ComponentsToShare=[geoComp], Position="Right", RelativeTo=system_CFD)
system_data = GetTemplate(TemplateName="External Data").CreateSystem(Position="Left", RelativeTo=system_FEM)
setupComp_data = system_data.GetComponent(Name="Setup")
setupComp_FEM = system_FEM.GetComponent(Name="Setup")
setupComp_data.TransferData(TargetComponent=setupComp_FEM)

"""创建几何"""
def get_geo_file(script_path, search_key_str = "geo_file_path"):
    with open(script_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if line.startswith(search_key_str):
            geo_file_str = line.split("=")[1] # 获取表征几何路径的字符串
            geo_file_str1 = geo_file_str.strip("' ").lstrip('r')
            geo_file = eval(geo_file_str1)
            break
    return geo_file
geo = system_CFD.GetContainer(ComponentName="Geometry")
geo.Edit(Interactive=False,IsSpaceClaimGeometry=True)
geo.RunScript(ScriptFile=script_path["geo_content"])
geo.Exit()
# 导入几何：SpaceClaim存在bug，若启用批处理计算，则几何得自己导入
geo.SetFile(FilePath=get_geo_file(script_path["geo_content"]))
# 几何属性为2D
geometryProperties1 = geo.GetGeometryProperties()
geometryProperties1.GeometryImportAnalysisType = "AnalysisType_2D"

"""CFD 网格划分"""
meshComp_CFD = system_CFD.GetComponent(Name="Mesh")
meshComp_CFD.Refresh()
mesh_CFD = system_CFD.GetContainer(ComponentName="Mesh")
#mesh_CFD.Edit(Interactive=False)
mesh_CFD.Edit()
cfdmesh_command = 'WB.AppletList.Applet("DSApplet").App.Script.doToolsRunMacro("%s")' \
                  % script_path["fluent_meshing_content"].replace("\\", "/") # ansys存在bug，命令难以执行带“\”的路径，需转换为“/”
mesh_CFD.SendCommand(Command=cfdmesh_command)
mesh_CFD.Exit()
meshComp_CFD.Update(AllDependencies=True)
"""CFD 求解计算"""
# 1. 启动
core_nums = 12
setupComp_CFD = system_CFD.GetComponent(Name="Setup")
setupComp_CFD.Refresh()
setup_CFD = system_CFD.GetContainer(ComponentName="Setup")
fluentLauncherSettings = setup_CFD.GetFluentLauncherSettings()
fluentLauncherSettings.SetEntityProperties(Properties=Set(Precision="Double",
      EnvPath={}, RunParallel=True, NumberOfProcessorsMeshing=core_nums, NumberOfProcessors=core_nums))
#setup_CFD.Edit(Interactive=False)
setup_CFD.Edit()
# 2. 运行计算
tui_command = '/file/read-journal \"{}\" yes yes'.format(script_path["fluent_content"])
setup_CFD.SendCommand(Command='/file/set-tui-version "21.2"')
setup_CFD.SendCommand(Command=tui_command)
setup_CFD.Exit()

"""导入材料数据"""

engineeringData = system_FEM.GetContainer(ComponentName="Engineering Data")
engineeringData.Import(Source=file_mat_FEM)

"""导入温度载荷"""
# 1. 获取Fluent导出的温度数据路径
import os
import re
def get_cfd_folder(setupComp_CFD):
    prj_files = GetAllFiles()
    cfd_file = setupComp_CFD.DirectoryName
    cfd_file = cfd_file.replace(" ", "-")
    for file in prj_files:
        if "wbpj" in file:
            directory = os.path.dirname(file)
            wbpj_name = os.path.basename(file).split(".")[0]
            cfd_folder = "{}\\{}_files\\dp0\\{}\\Fluent".format(directory, wbpj_name, cfd_file)
            break
    return cfd_folder
def get_cfd_output(script_path, search_key_str="export_file"):
    with open(script_path, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if search_key_str in line:
            start_index = line.find('"') + 1
            end_index = line.find('.txt', start_index)
            output_name = line[start_index:end_index]
            break
    return output_name
def get_all_cfdoutput(folder_path, file_key_str):
    cfd_output = None
    for root, dirs, files in os.walk(folder_path, topdown=False):
        output_names = [file for file in files if file_key_str in file]
        sorted_output_names = sorted(output_names, key=lambda x: int(re.search(r'-(\d+)\.\d+', x).group(1)))
        cfd_output = [os.path.join(root, file_name) for file_name in sorted_output_names]
    return cfd_output
cfd_folder = get_cfd_folder(setupComp_CFD)
cfd_output_name = get_cfd_output(script_path["fluent_tui"])
cfd_output_paths = get_all_cfdoutput(cfd_folder,cfd_output_name)

# 2. 导入数据：external data模块存在bug。导入到mechanical模块中后，无法选择
setup_data = system_data.GetContainer(ComponentName="Setup")
externalLoadFileData = setup_data.AddDataFile(FilePath=cfd_output_paths[-1]) # 导入最大时间载荷
cfd_temp_property = externalLoadFileData.GetDataProperty()
cfd_temp_property.FileIdentifier = os.path.basename(cfd_output_paths[-1])  # 改名字
## 温度载荷坐标变换：fluent是以x轴为对称轴。需要把结果数据转为y轴为对称轴
cfd_temp_property.SetDimensionType(Dimensions="Dimension2D")
externalLoadFileData.SetStartImportAtLine(FileDataProperty=cfd_temp_property, LineNumber=2)
cfd_temp_property.SetLengthUnit(Unit="m")
cfd_temp_property.ThetaXYUnit = "degree"
cfd_temp_property.ThetaYZUnit = "degree"
cfd_temp_property.ThetaXY = 90
cfd_temp_property.ThetaYZ = 180
## 温度载荷坐标定义
column_types = ["Node ID", "X Coordinate", "Y Coordinate", "Temperature"]
for column_type, column_data in zip(column_types, cfd_temp_property.ColumnsData):
    cfd_temp_property.SetColumnDataType(ColumnData=column_data, DataType=column_type)
    if column_type == "Temperature":
        column_data.Unit = "K"
setupComp_data.Update(AllDependencies=True)

"""静力学计算"""
setup_FEM = system_FEM.GetContainer(ComponentName="Setup")
setup_FEM.Edit()
mechanical_command = 'WB.AppletList.Applet("DSApplet").App.Script.doToolsRunMacro("%s")' \
                  % script_path["mechanical_content"].replace("\\", "/") # ansys存在bug，命令难以执行带“\”的路径，需转换为“/”
setup_FEM.SendCommand(Command=mechanical_command)