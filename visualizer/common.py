from debug import showCall

import logging

import PyQt5.QtGui as QtGui
from PyQt5.QtCore import Qt

from constants import TransferState, INF
from core import Bind
from core.packet import Packet


def threshold(min, value, max):
    if value<min: return min
    if value>max: return max
    return value


def HotColor(value):
    color= QtGui.QColor()
    color.setHsvF(0.3*(1-value), 1.0, 1.0)  # 0.3为绿色; 0.0为红色
    return color


def DeepColor(value, h= 0.0):  # h:0.0为红色
    color= QtGui.QColor()
    color.setHsvF(h, value, 1.0)
    return color

# ======================================================================================================================
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class TreeItem(QTreeWidgetItem):
    def __init__(self, parent, text):
        self.burl= self
        super().__init__(parent, [text])
        self.table= {}

    def __getitem__(self, key):
        if key in self.table:
            return self.table[key]
        else:
            self.table[key]= child= TreeItem(self.burl, str(key))
            return child

    def __delitem__(self, key):
        if key in self.table:
            index= self.indexOfChild(self.table[key])
            item= self.takeChild(index)
            item.clear()
            del self.table[key]

    def widget(self, column):
        self.treeWidget().itemWidget(self, column)

    def setWidget(self, column, widget):
        self.treeWidget().setItemWidget(self, column, widget)

    def setWidgets(self, *widgets):
        for col, widget in enumerate(widgets):
            self.setWidget(col+1, widget)

    def setTexts(self, *values):
        for col, value in enumerate(values):
            self.setText( col+1, str(value) )

    def clear(self):
        children= self.takeChildren()
        for child in children:
            child.clear()
        self.table.clear()


class TreeWidget(QTreeWidget):
    def __init__(self, *args):
        super().__init__(*args)
        self.table= {}

    def setHead(self, *values):
        for col, value in enumerate(values):
            self.headerItem().setText(col, str(value))

    def __getitem__(self, key):
        if key in self.table:
            return self.table[key]
        else:
            self.table[key]= child= TreeItem(self, str(key))
            return child

    def __delitem__(self, key):
        if key in self.table:
            index= self.indexOfTopLevelItem(self.table[key])
            item= self.takeTopLevelItem(index)
            item.clear()


# ----------------------------------------------------------------------------------------------------------------------
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem


class TableWidget(QTableWidget):
    def setHead(self, *values):
        self.setColumnCount(len(values))
        for col, value in enumerate(values):
            self.setHorizontalHeaderItem( col, QTableWidgetItem( str(value) )  )

    def setRow(self, row, *values):
        for col, value in enumerate(values):
            self.setItem(  row, col, QTableWidgetItem( str(value) )  )

# ======================================================================================================================
from PyQt5.QtWidgets import QSpinBox, QCheckBox, QComboBox, QDoubleSpinBox


class DoubleSpinBox(QDoubleSpinBox):
    def __init__(self, obj, attr):
        super().__init__(None)
        self.setRange(0.0, 1.0)
        self.setSingleStep(0.05)
        self.bindAttr(obj, attr)

    def wheelEvent(self, event):
        pass

    def bindAttr(self, obj, attr):
        # self.disconnect()
        self.editingFinished.connect( Bind(self._setAttr, obj, attr) )
        # getAttr
        self.setValue( obj.__getattribute__(attr) )

    def _setAttr(self, obj, attr):
        obj.__setattr__( attr, self.value() )


class SpinBox(QSpinBox):
    def __init__(self, obj, attr):
        super().__init__(None)
        self.setRange(1, INF)
        self.bindAttr(obj, attr)

    def wheelEvent(self, event):
        pass

    def bindAttr(self, obj, attr):
        # self.disconnect()
        self.editingFinished.connect( Bind(self._setAttr, obj, attr) )
        # getAttr
        self.setValue( obj.__getattribute__(attr) )

    def _setAttr(self, obj, attr):
        obj.__setattr__( attr, self.value() )


class CheckBox(QCheckBox):
    def __init__(self, obj, attr):
        super().__init__(None)
        self.bindAttr(obj, attr)

    def bindAttr(self, obj, attr):
        # self.disconnect()
        self.stateChanged.connect( Bind(self._setAttr, obj, attr) )
        # 绑定显示状态
        if obj.__getattribute__(attr):
            self.setCheckState(Qt.Checked)
        else:
            self.setCheckState(Qt.Unchecked)

    @showCall
    def _setAttr(self, obj, attr, state):
        if state == Qt.Unchecked:
            value= False
        else:
            value= True
        obj.__setattr__(attr, value)


class ComboBox(QComboBox):
    def __init__(self, obj, attr, elements):
        super().__init__()
        for row, elem in enumerate(elements):
            self.insertItem(row, str(elem), elem)
        self.bindAttr(obj, attr)

    def wheelEvent(self, event):
        pass

    def bindAttr(self, obj, attr):
        # self.disconnect()
        self.currentIndexChanged.connect( Bind(self._setAttr, obj, attr) )
        # getAttr
        data= obj.__getattribute__(attr)
        index= self.findData(data)

        if index == -1:  # 没有找到
            index= self.count()
            self.insertItem( index, str(data), data)
            logging.warning(f'{self} 中没有 {data} 项')
        self.setCurrentIndex(index)

    def _setAttr(self, obj, attr, string):
        data= self.itemData( self.currentIndex() )
        obj.__setattr__( attr, data )


# ======================================================================================================================
def TransferRecordToText(record)->str:
    state_str= TransferState.TYPE_STRING[ record['state'] ]
    name_str= record['packet_head'].name
    type_str= Packet.typeStr( record['packet_head'].type )
    nonce_str= '%8X'%(record['packet_head'].nonce)
    begin_str= record['begin']
    end_str= record['end']
    arrived_str= record['arrived']
    return f'{state_str}\nName:{name_str}\nType:{type_str}\nNonce:{nonce_str}\nBegin:{begin_str}\nEnd:{end_str}\nArrived:{arrived_str}'


# ======================================================================================================================
from PyQt5.QtWidgets import QAbstractItemView


class LogTableWidget(TableWidget):  # 大bug
    def __init__(self, parent):
        super().__init__(parent)
        self.setSortingEnabled(True)  # 设置可以排序  FIXME 排序后追加会有问题
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 设置不可编辑

    def init(self, hardware, logger):
        self.setHead('Order', 'Step', 'Action', 'Args')
        self.hardware= hardware
        self.logger= logger
        self.show_order= -1  # '-1': 比0 小即可

    @showCall
    def refresh(self):
        self._showLog()
        self.resizeColumnsToContents()

    def _showLog(self):  # FIXME 排序后追加会有问题
        if self.logger:
            # records= self.logger(hardware=self.hardware, order= lambda order:self.show_order<order)
            # self.setRowCount( self.rowCount() + len(records) )
            # for record in records:
            #     self.insertRow( 0 )
            #     self.setRow( 0, '%08X'%(record['order']), '%010d'%(record['time']), record['action'], record['args'] )
            #     self.show_order= max(self.show_order, record['order'])

            # records= self.logger(hardware=self.hardware)
            # self.setRowCount(len(records))
            # for row, record in enumerate(records):
            #     self.setRow( row, '%08X'%(record['order']), '%010d'%(record['time']), record['action'], record['args'] )
            pass

