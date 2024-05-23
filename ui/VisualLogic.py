from PyQt5.QtCore import QObject
from pathlib import Path
import os
class VisualLogic(QObject):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui

        # 事件连接
        self.signal_connect_slot()
    def retranslate_ui(self):
        pass

    def signal_connect_slot(self):
        # 信号与槽连接
        self.ui.button_show_result.clicked.connect(self.result2show)
    def result2show(self):
        result_choice = self.ui.comboBox_result.currentText()
        result_dir = Path(__file__).parent.parent / "result"
        # 获取文件夹中所有文件的路径
        file_paths = result_dir.glob("*")
        # 提取文件名
        file_names = [file.name for file in file_paths if file.is_file()]
        # 提取特定结果
        filtered_files = [file for file in file_names if result_choice in file]
        # 找到日期最新的文件名
        if filtered_files:
            newest_file = max(filtered_files)
            file_path =  result_dir / newest_file
            # 在系统中打开文件
            os.startfile(file_path.absolute())
