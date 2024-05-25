from PyQt5 import QtCore, uic
from PyQt5.QtWidgets import QHeaderView,QTableWidgetItem
import xml.etree.ElementTree as ET
from PyQt5.QtCore import QObject
from .info_alert import info_alert
from .script_builder import script_builder
from pathlib import Path
class MatLogic(QObject):
    def __init__(self, ui, mat_files, script_template):
        super().__init__()
        self.ui = ui
        self.filemat_FEM = mat_files[0:-1]
        self.filemat_CFD = mat_files[-1]
        self.get_materials = [self.mat_xml_reader(filemat) for filemat in self.filemat_FEM]
        self.bodymats_default = {
            "ambient_soil": "dry_sand",
            "insulation1": "magnesium_silicate",
            "insulation2": "glass_wool" ,
            "base3": "gravel",
            "base2": "ceramsite_hm",
            "base4": "concrete_hm",
            "base1": "fine_gravel",
            "base5": "firebrick" ,
            "tank": "tp347h"}
        self.bodymats_custom = self.bodymats_default
        self.script_template = script_template
        # 事件连接
        self.signal_connect_slot()
    def signal_connect_slot(self):
        # 信号与槽连接
        self.ui.table_mat_solid.itemSelectionChanged.connect(lambda: self.mat_item_selected(self.ui.table_mat_solid, self.ui.table_temp_solid))
        self.ui.table_mat_fluid.itemSelectionChanged.connect(lambda: self.mat_item_selected(self.ui.table_mat_fluid, self.ui.table_temp_fluid))
        self.ui.button_mat_appoint_default.clicked.connect(lambda: self.mat_appoint("default"))
        self.ui.button_mat_appoint.clicked.connect(lambda: self.mat_appoint("custom"))
        self.ui.button_mat_del.clicked.connect(self.mat_del)
        self.ui.button_mat_submit.clicked.connect(self.mat_script_builder)
    def retranslate_ui(self):
        # 设置QTableWidget的列宽比例，并显示水平标题
        table_temps = [self.ui.table_mat_fluid, self.ui.table_temp_fluid, self.ui.table_mat_solid, self.ui.table_temp_solid]
        for table in table_temps:
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 等比宽度
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # 等比宽度
            table.horizontalHeader().setVisible(True)
        # 将材料的xml数据打印到材料表格里
        self.mats2show()
        # 材料库打印到list控件里中
        all_mat_names = []
        for materials in self.get_materials:
            all_mat_names = all_mat_names + list(materials.keys())
        self.ui.mat_all_list.addItems(all_mat_names)

        # 几何选择部件给定
        self.ui.part_choice.clear()
        self.ui.part_choice.addItems(list(self.bodymats_default.keys()))
    @staticmethod
    def mat_xml_reader(xml_file):
        """
        读取ansys workbench导出的材料参数。
        :param xml_file: XML文件路径
        :return: 排序后的材料参数字典
        """
        """解析xml文件"""
        tree = ET.parse(xml_file)
        root = tree.getroot()
        materials = {}
        ignore_properties = ["Color", "Options Variable", "Material Unique Id",
                             "Zero-Thermal-Strain Reference Temperature"]
        # 遍历所有材料
        for material in root.findall(".//Material"):
            mat_name = material.find(".//Name").text
            properties = {}
            for property_data in material.findall(".//PropertyData"):
                property_id = property_data.get('property')
                property_name = root.find(f".//PropertyDetails[@id='{property_id}']/Name").text
                # 如果是不需要的属性，则略过
                if property_name in ignore_properties:
                    continue
                parameter_values = {}
                for parameter_value in property_data.findall(".//ParameterValue"):
                    parameter_id = parameter_value.get('parameter')
                    parameter_name = root.find(f".//ParameterDetails[@id='{parameter_id}']/Name").text

                    # 对于 Elasticity 属性，只保留 Young's Modulus、Poisson's Ratio、Temperature 参数
                    if property_name == "Elasticity" and parameter_name not in ["Young's Modulus", "Poisson's Ratio", "Temperature"]:
                        continue
                    if parameter_name in ignore_properties:
                        continue
                    value = parameter_value.find(".//Data").text
                    unit_elements = root.findall(f".//ParameterDetails[@id='{parameter_id}']/Units/Unit")
                    units = ' '.join([f"{unit_element.find('.//Name').text}{'^' + unit_element.get('power') if unit_element.get('power') else ''}"
                                         for unit_element in unit_elements])
                    parameter_values[parameter_name] = (value, units)

                properties[property_name] = parameter_values

            materials[mat_name] = properties

        """对材料进行排序"""
        solid_property_order = ["Density", "Thermal Conductivity", "Specific Heat", "Coefficient of Thermal Expansion",
                                "Elasticity"]
        fluid_property_order = ["Density", "Thermal Conductivity", "Specific Heat", "Viscosity"]
        sorted_materials = {}
        for mat_name, properties in materials.items():
            sorted_properties = {}
            property_order = fluid_property_order if "Viscosity" in properties else solid_property_order
            for prop in property_order:
                if prop in properties:
                    sorted_properties[prop] = properties[prop]
            # 添加任何不在排序规则中的属性
            for prop in properties:
                if prop not in sorted_properties:
                    sorted_properties[prop] = properties[prop]
            sorted_materials[mat_name] = sorted_properties
        return sorted_materials
    def mats2show(self):
        mat_tables = [self.ui.table_mat_solid, self.ui.table_mat_fluid]
        for materials, mat_table in zip(self.get_materials, mat_tables):
            row = mat_table.rowCount()
            # 打印材料参数
            for mat_name, properties in materials.items():
                # 表格第1列，材料名
                qt_mat_name = QTableWidgetItem(mat_name)
                qt_mat_name.setTextAlignment(QtCore.Qt.AlignCenter)
                mat_table.insertRow(row) # 添加第 rowPosition 行
                mat_table.setItem(row, 0, qt_mat_name)  # 给定第rowPosition行、0列的参数
                for column, (property_name, property_details) in enumerate(properties.items()):
                    mat_temperature_unit = property_details["Temperature"][1]
                    mat_temperature_value_strs = property_details["Temperature"][0]
                    mat_temperature_value_lists = mat_temperature_value_strs.split(",")
                    property_names = list(property_details.keys())
                    if len(mat_temperature_value_lists) > 1:
                        # 若材料的温度数量大于2，说明该材料属性随温度而变化，表格显示的是Tabular
                        qt_mat_content = "Tabular"
                    elif len(property_names) > 2:
                        # 若材料属性的字典长度大于2，说明该材料属性是弹性模量，要同时显示杨氏模量和泊松比
                        value_str1 = property_details[property_names[0]][0]
                        value_str2 = property_details[property_names[1]][0]
                        qt_mat_content = f"{self.format_data_v2(value_str1)}, {self.format_data_v2(value_str2)}"
                    else:
                        value_str1 = property_details[property_names[0]][0]
                        qt_mat_content = self.format_data_v2(value_str1)
                    qt_mat_value = QTableWidgetItem(qt_mat_content)
                    qt_mat_value.setTextAlignment(QtCore.Qt.AlignCenter)
                    mat_table.setItem(row, column + 1, qt_mat_value)
    def mat_item_selected(self, tab_mat_selected, tab_temp_selected):
        tab_mat_name = tab_mat_selected.objectName()
        # 先清空温度-参数表格
        tab_temp_selected.setRowCount(0)
        try:
            # 只显示选中的第1个材料参数
            selected_items = tab_mat_selected.selectedItems()
            item = selected_items[0]
            row_in_mat = item.row()  # 行数
            column = item.column() -1 # 列数，不考虑列名
            if item.text() == "Tabular":
                # 获取所有的固体/材料参数
                allmat_infos = self.get_materials[0] if "solid" in tab_mat_name else self.get_materials[1]
                allmat_names = list(allmat_infos.keys())
                allmat_names.reverse() # 表格控件逐行添加后，会导致表格行数和字典键值对序号发生偏移，需要在这里反向下
                # 获取到选中材料的行的属性
                select_mat_info = allmat_infos[allmat_names[row_in_mat]]
                allselect_mat_params = list(select_mat_info.keys())
                # 获取到选中的材料的列属性
                select_param_dict = select_mat_info[allselect_mat_params[column]]
                # 显示
                select_labels = list(select_param_dict.keys())
                value_strlist = select_param_dict[select_labels[0]][0].split(",")
                temp_strlist = select_param_dict[select_labels[-1]][0].split(",")
                value_list = self.format_data_v2(value_strlist)
                temp_list = self.format_data_v2(temp_strlist)
                if "Young's Modulus" in select_labels:
                    # 如果选中的材料包含杨式模量
                    value_strlist2 = select_param_dict[select_labels[1]][0].split(",")
                    value_list2 = self.format_data_v2(value_strlist2)
                    temp_list = [""] + temp_list + [""] + temp_list
                    value_list = ["杨氏模量"] +value_list + ["泊松比"] + value_list2
                for temp, value in zip(temp_list, value_list):
                    # 获取表格控件当前的行数
                    current_row = tab_temp_selected.rowCount()
                    # 设置显示的数据
                    temp = QTableWidgetItem(temp)
                    value = QTableWidgetItem(value)
                    # 设置表格项的对齐方式为居中
                    temp.setTextAlignment(QtCore.Qt.AlignCenter)
                    value.setTextAlignment(QtCore.Qt.AlignCenter)
                    # 显示
                    tab_temp_selected.insertRow(current_row)
                    tab_temp_selected.setItem(current_row, 0, temp)  # 第i行、j列的参数
                    tab_temp_selected.setItem(current_row, 1, value)  # 第i行、j列的参数
        except:
            pass
    def mat_appoint(self,choice="default"):
        try:
            if choice == "default":
                self.ui.mat_appoint_list.clear()
                for body,mat in self.bodymats_default.items():
                    mat_appoint_content = f"{mat}→{body}"
                    self.ui.mat_appoint_list.addItem(mat_appoint_content)  # 将材料分配方案输出到UI界面上
            else:
                body = self.ui.part_choice.currentText()
                mat_selected = self.ui.mat_all_list.selectedItems()
                mat_selected = mat_selected[0].text()
                mat_appointed = f"{mat_selected}→{body}"
                # 将字符串列表合并为一个字符串，然后检查特定字符是否在这个字符串中
                mat_appoint_content = [self.ui.mat_appoint_list.item(i).text()
                                   for i in range(self.ui.mat_appoint_list.count())]
                if body not in ''.join(mat_appoint_content):
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
    def mat_script_builder(self):
        """ 参数定义 """
        bodymats_custom = {
            self.ui.mat_appoint_list.item(i).text().split("→")[-1]: self.ui.mat_appoint_list.item(i).text().split("→")[0]
            for i in range(self.ui.mat_appoint_list.count())
        }
        is_success = len(bodymats_custom) == len(self.bodymats_default)
        if is_success:
            script_infos = [
                {
                    "template_name": "fluent_content",
                    "cmd_keys": ["define mat_path"],
                    "content2fill": [self.filemat_CFD],
                    "cmd_complete": "({key_str} \"{item_str}\")\n"
                },
                {
                    "template_name": "fluent_content",
                    "cmd_keys": ["define solid_zone_names", "define solid_mats"],
                    "content2fill": [list(bodymats_custom.keys()), list(bodymats_custom.values())],
                    "cmd_complete": "({key_str} '({item_str}))\n"
                },
                {
                    "template_name": "mechanical_content",
                    "cmd_keys": ["body_mats = "],
                    "content2fill": [bodymats_custom],
                    "cmd_complete": "{key_str}{item_str}\n"
                },
                {
                    "template_name": "multiphysics_calculation_flow",
                    "cmd_keys": ["file_mat_FEM = "],
                    "content2fill": [self.filemat_FEM[0]],
                    "cmd_complete": "{key_str} r\"{item_str}\"\n"
                }
            ]
            for script_info in script_infos:
                file_origin = self.script_template[script_info["template_name"]]
                file_new = file_origin.parent.parent / file_origin.name
                # 定义脚本路径：若已经生成自定义脚本，则不再是查找模板脚本、生成新脚本，而是查找已有的自定义脚本
                script_paths = [file_origin, file_new] if not file_new.exists() else [file_new, file_new]
                for cmd_keys, item in zip(script_info["cmd_keys"], script_info["content2fill"]):
                    if isinstance(item, dict):
                        item_cmd = item  # 对于字典类型的，在mechanical中使用，可直接使用
                    elif isinstance(item,list):
                        item_cmd = ' '.join(f'"{item}"' for item in item) # 对于列表类型的，在fluent中使用，需先转换成字符串
                    else:
                        item_cmd = str(item.absolute())
                    cmd_completes = script_info["cmd_complete"].format(key_str=cmd_keys, item_str=item_cmd)
                    is_success = script_builder(script_paths, cmd_keys, cmd_completes)
        info_alert("mat", is_success)
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
    def format_data_v2(self, var, number_decimal2save=1):
        """
        :param number_decimal2save:
        :param var: 传入参数，既可以是数字，也可以是字符串
        :return:
        """
        if isinstance(var, str):
            try:
                # 尝试将字符串转换为科学计数法型数字
                return f'{float(var):.{number_decimal2save}e}'
            except ValueError:
                # 如果转换失败，返回原始字符串
                return var
        elif isinstance(var, list):
            # 如果是列表，则递归调用convert_to_numeric()函数转换列表中的每个元素
            return [self.format_data_v2(item) for item in var]
        else:
            # 其他情况直接返回原始变量
            return f'{var:.{number_decimal2save}e}'