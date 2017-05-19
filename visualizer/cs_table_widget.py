from PyQt5.QtWidgets import QAbstractItemView

from core.packet import Name
from debug import showCall
from visualizer.common import TableWidget


class CSTableWidget(TableWidget):
    PACKET_NAME, CS_NUMBER= 0, 1

    def __init__(self, parent):
        super().__init__(parent)
        self.setSortingEnabled(True)  # 设置可以排序
        self.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置选择模式为单选
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑

        self.setHead('PacketName', 'CSNumber')
        self.monitor= None

    def install(self, announces, api):
        self.announces= announces
        self.api= api
        announces['playSteps'].append(self.refresh)

    @showCall
    def refresh(self, steps):
        self._show()
        self.resizeColumnsToContents()

    @showCall
    def _show(self):
        self.setRowCount( len(self.monitor.contents) )
        for row, (packet_name, store_nodes) in enumerate( self.monitor.contents.items() ):
            self.setRow(row, packet_name, len(store_nodes) )

    @showCall
    def selectionChanged(self, selected, deselected):
        item= self.item(self.currentRow(), self.PACKET_NAME)
        self.announces['selectedName'](  Name( item.text() )  )
