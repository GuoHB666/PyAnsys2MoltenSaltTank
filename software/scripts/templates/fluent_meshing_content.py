# encoding: utf-8
ns_lists = ['axis', 'wall_ambient_boundary', 'wall_ambient_fluid', 'wall_inner_salt2air', 'wall_inner_fluid']
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
                    if entity_type == 'edge':
                        for line in body.Edges:
                            result_ids.append(line.Id)
                    elif entity_type == 'face':
                        for face in body.Faces:
                            result_ids.append(face.Id)
                    elif entity_type == 'body':
                        result_ids.append(body.Id)
    return result_ids
# 创建连接关系
## 清除自动生成的连接关系
for group in DataModel.GetObjectsByType(DataModelObjectCategory.ConnectionGroup):
    group.Delete()
## 采用线-线接触方式，自动生成接触对
connection_group = Model.Connections.AddConnectionGroup()
connection_group.ToleranceType = ContactToleranceType.Value
connection_group.ToleranceValue = Quantity(5e-3, 'm')
connection_group.FaceFace = False
connection_group.EdgeEdge = ContactEdgeEdgeOption.Yes
Model.Connections.CreateAutomaticConnections()
#endregion



# 边界命名
## 先清除
if Model.NamedSelections:
    for ns in Model.NamedSelections.Children:
        ns.Delete()
## 对称轴名称
ns = Model.AddNamedSelection()
ns.Name =ns_lists[0]
ns.ScopingMethod = GeometryDefineByType.Worksheet
ns.GenerationCriteria.Add(None)
ns.GenerationCriteria[0].EntityType = SelectionType.GeoEdge
ns.GenerationCriteria[0].Criterion = SelectionCriterionType.LocationY
ns.GenerationCriteria[0].Operator = SelectionOperatorType.Equal
ns.GenerationCriteria[0].Value = Quantity('0 [m]')
ns.Generate()
#endregion
## 环境域边界名称
### 边界域
ns = Model.AddNamedSelection()
ns.Name = ns_lists[1]
ns.ScopingMethod = GeometryDefineByType.Worksheet
ns.GenerationCriteria.Add(None)
ns.GenerationCriteria[0].EntityType = SelectionType.GeoEdge
ns.GenerationCriteria[0].Criterion = SelectionCriterionType.LocationX
ns.GenerationCriteria[0].Operator = SelectionOperatorType.Largest
ns.GenerationCriteria.Add(None)
ns.GenerationCriteria[1].Criterion = SelectionCriterionType.LocationX
ns.GenerationCriteria[1].Operator = SelectionOperatorType.Smallest
ns.GenerationCriteria.Add(None)
ns.GenerationCriteria[2].Criterion = SelectionCriterionType.LocationY
ns.GenerationCriteria[2].Operator = SelectionOperatorType.Largest
ns.Generate()
### 外空气域流体边界层
#### 获取目标实体所有边的id
all_edge_ids = get_entity_ids('edge', 'ambient_fluid')
#### 读取现有Name selection
selected_ids = []
for ns in Model.NamedSelections.Children:
    selected_ids.extend(ns.Location.Ids)
#### 去除已有Name selection中的id
needed_ids = [x for x in all_edge_ids if x not in selected_ids]
#### 命名
ns = Model.AddNamedSelection()
ns.Name = ns_lists[2]
ns.Location = select_by_ids(needed_ids)
## 内流体域边界层
### 熔盐=空气交界面的Name Selection
inventory_edges_ids =  get_entity_ids("edge","inventory")
edge_id_salt2air = []
for edge_id in inventory_edges_ids:
    if inventory_edges_ids.count(edge_id) > 1:
        edge_id_salt2air.append(edge_id)
        break
ns = Model.AddNamedSelection()
ns.Name = ns_lists[3]
ns.Location = select_by_ids(edge_id_salt2air)

### 流体-罐壁交界面的Name Selection
all_edge_ids = get_entity_ids('edge', 'inventory')
### 读取现有Name Selection
selected_ids = []
for ns in Model.NamedSelections.Children:
    selected_ids.extend(ns.Location.Ids)
### 去除已有Name selection中的id
needed_ids = [x for x in all_edge_ids if x not in selected_ids]
### 命名
ns = Model.AddNamedSelection()
ns.Name = ns_lists[4]
ns.Location = select_by_ids(needed_ids)
#endregion




# 网格划分
## 全局网格设置
## 预清除
if Model.Mesh:
    for mesh_children in Model.Mesh.Children:
        mesh_children.Delete()
mesh = Model.Mesh
mesh.ElementSize = Quantity('300 [mm]')
mesh.AutomaticMeshBasedDefeaturing = 0
mesh.CaptureCurvature = True
mesh.CurvatureNormalAngle = Quantity(3, 'deg')
mesh.CaptureProximity = True
mesh.NumberOfCellsAcrossGap = 3
mesh.MinimumSize = Quantity(1, 'mm') # 最小曲率加密尺寸
mesh.ProximityMinimumSize = Quantity(1, 'mm') # 最小狭缝加密尺寸

## 外环境域网格
### 网格划分方法
body_id = get_entity_ids('body', 'ambient_fluid')
mesh_method = mesh.AddAutomaticMethod()
mesh_method.Location = select_by_ids(body_id)
mesh_method.Method = MethodType.QuadTri # 即为多区域网格划分方法
### 膨胀层
all_edge_ids = get_entity_ids('edge', 'ambient_fluid')
selected_ids = []
for ns in Model.NamedSelections.Children:
    if "axis" in ns.Name:
        selected_ids.extend(ns.Location.Ids)
needed_ids = [x for x in all_edge_ids if x not in selected_ids]
inflation = mesh.AddInflation()
inflation.Location = select_by_ids(body_id)
inflation.BoundaryLocation = select_by_ids(needed_ids)
inflation.MaximumLayers = 10
inflation.InflationOption = 1 # 膨胀方法为给定第1层网格高度，对应选项为1
inflation.FirstLayerHeight = Quantity(10, 'mm')
### 面网格映射
face_ids = get_entity_ids('face','ambient')
facemeshing = mesh.AddFaceMeshing()
facemeshing.Location = select_by_ids(face_ids)

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
### 网格尺寸
body_ids1 = get_entity_ids('body','base')
body_ids2 = get_entity_ids('body','insulation')
size = mesh.AddSizing()
size.Location = select_by_ids(body_ids1+body_ids2)
size.ElementSize = Quantity(40, 'mm')
local_curvature = size.PropertyByName('UseCurvatureSize') # 启用局部曲率加密和狭缝加密。加密参数采用默认全局大小即可
local_curvature.InternalValue = True
local_proximity = size.PropertyByName('UseProximitySize')
local_proximity.InternalValue = True
## 罐内流体域网格
### 尺寸
body_ids = get_entity_ids('body', 'inventory')
size = mesh.AddSizing()
size.Location = select_by_ids(body_ids)
size.ElementSize = Quantity(39, 'mm')
local_curvature = size.PropertyByName('UseCurvatureSize') # 启用局部曲率加密和狭缝加密。加密参数采用默认全局大小即可
local_curvature.InternalValue = True
local_proximity = size.PropertyByName('UseProximitySize')
local_proximity.InternalValue = True
### 膨胀
inflation = mesh.AddInflation()
inflation.Location = select_by_ids(body_ids)
ns1_ids = list(DataModel.GetObjectsByName(ns_lists[3])[0].Location.Ids)
ns2_ids = list(DataModel.GetObjectsByName(ns_lists[4])[0].Location.Ids)
ns1_ids.extend(ns2_ids)
inflation.BoundaryLocation = select_by_ids(ns1_ids)
inflation.MaximumLayers = 10
inflation.InflationOption = 2 # 膨胀方法为平滑过渡，对应选项为2
inflation.GrowthRate = 1.3


# 生成网格
mesh.GenerateMesh()

