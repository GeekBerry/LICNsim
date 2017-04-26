# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_edge_info.ui'
#
# Created by: PyQt5 UI code generator 5.8.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_EdgeInfo(object):
    def setupUi(self, EdgeInfo):
        EdgeInfo.setObjectName("EdgeInfo")
        EdgeInfo.resize(350, 208)
        self.gridLayout = QtWidgets.QGridLayout(EdgeInfo)
        self.gridLayout.setObjectName("gridLayout")
        self.tabWidget = QtWidgets.QTabWidget(EdgeInfo)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_attr = QtWidgets.QWidget()
        self.tab_attr.setObjectName("tab_attr")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.tab_attr)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.tree_attr = EdgeTreeWidget(self.tab_attr)
        self.tree_attr.setObjectName("tree_attr")
        self.tree_attr.headerItem().setText(0, "1")
        self.gridLayout_3.addWidget(self.tree_attr, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_attr, "")
        self.tab_log = QtWidgets.QWidget()
        self.tab_log.setObjectName("tab_log")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.tab_log)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.table_log = LogTableWidget(self.tab_log)
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
        self.gridLayout_2.addWidget(self.table_log, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab_log, "")
        self.gridLayout.addWidget(self.tabWidget, 0, 0, 1, 1)

        self.retranslateUi(EdgeInfo)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(EdgeInfo)

    def retranslateUi(self, EdgeInfo):
        _translate = QtCore.QCoreApplication.translate
        EdgeInfo.setWindowTitle(_translate("EdgeInfo", "Dialog"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_attr), _translate("EdgeInfo", "Attr"))
        item = self.table_log.horizontalHeaderItem(0)
        item.setText(_translate("EdgeInfo", "Order"))
        item = self.table_log.horizontalHeaderItem(1)
        item.setText(_translate("EdgeInfo", "Time"))
        item = self.table_log.horizontalHeaderItem(2)
        item.setText(_translate("EdgeInfo", "Action"))
        item = self.table_log.horizontalHeaderItem(3)
        item.setText(_translate("EdgeInfo", "Args"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_log), _translate("EdgeInfo", "Log"))

from visualizer import EdgeTreeWidget, LogTableWidget
