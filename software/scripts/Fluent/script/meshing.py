
"""refresh Fluent system"""
meshComponent_fluent = system_fluent.GetComponent(Name="Mesh")
meshComponent_fluent.Refresh()

"""Fluent mesh generation"""
mesh_fluent = system_fluent.GetContainer(ComponentName="Mesh")
mesh_fluent.Edit(Interactive=False)
mesh_fluent_path = r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\scripts\fluent\fluent_mesh.py"
mesh_fluent_content = open(mesh_fluent_path, 'r').read()
mesh_fluent.SendCommand(Language="Python", Command=mesh_fluent_content)
mesh_fluent.Exit()
"""transfer mesh file to Fluent"""
meshComponent_fluent.Update(AllDependencies=True)


