
from PyQt5.QtCore import QRectF, Qt, QObject
from PyQt5.QtGui import QPainter, QBrush, QColor

from collections import defaultdict

from debug import showCall
from core import clock
from common import strPercent
from core.icn_net import ICNNetHelper
from visualizer.ui_net import UINetHelper
from visualizer.common import HotColor, DeepColor, threshold, TransferRecordToText


class Painter:
    graph= None
    monitor= None
    paint_dict= {}

    def __init__(self):
        self.style= {}

    def install(self, announces, api):
        self.announces= announces
        self.api= api

    def refresh(self):  # 计算paint_dict
        pass

    def _paint(self):
        pass


# -----------------------------------------------------------------------------
class NodePainter(Painter):
    def __init__(self):
        super().__init__()
        self.paint_dict= defaultdict( lambda: {'size':0.5, 'color':Qt.white, 'text':''} )

    @showCall
    def _paint(self):
        for node_name, ui_node in UINetHelper.nodeItems(self.graph):
            entry= self.paint_dict[node_name]
            ui_node.setSize( entry['size'] )
            ui_node.setColor( entry['color'] )
            ui_node.setText( entry['text'] )


class NodePropertyPainter(NodePainter):
    def __init__(self):
        super().__init__()
        self.style['title']= '性能图'
        self.style['back_ground_color']= Qt.white
        self.is_property_changed= True

    def install(self, announces, api):
        super().install(announces, api)
        announces['NodeDialogClose'].append( self.propertyChanged )  # 只要窗口关闭,都视为对property有所修改

    @showCall
    def propertyChanged(self, *args):
        self.is_property_changed= True
        self.api['NetView::refreshPainter'](self)

    @showCall
    def refresh(self):
        super().refresh()
        if self.is_property_changed:
            self._calculate()
            self.is_property_changed= False
        self._paint()

    @showCall
    def _calculate(self):
        for node_name, icn_node in ICNNetHelper.nodeItems(self.graph):
            text= ''

            cs_unit= icn_node.units.get('cs', None)
            if cs_unit is not None:
                self.paint_dict[node_name]['size']= cs_unit.capacity / 100  # FIXME
                text+= f'CS容量:{cs_unit.capacity}\n'

            buffer_unit= icn_node.units.get('buffer', None)
            if buffer_unit is not None:
                self.paint_dict[node_name]['color']= DeepColor(buffer_unit.rate/100)  # FIXME
                text+= f'处理能力:{buffer_unit.rate}'

            self.paint_dict[node_name]['text']= text


# -----------------------------------------------------------------------------
from core.name import Name


class NameStorePainter(NodePainter):
    def __init__(self):
        super().__init__()
        self.style['title']= '缓存分布图'
        self.style['back_ground_color']= QColor(255, 240, 240)

        self.show_name= Name('')
        self.is_name_changed= False
        self.last_calculate_time= -1  # '-1': 一个不可能的时间即可

    def install(self, announces, api):
        super().install(announces, api)
        announces['selectedName'].append(self.setShowName)

    @showCall
    def setShowName(self, show_name):
        if self.show_name != show_name:
            self.show_name= show_name
            self.is_name_changed= True
            self.style['title']= f'"{self.show_name}" 缓存分布图'
            self.api['NetView::refreshPainter'](self)

    @showCall
    def refresh(self):
        super().refresh()
        if self.is_name_changed or self.last_calculate_time != clock.time():
            self._calculate()
            self.is_name_changed= False
            self.last_calculate_time= clock.time()
        self._paint()

    @showCall
    def _calculate(self):
        record= self.api['NodeStateMonitor::getNameStates'](self.show_name)

        for node_name in self.graph.nodes():
            if node_name in record.store:
                color= Qt.red
            elif node_name in record.pending:
                color= Qt.green
            else:
                color= Qt.lightGray

            self.paint_dict[node_name]['color']= color


class HitRatioPainter(NodePainter):
    def __init__(self):
        super().__init__()
        self.style['title']= '命中率图'
        self.style['back_ground_color']= QColor(240, 255, 240)

        self.hit_miss_table= defaultdict(lambda: {'hit': 0, 'miss': 0})
        self.last_calculate_time= -1  # '-1': 比0小即可

    @showCall
    def refresh(self):
        super().refresh()
        if self.last_calculate_time < clock.time():
            self._calculate()
            self.last_calculate_time= clock.time()
        self._paint()

    @showCall
    def _calculate(self):
        for node_name in self.graph.nodes():
            ratio= self.api['NameHitRatioMonitor::nodeRatio'](node_name)
            self.paint_dict[node_name]['color']= HotColor(ratio)
            self.paint_dict[node_name]['text']= f'命中率 {strPercent(ratio)}'


# ======================================================================================================================
from core.channel import Channel


class EdgePainter(Painter):
    def __init__(self):
        super().__init__()
        self.paint_dict= defaultdict( lambda: {'width': 0.0, 'color':Qt.lightGray, 'text':''} )

    @showCall
    def _paint(self):
        for edge_name, ui_edge in UINetHelper.edgeItems(self.graph):
            entry= self.paint_dict[edge_name]
            ui_edge.setWidth( entry['width'] )
            ui_edge.setColor( entry['color'] )
            ui_edge.setText( entry['text'] )
            ui_edge.showText()


class EdgesPropertyPainter(EdgePainter):
    def __init__(self):
        super().__init__()
        self.style['title']= '性能图'
        self.is_property_changed= True

    def install(self, announces, api):
        super().install(announces, api)
        announces['EdgeDialogClose'].append( self.propertyChanged )  # 只要窗口关闭,都视为对property有所修改

    def propertyChanged(self, *args):
        self.is_property_changed= True
        self.api['NetView::refreshPainter'](self)

    @showCall
    def refresh(self):
        if self.is_property_changed:
            self._calculate()
            self.is_property_changed= False
        self._paint()

    @showCall
    def _calculate(self):
        for edge_name, icn_edge in ICNNetHelper.edgeItems(self.graph):
            assert isinstance(icn_edge, Channel)

            self.paint_dict[edge_name]['width']= icn_edge.rate/10  # FIXME
            text = f'速率 {icn_edge.rate}\n'

            color= HotColor( threshold(0.0, icn_edge.delay/100, 1.0) ) # FIXME
            text += f'延迟 {icn_edge.delay}\n'

            color= DeepColor( 0.1+0.9*(1-icn_edge.loss), color)  # 0.1+0.9*loss 避免loss为0 时无颜色显示
            text += f'丢包率 {"%0.2f"%(icn_edge.loss*100)}%'

            self.paint_dict[edge_name]['color']= color
            self.paint_dict[edge_name]['text']= text


class RatePainter(EdgePainter):
    DELTA_TIME= 1000.0  # FIXME

    def __init__(self):
        super().__init__()
        self.style['title']= '占用率图'
        self.last_calculate_time= -1  # '-1': 比0小即可

    @showCall
    def refresh(self):
        if self.last_calculate_time < clock.time():
            self._calculate()
            self.last_calculate_time= clock.time()
        self._paint()

    @showCall
    def _calculate(self):
        # t0, t1= clock.time()-self.DELTA_TIME, clock.time()
        # records= self.monitor.transfer_t(begin= lambda t: t < t1, end= lambda t: t0 < t )
        # # 统计忙碌时长
        # occupy_dict= defaultdict(lambda: 0.0)
        # for record in records:
        #     edge_name= ( record['src'], record['dst'] )
        #     occupy_dict[edge_name] += min(t1, record['end']) - max(t0, record['begin'])  # 计算在t0~t1时间内信道占用时长
        #
        # for edge_name in occupy_dict:
        #     ratio= occupy_dict.get(edge_name, 0.0) / self.DELTA_TIME
        #     self.paint_dict[edge_name]['color']= HotColor(ratio)
        #     self.paint_dict[edge_name]['text']= f'占用率 {"%0.2f"%(ratio*100)}%'
        pass














