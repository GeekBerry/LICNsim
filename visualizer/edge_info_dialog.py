#!/usr/bin/python3
#coding=utf-8

from debug import showCall

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog


class EdgeInfoDialog(QDialog):
    @showCall
    def __init__(self, parent, icn_edge, logger):
        super().__init__(parent)
        from visualizer.ui.ui_edge_info import Ui_EdgeInfo
        self.ui= Ui_EdgeInfo()
        self.ui.setupUi(self)
        self.setWindowTitle(f'{icn_edge.name}信息')
        self.ui.tree_attr.init(icn_edge)
        self.ui.table_log.init(icn_edge.name, logger)

    def install(self, announces, api):  # TODO 可编辑Node信息, (编辑时实时修改界面显示, 还是靠刷新来完成)?
        announces['playSteps'].append(self.refresh)

    @showCall
    def refresh(self, steps= 0):
        self.ui.tree_attr.refresh()
        self.ui.table_log.refresh()

# ----------------------------------------------------------------------------------------------------------------------
from visualizer.common import TreeWidget
from visualizer.controller import bindModuleController


class EdgeTreeWidget(TreeWidget):
    @showCall
    def init(self, icn_edge):
        self.setHead('Attr', 'Value')
        self.icn_edge= icn_edge

    @showCall
    def refresh(self):
        self._showAttrs()
        self.expandToDepth(2)
        self.resizeColumnToContents(0)

    @showCall
    def _showAttrs(self):
        if self.icn_edge:
            if not bindModuleController(self, self.icn_edge):
                self['channel'].setTexts(self.icn_edge)


