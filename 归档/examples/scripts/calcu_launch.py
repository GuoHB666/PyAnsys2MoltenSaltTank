# encoding: utf-8
# 刷新Model Component数据
modelComp = mechSys.GetComponent(Name="Model")
modelComp.Refresh()
# 获得Mechanical中Model的数据容器
model = mechSys.GetContainer(ComponentName="Model")
model.Edit(Hidden=True)
#model.Edit()