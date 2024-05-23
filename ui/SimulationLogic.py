from PyQt5.QtWidgets import QHeaderView, QComboBox,QCheckBox
from PyQt5.QtCore import QObject, QThread
from pathlib import Path
from PyQt5.QtGui import QIntValidator
class SimulationLogic(QObject):
    def __init__(self, ui,ansys_simulation):
        super().__init__()
        self.ui = ui
        self.ansys_simulation = ansys_simulation
        self.thread = QThread() # 定义的子线程
        self.tab_boundary_rows = [i for i in range(self.ui.table_boundary_conditions.rowCount())]
        self.tab_boundary_checkrows = self.tab_boundary_rows
        self.heat_rows = self.get_heat_rows()
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
            com_box = QComboBox(); com_box.addItem('常量')
            check_box = QCheckBox(); check_box.setChecked(True)
            if row_index > 0: com_box.addItem('瞬时值')
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
       # info_alert("simulation",msg_info)
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
