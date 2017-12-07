from collections import defaultdict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap

from config import *
from core import threshold, normalizeINF, strPercent, Name
from gui import HotColor, DeepColor


class Painter:
    background_color = Qt.white

    def __init__(self, announces, api):
        self.announces = announces
        self.api = api
        self.visible = False  # 标记当前painter是否为当前渲染painter

    def pickUp(self):
        self.visible = True
        self.refresh()

    def putDown(self):
        self.visible = False

    def refresh(self):
        self.api['Scene.setBackgroundColor'](self.background_color)
        for node_id in self.api['Sim.nodes']():
            self.drawNode(node_id)
        for edge_id in self.api['Sim.edges']():
            self.drawEdge(edge_id)

    def drawNode(self, node_id):
        style = self.renderNode(node_id)
        self.api['Scene.renderNode'](node_id, style)

    def renderNode(self, node_id) -> dict:
        raise NotImplementedError

    def drawEdge(self, edge_id):
        style = self.renderEdge(edge_id)
        self.api['Scene.renderEdge'](edge_id, style)

    def renderEdge(self, edge_id) -> dict:
        # 默认线条类型
        return {
            'color': Qt.lightGray,
            'width': 0.5,
            'line': Qt.SolidLine,
            'show_arrow': False,
            'text': '',
            'show_text': False
        }


# ======================================================================================================================
class PropertyPainter(Painter):
    RED_DELAY = 25  # 当icn_edg 为 RED_DELAY 时, 边为红色
    background_color = QColor(240, 240, 240)

    def __init__(self, announces, api):
        super().__init__(announces, api)
        self.NODE_PIXMPA_TABLE = {
            'client': QPixmap(CLIENT_NDOE_IMAGE),
            'router': QPixmap(ROUTE_NDOE_IMAGE),
            'server': QPixmap(SERVER_NDOE_IMAGE),
        }

        self.LINE_STYLE_TABLE = {
            'wired': Qt.SolidLine,
            'wireless': Qt.DotLine,
        }

    def renderNode(self, node_id) -> dict:
        icn_node = self.api['Sim.node'](node_id)
        assert icn_node is not None

        size = 0.5
        text = ''
        shape = 'Pie'

        cs_unit = icn_node.units.get('cs', None)
        if cs_unit is not None:
            size = normalizeINF(cs_unit.capacity)
            text += f'CS 容量{cs_unit.capacity}\n'

        if hasattr(icn_node, 'pos'):
            x, y = icn_node.pos
            text += f'位置({round(x, 2)}, {round(y, 2)})\n'

        if hasattr(icn_node, 'node_type'):  # 根据 icn_node 类型决定图标
            shape = self.NODE_PIXMPA_TABLE[icn_node.node_type]

        return {
            'shape': shape,
            'color': Qt.white,
            'size': size,
            'text': text,
            'show_text': True
        }

    def renderEdge(self, edge_id):
        icn_edge = self.api['Sim.edge'](edge_id)
        assert icn_edge is not None  # DEBUG

        color = HotColor(threshold(0.0, icn_edge.delay / self.RED_DELAY, 1.0))
        color = DeepColor(1 - icn_edge.loss, color)

        width = normalizeINF(icn_edge.rate)

        line = Qt.SolidLine
        if hasattr(icn_edge, 'channel_type'):  # 根据 icn_edge 类型决定线段类型
            line = self.LINE_STYLE_TABLE[icn_edge.channel_type]

        text = f'速率 {icn_edge.rate}\n延迟 {icn_edge.delay}\n丢包率 {strPercent(icn_edge.loss)}'
        return {
            'color': color,
            'width': width,
            'show_arrow': True,
            'line': line,
            'text': text,
            'show_text': False
        }


# ======================================================================================================================
class NameStorePainter(Painter):
    background_color = QColor(255, 220, 220)
    name_table = None

    EMPTY_COLOR = Qt.lightGray
    STORE_COLOR = TRANS_D_COLOR = QColor(255, 0, 0)
    WEAK_STORE_COLOR = WEAK_TRANS_D_COLOR = QColor(255, 200, 200)
    PEND_COLOR = TRANS_I_COLOR = QColor(0, 255, 0)
    WEAK_PEND_COLOR = WEAK_TRANS_I_COLOR = QColor(200, 255, 200)

    def __init__(self, announces, api):
        super().__init__(announces, api)

        self.show_name = Name()
        announces['selectedName'].append(self._selectedName)

    def _selectedName(self, name):
        if name != self.show_name:
            self.show_name = name
            if self.visible:
                self.refresh()

    def refresh(self):
        self.name_table = self.api['NameMonitor.table']()
        if self.name_table is not None:
            self.prepareColor()
            super().refresh()
            # else 没有安装 NameMonitor ？？？  TODO raise something

    def prepareColor(self):
        self.nodes_color = defaultdict(lambda: self.EMPTY_COLOR)  # {node_id:color, ...}
        self.edges_color = defaultdict(lambda: self.EMPTY_COLOR)  # {edge_id:color, ...}
        # 先描绘请求情况
        for sub_name in self.name_table.forebear(self.show_name):  # 对于兴趣包，查找前缀
            record = self.name_table[sub_name]
            for node_id in record.pending:
                self.nodes_color[node_id] = self.PEND_COLOR if (sub_name == self.show_name) else self.WEAK_PEND_COLOR

            for edge_id in record.trans_i:
                self.edges_color[edge_id] = self.TRANS_I_COLOR if (
                sub_name == self.show_name) else self.WEAK_TRANS_I_COLOR
        # 后描绘数据情况，以覆盖同请求相交的部分
        for sub_name in self.name_table.descendant(self.show_name):  # 对于数据包，查找后缀
            record = self.name_table[sub_name]
            for node_id in record.store:
                self.nodes_color[node_id] = self.STORE_COLOR if (sub_name == self.show_name) else self.WEAK_STORE_COLOR

            for edge_id in record.trans_d:
                self.edges_color[edge_id] = self.TRANS_D_COLOR if (
                sub_name == self.show_name) else self.WEAK_TRANS_D_COLOR
        return True

    def renderNode(self, node_id) -> dict:
        return {
            'shape': 'Pie',
            'color': self.nodes_color[node_id],
            'size': 0.5,
            'text': '',
            'show_text': False
        }

    def renderEdge(self, edge_id) -> dict:
        color = self.edges_color[edge_id]
        return {
            'color': color,
            'width': 0.5,
            'show_arrow': bool(color is not self.EMPTY_COLOR),
            'text': '',
            'show_text': False
        }


# ======================================================================================================================
class HitRatioPainter(Painter):
    node_table = None
    background_color = QColor(220, 255, 220)

    def refresh(self):
        self.node_table = self.api['NodeMonitor.table']()
        if self.node_table is not None:
            super().refresh()
            # else 没有安装 NodeMonitor ？？？ TODO raise something

    def renderNode(self, node_id) -> dict:
        record = self.node_table[node_id]
        ratio = record.hitRatio()
        color = HotColor(ratio)
        text = f'命中率: {strPercent(ratio)}'

        return {
            'shape': 'Pie',
            'color': color,
            'size': 0.5,
            'text': text,
            'show_text': True
        }


# ======================================================================================================================
class OccupyPainter(Painter):
    background_color = QColor(220, 220, 255)

    def refresh(self):
        self.node_table = self.api['NodeMonitor.table']()
        self.edge_table = self.api['EdgeMonitor.table']()
        if (self.node_table is not None) and (self.edge_table is not None):
            super().refresh()
            # else 没有安装 NodeMonitor 或 EdgeMonitor ？？？ TODO raise something

    def renderNode(self, node_id) -> dict:
        record = self.node_table[node_id]
        occupy = record.forwardOccupy()

        if occupy > 1.0 or occupy < 0:
            print(node_id, occupy)

        color = HotColor(occupy)
        text = f'占用率: {strPercent(occupy)}'

        return {
            'shape': 'Rect',
            'color': color,
            'size': 0.5,
            'text': text,
            'show_text': True
        }

    def renderEdge(self, edge_id) -> dict:
        record = self.edge_table[edge_id]
        occupy = record.sendOccupy()
        color = HotColor(occupy)
        text = f'占用率: {strPercent(occupy)}'
        return {
            'color': color,
            'width': 0.5,
            'show_arrow': True,
            'text': text,
            'show_text': False
        }
