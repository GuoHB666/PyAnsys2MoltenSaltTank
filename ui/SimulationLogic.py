from PyQt5.QtWidgets import QHeaderView, QComboBox,QCheckBox
from PyQt5.QtCore import QObject, QThread
from pathlib import Path
from PyQt5.QtGui import QIntValidator
from .info_alert import info_alert
from .script_builder import script_builder
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
import sys
import re

class SimulationLogic(QObject):
    def __init__(self, ui,software_folder, template_script):
        super().__init__()
        self.script_template = template_script
        self.ui = ui
        self.software_folder = software_folder
        self.subthreads = None
        self.tab_boundary_allrows = [i for i in range(self.ui.table_boundary_conditions.rowCount())]
        self.tab_boundary_necessaryrows = self.tab_boundary_allrows # 脚本生成时需要检查的边界条件表行数
        self.charge_rows = self.get_charge_rows() # 边界条件表中必选框的行数
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
        self.ui.choice_working_condition.setDisabled(True)  # 设置 Combobox 为只读状态
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
        self.ui.choice_working_condition.currentTextChanged.connect(self.tab_boundary_changed)
        self.ui.button_tosimulate.released.connect(self.simulate_script_builder)
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
        if self.ui.simulate_time_input.text() == "":
            is_success = False
        else:
            content2fill_fluent.append(self.ui.simulate_time_input.text())
        # 生成脚本
        if is_success:
            script_custom = {}
            # 用于计算的脚本路径生成，得确保脚本文件一定存在
            for script_name, script_path in self.script_template.items():
                custom_script_path = script_path.parent.parent / script_path.name
                if not custom_script_path.exists():
                    is_success = False
                    break
                script_custom[script_name]= str(custom_script_path.absolute())
            # 基于字典，生成脚本
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
                # 开展脚本替换
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
        if is_success:
            template_simulate_flow = self.script_template["multiphysics_calculation_flow"]
            custom_simulate_flow = template_simulate_flow.parent.parent / template_simulate_flow.name
            self.simulate_with_ansys(str(custom_simulate_flow.absolute()))
    def tab_boundary_changed(self):
        operate_condition = self.ui.choice_working_condition.currentText()
        for row in self.charge_rows:
            if operate_condition == "充放热工况":
                self.ui.table_boundary_conditions.showRow(row)
                self.tab_boundary_necessaryrows = self.tab_boundary_allrows
            else:
                self.ui.table_boundary_conditions.hideRow(row)
                self.tab_boundary_necessaryrows = list(set(self.tab_boundary_allrows) - set(self.charge_rows))
    def simulate_with_ansys(self, script_multiphysics):
        # 启动分隔符
        self.update_brow_simulate("=" * 50)
        # 禁用按钮以防止重复启动线程
        self.buttons_enable(False)
        # 创建子线程类
        self.subthreads = [RunSimulationThread(script_multiphysics), SimulationTrackerThread()]
        # 子线程操作
        for subthread in self.subthreads:
            # 连接 子线程 的信号到槽函数
            subthread.update_signal.connect(self.update_brow_simulate)
            # 线程完成后重新启用按钮
            subthread.finished.connect(self.check_threads_allfinished)
            # 启动线程
            subthread.start()

    def check_threads_allfinished(self):
        is_all_run = all(thread.isRunning() for thread in self.subthreads)
        is_all_close = all(thread.isFinished() for thread in self.subthreads)
        if is_all_close:
            # 线程完成后重新启用按钮
            self.buttons_enable(True)
            # 结束分隔符
            self.update_brow_simulate("="*50)
    @pyqtSlot(str)
    def update_brow_simulate(self, message):
        self.ui.brow_simulate.append(message)
    def buttons_enable(self, button_statue=False):
        buttons = [self.ui.button_tosimulate]
        for script_button in buttons:
            script_button.setEnabled(button_statue)


import time
# 将父文件夹路径添加到sys.path
path_project = Path(__file__).parent.parent
sys.path.append(str(path_project))
# 现在可以使用 from ... import 语法导入父文件夹中的模块
from PyWbUnit.CoWbUnit import CoWbUnitProcess


class RunSimulationThread(QThread):
    update_signal = pyqtSignal(str)
    def __init__(self, script_multiphysics):
        super().__init__()
        self.script_multiphysics = script_multiphysics
    def run(self):
        try:
            # folder_user = r"D:\GuoHB\MyFiles\Code\PyAnsys2MoltenSaltTank\software\py_ansys_files\user_files"
            # journal = os.path.join(folder_user, "journal.txt")
            # ansys_events = {
            #     "system_building": "【{current_stage}/{all_stage}】 创建计算系统中\n",
            #     "system_builded": "【{current_stage}/{all_stage}】 计算系统创建结束\n",
            #     "geo_building": "【{current_stage}/{all_stage}】 开始创建几何\n",
            #     "geo_builded": "【{current_stage}/{all_stage}】 几何创建结束\n",
            #     "CFD_meshing": "【{current_stage}/{all_stage}】 开展CFD网格划分中\n",
            #     "CFD_meshed": "【{current_stage}/{all_stage}】 CFD网格划分结束\n",
            #     "CFD_runing": "【{current_stage}/{all_stage}】 开展CFD计算中\n",
            #     "CFD_runed": "【{current_stage}/{all_stage}】 CFD计算结束\n",
            #     "thermal_load_importing": "【{current_stage}/{all_stage}】 创建温度载荷中\n",
            #     "thermal_load_imported": "【{current_stage}/{all_stage}】 温度载荷创建结束\n",
            #     "Mechanical_runing": "【{current_stage}/{all_stage}】 开展固体域力学分析中\n",
            #     "Mechanical_runed": "【{current_stage}/{all_stage}】 固体域力学分析结束\n"
            # }
            # with open(journal, 'w', encoding='utf-8') as f:
            #     for i, (key, value) in enumerate(ansys_events.items(), start=1):
            #         journal_line = f"{value.format(current_stage=i, all_stage=len(ansys_events))}"
            #         f.write(journal_line)
            #         f.flush()  # 确保数据被立即写入文件
            #         time.sleep(10)
            ansys_simulation = CoWbUnitProcess(wbjpFolder=path_project / "software")
            ansys_simulation.simulation_run(self.script_multiphysics)
            # for i in range(10):
            #     time.sleep(1)  # 模拟耗时计算
            #     self.update_signal.emit(f"Worker 2 进度：{i + 1}/10")
            # self.update_signal.emit("Worker 2 完成")
        except Exception as e:
            print("An exception occurred:", e)
class SimulationTrackerThread(QThread):
    update_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
    def run(self):
        time.sleep(5) # 在正式查找日志文件之前，需延时等待 模拟计算 类的初始化
        journal = Path(__file__).parent.parent / "software" / "py_ansys_files" / "user_files" / "journal.txt"
        stage_old = 0
        time_start = time.time()
        while True:
            try:
                with open(journal, 'r') as file:
                    lines = file.readlines()
                    last_line = lines[-1].strip()  # 读取最后一行，去除了"\n"
                    expression = self.extract_expression(last_line)
                    stage_current = self.get_expression_result(expression)
                    if stage_current > stage_old:
                        time_start = time.time()
                        self.update_signal.emit(last_line)
                        if stage_current == 1:
                            return
                    else:
                        time_end = time.time()
                        text_to_add = f"\t 已运行 {time_end-time_start:.2f} s"
                        self.update_signal.emit(text_to_add)
                stage_old = stage_current # 更新状态参数
                time.sleep(2)
            except:
                time_end = time.time()
                self.update_signal.emit(f"***** 连接中，已用时 {time_end-time_start:.2f} s *****")
                time.sleep(2)
    @staticmethod
    def extract_expression(text):
        # 使用正则表达式匹配形如【2/12】的表达式
        match = re.search(r'【(.*?)】', text)
        if match:
            return match.group(1)  # 提取括号中的表达式
        return None
    @staticmethod
    def get_expression_result(expression):
        try:
            result = eval(expression)
            return result
        except Exception as e:
            print(f"Error evaluating expression: {expression}")
            print(e)
            return None