# encoding: utf-8
# 基于名称选中对应面
def GetLocByName(ns_name):
    for ns in Model.NamedSelections.Children:
        if ns.Name == ns_name: return ns


# 指定材料
matAss = Model.Materials.AddMaterialAssignment()
matAss.Material = "Steel"
matAss.Location = GetLocByName("ns_beamBody")
# 划分网格
mesh = Model.Mesh
mesh.ElementSize = Quantity("10 [mm]")
mesh.GenerateMesh()
# 获得Analyses对象
analysis = Model.Analyses[0]
# 添加固定约束
fixSup = analysis.AddFixedSupport()
fixSup.Location = GetLocByName("ns_fixSup")
# 加载压力载荷
pressLoad = analysis.AddPressure()
pressLoad.Location = GetLocByName("ns_press")
pressLoad.Magnitude.Output.DiscreteValues = [Quantity("0.5 [MPa]")]
# 求解
Model.Solve()
# 后处理操作
solution = analysis.Solution
misesResult = solution.AddEquivalentStress()
misesResult.EvaluateAllResults()