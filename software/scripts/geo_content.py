# Python Script, API Version = V20
import math
ClearAll()
origin_basexy = [0,0]
body_names = ["ambient_fluid", "inventory_air", "inventory_salt","tank","insulation1","insulation2",
              "base3","base5","base4","base4","base4","base2","ambient_soil","base1"]
geo_file_path = r"D:\GuoHB\MyFiles\Code\PyAnsys2MoltenSaltTank\software\geometry\geo.scdoc"
geo_param = {'Lbottom': [8305.0, 2000.0], 'thick_bottom': [10.0, 22.0], 'Lbottom_weld': [8.0, 8.0, 48.0], 'hbottom_weld': [18.68, 18.68], 'angle_bottom': 0.859, 'Rwall': 10175.0, 'Rtop': 24400.0, 'htop': 2231.0, 'hwall': [2000.0, 2000.0, 2000.0, 2000.0, 2000.0, 4410.0], 'thick_wall': [30.0, 22.0, 20.0, 16.0, 14.0, 10.0], 'ratio_weld': [4.0, 4.0, 4.0, 4.0, 4.0], 'num_insulation': 2.0, 'thick_insulation': [250.0, 220.0], 'num_corebase': 3.0, 'Lbase': [13200.0, 10750.0, 10000.0, 200.0, 3800.0, 250.0, 1000.0], 'hbase': [400.0, 1400.0, 300.0, 1100.0], 'inventory': 12900.0}
""""草图绘制"""

# Set New Sketch
result = SketchHelper.StartConstraintSketching()
plane = Plane.PlaneXY
result = ViewHelper.SetSketchPlane(plane)
# EndBlock

# base1: 细砾石
## 坐标
Hbase1 = geo_param["hbase"][0]
Lbase1 = geo_param["Lbase"][0]
pos1 = [origin_basexy[0], origin_basexy[1]]
pos2 = [pos1[0] + Hbase1, pos1[1]]
pos3 = [pos2[0], Lbase1]
## 绘图
point1 = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
point2 = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
point3 = Point2D.Create(MM(pos3[0]), MM(pos3[1]))
SketchRectangle.Create(point1, point2, point3)

# base2: 陶粒土
## 坐标
Hbase2 = geo_param["hbase"][1]
Lbase2 = geo_param["Lbase"][1]
pos1 = [origin_basexy[0] + Hbase1, origin_basexy[1]]
pos2 = [pos1[0] + Hbase2, pos1[1]]
pos3 = [pos2[0], Lbase2]
## 绘图
point1 = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
point2 = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
point3 = Point2D.Create(MM(pos3[0]), MM(pos3[1]))
SketchRectangle.Create(point1, point2, point3)
# base4: 陶粒混凝土
## 坐标
Hbase4 = geo_param["hbase"][3]
Lbase41 = geo_param["Lbase"][3]
Lbase42 = geo_param["Lbase"][4]
pos1 = [origin_basexy[0] + Hbase1, origin_basexy[1]]
pos2 = [pos1[0] + Hbase4, pos1[1]]
pos3 = [pos2[0], Lbase41 / 2]
pos4 = [pos1[0], pos1[1] + Lbase42 - Lbase41 / 2]
pos5 = [pos4[0] + Hbase4, pos4[1]]
pos6 = [pos4[0], pos3[1] + Lbase42]
pos7 = [pos1[0], pos1[1] + 2 * Lbase42 - Lbase41 / 2]
pos8 = [pos7[0] + Hbase4, pos7[1]]
pos9 = [pos7[0], pos6[1] + Lbase42]
## 绘图
point1 = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
point2 = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
point3 = Point2D.Create(MM(pos3[0]), MM(pos3[1]))
point4 = Point2D.Create(MM(pos4[0]), MM(pos4[1]))
point5 = Point2D.Create(MM(pos5[0]), MM(pos5[1]))
point6 = Point2D.Create(MM(pos6[0]), MM(pos6[1]))
point7 = Point2D.Create(MM(pos7[0]), MM(pos7[1]))
point8 = Point2D.Create(MM(pos8[0]), MM(pos8[1]))
point9 = Point2D.Create(MM(pos9[0]), MM(pos9[1]))
SketchRectangle.Create(point1, point2, point3)
SketchRectangle.Create(point4, point5, point6)
SketchRectangle.Create(point7, point8, point9)
# base5: 环形耐火砖
## 坐标
Lbase51 = geo_param["Lbase"][5]
Lbase52 = geo_param["Lbase"][6]
Hbase3 = geo_param["hbase"][2]
Hbase5 = Hbase2 + Hbase3
pos1 = [origin_basexy[0] + Hbase1, origin_basexy[1] + Lbase2]
pos2 = [pos1[0], pos1[1] + Lbase51]
pos3 = [pos2[0] + Hbase5, pos2[1]]
pos4 = [pos3[0], pos3[1] - Lbase52]
pos5 = [pos4[0] - Hbase3, pos4[1]]
## 绘图
point1 = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
point2 = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
point3 = Point2D.Create(MM(pos3[0]), MM(pos3[1]))
point4 = Point2D.Create(MM(pos4[0]), MM(pos4[1]))
point5 = Point2D.Create(MM(pos5[0]), MM(pos5[1]))
SketchRectangle.Create(point1, point2, point3)
SketchRectangle.Create(point4, point5, point3)
## 裁剪多余线段
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[27], 0.136536434463862)
TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[23], 0.161988494183368)
TrimSketchCurve.Execute(curveSelPoint)

# tank bottom: 从罐底边缘板外侧点，开始逆时针
## 坐标
Rwall = geo_param["Rwall"]
thic_wall1 = geo_param["thick_wall"][0]
Hbases = sum(geo_param["hbase"][0:3])
Lbottom1 = geo_param["Lbottom"][0]
Lbottom2 = geo_param["Lbottom"][1]
thick_bottom1 = geo_param["thick_bottom"][0]
thick_bottom2 = geo_param["thick_bottom"][1]
lbottom_weld1 = geo_param["Lbottom_weld"][0]
lbottom_weld2 = geo_param["Lbottom_weld"][1]
lbottom_weld3 = geo_param["Lbottom_weld"][2]
hbottom_weld1 = geo_param["hbottom_weld"][0]
hbottom_weld2 = geo_param["hbottom_weld"][1]
theta = geo_param["angle_bottom"]
theta_radians = math.radians(theta)
h_bulge = math.tan(theta_radians) * Lbottom1
pos1 = [origin_basexy[0]+Hbases+thick_bottom2,origin_basexy[1]+Rwall+thic_wall1+lbottom_weld2]
pos2 = [pos1[0],origin_basexy[1]+Lbottom1+Lbottom2]
pos3 = [pos2[0]-thick_bottom2,pos2[1]]
pos4 = [pos3[0],pos3[1]-Lbottom2]
pos5 = [pos4[0]+h_bulge,pos4[1]-Lbottom1]
pos6 = [pos5[0]+thick_bottom1,pos5[1]]
pos7 = [pos4[0]+thick_bottom1,pos4[1]]
pos8 = [pos1[0],pos7[1]+lbottom_weld3]
pos9 = [pos8[0],Rwall-lbottom_weld1]
## 绘图
point1 = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
point2 = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
point3 = Point2D.Create(MM(pos3[0]), MM(pos3[1]))
point4 = Point2D.Create(MM(pos4[0]), MM(pos4[1]))
point5 = Point2D.Create(MM(pos5[0]), MM(pos5[1]))
point6 = Point2D.Create(MM(pos6[0]), MM(pos6[1]))
point7 = Point2D.Create(MM(pos7[0]), MM(pos7[1]))
point8 = Point2D.Create(MM(pos8[0]), MM(pos8[1]))
point9 = Point2D.Create(MM(pos9[0]), MM(pos9[1]))
SketchLine.Create(point1, point2)
SketchLine.Create(point2, point3)
SketchLine.Create(point3, point4)
SketchLine.Create(point4, point5)
SketchLine.Create(point5, point6)
SketchLine.Create(point6, point7)
SketchLine.Create(point7, point8)
SketchLine.Create(point8, point9)


# tank wall
### 坐标
Hwalls = geo_param["hwall"]
thick_walls = geo_param["thick_wall"]
Hwelds = [geo_param["hbottom_weld"][0]]
for i,ratio_weld in enumerate(geo_param["ratio_weld"]):
    lwall_weldi = thick_walls[i]-thick_walls[i+1]
    Hwelds.append(lwall_weldi*ratio_weld)
Hwelds.append(geo_param["hbottom_weld"][1])
## 外侧
for i in range(len(Hwalls)):
    pos1 = [Hbases + thick_bottom2, Rwall + thick_walls[i] + lbottom_weld2] if i==0 else pos3
    pos2 = [pos1[0] + Hwelds[i], Rwall + thick_walls[i]]
    pos3 = [pos1[0] + Hwalls[i], pos2[1]]
    point1 = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
    point2 = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
    point3 = Point2D.Create(MM(pos3[0]), MM(pos3[1]))
    SketchLine.Create(point1, point2)
    SketchLine.Create(point2, point3)
## 内侧
pos2 = [pos3[0], pos3[1]-thick_walls[-1]]
pos3 = [pos3[0]-sum(Hwalls)+Hwelds[-1], pos2[1]]
pos4 = [pos3[0]-Hwelds[-1], pos3[1]-lbottom_weld1]
point1 = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
point2 = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
point3 = Point2D.Create(MM(pos3[0]), MM(pos3[1]))
point4 = Point2D.Create(MM(pos4[0]), MM(pos4[1]))
SketchLine.Create(point2, point3)
SketchLine.Create(point3, point4)

# tank top
Rtop = geo_param["Rtop"]
htop = geo_param["htop"]
orign_top = [Hbases + thick_bottom2 + sum(Hwalls) - (Rtop - htop), 0]
pos1 = [orign_top[0] + (Rtop - htop), Rwall]
pos2 = [pos1[0] + htop, 0]

point_origin = Point2D.Create(MM(orign_top[0]), MM(orign_top[1]))
point_start = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
point_end = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
senseClockWise = True
SketchArc.CreateSweepArc(point_origin, point_start, point_end, senseClockWise)

## 罐顶曲线等距
curvesToOffset = Selection.Create(GetRootPart().DatumPlanes[0].Curves[50])
offsetDistance = MM(-thick_walls[-1])
SketchOffsetCurve.Create(curvesToOffset, offsetDistance)
## 罐顶曲线和罐内壁合并
curveOneSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[51], 0.430046447607366)
curveTwoSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[47], 4.38418308836962)
SketchCorner.Create(curveOneSelPoint, curveTwoSelPoint)

# insulation
## 外侧
angle_insulation = [150,300]
thick_insulations = geo_param["thick_insulation"]

pos1 = [Hbases, Rwall + thick_walls[0] + thick_insulations[0]]
pos2 = [pos1[0] + 1e3, pos1[1]]
point1 = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
point2 = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
SketchLine.Create(point1, point2)

### 保温层内层顶部等距
curvesToOffset = Selection.Create(GetRootPart().DatumPlanes[0].Curves[51])
offsetDistance = MM(-thick_insulations[0])
result = SketchOffsetCurve.Create(curvesToOffset, offsetDistance)

### 保温层内侧顶部和垂直壁曲线合并
curveOneSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[52], 0.429013917472933)
curveTwoSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[53], 0.426155243450697)
result = SketchCorner.Create(curveOneSelPoint, curveTwoSelPoint)
# EndBlock

## 保温层外侧
pos1 = [Hbases - angle_insulation[0], Lbase2 + Lbase51]
pos2 = [pos1[0], pos1[1] + angle_insulation[1]]
pos3 = [pos2[0] + angle_insulation[0] * 1.5, pos2[1]]
pos4 = [pos3[0] + 258, Rwall + thick_walls[0] + sum(thick_insulations)]
pos5 = [10e3, pos4[1]]
point1 = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
point2 = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
point3 = Point2D.Create(MM(pos3[0]), MM(pos3[1]))
point4 = Point2D.Create(MM(pos4[0]), MM(pos4[1]))
point5 = Point2D.Create(MM(pos5[0]), MM(pos5[1]))
SketchLine.Create(point1, point2)
SketchLine.Create(point2, point3)
SketchLine.Create(point3, point4)
SketchLine.Create(point4, point5)

### 保温层顶部外侧等距
curvesToOffset = Selection.Create(GetRootPart().DatumPlanes[0].Curves[53])
offsetDistance = MM(-thick_insulations[1])
result = SketchOffsetCurve.Create(curvesToOffset, offsetDistance)
#### 保温层顶部和垂直壁曲线合并
curveOneSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[57], 0.428498607800516)
curveTwoSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[58], 7.03109010182316)
result = SketchCorner.Create(curveOneSelPoint, curveTwoSelPoint)
# EndBlock



# 草图闭合
## 基本长度
pos1 = [Hbases + thick_bottom2 + sum(Hwalls) + htop + thick_walls[-1] + sum(thick_insulations), 0]
pos2 = [origin_basexy[0], origin_basexy[1]]
point1 = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
point2 = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
SketchLine.Create(point1, point2)
## 草图误差，导致高度不准，需要额外处理
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[59], 0.0018314071838148)
TrimSketchCurve.Execute(curveSelPoint)


# 熔盐-空气交界面
salt_inventory = geo_param["inventory"]
pos1 = [origin_basexy[0]+ Hbases+thick_bottom2+salt_inventory,origin_basexy[1]]
pos2 = [pos1[0],pos1[1]+Rwall]
point1 = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
point2 = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
SketchLine.Create(point1, point2)

Rwelds = [5, 10]  # 下方焊缝半径、上方焊缝半径
# 外土壤、空气域
Hsoil = 2*Hbases
Hambient = 10*(sum(Hwalls)+htop)
Rsoil = 5*Rwall
pos1 = [Hbases - Hsoil, 0]
pos2 = [Hbases - angle_insulation[0], 0]
pos3 = [pos2[0], Rsoil]
pos4 = [pos2[0] + Hambient, 0]
point1 = Point2D.Create(MM(pos1[0]), MM(pos1[1]))
point2 = Point2D.Create(MM(pos2[0]), MM(pos2[1]))
point3 = Point2D.Create(MM(pos3[0]), MM(pos3[1]))
point4 = Point2D.Create(MM(pos4[0]), MM(pos4[1]))
result = SketchRectangle.Create(point1, point2, point3)
result = SketchRectangle.Create(point2, point3,point4)
# 裁剪多余线段
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[62], 9.84000330353842)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[65], 41.0048739091005)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[62], 10.105356408383)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[65], 40.737382408439)
result = TrimSketchCurve.Execute(curveSelPoint)
# EndBlock


# 草图绘制结束
mode = InteractionMode.Solid
result = ViewHelper.SetViewMode(mode, None)
# EndBlock

"""生成几何"""
# 生成三维实体
for face in GetRootPart().Bodies[0].Faces:
    selection = FaceSelection.Create(face)
    options = ExtrudeFaceOptions()
    options.ExtrudeType = ExtrudeType.ForceIndependent
    result = ExtrudeFaces.Execute(selection, MM(1), options)

Rwelds = [5, 10]  # 下方焊缝半径、上方焊缝半径

# 下方大角焊缝圆角
selection = EdgeSelection.Create(GetRootPart().Bodies[3].Edges[53],GetRootPart().Bodies[3].Edges[1],
GetRootPart().Bodies[4].Edges[44], GetRootPart().Bodies[2].Edges[1])
options = ConstantRoundOptions()
result = ConstantRound.Execute(selection, MM(Rwelds[0]), options, None)
# EndBlock

# 上方大角焊缝圆角
selection = EdgeSelection.Create(GetRootPart().Bodies[3].Edges[49], GetRootPart().Bodies[3].Edges[4],
GetRootPart().Bodies[2].Edges[4],  GetRootPart().Bodies[4].Edges[41])
options = ConstantRoundOptions()
result = ConstantRound.Execute(selection, MM(Rwelds[1]), options, None)
# EndBlock


# 生成二维实体
options = MidsurfaceOptions()
options.Group = False
options.OffsetType = MidSurfaceOffsetType.Bottom
command = Midsurface(options)
for body in GetRootPart().Bodies:
    selection = BodySelection.Create(body)
    command.AddFacePairsByRange(selection, MM(0), MM(2))
result = command.Execute()



# 几何命名
body_nums = len(GetRootPart().Bodies) / 2
for i in range(body_nums):
    selection = BodySelection.Create(GetRootPart().Bodies[i + body_nums])
    result = RenameObject.Execute(selection, body_names[i])
selection_lists = [[],[],[]] # 选择列表，顺序为ambient, insulation&base, inventory



# 共享拓扑
def component2share(index2share):
    inSelectedView = False
    faceLevel = False
    # 再隐藏非共享 component、显示待共享 component
    for i,component in enumerate(GetRootPart().Components):
        inSelectedView = VisibilityType.Show if i == index2share else VisibilityType.Hide
        for body in component.Content.Bodies:
            selection = BodySelection.Create(body)
            ViewHelper.SetObjectVisibility(selection, inSelectedView, inSelectedView, faceLevel)
    # Share Topology
    options = ShareTopologyOptions()
    options.Tolerance = MM(0.2)
    result = ShareTopology.FindAndFix(options)
## 生成component
for body in GetRootPart().Bodies:
    body_name = body.GetName()
    if body_name == "Solid":
        body.Delete()
        pass
    elif "ambient" in body_name:
        selection_lists[0].append(body)
    elif "insulation" in body_name or "base" in body_name:
        selection_lists[1].append(body)
    elif "inventory" in body_name:
        selection_lists[2].append(body)

for selection_list in selection_lists:
    selection = BodySelection.Create(selection_list)
    ComponentHelper.MoveBodiesToComponent(selection, None)
## 隐藏罐体
inSelectedView = False
faceLevel = False
selection = BodySelection.Create( GetRootPart().Bodies)
ViewHelper.SetObjectVisibility(selection, VisibilityType.Hide, inSelectedView, faceLevel)
## 隐藏/显示其他 component，然后共享拓扑
for i in range(len(GetRootPart().Components)):
    component2share(i)

# 保存
options = ExportOptions.Create()
DocumentSave.Execute(geo_file_path, options)