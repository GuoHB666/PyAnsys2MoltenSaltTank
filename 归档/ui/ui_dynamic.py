import sys
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QHeaderView, QTableWidgetItem
from PyQt5.QtWidgets import QTableWidgetItem,QFileDialog
import xml.etree.ElementTree as ET

class PyAnsysUI:
    def __init__(self):
        #super(PyAnsysUI, self).__init__() # 父类初始化。由于PyAnsysUI类没有父类，故这条代码没有用
        self.ui = uic.loadUi("py_ansys_ui.ui")
        self.mat_logic = MatLogic(self.ui)
        self.tree_logic = TreeLogic(self.ui)
        # UI初始化
        self.retranslate_ui()
        # 事件连接
        self.signal_connect_slot()
    def retranslate_ui(self):
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
        # (2) 将材料的xml数据打印到材料表格里
        self.mat_logic.mat_lib_show()
        # (3) 材料库打印到list中
        self.mat_logic.all_mat_show()
        # 2. 几何界面
    def signal_connect_slot(self):
        # 信号与槽连接
        self.ui.tree.clicked.connect(self.tree_logic.tree_on_clicked)
        self.ui.table_mat_solid.itemSelectionChanged.connect(lambda: self.mat_logic.on_item_selected(self.ui.table_mat_solid))
        self.ui.button_mat_appoint_default.clicked.connect(lambda: self.mat_logic.mat_appoint("default"))
        self.ui.button_mat_appoint.clicked.connect(lambda: self.mat_logic.mat_appoint("custom"))
        self.ui.button_mat_del.clicked.connect(self.mat_logic.mat_del)
    def ansys_script_generation(self):
        pass
    def simulate_with_ansys(self):
        pass
    def visualize_ansys_result(self):
        pass

class MatLogic:
    def __init__(self, ui):
        self.ui = ui
        self.mat_lib_xml = "..\data\constant\my_mats2.0.xml"
        self.mat_lib_dict = {}
        self.mat_lib_dict_get()
    def mat_lib_dict_get(self):
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
                mat_property = self.mat_get_prop(property_elem)
                self.mat_lib_dict.setdefault(mat_name, []).append(mat_property)
    def mat_lib_show(self):
        mat_title = ["name", "Density", "Thermal Conductivity", "Specific Heat", "Coefficient of Thermal Expansion",
                     "Young's Modulus", "Poisson's Ratio"]
        for mat_name, mat_props in self.mat_lib_dict.items():
            mat_type = mat_props[0]
            if mat_type == "Solid":
                # 固体材料
                rowPosition = self.ui.table_mat_solid.rowCount()
                self.ui.table_mat_solid.insertRow(rowPosition)
                # 赋值
                qt_value_name = QTableWidgetItem(mat_name)
                qt_value_name.setTextAlignment(QtCore.Qt.AlignCenter)
                self.ui.table_mat_solid.setItem(rowPosition, 0, qt_value_name)  # 第n行、0列的参数
                for mat_prop in mat_props[1:]:
                    if mat_prop[1][0] == 'Temperature':
                        mat_prop_index = mat_title.index(mat_prop[1][1])
                        qt_value1 = QTableWidgetItem("Tabular")
                        qt_value1.setTextAlignment(QtCore.Qt.AlignCenter)
                        qt_value2 = QTableWidgetItem("Tabular")
                        qt_value2.setTextAlignment(QtCore.Qt.AlignCenter)
                        self.ui.table_mat_solid.setItem(rowPosition, mat_prop_index, qt_value1)  # 第i行、j列的参数
                        if mat_prop[1][1] == "Young's Modulus":
                            self.ui.table_mat_solid.setItem(rowPosition, mat_prop_index+1, qt_value2)  # 第i行、j列的参数
                    elif mat_prop[1][0] == "Young's Modulus":
                        mat_prop_index = mat_title.index(mat_prop[1][0])
                        mat_prop_value = mat_prop[2]
                        qt_value1 = QTableWidgetItem(str(mat_prop_value[0]))
                        qt_value2 = QTableWidgetItem(str(mat_prop_value[1]))
                        qt_value1.setTextAlignment(QtCore.Qt.AlignCenter)
                        qt_value2.setTextAlignment(QtCore.Qt.AlignCenter)
                        self.ui.table_mat_solid.setItem(rowPosition, mat_prop_index,qt_value1)  # 第i行、j列的参数
                        self.ui.table_mat_solid.setItem(rowPosition, mat_prop_index+1,qt_value2)  # 第i行、j列的参数
                    else:
                        mat_prop_index = mat_title.index(mat_prop[1][0])
                        mat_prop_value = mat_prop[2]
                        qt_value = QTableWidgetItem(str(mat_prop_value))
                        qt_value.setTextAlignment(QtCore.Qt.AlignCenter)
                        self.ui.table_mat_solid.setItem(rowPosition, mat_prop_index, qt_value)  # 第i行、j列的参数
            else:
                # 流体材料
                    pass
    def on_item_selected(self,selected_tab):
        try:
            self.ui.table_temp_solid.setRowCount(0)  # 先清空温度-参数表格
            selected_items = selected_tab.selectedItems()
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
                    # 设置表格项的对齐方式为居中
                    temp.setTextAlignment(QtCore.Qt.AlignCenter)
                    value.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.ui.table_temp_solid.insertRow(i)
                    self.ui.table_temp_solid.setItem(i, 0, temp)  # 第i行、j列的参数
                    self.ui.table_temp_solid.setItem(i,1, value)  # 第i行、j列的参数
        except:
            pass
    def all_mat_show(self):
        all_mat_names = list(self.mat_lib_dict.keys())
        self.ui.mat_all_list.addItems(all_mat_names)
    def mat_appoint(self,choice="default"):
        try:
            if choice == "default":
                self.ui.mat_appoint_list.clear()
                all_mat_names = list(self.mat_lib_dict.keys())
                for i in range(self.ui.part_choice.count()):
                    part = self.ui.part_choice.itemText(i)
                    default_mat = all_mat_names[0] # 还没确定默认分配方案，先都分配为第1个材料
                    mat_appointed = '%s → %s'%(default_mat,part)
                    self.ui.mat_appoint_list.addItem(mat_appointed)
            else:
                current_part = self.ui.part_choice.currentText()
                mat_selected = self.ui.mat_all_list.selectedItems()
                mat_selected = mat_selected[0].text()
                mat_appointed = '%s → %s'%(mat_selected,current_part)
                mat_alr_appoint_list = [self.ui.mat_appoint_list.item(i).text()
                                   for i in range(self.ui.mat_appoint_list.count())]
                mat_alr_strs = ''.join(mat_alr_appoint_list) # 将字符串列表合并为一个字符串，然后检查特定字符是否在这个字符串中
                if current_part not in mat_alr_strs:
                    self.ui.mat_appoint_list.addItem(mat_appointed)

        except:
            pass
    def mat_del(self):
        selected_items = self.ui.mat_appoint_list.selectedItems()
        # 如果有选中的项目，移除它们
        try:
            item = selected_items[0]
            self.ui.mat_appoint_list.takeItem(self.ui.mat_appoint_list.row(item))
        except:
            pass
    def mat_get_prop(self,property_elem):
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
        property_data_scientific = self.format_data(property_data)
        return tr_value, mat_variables, property_data_scientific

    @staticmethod
    # 通过科学计数法表示数据
    def format_data(data):
        if isinstance(data, list):
            if isinstance(data[0], list):
                return [[f'{x:.2e}' for x in sublist] for sublist in data]
            else:
                return [f'{x:.2e}' for x in data]
        else:
            return f'{data:.2e}'

class TreeLogic:
    def __init__(self, ui):
        self.ui = ui
        self.tree_names = []
        self.get_tree_nodenames()
    def tree_on_clicked(self):
        # 树形节点点击逻辑
        try:
            tree_name = self.ui.tree.currentItem()  # 获取当前点击的树形节点名称
            page_num = self.tree_names.index(tree_name.text(0))
            self.ui.pages.setCurrentIndex(page_num)
        except:
            pass
    def get_tree_nodenames(self):
        # 获取树形节点名称逻辑
        self._get_rawtree_names(self.ui.tree.invisibleRootItem())
        index_to_remove = [0, 1, 6, 11]  # 定义需要删除的，有子节点的父节点名称索引
        index_to_remove.sort(reverse=True)  # 将索引按照倒序排列，使得从后往前删除，避免索引错位
        for index in index_to_remove:
            self.tree_names.pop(index)
        # print(self.tree_names)
    def _get_rawtree_names(self, item):
        # 获取原始树形节点名称逻辑
        self.tree_names.append(item.text(0))
        for i in range(item.childCount()):
            child_item = item.child(i)
            self._get_rawtree_names(child_item)




if __name__ == "__main__":
    try:
        App = QApplication(sys.argv)
        py_ansys_ui = PyAnsysUI()
        py_ansys_ui.ui.show()
        sys.exit(App.exec())
    except Exception as e:
        print("An exception occurred:", e)