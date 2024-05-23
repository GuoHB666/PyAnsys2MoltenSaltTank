# encoding: utf-8
# 刷新Model Component数据
modelComp = system_structural.GetComponent(Name="Model")
modelComp.Refresh()
# 获得Mechanical中Model的数据容器
model = system_structural.GetContainer(ComponentName="Model")
model.Edit(Hidden=True)
#model.Edit()