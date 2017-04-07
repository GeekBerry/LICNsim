from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from core.packet import Name

class CSTableWidget(QTableWidget):
    PACKET_NAME, CS_NUMBER= 0, 1

    def __init__(self, parent):
        super().__init__(parent)
        self.setSortingEnabled(True)  # 设置可以排序
        self.setSelectionMode(QAbstractItemView.SingleSelection)  # 设置选择模式为单选
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑

    def install(self, announces, api):
        announces['playSteps'].append(self._show)
        self.api= api

    def setNet(self, db):
        self.db= db
        self._show(None)

    def _show(self, steps):
        self.setColumnCount(2)
        self.setHorizontalHeaderItem(self.PACKET_NAME, QTableWidgetItem('PacketName') )
        self.setHorizontalHeaderItem(self.CS_NUMBER, QTableWidgetItem('CSNumber') )
        self.setRowCount( len(self.db.contents) )
        row= 0
        for packet_name, store_nodes in self.db.contents.items():
            self.setItem(  row, self.PACKET_NAME, QTableWidgetItem( str(packet_name) )  )
            self.setItem(   row, self.CS_NUMBER, QTableWidgetItem(  str( len(store_nodes) )  )   )
            row += 1

    def selectionChanged(self, selected, deselected):
        item= self.item(self.currentRow(), self.PACKET_NAME)
        self.api['View::viewStores'](  Name( item.text() )  )
