
from PyQt5.QtCore import QRectF, Qt, QObject
from PyQt5.QtGui import QPainter, QBrush, QColor

from collections import defaultdict

from debug import showCall
from core import clock
from core.icn_net import ICNNetHelper
from visualizer.ui_net import UINetHelper
from visualizer.common import HotColor, DeepColor, threshold, TransferRecordToText


class Painter:
    graph= None
    monitor= None

    def __init__(self, title):
        self.title= title
        self.paint_dict= None

    def install(self, announces, api):
        self.announces= announces
        self.api= api

    def paint(self):
        pass

    def update(self):  # 计算paint_dict
        pass


# -----------------------------------------------------------------------------
class NodePainter(Painter):
    def __init__(self, title, back_ground):
        super().__init__(title)
        self.back_ground_color= back_ground
        self.paint_dict= defaultdict( lambda: {'size':0.5, 'color':Qt.white, 'text':''} )


class NodePropertyPainter(NodePainter):
    def __init__(self):
        super().__init__('性能图', Qt.white)
        self.is_node_property_changed= True

    @showCall
    def paint(self):
        for node_name, ui_node in UINetHelper.nodeItems(self.graph):
            entry= self.paint_dict[node_name]
            ui_node.setSize( entry['size'] )
            ui_node.setColor( entry['color'] )
            ui_node.setText( entry['text'] )

    @showCall
    def update(self):
        if self.is_node_property_changed:
            self.calculate()
            self.is_node_property_changed= False

    @showCall
    def calculate(self):
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
class NameStorePainter(NodePainter):
    def __init__(self):
        super().__init__('缓存分布图', QColor(255, 240, 240))
        self.show_name= None
        self.is_name_changed= False
        self.last_calculate_time= -1  # '-1': 一个不可能的时间即可

    def install(self, announces, api):
        super().install(announces, api)
        announces['selectedName'].append(self.setShowName)

    def setShowName(self, show_name):  # XXX
        if self.show_name != show_name:
            self.show_name= show_name
            self.is_name_changed= True

        self.title= f'"{self.show_name}" 缓存分布图'
        self.api['NetView::triggerPainter'](self)

    @showCall
    def paint(self):
        for node_name, entry in self.paint_dict.items():
            ui_node= UINetHelper.node(self.graph, node_name)
            ui_node.setColor( entry['color'] )

    @showCall
    def update(self):
        if self.is_name_changed or self.last_calculate_time != clock.time():
            self.calculate()
            self.is_name_changed= False
            self.last_calculate_time= clock.time()

    @showCall
    def calculate(self):
        # TODO match 或 前缀查找等
        contents= self.monitor.contents.get(self.show_name, [])  # [NodeName, ...]

        for node_name in self.graph.nodes():  # clear
            self.paint_dict[node_name]['color']= Qt.white

        for node_name in contents:
            self.paint_dict[node_name]['color']= Qt.red


class HitRatioPainter(NodePainter):
    def __init__(self):
        super().__init__('命中率图', QColor(240, 255, 240))
        self.hit_miss_table= defaultdict( lambda:{'hit':0, 'miss':0})
        self.last_calculate_time= -1  # '-1': 比0小即可

    @showCall
    def paint(self):
        for node_name, ui_node in UINetHelper.nodeItems(self.graph):
            entry= self.paint_dict[node_name]
            ui_node.setColor( entry['color'] )
            ui_node.setText( entry['text'] )

    @showCall
    def update(self):
        if self.last_calculate_time < clock.time():
            self.calculate()
            self.last_calculate_time= clock.time()

    @showCall
    def calculate(self):
        records= self.monitor.node_t(time= lambda t: self.last_calculate_time < t <= clock.time())
        # 统计新增记录
        for node_record in records:
            node_name= node_record['node_name']
            self.hit_miss_table[node_name]['hit'] += node_record['hit']
            self.hit_miss_table[node_name]['miss'] += node_record['miss']

        for node_name, entry in self.hit_miss_table.items():  # FIXME 这段代码应该放在哪儿
            visits= entry['hit'] + entry['miss']
            ratio= entry['hit']/visits if visits else 0.0
            self.paint_dict[node_name]['color']= HotColor(ratio)
            self.paint_dict[node_name]['text']= f'命中率 {"%0.2f"%(ratio*100)}%'

# ======================================================================================================================
from core.channel import Channel


class EdgePainter(Painter):
    def __init__(self, title):
        super().__init__(title)
        self.paint_dict= defaultdict( lambda: {'width': 0.0, 'color':Qt.lightGray, 'text':''} )


class EdgesPropertyPainter(EdgePainter):
    def __init__(self):
        super().__init__('性能图')
        self.is_edge_property_changed= True

    @showCall
    def paint(self):
        for edge_name, ui_edge in UINetHelper.edgeItems(self.graph):
            entry= self.paint_dict[edge_name]
            ui_edge.setWidth( entry['width'] )
            ui_edge.setColor( entry['color'] )
            ui_edge.setText( entry['text'] )
            ui_edge.showText()

    @showCall
    def update(self):
        if self.is_edge_property_changed:
            self.calculate()
            self.is_edge_property_changed= False

    @showCall
    def calculate(self):
        for edge_name, icn_edge in ICNNetHelper.edgeItems(self.graph):
            assert isinstance(icn_edge, Channel)
            text= ''
            self.paint_dict[edge_name]['width']= icn_edge.rate/10  # FIXME
            text += f'速率 {icn_edge.rate}\n'

            color= HotColor( threshold(0.0, icn_edge.delay/100, 1.0) ) # FIXME
            text += f'延迟 {icn_edge.delay}\n'

            color= DeepColor( 0.1+0.9*(1-icn_edge.loss), color)  # 0.1+0.9*loss 避免loss为0 时无颜色显示
            text += f'丢包率 {"%0.2f"%(icn_edge.loss*100)}%'

            self.paint_dict[edge_name]['color']= color
            self.paint_dict[edge_name]['text']= text


class RatePainter(EdgePainter):
    DELTA_TIME= 1000.0  # FIXME

    def __init__(self):
        super().__init__('占用率图')
        self.last_calculate_time= -1  # '-1': 比0小即可

    @showCall
    def paint(self):
        for edge_name, ui_edge in UINetHelper.edgeItems(self.graph):
            entry= self.paint_dict[edge_name]
            ui_edge.setColor( entry['color'] )
            ui_edge.setText( entry['text'] )
            ui_edge.showText()

    @showCall
    def update(self):
        if self.last_calculate_time < clock.time():
            self.calculate()
            self.last_calculate_time= clock.time()

    @showCall
    def calculate(self):
        t0, t1= clock.time()-self.DELTA_TIME, clock.time()
        records= self.monitor.transfer_t(begin= lambda t: t < t1, end= lambda t: t0 < t )
        # 统计忙碌时长
        occupy_dict= defaultdict(lambda: 0.0)
        for record in records:
            edge_name= ( record['src'], record['dst'] )
            occupy_dict[edge_name] += min(t1, record['end']) - max(t0, record['begin'])  # 计算在t0~t1时间内信道占用时长

        for edge_name in occupy_dict:
            ratio= occupy_dict.get(edge_name, 0.0) / self.DELTA_TIME
            self.paint_dict[edge_name]['color']= HotColor(ratio)
            self.paint_dict[edge_name]['text']= f'占用率 {"%0.2f"%(ratio*100)}%'

















