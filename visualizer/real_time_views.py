from PyQt5.QtWidgets import QWidget
import numpy

from debug import showCall
from core.common import strPercent
from core import clock


class RealTimeView(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.last_calculate_time= clock.time()  # '-1' 一个不可能的时间

    @showCall
    def install(self, announces, api):
        announces['playSteps'].append(self.refresh)
        self.announces= announces
        self.api= api

    @showCall
    def refresh(self, steps=None):
        if self.isVisible():
            if self.last_calculate_time < clock.time():
                self._calculate()
                self.last_calculate_time= clock.time()
            self._paint()

    def _calculate(self): pass

    def _paint(self): pass


# ----------------------------------------------------------------------------------------------------------------------
from core.name import Name


class HitRatioRTV(RealTimeView):
    def __init__(self, parent):
        super().__init__(parent)
        from visualizer.ui.hit_ratio_RTV import Ui_hit_ratio_RTV
        self.ui= Ui_hit_ratio_RTV()
        self.ui.setupUi(self)

        self.show_name= Name('')
        self._paintTitle()

    def install(self, announces, api):
        super().install(announces, api)
        announces['selectedName'].append(self.setShowName)

    @showCall
    def setShowName(self, show_name):  # XXX
        if self.show_name != show_name:
            self.show_name= show_name
            self._paintTitle()
            self._paint()

    def _paintTitle(self):
        self.ui.title.setText(f'Name "{self.show_name}" 命中率图')

    @showCall
    def _paint(self):
        indexs, values= self.api['NameHitRatioMonitor::nameSegmZip'](self.show_name)
        self.ui.canvas.drawPolyLine( indexs, values, 'r')
        if values:
            self.ui.cur_ratio.setText( strPercent(values[-1]) )

        indexs, values= self.api['NameHitRatioMonitor::nameAccumZip'](self.show_name)
        self.ui.canvas.drawPolyLine( indexs, values, 'b', clear=False)
        if values:
            self.ui.avg_ratio.setText( strPercent(values[-1]) )


# ----------------------------------------------------------------------------------------------------------------------


class FlowRTV(RealTimeView):
    def __init__(self, parent):
        super().__init__(parent)
        from visualizer.ui.flow_RTV import Ui_flow_RTV
        self.ui= Ui_flow_RTV()
        self.ui.setupUi(self)

        self.show_name= Name('')
        self._paintTitle()

    def install(self, announces, api):
        super().install(announces, api)
        announces['selectedName'].append(self.setShowName)

    @showCall
    def setShowName(self, show_name):  # XXX
        if self.show_name != show_name:
            self.show_name= show_name
            self._paintTitle()
            self._paint()

    def _paintTitle(self):
        self.ui.title.setText(f'Name "{self.show_name}" 流量图')

    def _paint(self):
        indexs, num_counts, size_counts = self.api['FlowMonitor::nameSegmZip'](self.show_name)  #  DEBUG
        accum_indexs, accum_num_counts, accum_size_counts = self.api['FlowMonitor::nameAccumZip'](self.show_name)  #  DEBUG

        self.ui.num_canvas.drawPolyLine(indexs, num_counts)
        if num_counts:
            self.ui.segm_num.setText( str(num_counts[-1]) )

        self.ui.num_canvas.drawTwinX(indexs, accum_num_counts)
        if accum_num_counts:
            self.ui.accum_num.setText( str(accum_num_counts[-1]) )

        self.ui.size_canvas.drawPolyLine(indexs, size_counts)
        if size_counts:
            self.ui.segm_size.setText( str(size_counts[-1]) )

        self.ui.size_canvas.drawTwinX(indexs, accum_size_counts)
        if accum_num_counts:
            self.ui.accum_size.setText( str(accum_size_counts[-1]) )






