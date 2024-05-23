from PyQt5.QtCore import QObject

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
