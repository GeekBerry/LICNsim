#!/usr/bin/python3
#coding=utf-8

from debug import showCall

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from core.icn_net import ICNNetHelper


class EdgeInfoDialog(QDialog):
    def __new__(cls, parent, *args, **kwargs):
        dialog= QDialog.__new__(EdgeInfoDialog)
        QDialog.__init__(dialog, parent)

        from visualizer.ui.ui_edge_info import Ui_EdgeInfo
        dialog.ui= Ui_EdgeInfo()
        dialog.ui.setupUi(dialog)
        return dialog

    @showCall
    def __init__(self, parent, graph, src, dst, logger):
        icn_edge= ICNNetHelper.edge(graph, src, dst)
        self.src= src
        self.dst= dst

        self.setWindowTitle(f'{icn_edge.name}信息')
        self.ui.tree_attr.init(icn_edge)
        self.ui.table_log.init(icn_edge.name, logger)

    def install(self, announces, api):
        announces['playSteps'].append(self.refresh)
        self.announces= announces

    @showCall
    def refresh(self, steps= 0):
        if self.isVisible():
            self.ui.tree_attr.refresh()
            self.ui.table_log.refresh()

    @showCall
    def closeEvent(self, event):
        super().closeEvent(event)
        self.announces['EdgeDialogClose'](self.src, self.dst)


# ----------------------------------------------------------------------------------------------------------------------
from visualizer.common import TreeWidget
from visualizer.common import SpinBox, CheckBox, ComboBox, DoubleSpinBox


class EdgeTreeWidget(TreeWidget):
    @showCall
    def init(self, icn_edge):
        self.setHead('Attr', 'Value')
        self.icn_edge= icn_edge

    @showCall
    def refresh(self):
        assert self.icn_edge
        self._showAttrs()
        self.expandToDepth(2)
        self.resizeColumnToContents(0)

    @showCall
    def _showAttrs(self):
        self['rate'].setWidgets( SpinBox(self.icn_edge, 'rate') )
        self['buffer_size'].setWidgets( SpinBox(self.icn_edge, 'buffer_size') )
        self['delay'].setWidgets( SpinBox(self.icn_edge, 'delay') )
        self['loss'].setWidgets( DoubleSpinBox(self.icn_edge, 'loss') )

        self['buffer'].clear()
        self['buffer'].setTexts( len(self.icn_edge._bucket) )
        for row, each in enumerate(self.icn_edge._bucket):
            self['buffer'][row].setTexts( each )


