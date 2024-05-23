
"""launch calculation: parallel ran with 4 core"""
setupComponent_fluent = system_fluent.GetComponent(Name="Setup")
setupComponent_fluent.Refresh()
setup_fluent = system_fluent.GetContainer(ComponentName="Setup")
fluentLauncherSettings = setup_fluent.GetFluentLauncherSettings()
fluentLauncherSettings.SetEntityProperties(Properties=Set(EnvPath={}, RunParallel=True, NumberOfProcessorsMeshing=4, NumberOfProcessors=4))
setup_fluent.Edit(Interactive=False)
