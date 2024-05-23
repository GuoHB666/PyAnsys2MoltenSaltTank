# encoding: utf-8
### 材料赋值区
bodys = None
mats = None
for i, body_name in enumerate(bodys):
    body = DataModel.GetObjectsByName(body_name)[0]
    body.Material = mats[i]