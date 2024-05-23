# Python Script, API Version = V18
# 定义函数：通过坐标点选择面对象
def GetFaceObjByPt(pt):
    for face in GetRootPart().GetDescendants[IDesignFace]():
        if face.Shape.ContainsPoint(pt): return face
# 创建悬臂梁实体区域
BlockBody.Create(Point.Origin, Point.Create(MM(200), MM(25), MM(20)))
GetRootPart().SetName("Beam")
# 选择beam实体，用于后续材料赋予
Selection.Create(GetRootPart().Bodies).CreateAGroup("ns_beamBody")
# 定义固定约束加载面并为其命名
fixSupFace = GetFaceObjByPt(Point.Create(0, MM(12.5), MM(10)))
Selection.Create(fixSupFace).CreateAGroup("ns_fixSup")
# 定义压力载荷加载面并为其命名
pressFace = GetFaceObjByPt(Point.Create(MM(50), MM(12.5), MM(20)))
Selection.Create(pressFace).CreateAGroup("ns_press")
# 保存文件
options = ExportOptions.Create()
DocumentSave.Execute(r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\geometry\geo.scdoc", options)