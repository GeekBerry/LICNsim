from PyQt5.QtWidgets import QAbstractItemView
from core.name import Name
from gui.common import TreeWidget
from debug import showCall


class NameTreeWidget(TreeWidget):
    NAME_SEG= 0

    def __init__(self, parent):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑
        self.itemClicked.connect(self.itemClickedEvent)

        self.setHead('Name', 'FullName', 'PendNum', 'StoreNum', 'TransNum')

    def install(self, announces, api):
        self.announces= announces
        self.api= api
        announces['playSteps'].append(self.refresh)

    @showCall
    def refresh(self, steps=None):
        name_tree= self.api['Monitor.getNameTree']()
        self.showNameTree(self, name_tree)

    def showNameTree(self, tree_item, name_tree):
        for name_key, sub_tree in name_tree.children.items():
            full_name= self.getName(tree_item[name_key])

            record= self.api['Monitor.getNameStateRecord'](full_name)
            pend_num= len(record.pending)
            store_num= len(record.store)
            trans_num= len(record.transfer)
            tree_item[name_key].setTexts(full_name, pend_num, store_num, trans_num)  # name_node

            self.showNameTree(tree_item[name_key], sub_tree)

    def itemClickedEvent(self, tree_item, p_int):
        self.announces['selectedName']( self.getName(tree_item) )

    def getName(self, tree_item):
        forebears= []
        while tree_item:
            forebears.append( tree_item.text(self.NAME_SEG) )
            tree_item= tree_item.parent()
        return Name('/'.join(forebears[::-1]))
