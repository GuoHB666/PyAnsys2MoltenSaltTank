

# Python Script, API Version = V20
# Set New Sketch
result = SketchHelper.StartConstraintSketching()
# EndBlock

# Sketch Circle
plane = Plane.PlaneXY
result = ViewHelper.SetSketchPlane(plane)
origin = Point2D.Create(MM(0), MM(0))
result = SketchCircle.Create(origin, MM(25))

baseSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].Curves[0].GetChildren[ICurvePoint]()[0])
targetSel = SelectionPoint.Create(GetRootPart().DatumPlanes[0].GetChildren[IDatumPoint]()[0])

result = Constraint.CreateCoincident(baseSel, targetSel)
# EndBlock

mode = InteractionMode.Solid
result = ViewHelper.SetViewMode(mode, None)
# EndBlock

# Extrude 1 Face
selection = FaceSelection.Create(GetRootPart().Bodies[0].Faces[0])
options = ExtrudeFaceOptions()
options.ExtrudeType = ExtrudeType.Add
result = ExtrudeFaces.Execute(selection, MM(200), options)
# EndBlock

# Create Named Selection Group
primarySelection = FaceSelection.Create(GetRootPart().Bodies[0].Faces[1])
secondarySelection = Selection.Empty()
result = NamedSelection.Create(primarySelection, secondarySelection)
# EndBlock

# Rename Named Selection
result = NamedSelection.Rename("Group1", "inlet")
# EndBlock

# Create Named Selection Group
primarySelection = FaceSelection.Create(GetRootPart().Bodies[0].Faces[2])
secondarySelection = Selection.Empty()
result = NamedSelection.Create(primarySelection, secondarySelection)
# EndBlock

# Rename Named Selection
result = NamedSelection.Rename("Group1", "outlet")
# EndBlock

# Create Named Selection Group
primarySelection = FaceSelection.Create(GetRootPart().Bodies[0].Faces[0])
secondarySelection = Selection.Empty()
result = NamedSelection.Create(primarySelection, secondarySelection)
# EndBlock

# Rename Named Selection
result = NamedSelection.Rename("Group1", "wall")
# EndBlock

# Create Named Selection Group
primarySelection = BodySelection.Create(GetRootPart().Bodies[0])
secondarySelection = Selection.Empty()
result = NamedSelection.Create(primarySelection, secondarySelection)
# EndBlock

# Rename Named Selection
result = NamedSelection.Rename("Group1", "fluid")
# EndBlock



# Save
options = ExportOptions.Create()
geo_file = r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\geometry\geo_fluid.scdoc"
DocumentSave.Execute(geo_file, options)
# EndBlock