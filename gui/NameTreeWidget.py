from PyQt5.QtWidgets import QAbstractItemView

from core import Name
from gui.common import TreeWidget
from debug import showCall


class NameTreeWidget(TreeWidget):  # 配合着 NameMonitor 使用
    def __init__(self, parent, announces, api):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.setAlternatingRowColors(True)  # 隔行显示颜色

        self.announces= announces
        self.api= api
        announces['playSteps'].append(self.playSteps)

        self.itemClicked.connect(self.itemClickedEvent)

    def playSteps(self, steps):
        if self.isVisible():
            self.refresh()

    def refresh(self):
        # self.clearSelection()
        name_table= self.api['NameMonitor.table']()
        assert name_table is not None
        self.setHeads('Name', 'PendNum', 'StoreNum', 'TransNum')
        self.showNameTree(self, name_table.name_tree)

    def showNameTree(self, tree_item, name_tree):
        for name_node in name_tree:
            if name_node.hasValue():
                record= name_node.getValue()
                values= len(record.pending), len(record.store), len(record.transfer)
            else:
                values= ()
            tree_item[name_node.key].setValues(*values)
            self.showNameTree(tree_item[name_node.key], name_node)

    def itemClickedEvent(self, tree_item, col):
        name= Name(tree_item.getPath())
        self.announces['selectedName'](name)



























