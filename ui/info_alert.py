from PyQt5.QtWidgets import QMessageBox
def info_alert(status_type, status):
    status_dict = {
        "geo":{
            True: ["成功", "几何脚本生成成功!"],
            False: ["失败", "几何脚本生成失败"]
        },
        "mat": {
            True: ["成功","几何的材料属性给定完成!"],
            False: ["失败", "几何的材料属性给定出错!"]
        },
        "simulation": {
            True: ["成功", "物理过程描述正确!"],
            False: ["失败", "物理过程描述出错!"]
        },
        "visulation":{
            False:["失败","暂无云图数据"]
        }

    }
    msg = QMessageBox();
    msg_info = status_dict[status_type][status][1]
    msg_title = status_dict[status_type][status][0]
    # 根据设置情况，生成对话框
    icon = QMessageBox.Information if status else QMessageBox.Critical
    msg.setIcon(icon); msg.setText(msg_info); msg.setWindowTitle(msg_title)
    # 将OK按钮移到对话框中间
    ok_button = msg.addButton(QMessageBox.Ok); ok_button.setMinimumWidth(100)
    # 生成OK按钮
    msg.exec_()
