from PyQt5.QtWidgets import QAbstractItemView

from core import Name
from gui.common import TreeWidget
from debug import showCall


class NameTreeWidget(TreeWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.setAlternatingRowColors(True)  # 隔行显示颜色

        self.itemClicked.connect(self.itemClickedEvent)
        self.setHeads('Name', 'PendNum', 'StoreNum', 'TransNum')

    def install(self, announces, api):
        self.announces= announces
        self.api= api
        announces['playSteps'].append(self.playSteps)

    def playSteps(self, steps):
        if self.isVisible():
            self.refresh()

    def refresh(self):
        # self.clearSelection()
        name_tree= self.api['NameStoreMonitor.tree']()
        assert name_tree is not None
        self.showNameTree(self, name_tree)

    def showNameTree(self, tree_item, name_tree):
        for name_node in name_tree:
            if name_node.hasValue():
                store_record= name_node.getValue()
                values= len(store_record.pending), len(store_record.store), len(store_record.transfer)
            else:
                values= ()
            tree_item[name_node.key].setValues(*values)

            self.showNameTree(tree_item[name_node.key], name_node)

    def itemClickedEvent(self, tree_item, col):
        name= Name(tree_item.getPath())
        self.announces['selectedName'](name)



























