# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_node_info.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_NodeInfo(object):
    def setupUi(self, NodeInfo):
        NodeInfo.setObjectName("NodeInfo")
        NodeInfo.resize(821, 364)
        self.gridLayout = QtWidgets.QGridLayout(NodeInfo)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(NodeInfo)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_unit = QtWidgets.QWidget()
        self.tab_unit.setObjectName("tab_unit")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.tab_unit)
        self.gridLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.tree_unit = UnitTreeWidget(self.tab_unit)
        self.tree_unit.setObjectName("tree_unit")
        self.tree_unit.headerItem().setText(0, "1")
        self.gridLayout_4.addWidget(self.tree_unit, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_unit, "")
        self.tab_cs = QtWidgets.QWidget()
        self.tab_cs.setObjectName("tab_cs")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_cs)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.table_cs = NodeCSTableWidget(self.tab_cs)
        self.table_cs.setObjectName("table_cs")
        self.table_cs.setColumnCount(0)
        self.table_cs.setRowCount(0)
        self.gridLayout_3.addWidget(self.table_cs, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_cs, "")
        self.tab_infotable = QtWidgets.QWidget()
        self.tab_infotable.setObjectName("tab_infotable")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_infotable)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tree_info = NodeInfoTreeWidget(self.tab_infotable)
        self.tree_info.setObjectName("tree_info")
        self.tree_info.headerItem().setText(0, "1")
        self.gridLayout_2.addWidget(self.tree_info, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_infotable, "")
        self.tab_log = QtWidgets.QWidget()
        self.tab_log.setObjectName("tab_log")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.tab_log)
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.table_log = NodeLogTableWidget(self.tab_log)
        self.table_log.setObjectName("table_log")
        self.table_log.setColumnCount(4)
        self.table_log.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.table_log.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_log.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_log.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table_log.setHorizontalHeaderItem(3, item)
        self.gridLayout_5.addWidget(self.table_log, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_log, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(NodeInfo)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(NodeInfo)

    def retranslateUi(self, NodeInfo):
        _translate = QtCore.QCoreApplication.translate
        NodeInfo.setWindowTitle(_translate("NodeInfo", "Dialog"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_unit), _translate("NodeInfo", "Units"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_cs), _translate("NodeInfo", "ContentStore"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_infotable), _translate("NodeInfo", "InfoTable"))
        item = self.table_log.horizontalHeaderItem(0)
        item.setText(_translate("NodeInfo", "Order"))
        item = self.table_log.horizontalHeaderItem(1)
        item.setText(_translate("NodeInfo", "Time"))
        item = self.table_log.horizontalHeaderItem(2)
        item.setText(_translate("NodeInfo", "Action"))
        item = self.table_log.horizontalHeaderItem(3)
        item.setText(_translate("NodeInfo", "Args"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_log), _translate("NodeInfo", "Log"))

from visualizer import NodeCSTableWidget, NodeInfoTreeWidget, NodeLogTableWidget, UnitTreeWidget
