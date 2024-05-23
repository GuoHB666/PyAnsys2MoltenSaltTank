from PyQt5.QtCore import QObject
from pathlib import Path
from PyQt5.QtGui import QIcon
class TreeLogic(QObject):
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.tree_names = []
        self.get_tree_nodenames()
        # 事件连接
        self.signal_connect_slot()
    def retranslate_ui(self):
        # 设置树形控件节点图标
        folder_img = Path(__file__).parent / "resources" / "icons"
        img_files = [
            folder_img / "ansys_pdslogo.gif",
            folder_img / "tank.png",
            folder_img / "select_mater35.gif",
            folder_img / "AnsysReportLogo.png",
            folder_img / "PP_TimeStep35.gif",
            folder_img / "B_ExtendSplit35.gif",
            folder_img / "result_proc.jpg",
        ]
        for index, img_file in enumerate(img_files):
            icon = QIcon(str(img_file.absolute()))
            item = self.ui.tree.headerItem() if index == 0 else self.ui.tree.topLevelItem(index - 1)  # 减去标题项的索引
            if item:  # 确保节点存在
                item.setIcon(0, icon)


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
