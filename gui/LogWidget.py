from core import clock
from gui.common import TableWidget


class LogTableWidget(TableWidget):
    ORDER, TIME, ID, OPERATE, DESTINATION, P_HEAD= range(0, 6)
    HEADS= ('Order', 'Time', 'ID', 'Operate', 'Destination', 'PacketHead')

    def init(self):
        self.setHeads('Order', 'Time', 'ID', 'Operate', 'Destination', 'PacketHead')

    def setRecords(self, records):
        self.setSortingEnabled(False)

        self.clearContents()
        self.setRowCount(len(records))
        for row, record in enumerate( reversed(records) ):  # reversed 逆 Order 序
            self.setRow(row, record['order'], record['time'], record['id'], record['operate'], record['dst'], record['p_head'])

        self.setSortingEnabled(True)


# ======================================================================================================================
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt

from gui.common import UIFrom
from gui.ui.log_widget import Ui_log_table


@UIFrom(Ui_log_table)
class LogWidget(QWidget):
    ALL_COMBO_TEXT= '...all...'

    def __init__(self, parent):
        self.last_play_time= 0
        self.db_table= None

        assert isinstance(self.ui, Ui_log_table)
        self.ui.refresh_button.clicked.connect(self._refreshClickedSlot)

        self.ui.id_combo.addItem(self.ALL_COMBO_TEXT, None)
        self.ui.operate_combo.addItem(self.ALL_COMBO_TEXT, None)
        self.ui.packet_combo.addItem(self.ALL_COMBO_TEXT, None)

        self.ui.table.init()  # 一些需要在UIFrom.setupUi后执行的初始化
        self.ui.table.cellDoubleClicked.connect(self._cellDoubleClickedSlot)

    def install(self, announces, api):
        self.db_table= api['DB.table']('log_t')
        announces['playSteps'].append(self.playSteps)

    def playSteps(self, steps):
        cur_time= clock.time()

        if self.isVisible():
            self.ui.time_start_box.setValue(self.last_play_time)
            self.ui.time_end_box.setValue(cur_time)

            if self.ui.refresh_check.checkState() == Qt.Checked:
                self.refresh()

        self.last_play_time= cur_time

    def refresh(self):
        assert self.db_table is not None

        condition= self._loadCondition()
        records = list( self.db_table.query(**condition) )
        self.ui.table.setRecords(records)
        self.ui.num_label.setText(  str( len(records) )  )

    # -------------------------------------------------------------------------
    def _loadCondition(self):  # TODO 重构
        condition= {}
        # 设置时间范围条件
        time_start= self.ui.time_start_box.value()
        time_end= self.ui.time_end_box.value()
        condition['time']= lambda t: time_start <= t <= time_end

        # 设置 Operate 条件
        data= self.ui.operate_combo.currentData()
        if data is not None:
            condition['operate']= data
        # 设置 ID 条件
        data= self.ui.id_combo.currentData()
        if data is not None:
            condition['id']= data
        # 设置 PacketHead 条件
        data= self.ui.packet_combo.currentData()
        if data is not None:
            condition['p_head']= data

        return condition

    def _refreshClickedSlot(self, bool=False):
        self.refresh()

    def _cellDoubleClickedSlot(self, row, col):  # TODO 重构
        if col == self.ui.table.ID:
            text= self.ui.table.getCellText(row, col)
            data= self.ui.table.getCellData(row, col)
            index= self.ui.id_combo.addItem(text, data)
            self.ui.id_combo.setCurrentIndex(index)
        elif col == self.ui.table.OPERATE:
            text= self.ui.table.getCellText(row, col)
            data= self.ui.table.getCellData(row, col)
            index= self.ui.operate_combo.addItem(text, data)
            self.ui.operate_combo.setCurrentIndex(index)
        elif col == self.ui.table.P_HEAD:
            text= self.ui.table.getCellText(row, col)
            data= self.ui.table.getCellData(row, col)
            index= self.ui.packet_combo.addItem(text, data)
            self.ui.packet_combo.setCurrentIndex(index)

