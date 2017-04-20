#!/usr/bin/python3
#coding=utf-8

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from visualizer.common import QtUiBase
from debug import showCall


class NodeInfoDialog(QDialog, QtUiBase):
    def __init__(self, parent, UIForm, icn_node, logger):
        QDialog.__init__(self, parent)
        QtUiBase.setupUi(self, UIForm)
        self.setWindowTitle(f'Node{icn_node.name}信息')
        self.setAttribute(Qt.WA_DeleteOnClose)  # 关闭时就析构

        self.ui.tree_unit.init(icn_node)
        self.ui.table_cs.init( icn_node.units.get('cs') )
        self.ui.tree_info.init( icn_node.units.get('info') )
        self.ui.table_log.init( icn_node.name, logger )

    # TODO 可编辑Node信息, (编辑时实时修改界面显示, 还是靠刷新来完成)?

#=======================================================================================================================
from visualizer.common import HeadTreeItem
from PyQt5.QtWidgets import QTreeWidget, QAbstractItemView

class UnitTreeWidget(QTreeWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑

    def init(self, icn_node):
        self.setHeaderItem( HeadTreeItem(self, 'Key', 'Value') )
        self.icn_node= icn_node
        self._showUnits()
        self._showAPI()
        self._showAnnounces()

        self.setColumnWidth(0, 200)
        self.expandToDepth(0)

    @showCall
    def _showUnits(self):
        if self.icn_node:
            for unit_name, unit in self.icn_node.units.items():
                self.headerItem()[unit_name].setTexts(unit)

    def _showAPI(self):
        if self.icn_node:
            self.headerItem()['API'].setTexts('对应函数')
            for api_name, func in self.icn_node.api.items():
                self.headerItem()['API'][api_name].setTexts(func)

    def _showAnnounces(self):
        if self.icn_node:
            self.headerItem()['Announce'].setTexts('接收者')
            for anno_name, announce in self.icn_node.announces.items():
                self.headerItem()['Announce'][anno_name].setTexts(f'{len(announce)}个')
                for index, receiver in enumerate(announce):
                    self.headerItem()['Announce'][anno_name][index].setTexts(receiver)

# ----------------------------------------------------------------------------------------------------------------------
from core.packet import Packet
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView


class NodeCSTableWidget(QTableWidget):
    PACKET_NAME, PACKET_TYPE, PACKET_NONCE, PACKET_SIZE= 0, 1, 2, 3
    def __init__(self, parent):
        super().__init__(parent)
        self.setSortingEnabled(True)  # 设置可以排序
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑

    def init(self, cs_unit):
        self.setColumnCount(4)
        self.setHorizontalHeaderItem(self.PACKET_NAME, QTableWidgetItem('Name') )
        self.setHorizontalHeaderItem(self.PACKET_TYPE, QTableWidgetItem('Type') )
        self.setHorizontalHeaderItem(self.PACKET_NONCE, QTableWidgetItem('Nonce') )
        self.setHorizontalHeaderItem(self.PACKET_SIZE, QTableWidgetItem('Size') )
        self.cs_unit= cs_unit
        self._showCSTable()

        self.setColumnWidth(self.PACKET_NAME, 200)

    def _showCSTable(self):
        if self.cs_unit:
            cs_table= self.cs_unit.table
            self.setRowCount( len(cs_table) )
            for row, packet in enumerate( cs_table.values() ):
                self.setRow(row, packet.name, Packet.typeStr(packet.type), hex(packet.nonce), packet.size)

    def setRow(self, row, *values):
        for col, value in enumerate(values):
            item=  QTableWidgetItem( str(value) )
            print(item, item.text())
            self.setItem( row, col, item )

# ----------------------------------------------------------------------------------------------------------------------
from core.info_table import isPending, sendIPast
from PyQt5.QtWidgets import QTreeWidget


class NodeInfoTreeWidget(QTreeWidget):
    def init(self, info_unit):
        self.setHeaderItem( HeadTreeItem(self, 'Key', 'Value') )
        self.info_unit= info_unit

        self._show()
        self.setColumnWidth(0, 200)
        self.expandToDepth(1)

    def _show(self):
        for packet_name, info in self.info_unit.table.items():
            for faceid, entry in info.items():
                self.headerItem()[packet_name][faceid]['isPending'].setTexts(isPending(entry))
                self.headerItem()[packet_name][faceid]['sendIPast'].setTexts(sendIPast(entry))

                for p_type in Packet.TYPES:
                    self.headerItem()[packet_name][faceid]['recv'][ Packet.typeStr(p_type) ].setTexts( entry.recv[p_type] )

                for p_type in Packet.TYPES:
                    self.headerItem()[packet_name][faceid]['send'][ Packet.typeStr(p_type) ].setTexts( entry.send[p_type] )

# ----------------------------------------------------------------------------------------------------------------------
class NodeLogTableWidget(QTableWidget):
    ORDER, TIME, ACTION, ARGS= 0, 1, 2, 3
    def __init__(self, parent):
        super().__init__(parent)
        self.setSortingEnabled(True)  # 设置可以排序
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑

    @showCall
    def init(self, hardware, logger):
        self.hardware= hardware
        self.logger= logger

        self._show()
        self.setColumnWidth(self.ARGS, 300)

    def _show(self):
        if self.logger:
            records= self.logger(hardware=self.hardware)
            for row, record in enumerate(records):
                self.insertRow(row)
                self.setRow( row, '%08X'%(record['order']), '%010d'%(record['time']), record['action'], record['args'] )

    def setRow(self, row, *values):
        for col, value in enumerate(values):
            item=  QTableWidgetItem( str(value) )
            print(item, item.text())
            self.setItem( row, col, item )
