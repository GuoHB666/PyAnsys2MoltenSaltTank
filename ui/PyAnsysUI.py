from PyQt5 import uic
from PyQt5.QtWidgets import QWidget,QTabWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QObject
from pathlib import Path
from .TreeLogic import TreeLogic # 导入同一包文件夹下的TreeLogic
from .GeoLogic import GeoLogic
from .MatLogic import MatLogic
from .SimulationLogic import SimulationLogic
from .VisualLogic import VisualLogic
from PyWbUnit import CoWbUnitProcess
class PyAnsysUI(QObject):
    def __init__(self, path_prj=Path(__file__).parent.parent):
        super().__init__()
        # 定义用到的全局变量
        self.ui = uic.loadUi(path_prj / "ui" / "py_ansys_ui3.0.ui")
        self.scripts_folder = path_prj / "software" / "scripts"
        self.result_folder = path_prj / "result"
        self.constant_folder = path_prj / "constant"
        self.mat_files = [self.constant_folder / "mat_FEM_solid.xml", self.constant_folder / "mat_FEM_fluid.xml", self.constant_folder / "mat_CFD.scm"]
        self.template_script = {
            "geo_content": self.scripts_folder / "templates" / "geo_content.py",
            "fluent_content": self.scripts_folder / "templates" / "fluent_content.jou",
            "mechanical_content": self.scripts_folder / "templates" / "mechanical_content.py"
        }
        # 清空脚本文件
        self.script_cleans(self.scripts_folder)
        # ansys求解的对象
        self.ansys_simulation = CoWbUnitProcess()
        # 图形化显示涉及到的类
        self.tree_logic = TreeLogic(self.ui)
        self.geo_logic = GeoLogic(self.ui, self.template_script)
        self.mat_logic = MatLogic(self.ui, self.mat_files, self.template_script)
        self.simulation_logic = SimulationLogic(self.ui,self.ansys_simulation, self.template_script)
        self.visual_logic = VisualLogic(self.ui)
        # UI初始化
        self.retranslate_ui()
    def retranslate_ui(self):
        # 最大化窗口
       # self.ui.showMaximized()
        # 设置整个UI文件中所有控件的字体为 8 号
        self.set_font(self.ui, 10, 'Times New Roman')
        # 循环调用各个图形化类单独的UI初始化程序
        sub_logics = [self.tree_logic, self.geo_logic, self.mat_logic, self.simulation_logic]
        for sub_logic in sub_logics:
            sub_logic.retranslate_ui()
    def set_font(self, widget, font_size, font_family):
        # 如果是QWidget，设置其字体
        if isinstance(widget, QWidget):
            font = QFont(font_family, font_size)
            font.setPointSize(font_size)
            widget.setFont(font)
        # 递归设置其子控件的字体
        for child_widget in widget.findChildren(QWidget):
            self.set_font(child_widget, font_size, font_family)
    @staticmethod
    def script_cleans(folder):
        """
        清除脚本文件夹里生成的几何脚本
        :return:
        """
        if folder.is_dir():
            for item in folder.iterdir():
                if item.is_file():
                    item.unlink()  # 删除文件
                    print(f"{item.name}:delete")
                elif item.is_dir():
                    print(f"{item.name}:remain")