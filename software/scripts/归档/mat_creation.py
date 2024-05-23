# -*- coding: utf-8 -*-
# 创建静结构分析流程
# 获得Engineering Data数据容器
engData = mechSys.GetContainer(ComponentName="Engineering Data")
# 封装创建材料的方法
def CreateMaterial(name, density, *elastic):
    mat = engData.CreateMaterial(Name=name)
    mat.CreateProperty(Name="Density").SetData(Variables=["Density"],
                                               Values=[["%s [kg m^-3]" % density]])
    elasticProp = mat.CreateProperty(Name="Elasticity", Behavior="Isotropic")
    elasticProp.SetData(Variables=["Young's Modulus"], Values=[["%s [MPa]" % elastic[0]]])
    elasticProp.SetData(Variables=["Poisson's Ratio"], Values=[["%s" % elastic[1]]])

# 创建材料Steel，密度：7850kg/m3，杨氏模量：208e3MPa，泊松比：0.3
CreateMaterial("Steel", 7850, 209.e3, 0.3)