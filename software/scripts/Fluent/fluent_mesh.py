
# encoding: utf-8
body = DataModel.GetObjectsByName("fluid")[0]
mesh = Model.Mesh
mesh.ElementSize = Quantity("4 [mm]")
method = mesh.AddAutomaticMethod()
method.Location = body # body must be firstly gived, and then multizone method
method.Method = MethodType.MultiZone
mesh.GenerateMesh()

# note: the first line and the end line must be empty line so that command be executable

