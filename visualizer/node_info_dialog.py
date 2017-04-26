#!/usr/bin/python3
#coding=utf-8

import sys
from debug import showCall

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QAbstractItemView

from visualizer.common import TreeWidget, TableWidget


class NodeInfoDialog(QDialog):
    def __init__(self, parent, icn_node, logger):
        super().__init__(parent)
        from visualizer.ui.ui_node_info import Ui_NodeInfo
        self.ui= Ui_NodeInfo()
        self.ui.setupUi(self)

        self.setWindowTitle(f'{icn_node.name}信息')
        # self.setAttribute(Qt.WA_DeleteOnClose)  # FIXME 关闭时析构

        self.ui.tree_unit.init(icn_node)
        self.ui.table_cs.init( icn_node.units.get('cs') )
        self.ui.tree_info.init( icn_node.units.get('info') )
        self.ui.table_log.init(icn_node.name, logger)

    def install(self, announces, api):  # TODO 可编辑Node信息, (编辑时实时修改界面显示, 还是靠刷新来完成)?
        announces['playSteps'].append(self.refresh)

    def uninstall(self, announces, api):
        announces['playSteps'].discard(self.refresh)

    @showCall
    def refresh(self, steps= 0):
        if self.isVisible():
            self.ui.tree_unit.refresh()
            self.ui.table_cs.refresh()
            self.ui.tree_info.refresh()
            self.ui.table_log.refresh()

#=======================================================================================================================
from visualizer.controller import bindModuleController

class UnitTreeWidget(TreeWidget):
    def init(self, icn_node):
        self.setHead('Key', 'Value')
        self.icn_node= icn_node

    @showCall
    def refresh(self):
        self['Node'].setTexts(self.icn_node)
        self._showUnits()
        self._showAPI()
        self._showAnnounces()
        self.expandToDepth(2)
        self.resizeColumnToContents(0)

    def _showUnits(self):
        if self.icn_node:
            for unit_name, unit in self.icn_node.units.items():
                if bindModuleController(self[unit_name], unit):
                    pass
                else:
                    self[unit_name].setTexts(unit)

    def _showAPI(self):
        if self.icn_node:
            self['API'].setTexts('对应函数')
            for api_name, func in self.icn_node.api.items():
                self['API'][api_name].setTexts(func)

    def _showAnnounces(self):
        if self.icn_node:
            self['Announce'].setTexts('接收者')
            for anno_name, announce in self.icn_node.announces.items():
                self['Announce'][anno_name].setTexts(f'{len(announce)}个')
                for index, receiver in enumerate(announce):
                    self['Announce'][anno_name][index].setTexts(receiver)

# ----------------------------------------------------------------------------------------------------------------------
from core.packet import Packet
class NodeCSTableWidget(TableWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSortingEnabled(True)  # 设置可以排序
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑

    def init(self, cs_unit):
        self.setHead('Name', 'Type', 'Nonce', 'Size')
        self.cs_unit= cs_unit

    @showCall
    def refresh(self):
        self._showCSTable()
        self.resizeColumnsToContents()

    def _showCSTable(self):
        if self.cs_unit:
            cs_table= self.cs_unit.table
            self.setRowCount( len(cs_table) )
            for row, packet in enumerate( cs_table.values() ):
                self.setRow(row, packet.name, Packet.typeStr(packet.type), hex(packet.nonce), packet.size)

# ----------------------------------------------------------------------------------------------------------------------
from core.info_table import isPending, sendIPast
class NodeInfoTreeWidget(TreeWidget):
    def init(self, info_unit):
        self.setHead('Key', 'Value')
        self.info_unit= info_unit

    @showCall
    def refresh(self):
        self._showInfo()
        self.expandToDepth(1)
        self.resizeColumnToContents(0)  # XXX 或者 self.setColumnWidth(0, 200)

    def _showInfo(self):
        for packet_name, info in self.info_unit.table.items():
            for faceid, entry in info.items():
                self[packet_name][faceid]['isPending'].setTexts( isPending(entry) )
                self[packet_name][faceid]['sendIPast'].setTexts( sendIPast(entry) )

                for p_type in Packet.TYPES:
                    self[packet_name][faceid]['recv'][ Packet.typeStr(p_type) ].setTexts( entry.recv[p_type] )

                for p_type in Packet.TYPES:
                    self[packet_name][faceid]['send'][ Packet.typeStr(p_type) ].setTexts( entry.send[p_type] )
