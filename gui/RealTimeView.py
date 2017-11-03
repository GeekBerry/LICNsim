from PyQt5.QtWidgets import QWidget

from core import clock, Name
from gui.common import UIFrom
from gui.ui.flow_rtv import Ui_flow_rtv


@UIFrom(Ui_flow_rtv)
class FlowRTV(QWidget):  # TODO 添加 cache
    SIZE = 20
    SCALE_MAP = (1, 10, 100, 1000)  # 对应 scale_slider 的格子
    FIELD= {'数量(Number)': 'p_num', '尺寸(Size)': 'p_size'}

    def __init__(self, parent):  # FIXME 用了 UIFrom 就必须要写 __init__ (哪怕什么也不执行), 否则 canvas 无法正确绘制, 为何???
        self.show_name = Name()
        self.db_table= None

        self.ui.mode_combo.addItems( self.FIELD.items() )
        self.ui.mode_combo.currentIndexChanged.connect( lambda *args:self.refresh() )

        assert isinstance(self.ui, Ui_flow_rtv)
        self.ui.scale_slider.wheelEvent = lambda *args: None  # 禁用鼠标滚轮
        self.ui.scale_slider.valueChanged.connect(self._valueChangedSlot)
        self.ui.scale_slider.setValue(1)  # SCALE_MAP[1] == 10  以此激活 self._valueChangedSlot 来设置 self.scale

    def install(self, announces, api):
        self.db_table = api['DB.table']('flow_t')
        announces['playSteps'].append(self.playSteps)
        announces['selectedName'].append(self.selectedName)

    def selectedName(self, name):
        if name != self.show_name:
            self.show_name = name
            self.refresh()

    def playSteps(self, steps):
        if self.isVisible():
            self.refresh()

    def refresh(self):
        if self.db_table is None:  # 数据库还未连接
            return
        # 计算值
        text= self.ui.mode_combo.currentText()
        field= self.ui.mode_combo.currentData()

        indexs= self.calculateIndexs()
        values= self.reduceField(indexs, field, self.show_name)
        # 显示工作
        self.ui.name_label.setText( repr(self.show_name) )  # 显示前缀
        self.ui.canvas.drawPolyLine(indexs, values)
        self.ui.note_label.setText( f'{text}: {values[-1]}' )

    def calculateIndexs(self):
        # 计算下标  FIXME 下标和拉取范围计算有点问题
        last_i = clock.time() // self.scale
        indexs = [(last_i - i + 1) * self.scale for i in range(self.SIZE, 0, -1)]  # 获得下标的终点
        return indexs

    def reduceField(self, indexs, field, prefix):  # 在数据库中拉取 indexs 对应的数据
        values= []
        for i in indexs:
            records= self.db_table.query( time=lambda t: i-self.scale < t <= i, p_name=lambda name: prefix.isPrefix(name) )

            value= 0
            for record in records:
                value += record[field]
            values.append(value)

        return values

    # -------------------------------------------------------------------------
    def _valueChangedSlot(self, value):
        self.scale = self.SCALE_MAP[value]
        self.ui.scale_label.setText( str(self.scale) )
        self.refresh()
