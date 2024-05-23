import sys
from PyQt5 import QtCore, QtGui, QtWidgets,uic
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QHeaderView

from PyQt5.QtWidgets import QTableWidgetItem
import xml.etree.ElementTree as ET





class PyAnsysUI:
    def __init__(self):
        # 从文件中加载UI定义
        self.ui = uic.loadUi("py_ansys_ui.ui")
        # 变量初始化
        self.mat_lib_dict = {}
        self.mat_lib_xml = "..\data\constant\my_mats2.0.xml"
        self.tree_names = []
        self._get_tree_nodenames()
        # UI二次美化与赋值
        self._retranslateUi()
        # 事件连接
        self.signal_connect_slot()
    def signal_connect_slot(self):
        """信号与槽"""
        # 1. 左侧树形选项卡 的点击事件
        self.ui.tree.clicked.connect(self.tree_on_clicked)
        # 2. 【物性参数】界面的事件
        # self.ui.button_default_mat.clicked.connect(self.mat_default)
        # self.ui.buttom_add_mat.clicked.connect(lambda: self.add_table_row(tab="mat"))
        # self.ui.buttom_add_mat_temp.clicked.connect(lambda: self.add_table_row(tab="temp"))
        self.ui.table_mat_solid.itemSelectionChanged.connect(lambda: self.on_item_selected(self.ui.table_mat_solid))
    def _retranslateUi(self):
        # 1. 材料界面
        # (1) 设置QTableWidget的列宽为均匀分布，并显示水平标题
        self.ui.table_mat_fluid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.table_mat_fluid.horizontalHeader().setVisible(True)
        self.ui.table_temp_fluid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.table_temp_fluid.horizontalHeader().setVisible(True)
        self.ui.table_mat_solid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.table_mat_solid.horizontalHeader().setVisible(True)
        self.ui.table_temp_solid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.table_temp_solid.horizontalHeader().setVisible(True)
        # (2) 读取材料的xml数据，并打印到表格里
        self.get_mat_lib()
        self.mat_lib_show()
    def _get_rawtree_names(self, item):
        # 迭代获得左侧树形选项卡各节点名称
        self.tree_names.append(item.text(0))
        for i in range(item.childCount()):
            child_item = item.child(i)
            self._get_rawtree_names(child_item)
    def _get_tree_nodenames(self):
        self._get_rawtree_names(self.ui.tree.invisibleRootItem())
        index_to_remove = [0,1,6,11] # 定义需要删除的，有子节点的父节点名称索引
        index_to_remove.sort(reverse=True)  # 将索引按照倒序排列，使得从后往前删除，避免索引错位
        for index in index_to_remove:
            self.tree_names.pop(index)
        # print(self.tree_names)
    def tree_on_clicked(self):
        try:
            tree_name = self.ui.tree.currentItem()  # 获取当前点击的树形节点名称
            page_num = self.tree_names.index(tree_name.text(0))
            self.ui.pages.setCurrentIndex(page_num)
        except:
            pass
    def add_table_row(self,tab):
        tables = {
            "mat": [self.ui.table_mat_fluid, self.ui.table_mat_solid],
            "temp": [self.ui.table_temp_fluid, self.ui.table_temp_solid]
        }
        current_index = self.ui.tab_mat.currentIndex()
        target_table = tables[tab][current_index]
        target_table.setRowCount(target_table.rowCount() + 1)
    def get_mat_lib(self):
        # 解析xml文件
        tree = ET.parse(self.mat_lib_xml)
        root = tree.getroot()
        # 获取单位并做相应设置
        unit_elem = root.find("Unit")
        # 遍历材料元素
        for mat_elem in root.findall("Material"):
            mat_name = mat_elem.get("name")
            mat_type = mat_elem.find("mat_type").text
            self.mat_lib_dict.setdefault(mat_name, []).append(mat_type)
            # 材料遍历赋值
            for property_elem in mat_elem.findall("property"):
                mat_property = self.get_mat_prop(property_elem)
                self.mat_lib_dict.setdefault(mat_name, []).append(mat_property)
    def mat_lib_show(self):
        mat_title = ["name", "Density", "Thermal Conductivity", "Specific Heat", "Coefficient of Thermal Expansion",
                     "Young's Modulus", "Poisson's Ratio"]
        for mat_name, mat_props in self.mat_lib_dict.items():
            mat_type = mat_props[0]
            if mat_type == "Solid":
                rowPosition = self.ui.table_mat_solid.rowCount()
                self.ui.table_mat_solid.insertRow(rowPosition)
                # 赋值
                self.ui.table_mat_solid.setItem(rowPosition, 0, QTableWidgetItem(mat_name))  # 第n行、0列的参数
                for mat_prop in mat_props[1:]:
                    if mat_prop[1][0] == 'Temperature':
                        mat_prop_index = mat_title.index(mat_prop[1][1])
                        mat_prop_value = "Tabular"
                        self.ui.table_mat_solid.setItem(rowPosition, mat_prop_index,
                                                        QTableWidgetItem(mat_prop_value))  # 第i行、j列的参数
                        if mat_prop[1][1] == "Young's Modulus":
                            self.ui.table_mat_solid.setItem(rowPosition, mat_prop_index+1,
                                                            QTableWidgetItem(mat_prop_value))  # 第i行、j列的参数
                    elif mat_prop[1][0] == "Young's Modulus":
                        mat_prop_index = mat_title.index(mat_prop[1][0])
                        mat_prop_value = mat_prop[2]
                        self.ui.table_mat_solid.setItem(rowPosition, mat_prop_index,
                                                        QTableWidgetItem(str(mat_prop_value[0])))  # 第i行、j列的参数
                        self.ui.table_mat_solid.setItem(rowPosition, mat_prop_index+1,
                                                        QTableWidgetItem(str(mat_prop_value[1])))  # 第i行、j列的参数
                    else:
                        mat_prop_index = mat_title.index(mat_prop[1][0])
                        mat_prop_value = mat_prop[2]
                        self.ui.table_mat_solid.setItem(rowPosition, mat_prop_index,
                                                        QTableWidgetItem(str(mat_prop_value)))  # 第i行、j列的参数
            else:
                    pass
    def on_item_selected(self,selected_tab):
        self.ui.table_temp_solid.setRowCount(0)  # 先清空温度-参数表格
        selected_items = selected_tab.selectedItems()
        try:
            item = selected_items[0]
            if item.text() == "Tabular":
                row = item.row()
                column = item.column()
                mat_names = list(self.mat_lib_dict.keys())
                temps = self.mat_lib_dict[mat_names[row]][column-1][2][0] if column == 6 \
                    else self.mat_lib_dict[mat_names[row]][column][2][0]
                values = self.mat_lib_dict[mat_names[row]][column-1][2][2] if column == 6 \
                    else self.mat_lib_dict[mat_names[row]][column][2][1]
                for i in range(len(temps)):
                    temp = QTableWidgetItem(str(temps[i]))
                    value = QTableWidgetItem(str(values[i]))
                    self.ui.table_temp_solid.insertRow(i)
                    self.ui.table_temp_solid.setItem(i, 0, temp)  # 第i行、j列的参数
                    self.ui.table_temp_solid.setItem(i,1, value)  # 第i行、j列的参数
        except:
            pass
    def mat_default(self):
        self.ui.table_mat_solid.setRowCount(0)
        self.ui.table_temp_solid.setRowCount(0)
        self.ui.table_mat_fluid.setRowCount(0)
        self.ui.table_temp_fluid.setRowCount(0)
        self.mat_lib_show()
    @staticmethod
    def get_mat_prop(property_elem):
        property_type = property_elem.get("type")
        temperatures_elem = property_elem.find("T")
        tr_elem = property_elem.find("Tr")
        value_elem = property_elem.find("Value")
        tr_value = None
        # 先检查是否是弹性模量参数，再决定获取值的方法
        if property_type == "Elasticity":
            elastic_modulus_elem = value_elem.find("ElasticModulus")  # 提取弹性模量
            poisson_ratio_elem = value_elem.find("PoissonRatio")  # 提取泊松比
            elastic_modulus = elastic_modulus_elem.text
            poisson_ratio = poisson_ratio_elem.text
            if temperatures_elem is not None:
                temperatures = list(map(float, temperatures_elem.text.split(',')))
                elastic_modulus = elastic_modulus.split(',')
                poisson_ratio = poisson_ratio.split(',')
                # 转化为数字列表
                elastic_modulus = list(map(float, elastic_modulus))
                poisson_ratio = list(map(float, poisson_ratio))
                property_data = [temperatures, elastic_modulus, poisson_ratio]
            else:
                elastic_modulus = float(elastic_modulus)
                poisson_ratio = float(poisson_ratio)
                property_data = [elastic_modulus, poisson_ratio]
        else:
            values = value_elem.text
            if tr_elem is not None:
                tr_value = tr_elem.text
            if temperatures_elem is not None:
                temperatures = list(map(float, temperatures_elem.text.split(',')))
                values = list(map(float, values.split(',')))
                property_data = [temperatures, values]
            else:
                property_data = float(values)
        temperature_variables = [] if temperatures_elem is None else ["Temperature"]
        property_variables = ["Young's Modulus", "Poisson's Ratio"] if property_type == "Elasticity" else [
            property_type]
        mat_variables = temperature_variables + property_variables
        # 基于单位，对数据进行处理，而后科学计数法显示
        property_data_scientific = format_data(property_data)
        return tr_value, mat_variables, property_data_scientific


# 通过科学计数法表示数据
def format_data(data):
    if isinstance(data, list):
        if isinstance(data[0], list):
            return [[f'{x:.2e}' for x in sublist] for sublist in data]
        else:
            return [f'{x:.2e}' for x in data]
    else:
        return f'{data:.2e}'









if __name__ == "__main__":
    App = QApplication(sys.argv)    # 创建QApplication对象，作为GUI主程序入口
    py_ansys_ui = PyAnsysUI()
    py_ansys_ui.ui.show()               # 显示主窗体
    sys.exit(App.exec())   # 循环中等待退出程序

