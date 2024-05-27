import matplotlib
matplotlib.use('Qt5Agg')  # 或者使用 'Qt5Agg'
import sys
from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QHeaderView, QMessageBox,QTableWidgetItem,QComboBox,QCheckBox,QFileDialog,QVBoxLayout
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap,QFont
import xml.etree.ElementTree as ET
from PyWbUnit import CoWbUnitProcess
from PyQt5.QtCore import QObject, QThread
from pathlib import Path
from PyQt5.QtGui import QIntValidator
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QSizePolicy
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
from scipy import interpolate

def script_generation(script_info, template_name, key_replacement):
    keyword = list(key_replacement.keys())[0]
    replacement = list(key_replacement.values())[0]
    template_content = script_info[template_name]['content']
    template_content_lines = template_content.split('\n')
    for i, line in enumerate(template_content_lines):
        if keyword in line:
            # 替换整行内容
            template_content_lines[i] = replacement
    new_content = '\n'.join(template_content_lines)
    script_info[template_name]['content'] = new_content # 更新script_info
    new_path = script_info[template_name]['path']
    with open(new_path, 'w', encoding='utf-8') as new_file:
        new_file.write(new_content)
    return script_info

class PyAnsysUI(QObject):
    def __init__(self):
        super().__init__()
        # 定义用到的全局变量
        self.ui = uic.loadUi(r".\ui\py_ansys_ui2.0.ui")
        self.mat_lib_xml = r".\data\constant\my_mats2.0.xml"
        self.scripts_folder = Path(r".\software\scripts")
        self.result_folder = Path(r".\data\result")
        self.script_content = self.get_script_info()
        # ansys求解的对象
        self.ansys_simulation = CoWbUnitProcess()
        # 图形化显示涉及到的类
        self.tree_logic = TreeLogic(self.ui)
        self.geo_logic = GeoLogic(self.ui, self.script_content)
        self.mat_logic = MatLogic(self.ui, self.mat_lib_xml, self.script_content)
        self.simulation_logic = SimulationLogic(self.ui,self.ansys_simulation)
        self.visualizer_logic = ResultVisualizer(self.ui,self.result_folder)
        # UI初始化
        self.retranslate_ui()
    def retranslate_ui(self):
        # 设置整个UI文件中所有控件的字体为12号
        self.set_font_size_recursive(self.ui, 10,'Times New Roman')
        sub_logics = [self.mat_logic,self.simulation_logic, self.geo_logic, self.visualizer_logic]
        # 循环调用各个图形化类单独的UI初始化程序
        for sub_logic in sub_logics:
            sub_logic.retranslate_ui()
    def get_script_info(self):
        script_templates_folder = self.scripts_folder / "templates" # 脚本模板
        script_run_folder = self.scripts_folder / "test" #
        files_content = {}
        files_in_folder = [file for file in script_templates_folder.iterdir() if file.is_file()]
        for file_path in files_in_folder:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
                file_script = script_run_folder / file_path.name
                file_script = str(file_script.absolute())
                files_content[file_path.name] = {'path':file_script,'content':file_content}
        return files_content
    def set_font_size_recursive(self, widget, font_size,font_family):
        # 如果是QWidget，设置其字体
        if isinstance(widget, QWidget):
            font = QFont(font_family, font_size)
            font.setPointSize(font_size)
            widget.setFont(font)
        # 递归设置其子控件的字体
        for child_widget in widget.findChildren(QWidget):
            self.set_font_size_recursive(child_widget, font_size, font_family)
class TreeLogic(QObject):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.tree_names = []
        self.get_tree_nodenames()
        # 事件连接
        self.signal_connect_slot()
    def signal_connect_slot(self):
        # 信号与槽连接
        self.ui.tree.clicked.connect(self.tree_on_clicked)
    def tree_on_clicked(self):
        # 树形节点点击逻辑
        tree_name = self.ui.tree.currentItem()  # 获取当前点击的树形节点名称
        page_num = self.tree_names.index(tree_name.text(0))
        self.ui.pages.setCurrentIndex(page_num)
    def get_tree_nodenames(self):
        root = self.ui.tree.invisibleRootItem()
        for index in range(root.childCount()):
            self.tree_names.append(root.child(index).text(0))
class GeoLogic(QObject):
    def __init__(self, ui,script_info):
        super().__init__()
        self.ui = ui
        self.geo_paths = {
            "HM":{
                    "geo_path": r"D:\hm",
                    "geo_name_pic": r".\ui\resources\images\hm_name.jpg",
                    "geo_pic": r".\ui\resources\images\hm_geo.jpg"
                },
            "DLH":{
                    "geo_path": r"D:\dlh",
                    "geo_name_pic": r".\ui\resources\images\dlh_name.jpg",
                    "geo_pic": r".\ui\resources\images\dlh_geo.jpg"
                },
            "Custom": {"geo_path": "", "geo_name_pic": "", "geo_pic": ""},
            "Default": {"geo_path": "", "geo_name_pic": "", "geo_pic": ""}
        }
        self.geo_paths["Default"] = self.geo_paths["HM"]
        self.target_geo = self.geo_paths["Default"]
        self.script_info = script_info
        # 事件连接
        self.signal_connect_slot()
    def retranslate_ui(self):
        # 调用函数设置 label_name_pic 的属性
        self.set_label_properties(self.ui.label_name_pic, self.geo_paths["Default"]["geo_name_pic"])
        # 调用函数设置 label_geo_pic 的属性
        self.set_label_properties(self.ui.label_geo_pic, self.geo_paths["Default"]["geo_pic"])
    def signal_connect_slot(self):
        # 信号与槽连接
        self.ui.button_geo_scripts.clicked.connect(self.geo_script_generation)
        self.ui.choice_geo.currentIndexChanged.connect(self.geo_choice)
    def geo_choice(self,index):
        self.target_geo = list(self.geo_paths.values())[index] # 以序号形式查找字典
        if index == 2:
            options = QFileDialog.Options(); options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getOpenFileName(self.ui, "Select File", "",
                          "Text Files (*.txt)", options=options)
            if fileName:
                self.target_geo["geo_path"] = fileName
            else:
                self.target_geo = self.geo_paths["Default"]
        # 调用函数设置 label_name_pic 的属性
        self.set_label_properties(self.ui.label_name_pic, self.target_geo["geo_name_pic"])
        # 调用函数设置 label_geo_pic 的属性
        self.set_label_properties(self.ui.label_geo_pic, self.target_geo["geo_pic"])
    def geo_script_generation(self):
        template_name = 'geo_import.py'
        template_key = 'geo_file = '
        replacement = f'geo_file = r\'{self.target_geo["geo_path"]}\''
        key_replacement = {template_key:replacement}
        self.script_info = script_generation(self.script_info, template_name,key_replacement)

        msg_info = True
        info_alert("geo", msg_info)
    @staticmethod
    def set_label_properties(label, pixmap_path):
        pixmap = QPixmap(pixmap_path)
        label.setPixmap(pixmap)
        label.setScaledContents(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setAlignment(Qt.AlignCenter)
class MatLogic(QObject):
    def __init__(self, ui,mat_lib_xml,script_info):
        super().__init__()
        self.ui = ui
        self.mat_lib_xml = mat_lib_xml
        self.mat_lib_dict = {}
        self.mats_get()
        self.script_info = script_info
        # 事件连接
        self.signal_connect_slot()
    def signal_connect_slot(self):
        # 信号与槽连接
        self.ui.table_mat_solid.itemSelectionChanged.connect(lambda: self.mat_item_selected(self.ui.table_mat_solid))
        self.ui.button_mat_appoint_default.clicked.connect(lambda: self.mat_appoint("default"))
        self.ui.button_mat_appoint.clicked.connect(lambda: self.mat_appoint("custom"))
        self.ui.button_mat_del.clicked.connect(self.mat_del)
        self.ui.button_mat_scripts.clicked.connect(self.mat_script_generation)
    def retranslate_ui(self):
        # 设置QTableWidget的列宽为均匀分布，并显示水平标题
        tables = [self.ui.table_mat_fluid, self.ui.table_temp_fluid, self.ui.table_mat_solid, self.ui.table_temp_solid]
        for table in tables:
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.horizontalHeader().setVisible(True)
        # 将材料的xml数据打印到材料表格里
        self.mats_show()
        # 材料库打印到list中
        all_mat_names = list(self.mat_lib_dict.keys()); self.ui.mat_all_list.addItems(all_mat_names)
    def mats_get(self):
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
    def mats_show(self):
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
    def mat_item_selected(self, selected_tab):
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
    def mat_appoint(self,choice="default"):
        try:
            if choice == "default":
                self.ui.mat_appoint_list.clear()
                all_mat_names = list(self.mat_lib_dict.keys())
                for i in range(self.ui.part_choice.count()):
                    part = self.ui.part_choice.itemText(i)
                    default_mat = all_mat_names[0] # 还没确定默认分配方案，先都分配为第1个材料
                    mat_appointed = '%s → %s'%(default_mat,part)
                    self.ui.mat_appoint_list.addItem(mat_appointed) # 将材料分配方案输出到UI界面上

            else:
                part = self.ui.part_choice.currentText()
                mat_selected = self.ui.mat_all_list.selectedItems()
                mat_selected = mat_selected[0].text()
                mat_appointed = '%s → %s'%(mat_selected,part)
                # 将字符串列表合并为一个字符串，然后检查特定字符是否在这个字符串中
                mat_alr_appoint_list = [self.ui.mat_appoint_list.item(i).text()
                                   for i in range(self.ui.mat_appoint_list.count())]
                if part not in ''.join(mat_alr_appoint_list):
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
    def mat_script_generation(self):
        current_parts = []; current_mats = []
        # 遍历 QListWidget 中的每个条目
        for i in range(self.ui.mat_appoint_list.count()):
            appoint_str = self.ui.mat_appoint_list.item(i).text()
            # 使用 split() 方法来分割条目内容
            split_text = appoint_str.split(" → ")
            # 将分割后的内容分别添加到对应的列表中
            current_mats.append(split_text[0]); current_parts.append(split_text[1])
        all_parts = [self.ui.part_choice.itemText(i) for i in range(self.ui.part_choice.count())]
        if len(current_mats) is not len(all_parts):
            msg_info = False
        else:
            msg_info = True
            template_name = 'calcu_content.py'
            key_replacements = {
                'bodys = ': f'bodys = {current_parts}',
                'mats = ': f'mats = {current_mats}'
            }
            for key, replacement in key_replacements.items():
                key_replacement = {key:replacement}
                self.script_info = script_generation(self.script_info,template_name,key_replacement)
        info_alert("mat",msg_info)
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
class SimulationLogic(QObject):
    def __init__(self, ui,ansys_simulation):
        super().__init__()
        self.ui = ui
        self.ansys_simulation = ansys_simulation
        self.thread = QThread() # 定义的子线程
        self.tab_boundary_rows = [i for i in range(self.ui.table_boundary_conditions.rowCount())]
        self.tab_boundary_checkrows = self.tab_boundary_rows
        self.heat_rows = self.get_heat_rows()
        # self.simulate_events = ["开始创建连接。。。", "创建仿真系统中。。。",
        #                         "仿真系统创建完成，开展几何建模中。。。","几何建模完成，导入模型中。。。",
        #                         "模型导入完成，创建材料参数中。。。","材料创建成功，启动模拟计算中。。。",
        #                         "开始计算。。。", "计算完成！断开连接、保存并退出Ansys"]
        self.simulate_events = ["开始创建连接。。。", "创建仿真系统中。。。",
                                "仿真系统创建完成，开展几何建模中。。。","几何建模完成，导入模型中。。。",
                                "模型导入完成，划分网格中。。。","网格划分成功，启动Fluent中。。。",
                                "开始计算。。。", "计算完成！断开连接、保存并退出Ansys"]
        # 事件连接
        self.signal_connect_slot()
    def get_heat_rows(self):
        heat_rows = []
        for row in self.tab_boundary_rows:
            row_header = self.ui.table_boundary_conditions.verticalHeaderItem(row).text()
            if "进口" in row_header or "出口" in row_header:
                heat_rows.append(row)
        return heat_rows
    def retranslate_ui(self):
        self.ui.progressBar_simulate.setValue(0) # 初始化进度条进度为0
        self.ui.brow_simulate.clear()
        self.ui.brow_simulate.setFontFamily("Arial")  # 设置字体类型
        """边界条件中的表格相关样式"""
        # 固定表格宽度、显示标题行
        header_targets = [self.ui.table_boundary_conditions.horizontalHeader(),
                      self.ui.table_boundary_conditions.verticalHeader()]
        for header_target in header_targets:
            header_target.setSectionResizeMode(QHeaderView.Fixed)
            header_target.setSectionsClickable(False)
            header_target.setSectionsMovable(False)
            header_target.setVisible(True)
        # 初始化表格内容: 添加选项框、复选框
        self.ui.table_boundary_conditions.setColumnWidth(0, 10)  # 将第一列的宽度设置为 150 像素
        for row_index in self.tab_boundary_rows:
            com_box = QComboBox(); com_box.addItem('常序列')
            check_box = QCheckBox(); check_box.setChecked(True)
            if row_index > 0: com_box.addItem('时间序列')
            if row_index in self.heat_rows: check_box.setEnabled(False)
            self.ui.table_boundary_conditions.setCellWidget(row_index,0,check_box)
            self.ui.table_boundary_conditions.setCellWidget(row_index,1,com_box)
        """修改文字的颜色"""
        self.ui.label_simulate_notes.setStyleSheet("color: gray")  # 设置样式表以将颜色更改为灰
        """保证模拟时间输入框只能输入正数"""
        validator = QIntValidator() # 创建一个整数验证器
        validator.setRange(1, 999999) # 设置验证器的范围
        self.ui.simulate_time_input.setValidator(validator) # 设置验证器到 QLineEdit 中
    def signal_connect_slot(self):
        self.ui.button_simulate_run.released.connect(self.simulate_with_ansys)
        self.ui.choice_working_condition.currentTextChanged.connect(self.tab_boundary_changed)
        # 根据输入选项，生成相应的计算脚本
        self.ui.button_simulate_scripts.released.connect(self.simulate_script_generation)
        # 通过连接 progressChanged 信号到 handle_progress_changed 槽函数，使得主线程能够监听、处理子线程的进度信息
        self.ansys_simulation.progressChanged.connect(self.handle_progress_changed)
    def simulate_script_generation(self):
        msg_info = True
        allcheckbox_unchecked = True
        """检查各输入值是否合法"""
        # 边界条件表格
        for row in self.tab_boundary_checkrows:
            checkBoxItem = self.ui.table_boundary_conditions.cellWidget(row, 0)
            if checkBoxItem.isChecked():
                allcheckbox_unchecked = False
                item_choice = self.ui.table_boundary_conditions.cellWidget(row, 1)
                item_value = self.ui.table_boundary_conditions.item(row, 2)
                try:
                    choice = item_choice.currentText(); value = item_value.text()
                    if choice == "时间序列":
                        if Path(value).is_file():
                            print("文件有效")
                        else: raise ValueError
                    else:
                        value = float(value)
                except:
                    msg_info = False
                    break
        # 模拟时间
        if allcheckbox_unchecked or \
                (self.ui.simulate_time_input.isEnabled() \
                 and self.ui.simulate_time_input.text() == ""):
            msg_info = False
        info_alert("simulation",msg_info)
    def tab_boundary_changed(self):
        operate_condition = self.ui.choice_working_condition.currentText()
        for row in self.heat_rows:
            if operate_condition == "充放热工况":
                self.ui.table_boundary_conditions.showRow(row)
                self.tab_boundary_checkrows = self.tab_boundary_rows
                self.ui.simulate_time_input.setDisabled(False)
            else:
                self.ui.table_boundary_conditions.hideRow(row)
                self.tab_boundary_checkrows = list(set(self.tab_boundary_rows) - set(self.heat_rows))
                self.ui.simulate_time_input.setDisabled(True)
    def simulate_with_ansys(self):
        # 创建子线程
        self.ansys_simulation.moveToThread(self.thread)
        # 运行ansys的模拟计算函数
       # self.thread.started.connect(self.ansys_simulation.simula_system_run)
        self.thread.started.connect(self.ansys_simulation.simulation_run)
        self.thread.start()
    def buttons_status(self, button_statue=False):
        buttons = [self.ui.button_simulate_run,
            self.ui.button_mat_scripts,self.ui.button_geo_scripts, self.ui.button_simulate_scripts]
        for script_button in buttons:
            script_button.setEnabled(button_statue)
    # 主线程中处理信号的槽函数
    def handle_progress_changed(self, progress_count):
        try:
            if progress_count == 0:
                self.ui.brow_simulate.append("=" * 50)
                self.buttons_status(False)
            progress = ((progress_count + 1) / len(self.simulate_events)) * 100
            event = self.simulate_events[progress_count]
            self.ui.brow_simulate.append(event)  # 更新显示框
            self.ui.progressBar_simulate.setValue(int(progress)) # 更新进度条
            if progress_count == len(self.simulate_events)-1:
                self.thread.quit()  # 通知线程停止
                self.thread.wait()
                self.thread.started.disconnect()  # 断开连接，保证之后重新计算时started.connect不会多次连接到simula_system_run函数中
                self.ui.brow_simulate.append("=" * 50)
                self.buttons_status(True)
        except Exception as e:
            print("An exception occurred:", e)


def info_alert(status_type, status):
    status_dict = {
        "geo":{
            True: ["成功", "几何模型确定成功!"],
            False: ["失败", "几何模型确定失败"]
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

class ResultVisualizer(QObject):
    def __init__(self, ui,result_folder):
        super().__init__()
        self.ui = ui
        self.result_folder = result_folder
        """绘图的控件准备"""
        # 创建 Matplotlib 图表
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        # 创建布局以放置 Matplotlib 图表
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        # 设置 groupBox 的布局
        self.ui.groupbox_contour.setLayout(self.layout)

        """事件连接"""
        self.signal_connect_slot()
    def retranslate_ui(self):
        pass

    def signal_connect_slot(self):
        # 信号与槽连接
        self.ui.button_show_contour.clicked.connect(self.contour_visualization)
    def contour_visualization(self):
        try:
            self.figure.clear()
            """获取数据"""
            data_path = self.result_folder / "fluent_T_2D.txt"
            # 读取数据
            data = pd.read_csv(data_path,sep="\s+")
            # 提取坐标和速度数据
            y = data.iloc[:, 2]
            z = data.iloc[:, 3]
            result = data.iloc[:, 4] - 273.15
            coords = [z, y]
            input_labels = ["x1[m]", "x2[m]"]
            out_label = "T[°C]"
            """绘图"""
            ax = self.figure.add_subplot()
            self.plot_contour2D(ax,coords, result, input_labels, out_label)
            self.canvas.draw()
        except:
            info_alert("visulation", False)
    def plot_contour2D(self,ax, coords, result, input_labels, out_labels):
        """
        简单2D云图使用自己编写的程序即可实现，复杂云图得用其他工具包
        :param ax:
        :param coords:
        :param result:
        :param input_labels:
        :param out_labels:
        :return:
        """
        print(1)
        levels_contour = np.linspace(min(result), max(result), 20)
        levels_cbar = np.linspace(round(min(result),2),round(max(result),2), 5)
        x1_meshnode = np.linspace(min(coords[0]), max(coords[0]), 1000)
        x2_meshnode = np.linspace(min(coords[1]), max(coords[1]), 1000)
        # 生成二维数据坐标点
        x1_interpolate, x2_interpolate = np.meshgrid(x1_meshnode, x2_meshnode)
        # 通过griddata函数插值得到所有的(X1, Y1)处对应的值
        result_interpolate = interpolate.griddata(tuple(coords), result, (x1_interpolate, x2_interpolate),
                                                  method='cubic')
        # fig, ax = plt.subplots(figsize=(12, 8))
        # ax.axis('off')
        # level设置云图颜色范围以及颜色梯度划分。其中，设置cmap为jet，即最小值为蓝色，最大为红色，和有限元软件云图配色类似
        result_contour = ax.contourf(x1_interpolate, x2_interpolate, result_interpolate, levels_contour, cmap=cm.jet)
        ax.set_xlabel(input_labels[0], size=15)
        ax.set_ylabel(input_labels[1], size=15)
        ax.set_aspect('equal')
        # 为结果云图添加colorbar
        cbar = plt.colorbar(result_contour,orientation='horizontal')
        cbar.set_label(out_labels, size=18)
        cbar.set_ticks(levels_cbar)

if __name__ == "__main__":
    try:
        App = QApplication(sys.argv)
        py_ansys_ui = PyAnsysUI()
        py_ansys_ui.ui.show()
        #py_ansys_ui.ui.showFullScreen()
        sys.exit(App.exec())
    except Exception as e:
        print("An exception occurred:", e)