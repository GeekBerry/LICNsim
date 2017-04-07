
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog

class NodeInfoDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAttribute(Qt.WA_DeleteOnClose)  # 关闭时就析构

    # TODO 显示CS和infoTable, 可编辑Node信息, (编辑时实时修改界面显示, 还是靠刷新来完成)?


