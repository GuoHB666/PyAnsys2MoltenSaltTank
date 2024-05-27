# encoding: utf-8

"""===================================初始化===================================="""
ns_lists = ['axis', 'wall_tank_inner', 'wall_base_bottom']
body_mats = {'ambient_soil': 'dry_sand', 'insulation1': 'magnesium_silicate', 'insulation2': 'glass_wool', 'base3': 'coarse_sand', 'base2': 'ceramsite_hm', 'base4': 'concrete_hm', 'base1': 'fine_gravel', 'base5': 'firebrick', 'tank': 'tp347h'}
salt_inventory = 12900 # 熔盐液位，单位mm
def select_by_ids(ids):
    ExtAPI.SelectionManager.ClearSelection()
    selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    selection.Ids = ids
    return selection


def get_entity_ids(entity_type, body_name):
    result_ids = []
    for assembly in DataModel.GeoData.Assemblies:
        for part in assembly.Parts:
            for body in part.Bodies:
                if body_name in body.Name:
                    entities = {'edge': body.Edges, 'face': body.Faces, 'body': [body]}
                    result_ids.extend(entity.Id for entity in entities[entity_type])
    return result_ids


def get_maxsize(vertice_ids, dimension, is_max=True):
    coordinates = {
        "X": [DataModel.GeoData.GeoEntityById(id).X for id in vertice_ids],
        "Y": [DataModel.GeoData.GeoEntityById(id).Y for id in vertice_ids],
        "Z": [DataModel.GeoData.GeoEntityById(id).Z for id in vertice_ids]
    }
    if dimension not in coordinates:
        raise ValueError("Invalid dimension. Use 'X', 'Y', or 'Z'.")
    return max(coordinates[dimension]) if is_max else min(coordinates[dimension])


# 单位转换：采用mm、Mpa
ExtAPI.Application.ActiveUnitSystem = MechanicalUnitSystem.StandardNMM
# 先统一清除
## 有固定规律的：不必要坐标变换、连接关系、网格方法、Name Selection
collections = [
    Model.PartTransformGroup.Children if Model.PartTransformGroup else [],
    DataModel.GetObjectsByType(DataModelObjectCategory.ConnectionGroup),
    Model.Mesh.Children,
    Model.NamedSelections.Children if Model.NamedSelections else []
]
for collection in collections:
    for item in collection:
        item.Delete()
## 不必要边界条件和后处理
undeleted_options = ["Setting", "Solution", "Load", "Initial"]
for analysis in DataModel.AnalysisList:
    for analysis_children in analysis.Children:
        if not any(undeleted_option in analysis_children.Name for undeleted_option in undeleted_options):
            analysis_children.Delete()
        if "Solution" in analysis_children.Name:
            for result in analysis_children.Children:
                if not "Information" in result.Name:
                    result.Delete()
## 不必要的温度载荷
import_load_groups = []
for analysis in DataModel.AnalysisList:
    for analysis_children in analysis.Children:
        if "Load" in analysis_children.Name:
            import_load_group = analysis_children
            import_load_groups.append(import_load_group)
            for import_load in import_load_group.Children:
                import_load.Delete()
#### ansys bug，无法插入温度载荷后马上给定几何。得等一会儿，因此自己把插入温度载荷放到前边
thermal_loads = [import_load_groups[0].AddImportedBodyTemperature(), import_load_groups[1].AddImportedTemperature()]
## 不必要局部坐标
for coordinate in Model.CoordinateSystems.Children:
    if "Global" not in coordinate.Name:
        coordinate.Delete()
"""===================================开展计算===================================="""
# 定义局部坐标
local_cs = Model.CoordinateSystems.AddCoordinateSystem()
local_cs.OriginDefineBy = CoordinateSystemAlignmentType.Fixed
local_cs.OriginX = Quantity(0, "mm")
local_cs.OriginY = Quantity(0, "mm")
local_cs.PrimaryAxisDefineBy = CoordinateSystemAlignmentType.GlobalY
local_cs.SecondaryAxisDefineBy = CoordinateSystemAlignmentType.GlobalX

# 坐标变换，y轴变成对称轴
## 先获得所有实体的id
all_body_ids = get_entity_ids('body', '')
## 进行坐标变换
part_transform = Model.AddPartTransform()
part_transform.Location = select_by_ids(all_body_ids)
part_transform.DefineBy = PartTransformationDefinitionType.CoordinateSystem
part_transform.TargetCoordinateSystem = local_cs
Model.PartTransformGroup.TransformGeometry()


## 使用2D轴对称
geometry = Model.Geometry
geometry.Model2DBehavior = Model2DBehavior.AxiSymmetric


# 边界命名
def add_named_selection(name, dimension, value, coordinate_system):
    ns = Model.AddNamedSelection()
    ns.Name = name
    ns.ScopingMethod = GeometryDefineByType.Worksheet
    ns.GenerationCriteria.Add(None)
    ns.GenerationCriteria[0].EntityType = SelectionType.GeoEdge
    ns.GenerationCriteria[0].Criterion = SelectionCriterionType.LocationY if dimension == 'Y' else SelectionCriterionType.LocationX
    ns.GenerationCriteria[0].Operator = SelectionOperatorType.Equal
    ns.GenerationCriteria[0].Value = Quantity('{} [m]'.format(value))
    ns.GenerationCriteria[0].CoordinateSystem = coordinate_system
    ns.Generate()
def add_named_selection2(name, location_ids):
    ns = Model.AddNamedSelection()
    ns.Name = name
    ns.Location = select_by_ids(location_ids)
    ns.Generate()
## 轴对称和地基最底面：都是采用 worksheet的方法
add_named_selection(ns_lists[0], 'Y', 0, local_cs)  # Axis
add_named_selection(ns_lists[2] , 'X', 0, local_cs)  # Base bottom
## 内壁面命名
tank_vertice_ids = []
inventory_vertice_ids = []
for assembly in DataModel.GeoData.Assemblies:
    for part in assembly.Parts:
        for body in part.Bodies:
            if "tank" in body.Name:
                for vertice in body.Vertices:
                    tank_vertice_ids.append(vertice.Id)
            elif "inventory" in body.Name:
                for vertice in body.Vertices:
                    inventory_vertice_ids.append(vertice.Id)
location_tanktop = get_maxsize(tank_vertice_ids,"Y",is_max=True)
location_tankbottom = get_maxsize(tank_vertice_ids,"Y",is_max=False)
Rwall = get_maxsize(inventory_vertice_ids,"X",is_max=True)
tank_edge_ids = []
for assembly in DataModel.GeoData.Assemblies:
    for part in assembly.Parts:
        for body in part.Bodies:
            if "tank" in body.Name:
                for edge in body.Edges:
                    is_select = True
                    for vertice in edge.Vertices:
                        if vertice.Y <= location_tankbottom or vertice.Y >= location_tanktop or vertice.X > Rwall:
                            is_select = False
                    if is_select:
                        tank_edge_ids.append(edge.Id)
selected_ids = [location_id for ns in Model.NamedSelections.Children for location_id in ns.Location.Ids]
wall_tank_ids = [x for x in tank_edge_ids if x not in selected_ids]
### 命名
add_named_selection2(ns_lists[1], wall_tank_ids)


# 抑制不需要几何并进行相应材料给定
unneed_bodies = ["insulation", "ambient", "inventory"]
for part in Model.Geometry.Children:
    for body in part.Children:
        if any(unneed_body in body.Name for unneed_body in unneed_bodies):
            body.Suppressed = True
        else:
            for body_short_name, mat_name in body_mats.items():
                if body_short_name in body.Name:
                    body.Material = mat_name
                    break
# 接触关系
## 采用线-线接触方式，自动生成接触对
connection_group = Model.Connections.AddConnectionGroup()
connection_group.ToleranceType = ContactToleranceType.Value
connection_group.ToleranceValue = Quantity(5e-3, 'm')
connection_group.FaceFace = False
connection_group.EdgeEdge = ContactEdgeEdgeOption.Yes
Model.Connections.CreateAutomaticConnections()
## 使用摩擦接触，摩擦系数为0.3
for contact_groups in Model.Connections.Children:
    for contact in contact_groups.Children:
        # 统一把目标面改为储罐
        if "tank" not in contact.ContactBodies:
            contact.FlipContactTarget()
            contact.RenameBasedOnDefinition()
        contact.ContactType = ContactType.Frictional
        contact.FrictionCoefficient = 0.3


# 网格划分
## 全局网格设置
mesh = Model.Mesh
mesh.ElementSize = Quantity('40 [mm]')
mesh.AutomaticMeshBasedDefeaturing = 0
mesh.CaptureCurvature = True
mesh.CurvatureNormalAngle = Quantity(3, 'deg')
mesh.CaptureProximity = True
mesh.NumberOfCellsAcrossGap = 3
mesh.MinimumSize = Quantity(1, 'mm') # 最小曲率加密尺寸
mesh.ProximityMinimumSize = Quantity(1, 'mm') # 最小狭缝加密尺寸
## 隔热域网格
### 网格划分方法
body_ids = get_entity_ids('body','base')
unneed_id = get_entity_ids('body','base5')[0]
body_ids.remove(unneed_id)
mesh_method = mesh.AddAutomaticMethod()
mesh_method.Location = select_by_ids(body_ids)
mesh_method.Method = MethodType.QuadTri # 即为多区域网格划分方法
### 面网格映射
face_ids = get_entity_ids('face','base')
facemeshing = mesh.AddFaceMeshing()
facemeshing.Location = select_by_ids(face_ids)
## 生成网格
mesh.GenerateMesh()




# 定义分析对象
analysis_mechanical = DataModel.AnalysisList[0]
analysis_thermal = DataModel.AnalysisList[1]
# 给定边界条件
## 轴对称约束
displacement = analysis_mechanical.AddDisplacement()
displacement.Location = DataModel.GetObjectsByName(ns_lists[0])[0]
displacement.XComponent.Output.DiscreteValues = [Quantity(0, "m")]
## 固定约束
fix_support = analysis_mechanical.AddFixedSupport()
fix_support.Location = DataModel.GetObjectsByName(ns_lists[2])[0]
## 施加重力加速度
earth_gravity = analysis_mechanical.AddEarthGravity()
## 液位载荷
### 定义局部坐标2
local_coordinate_system2 = Model.CoordinateSystems.AddCoordinateSystem()
local_coordinate_system2.OriginDefineBy = CoordinateSystemAlignmentType.Fixed
local_coordinate_system2.OriginX = Quantity(0, "m")
local_coordinate_system2.OriginY = Quantity(location_tankbottom, "m")
### 施加
hydrostatic_pressure = analysis_mechanical.AddHydrostaticPressure()
hydrostatic_pressure.FluidDensity = Quantity(1725, "kg m^-1 m^-1 m^-1") # 熔盐密度
hydrostatic_pressure.DefineBy = LoadDefineBy.Components
hydrostatic_pressure.CoordinateSystem = local_coordinate_system2
hydrostatic_pressure.YCoordinate = Quantity(salt_inventory, "mm")
hydrostatic_pressure.Location = DataModel.GetObjectsByName(ns_lists[1])[0]
hydrostatic_pressure.YComponent.Output.DiscreteValues = [Quantity(9.8, "m s^-2")]
## 温度载荷
for thermal_load in thermal_loads:
    thermal_load.Location = select_by_ids(all_body_ids)
    thermal_load.ImportLoad()

# 开始求解
## 静力学分析
analysis_setting = analysis_mechanical.AnalysisSettings
analysis_setting.NewtonRaphsonOption = NewtonRaphsonType.Unsymmetric # 求解算法：改为非对称
analysis_mechanical.Solve(True)
## 热分析（仅用于导出温度场）
analysis_thermal.Solve(True)

"""===================================后处理===================================="""
# 后处理
## 启用轴对称显示
# symmetry = Model.AddSymmetry()
# symmetry.PropertyByName("ExpansionType_1").InternalValue = 2 # 转为轴对称显示
# symmetry.PropertyByName("ExpansionNumRepeat_1").InternalValue = 10

## 插入总位移和总应力显示
mechanical_analysis_solution = analysis_mechanical.Solution
total_deformation = mechanical_analysis_solution.AddTotalDeformation()
tank_id = get_entity_ids("body", "tank")
total_deformation.Location = select_by_ids(tank_id)
equivalent_stress = mechanical_analysis_solution.AddEquivalentStress()
equivalent_stress.Location = select_by_ids(tank_id)
mechanical_analysis_solution.EvaluateAllResults()
## 插入温度场显示
thermal_analysis_solution = analysis_thermal.Solution
temperature = thermal_analysis_solution.AddTemperature()
temperature.Location = select_by_ids(tank_id)
thermal_analysis_solution.EvaluateAllResults()
## 导出
import time
import wbjn
import os
def get_out_path(file_name):
    cmd = "returnValue(GetUserFilesDirectory())"
    ansys_user_dir = wbjn.ExecuteCommand(ExtAPI,cmd)
    desired_level = 3  # 根据层级返回所需的上级目录
    current_path = ansys_user_dir
    for _ in range(desired_level):
        current_path = os.path.dirname(current_path)
    prj_dir = current_path
    result_dir = os.path.join(prj_dir, "result")

    out_name = "{}_{}.avz".format(time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time())), file_name)
    return os.path.join(result_dir, out_name)


result_objs = {
    "deformation": total_deformation,
    "stress": equivalent_stress,
    "temperature": temperature
}
for file_name, result_obj in result_objs.items():
    result_obj.Activate()  # 激活对象，相当于选中
    Graphics.GlobalLegendSettings.ShowDateAndTime = False
    selection = ExtAPI.SelectionManager.CreateSelectionInfo(SelectionTypeEnum.GeometryEntities)
    setting3d = Ansys.Mechanical.Graphics.Graphics3DExportSettings()
    setting3d.Background = GraphicsBackgroundType.White
    Graphics.Export3D(get_out_path(file_name), Graphics3DExportFormat.AVZ, setting3d)

