#!/usr/bin/python3
#coding=utf-8

import sys
from debug import showCall

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QPushButton, QComboBox, QFileDialog

from visualizer.common import TreeWidget, TableWidget
from core.icn_net import ICNNetHelper


# class UI_Class:
#     def __init__(self, UI_Form):
#         self.UI_Form= UI_Form
#
#     def __call__(self, cls):
#         def constructors(parent, *args, **kwargs):
#             BaseClass= cls.mor()[1]
#             obj= BaseClass.__new__(cls)
#             BaseClass.__init__(obj, parent)
#             obj.ui= self.UI_Form()
#             obj.ui.setupUi(obj)
#             return obj
#         return constructors


class NodeInfoDialog(QDialog):
    def __new__(cls, parent, *args, **kwargs):
        dialog= QDialog.__new__(cls)
        QDialog.__init__(dialog, parent)

        from visualizer.ui.ui_node_info import Ui_NodeInfo
        dialog.ui= Ui_NodeInfo()
        dialog.ui.setupUi(dialog)
        return dialog

    @showCall
    def __init__(self, parent, graph, node_name, logger):
        icn_node= ICNNetHelper.node(graph, node_name)
        self.node_name= node_name

        self.setWindowTitle(f'{icn_node.name}信息')
        self.ui.tree_unit.init(icn_node)
        self.ui.table_cs.init( icn_node.units.get('cs') )
        self.ui.tree_info.init( icn_node.units.get('info') )
        self.ui.table_log.init(icn_node.name, logger)

    def install(self, announces, api):  # TODO 可编辑Node信息, (编辑时实时修改界面显示, 还是靠刷新来完成)?
        announces['playSteps'].append(self.refresh)
        self.announces= announces

    def uninstall(self, announces, api):
        announces['playSteps'].discard(self.refresh)

    @showCall
    def refresh(self, steps= None):
        if self.isVisible():
            self.ui.tree_unit.refresh()
            self.ui.table_cs.refresh()
            self.ui.tree_info.refresh()
            self.ui.table_log.refresh()

    @showCall
    def closeEvent(self, event):
        super().closeEvent(event)
        self.announces['NodeDialogClose'](self.node_name)


# ======================================================================================================================
import constants
from core.node import NodeBufferUnit
from core.info_table import InfoUnit
from core.policy import PolicyUnit
from core.cs import ContentStoreUnit

from visualizer.common import SpinBox, CheckBox, ComboBox, DoubleSpinBox


class UnitTreeWidget(TreeWidget):
    def init(self, icn_node):
        self.setHead('Key', 'Value')
        self.icn_node= icn_node
        self.expandToDepth(2)

    @showCall
    def refresh(self):
        assert self.icn_node

        self['Node'].setTexts(self.icn_node)
        self._showUnits()
        self._showAPI()
        self._showAnnounces()
        self.resizeColumnToContents(0)

    @showCall
    def _showUnits(self):
        for unit_name, unit in self.icn_node.units.items():
            if isinstance(unit, NodeBufferUnit):
                self[unit_name]['size'].setWidgets(SpinBox(unit, 'buffer_size'))
                self[unit_name]['rate'].setWidgets(SpinBox(unit, 'rate'))
                self[unit_name]['buffer'].clear()
                self[unit_name]['buffer'].setTexts( len(unit._bucket) )
                for row, each in enumerate(unit._bucket):
                    self[unit_name]['buffer'][row].setTexts( each )
            elif isinstance(unit, ContentStoreUnit):
                self[unit_name]['size'].setTexts( len(unit) )
                self[unit_name]['capacity'].setWidgets( SpinBox(unit, 'capacity') )
            elif isinstance(unit, InfoUnit):
                self[unit_name]['max_size'].setWidgets( SpinBox(unit, 'max_size') )
                self[unit_name]['life_time'].setWidgets( SpinBox(unit, 'life_time') )
            elif isinstance(unit, PolicyUnit):
                box= ComboBox(unit, 'PolicyType', constants.POLICY_LIST)
                self[unit_name]['PolicyType'].setWidgets(box)
            else:
                self[unit_name].setTexts(unit)

    # FIXME 根据文件选类
    #     self.cls= None
    #     self.button= QPushButton()
    #     self.button.clicked.connect(self.xxx)
    #     self.box= ComboBox(self, 'cls', [])
    #     self['附加'].setWidgets(self.button, self.box)
    #
    # def xxx(self, *args):
    #     file_name, filter= QFileDialog.getOpenFileName(self, filter='Python Script (*.py)')
    #     if file_name:
    #         self.button.setText(file_name)
    #         class_list= getFileClass('C:\\Users\\bupt632\\Desktop\\LICNsim\\constants.py')
    #         self.box.clear()
    #         for each in class_list:
    #             self.box.addItem(repr(each), each)

    @showCall
    def _showAPI(self):
        self['API'].setTexts('对应函数')
        for api_name, func in self.icn_node.api.items():
            self['API'][api_name].setTexts(func)

    @showCall
    def _showAnnounces(self):
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
                self.setRow(row, packet.name, Packet.TYPE_STRING[packet.type], hex(packet.nonce), packet.size)


# ----------------------------------------------------------------------------------------------------------------------
class NodeInfoTreeWidget(TreeWidget):
    def init(self, info_unit):
        self.setHead('Key', 'Value')
        self.info_unit= info_unit
        self.expandToDepth(1)

    @showCall
    def refresh(self):
        self._showInfo()
        self.resizeColumnToContents(0)  # XXX 或者 self.setColumnWidth(0, 200)

    def _showInfo(self):
        for packet_name, row in self.info_unit.table.items():
            for faceid, cell in row.items():
                self[packet_name][faceid]['isPending'].setTexts( cell.isPending() )
                self[packet_name][faceid]['sendInterestPast'].setTexts( cell.sendInterestPast() )

                for p_type, type_name in enumerate(Packet.TYPE_STRING):
                    self[packet_name][faceid]['recv'][type_name].setTexts( cell.recv[p_type] )

                for p_type, type_name in enumerate(Packet.TYPE_STRING):
                    self[packet_name][faceid]['send'][type_name].setTexts(cell.sendStart[p_type])
