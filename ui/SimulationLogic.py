from PyQt5.QtWidgets import QHeaderView, QComboBox,QCheckBox
from PyQt5.QtCore import QObject, QThread
from pathlib import Path
from PyQt5.QtGui import QIntValidator
from .info_alert import info_alert
from .script_builder import script_builder
class SimulationLogic(QObject):
    def __init__(self, ui,ansys_simulation, template_script):
        super().__init__()
        self.script_template = template_script
        self.ui = ui
        self.ansys_simulation = ansys_simulation
        self.thread = QThread() # 定义的子线程
        self.tab_boundary_allrows = [i for i in range(self.ui.table_boundary_conditions.rowCount())]
        self.tab_boundary_necessaryrows = self.tab_boundary_allrows # 脚本生成时需要检查的边界条件表行数
        self.charge_rows = self.get_charge_rows() # 边界条件表中必选框的行数
        self.simulate_events = ["开始创建连接。。。", "创建仿真系统中。。。",
                                "仿真系统创建完成，开展几何建模中。。。","几何建模完成，导入模型中。。。",
                                "模型导入完成，划分网格中。。。","网格划分成功，启动Fluent中。。。",
                                "开始计算。。。", "计算完成！断开连接、保存并退出Ansys"]
        # 事件连接
        self.signal_connect_slot()
    def get_charge_rows(self):
        heat_rows = []
        for row in self.tab_boundary_allrows:
            row_header = self.ui.table_boundary_conditions.verticalHeaderItem(row).text()
            if "Inlet" in row_header or "Outlet" in row_header:
                heat_rows.append(row)
        return heat_rows
    def retranslate_ui(self):
        # 设置工况选项为第1个选项，并给定相应边界条件表格
        self.ui.choice_working_condition.setCurrentIndex(0)
        self.tab_boundary_changed()
        # 进度框内容初始化
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
        # 查找到类型列，然后设置宽度、填下多选框
        for col in range(self.ui.table_boundary_conditions.columnCount()):
            header_item = self.ui.table_boundary_conditions.horizontalHeaderItem(col)
            if header_item and header_item.text() == 'Type':
                col_type = col
        self.ui.table_boundary_conditions.setColumnWidth(col_type, 150)  # 将第一列的宽度设置为 150 像素
        for row_index in self.tab_boundary_allrows:
            com_box = QComboBox()
            com_box.addItem('Constant')
            if row_index >= min(self.charge_rows):
                com_box.addItem('Trasient')
            self.ui.table_boundary_conditions.setCellWidget(row_index,col_type,com_box)
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
        self.ui.button_simulate_scripts.released.connect(self.simulate_script_builder)
        # 通过连接 progressChanged 信号到 handle_progress_changed 槽函数，使得主线程能够监听、处理子线程的进度信息
        self.ansys_simulation.progressChanged.connect(self.handle_progress_changed)
    def simulate_script_builder(self):
        is_success = True
        """检查各输入值是否合法"""
        # 获得“Type”列和“Value”列
        column_search = [-1,-1]
        for col in range(self.ui.table_boundary_conditions.columnCount()):
            header_item = self.ui.table_boundary_conditions.horizontalHeaderItem(col)
            if header_item and header_item.text() == 'Type':
                column_search[0] = col
            elif header_item and header_item.text() == 'Value':
                column_search[1] = col
        # 边界条件表格检查、获得
        content2fill_fluent = []
        for row in self.tab_boundary_necessaryrows:
            row_header = self.ui.table_boundary_conditions.verticalHeaderItem(row).text()
            row_type = self.ui.table_boundary_conditions.cellWidget(row, column_search[0])
            row_value = self.ui.table_boundary_conditions.item(row, column_search[1])
            if row_value is None:
                is_success = False
                break
            else:
                script_path = row_value.text()
                if "Trasient" in row_type.currentText() and not Path(script_path).is_file():
                    is_success = False
                    break
                if "Ambient" in row_header or "Init salt" in row_header:
                    content2fill_fluent.append(script_path)
        # 模拟时间检查
        if self.ui.simulate_time_input.isEnabled() and self.ui.simulate_time_input.text() == "":
            is_success = False
        else:
            content2fill_fluent.append(self.ui.simulate_time_input.text())
        print(content2fill_fluent)
        # 生成几何脚本
        if is_success:
            script_custom = {}
            # 用于计算的脚本路径生成，得确保脚本文件一定存在
            for script_name, script_path in self.script_template.items():
                custom_script_path = script_path.parent.parent / script_path.name
                if not custom_script_path.exists():
                    is_success = False
                    break
                script_custom[script_name]= str(custom_script_path.absolute())
            script_infos = [
                {
                    "template_name": "fluent_content",
                    "cmd_keys": ["define init_ambient_temp", "define init_salt_temp", "define simulate_hour"],
                    "content2fill": content2fill_fluent,
                    "cmd_complete": "({key_str} {item_str})\n"
                },
                {
                    "template_name": "multiphysics_calculation_flow",
                    "cmd_keys": ["script_path = "],
                    #"content2fill": [self.script_template],
                    "content2fill": [script_custom],
                    "cmd_complete": "{key_str}{item_str}\n"
                }
            ]
            for script_info in script_infos:
                file_origin = self.script_template[script_info["template_name"]]
                file_new = file_origin.parent.parent / file_origin.name
                # 定义脚本路径：对于模拟求解，一定是基于已有的文件
                if not file_new.exists():
                    is_success = False
                    break
                script_paths = [file_new, file_new]
                # 开展脚本
                for cmd_keys, item in zip(script_info["cmd_keys"], script_info["content2fill"]):
                    if isinstance(item, (dict, str, float)):
                       item_cmd = str(item)
                    elif isinstance(item,list):
                        item_cmd = ' '.join(f'"{item}"' for item in item) # 对于列表类型的，在fluent中使用，需先转换成字符串
                    else:
                        item_cmd = str(item.absolute())
                    cmd_completes = script_info["cmd_complete"].format(key_str=cmd_keys, item_str=item_cmd)
                    is_success = script_builder(script_paths, cmd_keys, cmd_completes)
        info_alert("simulation", is_success)
    def tab_boundary_changed(self):
        operate_condition = self.ui.choice_working_condition.currentText()
        for row in self.charge_rows:
            if operate_condition == "充放热工况":
                self.ui.table_boundary_conditions.showRow(row)
                self.tab_boundary_necessaryrows = self.tab_boundary_allrows
                self.ui.simulate_time_input.setDisabled(False)
            else:
                self.ui.table_boundary_conditions.hideRow(row)
                self.tab_boundary_necessaryrows = list(set(self.tab_boundary_allrows) - set(self.charge_rows))
                self.ui.simulate_time_input.setDisabled(True)
    def simulate_with_ansys(self):
        # 创建子线程
        self.ansys_simulation.moveToThread(self.thread)
        # 开展ansys计算
        self.thread.started.connect(self.ansys_simulation.simula_system_run)
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
