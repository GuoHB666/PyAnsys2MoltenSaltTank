"""import geo for Fluent"""
geo_file = r"D:\GuoHB\MyFiles\Code\PyAnsysWorkbench\software\geometry\geo_fluid.scdoc"
geo=system_fluent.GetContainer("Geometry")
geo.SetFile(FilePath=geo_file)