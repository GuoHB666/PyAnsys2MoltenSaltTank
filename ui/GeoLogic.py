from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import QSizePolicy
from pathlib import Path
import math
from .info_alert import info_alert
import re
from .script_builder import script_builder
class GeoLogic(QObject):
    def __init__(self, ui, script_template):
        super().__init__()
        self.ui = ui
        self.img_paths = [
            Path(__file__).parent / "resources" / "images" / "geo_tank.jpg",
            Path(__file__).parent / "resources" / "images" / "geo_insulation2base.jpg"
        ]
        self.script_template = script_template
        # 默认几何参数
        self.geo_parm_default = {
            "Lbottom": [20610 / 2 - 2000, 2000],
            "thick_bottom": [10, 22],
            "Lbottom_weld": [8, 8, 48],
            "hbottom_weld": [18.68, 18.68],
            "angle_bottom": math.degrees(math.atan(1.5 / 100)),
            "Rwall": 10175,
            "Rtop": 24400,
            "htop": 2231,
            "hwall": [2000, 2000, 2000, 2000, 2000, 2210 + 2200],
            "thick_wall": [30, 22, 20, 16, 14, 10],
            "ratio_weld": [4, 4, 4, 4, 4],
            "num_insulation": 2,
            "thick_insulation": [250,220], # 内侧、外侧
            "num_corebase": 3,
            "Lbase": [13200, 10750, 10000, 200, 3800 ,250,1000], # 从最底下到上方
            "hbase": [400, 1400, 300, 1100],
            "inventory": 12.9e3
        }
        # 默认工况参数
        self.geo_param = self.geo_parm_default
        # 几何参数涉及到的控件
        self.geo_widgets = [self.ui.line_Lbottom, self.ui.line_thickbottom,self.ui.line_Lbweld ,
                       self.ui.line_thickbweld, self.ui.line_bangle , self.ui.line_Rwall ,
                       self.ui.line_Rtop , self.ui.line_htop, self.ui.line_hwall ,
                       self.ui.line_thickwall, self.ui.line_ratiowweld,
                       self.ui.line_insulationnum, self.ui.line_thickinsulation,
                       self.ui.line_basecorenum, self.ui.line_Lbase, self.ui.line_hbase,
                        self.ui.line_inventory]
        # 事件连接
        self.signal_connect_slot()
    def retranslate_ui(self):
        labels = [self.ui.label_img_geo,self.ui.label_img_insulation2base]
        for i,img_path in enumerate(self.img_paths):
            img_path = str(img_path.absolute())
            label = labels[i]
            self.set_label_properties(label, img_path)
    def signal_connect_slot(self):
        # 信号与槽连接
        self.ui.button_geodefault.clicked.connect(self.show_default_geo_params)
        self.ui.button_geosubmit.clicked.connect(self.geo_script_generation)
        self.ui.box_geo.currentIndexChanged.connect(self.insulation_structure_choice)
    def geo_script_generation(self):
        """
        读取控件参数并生成脚本文件
        :return:
        """
        """参数定义"""
        is_success = False
        geo_params_custom = {}
        file_geo_template = self.script_template["geo_content"]
        file_geo = file_geo_template.parent.parent.parent / "geometry" / "geo.scdoc"
        """读取控件选项里各个几何参数的大小"""
        for widget, key in zip(self.geo_widgets,self.geo_parm_default):
            value_strs = widget.text()
            value_list = value_strs.split(" ")
            if not is_satisfied_input(value_strs):
                is_success = False
                break
            if value_strs == "":
                value = None
                is_success = False # 若读取到空控件，表明信息没填写，则无法生成后续脚本
                break
            elif len(value_list) == 1:
                value = float(value_list[0])
            else:
                value = [float(value_str) for value_str in value_strs.split(" ")]
                is_success = True
            geo_params_custom[key] = value
        if is_success:
            script_infos = [
                {
                    "template_name": "geo_content",
                    "cmd_keys": ["geo_file_path = "],
                    "content2fill": [file_geo.absolute()],
                    "cmd_complete": "{key_str}r\"{item_str}\"\n"
                },
                {
                    "template_name": "geo_content",
                    "cmd_keys": ["geo_param = "],
                    "content2fill": [geo_params_custom],
                    "cmd_complete": "{key_str}{item_str}\n"
                },
                {
                    "template_name": "mechanical_content",
                    "cmd_keys": ["salt_inventory = "],
                    "content2fill": [geo_params_custom["inventory"]],
                    "cmd_complete": "{key_str}{item_str}\n"
                },
                {
                    "template_name": "fluent_meshing_content",
                    "cmd_keys": ["test_for_delete = "],
                    "content2fill": ["-1"],
                    "cmd_complete": "{key_str}{item_str}\n"
                }
                ]
            for script_info in script_infos:
                file_origin = self.script_template[script_info["template_name"]]
                file_new = file_origin.parent.parent / file_origin.name
                # 定义脚本路径：若已经生成自定义脚本，则不再是查找模板脚本、生成新脚本，而是查找已有的自定义脚本
                script_paths = [file_origin, file_new] if not file_new.exists() else [file_new, file_new]
                for cmd_keys, item in zip(script_info["cmd_keys"], script_info["content2fill"]):
                    if isinstance(item, (dict, str, float)):
                       item_cmd = str(item)
                    elif isinstance(item,list):
                        item_cmd = ' '.join(f'"{item}"' for item in item) # 对于列表类型的，在fluent中使用，需先转换成字符串
                    else:
                        item_cmd = str(item.absolute())
                    cmd_completes = script_info["cmd_complete"].format(key_str=cmd_keys, item_str=item_cmd)
                    if not script_builder(script_paths, cmd_keys, cmd_completes):
                        is_success = False
                        break
        info_alert("geo",is_success)
    def insulation_structure_choice(self, index):
        label = self.ui.label_img_insulation2base
        if index == 0:
            img_path = str(self.img_paths[1].absolute())
        else:
            img_path = None
        self.set_label_properties(label, img_path)
    def show_default_geo_params(self):
        self.ui.box_geo.setCurrentIndex(0)
        # 使用 zip() 函数同时遍历两个列表
        for (key, value), widget_line in zip(self.geo_parm_default.items(), self.geo_widgets):
            if isinstance(value, int):
                content = str(value)
            elif isinstance(value, float):
                content = "{:.3f}".format(value)
            else:
                # 使用 join() 方法将列表转换为字符串，并使用空格作为分隔符。之后，需去除方括号
                content = ' '.join("{:.2f}".format(x) for x in value)
                content = content.replace("[", "").replace("]", "")
            widget_line.setText(content)
            widget_line.setCursorPosition(0) # 将光标移动到开头
    @staticmethod
    def set_label_properties(label, pixmap_path):
        pixmap = QPixmap(pixmap_path) # 从文件路径创建 QPixmap 对象
        label.setPixmap(pixmap)  # 将 pixmap 设置为标签的图片
        label.setScaledContents(True)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setAlignment(Qt.AlignCenter)



def is_satisfied_input(s):
    # Check if the string matches the pattern for spaces or numbers (including decimals)
    pattern = r'^\s*(\d+(\.\d+)?\s*)*$'
    return bool(re.match(pattern, s))