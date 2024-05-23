# -*- coding: utf-8 -*-
# # 纯案例源码
# mechSys = GetTemplate(TemplateName="Static Structural", Solver="ANSYS").CreateSystem()
# systems=GetAllSystems()

# 以下代码先创建一个【Engineering Data】，再创建一个【Static Structural】。之后，再把这两个系统连接起来
system_mat = GetTemplate(TemplateName="EngData").CreateSystem()
system_structural = GetTemplate(TemplateName="Static Structural",Solver="ANSYS").CreateSystem(
    ComponentsToShare=[system_mat.GetComponent(Name="Engineering Data")],
    Position="Right",RelativeTo=system_mat)
