from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from core.packet import Name
from debug import showCall


class CSTableWidget(QTableWidget):
    PACKET_NAME, CS_NUMBER= 0, 1

    def __init__(self, parent):
        super().__init__(parent)
        self.setSortingEnabled(True)  # 设置可以排序
        self.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置选择模式为单选
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑

    def init(self, monitor):
        self.monitor= monitor
        self.setColumnCount(2)
        self.setHorizontalHeaderItem(self.PACKET_NAME, QTableWidgetItem('PacketName') )
        self.setHorizontalHeaderItem(self.CS_NUMBER, QTableWidgetItem('CSNumber') )
        self._show()

    def install(self, announces, api):
        announces['playSteps'].append(self.refresh)
        self.api= api

    def refresh(self, steps):
        self._show()
        self.setColumnWidth(0, 200)

    def _show(self):
        self.setRowCount(len(self.monitor.contents))
        row= 0
        for packet_name, store_nodes in self.monitor.contents.items():
            self.setItem(  row, self.PACKET_NAME, QTableWidgetItem( str(packet_name) )  )
            self.setItem(   row, self.CS_NUMBER, QTableWidgetItem(  str( len(store_nodes) )  )   )
            row += 1

    @showCall
    def selectionChanged(self, selected, deselected):
        item= self.item(self.currentRow(), self.PACKET_NAME)
        self.api['View::setShowName'](  Name( item.text() )  )

