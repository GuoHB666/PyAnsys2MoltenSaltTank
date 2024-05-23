# -*- coding: utf-8 -*-
folder_path = r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\examples\geometry"
file_path = "\geo.scdoc"
geo_file = folder_path + file_path
geo=mechSys.GetContainer("Geometry")
geo.SetFile(FilePath=geo_file)

