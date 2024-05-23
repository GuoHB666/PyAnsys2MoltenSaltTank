
# Python Script, API Version = V20
## 注：采用的是Index模式
#ClearAll()
"""几何名称"""
body_names = [
    "ambient_air", "inventory_air", "inventory_salt",
    "tank", "insulation_inner", "insulation_outer",
    "base_gravel", "base_concrete", "base_concrete", "base_concrete",
    "base_ceramsite","ambient_soil",
    "base_firebrick", "base_fine"]

"""几何尺寸定义, mm"""
# 土壤域和外空气域
Hsoil = 4e3
Hambient = 165e3
Rsoil = 66e3
# 地基
Hbases = [400, 1400, 300]  # 细砾石、陶粒、砾石
pos_concrete = [1100, 200, 3800]  # 陶粒混凝土支撑层位置，包括高度、单个支撑层宽度、各支撑层间隙
pos_firebrick = [250, 750]  # 耐火砖位置，包括垂直高度、水平宽度
Rbases = [11000, 13200]  # 地基最上方、最下方

# 储罐
## 整体尺寸
Rtanks = [24400, 20350 / 2, 20610 / 2]  # 罐顶内壁半径、罐壁内半径、罐底内半径
Ltankbottom = [Rtanks[2] - 2000, 2000]  # 罐底中心板长度、边缘板长度
thick_bottoms = [22, 10, 163]  # 罐底边缘板、中心板、总高度
thick_tank_walls = [30, 22, 20, 16, 14, 10]  # 罐壁厚度
Htankwalls = [2000, 2000, 2000, 2000, 2000, 2210 + 2200]  # 罐壁高度
Htop = 2221.3
## 局部罐底大角焊缝
Hwelds = [(thick_tank_walls[i] - thick_tank_walls[i + 1]) * 4 for i in range(len(Htankwalls) - 1)]  # 焊缝尺寸
Hwelds.insert(0, 18.68)  # 罐底大角焊缝外侧高度
Hwelds.append(18.68)  # 罐底大角焊缝内侧高度
width_weld_bottom = [8, 8]  # 罐底大角焊缝
Rwelds = [5, 10]  # 下方焊缝半径、上方焊缝半径
pos_weld = [400, 300]  # 焊缝切割尺寸，高度400mm，长度300
# 保温层
thick_insulations = [250, 220]  # 内侧、外侧
angle_insulation = [150,300]

# 熔盐液位，单位mm
salt_level = 12.9e3

# 土壤域及空气域
Hsoil = 4e3
Hair = 165e3
Rsoil = 66e3

""""草图绘制"""
# Set New Sketch
result = SketchHelper.StartConstraintSketching()
plane = Plane.PlaneXY
result = ViewHelper.SetSketchPlane(plane)
# EndBlock

# fine_gravel

point1 = Point2D.Create(MM(0), MM(0))
point2 = Point2D.Create(MM(Hbases[0]), MM(0))
point3 = Point2D.Create(MM(Hbases[0]), MM(Rbases[1]))
result = SketchRectangle.Create(point1, point2, point3)

# EndBlock

# ceramsite
point1 = Point2D.Create(MM(Hbases[0]), MM(0))
point2 = Point2D.Create(MM(sum(Hbases[0:2])), MM(0))
point3 = Point2D.Create(MM(sum(Hbases[0:2])), MM(Rbases[0]))
result = SketchRectangle.Create(point1, point2, point3)
# EndBlock
# ceramsite concrete
point1 = Point2D.Create(MM(Hbases[0]), MM(0))
point2 = Point2D.Create(MM(Hbases[0]), MM(pos_concrete[1] / 2))
point3 = Point2D.Create(MM(Hbases[0] + pos_concrete[0]), MM(0))
result = SketchRectangle.Create(point1, point2, point3)

point1 = Point2D.Create(MM(Hbases[0]), MM(pos_concrete[2] - pos_concrete[1] / 2))
point2 = Point2D.Create(MM(Hbases[0]), MM(pos_concrete[2] + pos_concrete[1] / 2))
point3 = Point2D.Create(MM(Hbases[0] + pos_concrete[0]), MM(pos_concrete[2] - pos_concrete[1] / 2))
result = SketchRectangle.Create(point1, point2, point3)

point1 = Point2D.Create(MM(Hbases[0]), MM(pos_concrete[2] * 2 - pos_concrete[1] / 2))
point2 = Point2D.Create(MM(Hbases[0]), MM(pos_concrete[2] * 2 + pos_concrete[1] / 2))
point3 = Point2D.Create(MM(Hbases[0] + pos_concrete[0]), MM(pos_concrete[2] * 2 - pos_concrete[1] / 2))
result = SketchRectangle.Create(point1, point2, point3)

# firebrick
point1 = Point2D.Create(MM(Hbases[0]), MM(Rbases[0] + pos_firebrick[0]))
point2 = Point2D.Create(MM(sum(Hbases)), MM(Rbases[0] + pos_firebrick[0]))
point3 = Point2D.Create(MM(sum(Hbases)), MM(Rbases[0] - pos_firebrick[1]))
point4 = Point2D.Create(MM(sum(Hbases[0:2])), MM(Rbases[0] - pos_firebrick[1]))
result = SketchLine.Create(point1, point2)
result = SketchLine.Create(point2, point3)
result = SketchLine.Create(point3, point4)
# EndBlock

# gravel：无需绘制
# EndBlock


# tank bottom: 从罐底边缘板外侧点，开始逆时针
point1x = sum(Hbases) + thick_bottoms[0]
point2x = point1x
point3x = point1x - thick_bottoms[0]
point4x = point3x
point5x = point4x + thick_bottoms[2]
point6x = point5x + thick_bottoms[1]
point7x = point4x + thick_bottoms[1]
point8x = point4x + thick_bottoms[0]
point9x = point8x

point1y = Rtanks[1] + thick_tank_walls[0] + width_weld_bottom[0]
point2y = Rtanks[2]
point3y = point2y
point4y = point3y - Ltankbottom[1]
point5y = 0
point6y = 0
point7y = point4y
point8y = point4y + 4 * (thick_bottoms[0] - thick_bottoms[1])
point9y = Rtanks[1] - width_weld_bottom[0]
point1 = Point2D.Create(MM(point1x), MM(point1y))
point2 = Point2D.Create(MM(point2x), MM(point2y))
point3 = Point2D.Create(MM(point3x), MM(point3y))
point4 = Point2D.Create(MM(point4x), MM(point4y))
point5 = Point2D.Create(MM(point5x), MM(point5y))
point6 = Point2D.Create(MM(point6x), MM(point6y))
point7 = Point2D.Create(MM(point7x), MM(point7y))
point8 = Point2D.Create(MM(point8x), MM(point8y))
point9 = Point2D.Create(MM(point9x), MM(point9y))

result = SketchLine.Create(point1, point2)
result = SketchLine.Create(point2, point3)
result = SketchLine.Create(point3, point4)
result = SketchLine.Create(point4, point5)
result = SketchLine.Create(point5, point6)
result = SketchLine.Create(point6, point7)
result = SketchLine.Create(point7, point8)
result = SketchLine.Create(point8, point9)

# tank wall
## 外侧
for i in range(len(Htankwalls)):
    if i == 0:
        point1x = sum(Hbases) + thick_bottoms[0]
        point1y = Rtanks[1] + thick_tank_walls[i] + width_weld_bottom[0]
    else:
        point1x = point3x
        point1y = point3y
    point2x = point1x + Hwelds[i]
    point3x = point1x + Htankwalls[i]
    point2y = Rtanks[1] + thick_tank_walls[i]
    point3y = point2y
    point1 = Point2D.Create(MM(point1x), MM(point1y))
    point2 = Point2D.Create(MM(point2x), MM(point2y))
    point3 = Point2D.Create(MM(point3x), MM(point3y))
    result = SketchLine.Create(point1, point2)
    result = SketchLine.Create(point2, point3)

## 内侧
# point1x = point3x # 最顶部
point2x = point3x  # 最顶部
point3x = point3x - sum(Htankwalls) + Hwelds[-1]
point4x = point3x - Hwelds[-1]
# point1y = point3y
point2y = point3y - thick_tank_walls[i]
point3y = point2y
point4y = point3y - width_weld_bottom[-1]

point1 = Point2D.Create(MM(point1x), MM(point1y))
point2 = Point2D.Create(MM(point2x), MM(point2y))
point3 = Point2D.Create(MM(point3x), MM(point3y))
point4 = Point2D.Create(MM(point4x), MM(point4y))

# result = SketchLine.Create(point1, point2)
result = SketchLine.Create(point2, point3)
result = SketchLine.Create(point3, point4)

## 罐顶曲线
### 罐顶内侧曲线生成
orign_top = [sum(Hbases) + thick_bottoms[0] + sum(Htankwalls) - (Rtanks[0] - Htop), 0]
point1 = [orign_top[0] + (Rtanks[0] - Htop), Rtanks[1]]
point2 = [point1[0] + Htop, 0]
origin = Point2D.Create(MM(orign_top[0]), MM(orign_top[1]))
start = Point2D.Create(MM(point1[0]), MM(point1[1]))
end = Point2D.Create(MM(point2[0]), MM(point2[1]))
senseClockWise = True
result = SketchArc.CreateSweepArc(origin, start, end, senseClockWise)

### 罐顶曲线等距
curvesToOffset = Selection.Create(GetRootPart().DatumPlanes[0].Curves[45])
offsetDistance = MM(-10)
result = SketchOffsetCurve.Create(curvesToOffset, offsetDistance)
### 罐顶曲线和罐内壁合并
curveOneSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[42], 4.39106300856658)
curveTwoSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[46], 0.429924368684054)
result = SketchCorner.Create(curveOneSelPoint, curveTwoSelPoint)
# EndBlock

# 保温层
## 内侧
### 保温层内层的垂直壁曲线
point1 = [sum(Hbases), Rtanks[1] + thick_tank_walls[0] + thick_insulations[0]]
point2 = [point1[0] + 10e3, point1[1]]
start = Point2D.Create(MM(point1[0]), MM(point1[1]))
end = Point2D.Create(MM(point2[0]), MM(point2[1]))
result = SketchLine.Create(start, end)

### 保温层内层顶部等距
curvesToOffset = Selection.Create(GetRootPart().DatumPlanes[0].Curves[46])
offsetDistance = MM(-thick_insulations[0])
result = SketchOffsetCurve.Create(curvesToOffset, offsetDistance)

### 保温层内侧顶部和垂直壁曲线合并
curveOneSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[46], 0.429013917472933)
curveTwoSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[48], 0.426155243450697)
result = SketchCorner.Create(curveOneSelPoint, curveTwoSelPoint)
# EndBlock

# Trim Sketch Corner
curveOneSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[48], 0.426170923042813)
curveTwoSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[47], 14.6829573676078)
result = SketchCorner.Create(curveOneSelPoint, curveTwoSelPoint)

## 外侧
### 保温层下方绘制
position1 = [sum(Hbases) - angle_insulation[0], Rbases[0] + pos_firebrick[0]]
position2 = [position1[0], position1[1] + angle_insulation[1]]
position3 = [position2[0] + angle_insulation[0]*1.5, position2[1]]
position4 = [position3[0] + 258, Rtanks[1] + thick_tank_walls[0] + sum(thick_insulations)]
position5 = [10e3, position4[1]]

point1 = Point2D.Create(MM(position1[0]), MM(position1[1]))
point2 = Point2D.Create(MM(position2[0]), MM(position2[1]))
point3 = Point2D.Create(MM(position3[0]), MM(position3[1]))
point4 = Point2D.Create(MM(position4[0]), MM(position4[1]))
point5 = Point2D.Create(MM(position5[0]), MM(position5[1]))
result = SketchLine.Create(point1, point2)
result = SketchLine.Create(point2, point3)
result = SketchLine.Create(point3, point4)
result = SketchLine.Create(point4, point5)
### 保温层顶部外侧等距
curvesToOffset = Selection.Create(GetRootPart().DatumPlanes[0].Curves[48])
offsetDistance = MM(-thick_insulations[1])
result = SketchOffsetCurve.Create(curvesToOffset, offsetDistance)

#### 保温层顶部和垂直壁曲线合并
curveOneSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[53], 0.428498607800516)
curveTwoSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[52], 7.03109010182316)
result = SketchCorner.Create(curveOneSelPoint, curveTwoSelPoint)
# EndBlock


# 草图闭合
## 基本长度
position1 = [sum(Hbases) + thick_bottoms[0] + sum(Htankwalls) + Htop + 10 + sum(thick_insulations), 0]
position2 = [0, 0]
point1 = Point2D.Create(MM(position1[0]), MM(position1[1]))
point2 = Point2D.Create(MM(position2[0]), MM(position2[1]))
result = SketchLine.Create(point1, point2)
## 草图误差，导致高度不准，需要额外延伸
curveOneSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[54], 0.000330894000995841)
curveTwoSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[53], 1.44599554779633E-05)
result = SketchCorner.Create(curveOneSelPoint, curveTwoSelPoint)

# Sketch Circle


## 罐壁曲线固定约束，为圆角裁剪做准备
curveSelList = Selection.Create(GetRootPart().DatumPlanes[0].Curves[32])
result = Constraint.CreateFixed(curveSelList)
curveSelList = Selection.Create(GetRootPart().DatumPlanes[0].Curves[31])
result = Constraint.CreateFixed(curveSelList)
curveSelList = Selection.Create(GetRootPart().DatumPlanes[0].Curves[23])
result = Constraint.CreateFixed(curveSelList)
curveSelList = Selection.Create(GetRootPart().DatumPlanes[0].Curves[43])
result = Constraint.CreateFixed(curveSelList)
curveSelList = Selection.Create(GetRootPart().DatumPlanes[0].Curves[44])
result = Constraint.CreateFixed(curveSelList)
curveSelList = Selection.Create(GetRootPart().DatumPlanes[0].Curves[30])
result = Constraint.CreateFixed(curveSelList)
# EndBlock

## 绘制圆形
origin = Point2D.Create(MM(2157), MM(10162))
result = SketchCircle.Create(origin, MM(Rwelds[1]))
origin = Point2D.Create(MM(2163), MM(10225))
result = SketchCircle.Create(origin, MM(Rwelds[1]))
origin = Point2D.Create(MM(2133), MM(10226))
result = SketchCircle.Create(origin, MM(Rwelds[0]))
origin = Point2D.Create(MM(2137), MM(10161))
result = SketchCircle.Create(origin, MM(Rwelds[0]))
# EndBlock

## 圆角相切约束
baseSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[58], 3.40339204138895)
targetSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[30], 1.80597838617826)
result = Constraint.CreateTangent(baseSel, targetSel)
baseSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[44], 0.0173419068856678)
targetSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[58], 1.89804556154383)
result = Constraint.CreateTangent(baseSel, targetSel)
baseSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[55], 2.87979326579065)
targetSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[44], 0.00502580600621701)
result = Constraint.CreateTangent(baseSel, targetSel)
baseSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[55], 3.46884188833877)
targetSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[43], 14.3631520750884)
result = Constraint.CreateTangent(baseSel, targetSel)
baseSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[57], 3.59974158223846)
targetSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[31], 0.00296329653713286)
result = Constraint.CreateTangent(baseSel, targetSel)
baseSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[57], 2.68344372494112)
targetSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[23], 0.0051692984110101)
result = Constraint.CreateTangent(baseSel, targetSel)
baseSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[56], 3.665191429188)
targetSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[32], 0.00637162040703432)
result = Constraint.CreateTangent(baseSel, targetSel)
baseSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[56], 3.40339204138893)
targetSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[31], 0.0147775625648342)
result = Constraint.CreateTangent(baseSel, targetSel)
# EndBlock

## 圆角裁剪
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[56], 5.21943504658567)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[32], 0.000537892733511125)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[31], 0.019949425164334)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[57], 6.08342940491739)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[23], 0.00101614235199321)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[31], 0.00069596059088651)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[55], 0.403061447381787)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[43], 14.3910362292908)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[44], 0.000415137267529012)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[58], 0.550196086187907)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[44], 0.0194549642324459)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[30], 1.81310119074342)
result = TrimSketchCurve.Execute(curveSelPoint)
# EndBlock

# 空气-熔盐界面直线绘制
position1 = [sum(Hbases) + thick_bottoms[0] + salt_level, 0]
position2 = [position1[0], Rtanks[1]]
point1 = Point2D.Create(MM(position1[0]), MM(position1[1]))
point2 = Point2D.Create(MM(position2[0]), MM(position2[1]))
result = SketchLine.Create(point1, point2)


# 外土壤域和空气域
## 草图绘制、裁剪
### 绘图
position1 = [sum(Hbases) - Hsoil, 0]
position2 = [sum(Hbases) - angle_insulation[0],0]
position3 = [position2[0], Rsoil]
position4 = [position2[0]+Hair,0]
point1 = Point2D.Create(MM(position1[0]), MM(position1[1]))
point2 = Point2D.Create(MM(position2[0]), MM(position2[1]))
point3 = Point2D.Create(MM(position3[0]), MM(position3[1]))
point4 = Point2D.Create(MM(position4[0]), MM(position4[1]))
result = SketchRectangle.Create(point1, point2, point3)
result = SketchRectangle.Create(point2, point3,point4)
### 裁剪多余线段
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[61], 10.8870655682575)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[63], 55.3452416791563)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[66], 9.33539961687785)
result = TrimSketchCurve.Execute(curveSelPoint)
curveSelPoint = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[68], 56.145595119974)
result = TrimSketchCurve.Execute(curveSelPoint)

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



# 共享拓扑
## 先创建 component
### 外空气域和土壤域
selection = BodySelection.Create([GetRootPart().Bodies[25],
	GetRootPart().Bodies[14]])
result = ComponentHelper.MoveBodiesToComponent(selection, None)
### 保温层和地基
selection = BodySelection.Create([GetRootPart().Bodies[17],
	GetRootPart().Bodies[18],
	GetRootPart().Bodies[20],
	GetRootPart().Bodies[19],
	GetRootPart().Bodies[21],
	GetRootPart().Bodies[22],
	GetRootPart().Bodies[23],
	GetRootPart().Bodies[24],
	GetRootPart().Bodies[25]])
result = ComponentHelper.MoveBodiesToComponent(selection, None)
### 内空气域和熔盐域
selection = BodySelection.Create([GetRootPart().Bodies[14], GetRootPart().Bodies[15]])
result = ComponentHelper.MoveBodiesToComponent(selection, None)


## 共享拓扑
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

inSelectedView = False
faceLevel = False
# 隐藏罐体
selection = BodySelection.Create(GetRootPart().Bodies[14])
ViewHelper.SetObjectVisibility(selection, VisibilityType.Hide, inSelectedView, faceLevel)
for i in range(len(GetRootPart().Components)):
    # 隐藏/显示其他 component，然后共享拓扑
    component2share(i)
