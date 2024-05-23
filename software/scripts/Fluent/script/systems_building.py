
# -*- coding: utf-8 -*-
"""Simulation system created"""
system_geo = GetTemplate(TemplateName="Geometry").CreateSystem()
geometryComponent1 = system_geo.GetComponent(Name="Geometry")
system_fluent = GetTemplate(TemplateName="Fluid Flow").CreateSystem(
    ComponentsToShare=[geometryComponent1],
    Position="Right",
    RelativeTo=system_geo)

