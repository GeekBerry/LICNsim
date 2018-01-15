from PyQt5.QtWidgets import QAbstractItemView

from core import Name
from gui import TreeWidget
from debug import showCall


class NameInfoWidget(TreeWidget):
    def __init__(self, parent, announces, api):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑

        self.announces= announces
        self.api= api

        self.selected_name= Name()

        announces['playSteps'].append(self.playSteps)
        api['NameInfo.selectedName']= lambda :self.selected_name

        self.itemClicked.connect(self.itemClickedSlot)

    def playSteps(self, steps):
        if self.isVisible():
            self.refresh()

    def refresh(self):
        name_table= self.api['Monitor.getNameTable']()
        if name_table is None:
            return  # 没有安装 NameMonitor ？？？

        self.setHeads('Name', 'PendNum', 'StoreNum', 'TransINum', 'TransDNum')
        # self.clearSelection() XXX 是否需要清空
        self.showNameTree(self, name_table.root)

    def showNameTree(self, tree_item, name_tree):
        for name_node in name_tree:
            if name_node.hasValue():
                record= name_node.getValue()
                values= len(record.pending), len(record.store), len(record.trans_i), len(record.trans_d)
            else:
                values= ()
            tree_item[name_node.key].setValues(*values)
            self.showNameTree(tree_item[name_node.key], name_node)

    def itemClickedSlot(self, tree_item, col):
        self.selected_name= Name(tree_item.getPath())
        self.announces['selectedName'](self.selected_name)



























