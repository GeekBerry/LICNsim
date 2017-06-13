from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtCore import Qt

from collections import defaultdict

from name import Name
from debug import showCall
from visualizer.common import TableWidget

# TODO 改为Tree
class CSTableWidget(TableWidget):
    PACKET_NAME, CS_NUMBER= 0, 1

    def __init__(self, parent):
        super().__init__(parent)
        self.setSortingEnabled(True)  # 设置可以排序
        self.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置选择模式为单选
        # self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑

        self.setHead('PacketName', 'StoredNum', 'PendingNum')
        self.monitor= None

    def install(self, announces, api):
        self.announces= announces
        self.api= api
        announces['playSteps'].append(self.refresh)

    @showCall
    def refresh(self, steps=None):
        self._show()
        self.resizeColumnsToContents()

    @showCall
    def _show(self):
        items= list( self.api['NodeStateMonitor::getNameItems']() )
        print(items)

        self.setRowCount( len(items) )
        for row, (name, record) in enumerate(items):
            self.setRow( row, name, len(record.store), len(record.pending) )

    @showCall
    def mousePressEvent(self, event):
        super().mousePressEvent(event)

        if event.button() == Qt.LeftButton:
            if self.selectedItems():  # 有所选中
                name_item= self.item(self.currentRow(), self.PACKET_NAME)
                self.announces['selectedName'](  Name( name_item.text() )  )
            else:
                self.announces['selectedName']( Name('') )
        elif event.button() == Qt.RightButton:
            self.announces['selectedName']( Name('') )
            self.clearSelection()
            self.clearFocus()
        else: pass

        super().mousePressEvent(event)
