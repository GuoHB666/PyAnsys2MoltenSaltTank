from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QObject
from pathlib import Path
from TreeLogic import TreeLogic # 导入同一文件夹下的TreeLogic

class PyAnsysUI(QObject):
    def __init__(self, path_prj=Path(__file__).parent.parent):
        super().__init__()
        # 定义用到的全局变量
        self.ui = uic.loadUi(path_prj / "ui" / "py_ansys_ui2.0.ui")
        self.mat_lib_xml = path_prj.parent / "constant" / "my_mats2.0.xml"
        self.scripts_folder = path_prj.parent / "software" / "scripts"
        self.result_folder = path_prj.parent / "result"
        # ansys求解的对象

        # 图形化显示涉及到的类
        self.tree_logic = TreeLogic(self.ui)
        # UI初始化
        self.retranslate_ui()
    def retranslate_ui(self):
        # 设置整个UI文件中所有控件的字体为 8 号
        self.set_font_size_recursive(self.ui, 10,'Times New Roman')
    def set_font_size_recursive(self, widget, font_size,font_family):
        # 如果是QWidget，设置其字体
        if isinstance(widget, QWidget):
            font = QFont(font_family, font_size)
            font.setPointSize(font_size)
            widget.setFont(font)
        # 递归设置其子控件的字体
        for child_widget in widget.findChildren(QWidget):
            self.set_font_size_recursive(child_widget, font_size, font_family)