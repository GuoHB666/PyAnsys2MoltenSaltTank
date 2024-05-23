# -*- coding: utf-8 -*-
template_mat = GetTemplate(TemplateName="EngData")
template_statoc_thermal = GetTemplate(
    TemplateName="Steady-State Thermal",
    Solver="ANSYS")
template_static_structural = GetTemplate(
    TemplateName="Static Structural",
    Solver="ANSYS")
system_mat = template_mat.CreateSystem()
system_thermal = template_statoc_thermal.CreateSystem(
    ComponentsToShare=[system_mat.GetComponent(Name="Engineering Data")],
    Position="Right",
    RelativeTo=system_mat)
system_structural = template_static_structural.CreateSystem(
    ComponentsToShare=[system_thermal.GetComponent(Name="Engineering Data")],
    Position="Right",
    RelativeTo=system_thermal)

solutionComponent_thermal = system_thermal.GetComponent(Name="Solution")
solutionComponent_thermal.TransferData(TargetComponent= system_structural.GetComponent(Name="Setup"))

