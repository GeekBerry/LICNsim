from collections import defaultdict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from gui.common import HotColor, DeepColor
from common import threshold
from debug import showCall


class Painter:
    def __init__(self):
        self.node_style= defaultdict( lambda:{'size':0.5, 'color':Qt.white, 'text':'', 'show_text':False} )
        self.edge_style= defaultdict( lambda:{'width': 0.0, 'color':Qt.lightGray, 'text':'', 'show_text':False} )

    def install(self, announces, api):
        self.announces= announces
        self.api= api

    def getStyleDict(self)->dict:
        return dict()


# ======================================================================================================================
class PropertyPainter(Painter):
    def getStyleDict(self)->dict:  # XXX 粗暴的进行全盘渲染, TODO cache
        self._calculate( self.api['Topo.nodeIds'](), self.api['Topo.edgeIds']() )
        return {
            'back_ground_color': Qt.white,
            'node_style': self.node_style,
            'edge_style': self.edge_style
        }

    @showCall
    def _calculate(self, node_ids, edge_ids):  # FIXME 将计算与渲染分离
        # 计算, 绘制, 渲染节点
        for node_id in node_ids:
            icn_node= self.api['ICNNet.getNode'](node_id)
            assert icn_node is not None  # DEBUG

            text= ''
            cs_unit= icn_node.units.get('cs', None)
            if cs_unit is not None:
                self.node_style[node_id]['size']= cs_unit.capacity / 100  # FIXME
                text+= f'CS容量:{cs_unit.capacity}\n'

            buffer_unit= icn_node.units.get('buffer', None)
            if buffer_unit is not None:
                self.node_style[node_id]['color']= DeepColor(buffer_unit.rate/100)  # FIXME
                text+= f'处理能力:{buffer_unit.rate}'

            self.node_style[node_id]['text']= text

        # 计算, 绘制, 渲染边
        for src_id, dst_id in edge_ids:
            icn_edge= self.api['ICNNet.getEdge'](src_id, dst_id)
            assert icn_edge is not None  # DEBUG

            self.edge_style[ (src_id, dst_id) ]['width']= icn_edge.rate/10  # FIXME
            text = f'速率 {icn_edge.rate}\n'

            color= HotColor( threshold(0.0, icn_edge.delay/100, 1.0) ) # FIXME
            text += f'延迟 {icn_edge.delay}\n'

            color= DeepColor( 0.1+0.9*(1-icn_edge.loss), color)  # 0.1+0.9*loss 避免loss为0 时无颜色显示
            text += f'丢包率 {"%0.2f"%(icn_edge.loss*100)}%'

            self.edge_style[ (src_id, dst_id) ]['color']= color
            self.edge_style[ (src_id, dst_id) ]['show_text']= True
            self.edge_style[ (src_id, dst_id) ]['text']= text


# ======================================================================================================================
from core.name import Name
from module.Monitors import NameStateMonitor


class NameStatePainter(Painter):
    def __init__(self):
        super().__init__()
        self.show_name= Name('')

    def install(self, announces, api):
        super().install(announces, api)
        announces['selectedName'].append(self.selectedName)

    def selectedName(self, name):
        if name != self.show_name:
            self.show_name= name
            self.announces['painterUpdated'](self)

    def getStyleDict(self)->dict:
        self._calculate( self.api['Topo.nodeIds'](), self.api['Topo.edgeIds']() )
        return {
            'back_ground_color': QColor(255, 240, 240),
            'node_style': self.node_style,
            'edge_style': self.edge_style
        }

    def _calculate(self, node_ids, edge_ids):  # FIXME 将计算与渲染分离
        record= self.api['Monitor.getNameStateRecord'](self.show_name)
        assert isinstance(record, NameStateMonitor.Record)
        # 计算, 绘制, 渲染节点
        for node_id in node_ids:
            if node_id in record.store:
                color= Qt.red
                text= f'储存 {self.show_name}'
            elif node_id in record.pending:
                color= Qt.green
                text= f'等待 {self.show_name}'
            else:
                color= Qt.lightGray
                text= ''
            self.node_style[node_id]['color']= color
            self.node_style[node_id]['text']= text

        for edge_id in edge_ids:
            if edge_id in record.transfer:
                self.edge_style[edge_id]['color']= Qt.blue
                self.edge_style[edge_id]['text']= f'传输"{self.show_name}"中'
                self.edge_style[edge_id]['show_text']= True
            else:
                self.edge_style[edge_id]['color']= Qt.lightGray
                self.edge_style[edge_id]['text']= ''
                self.edge_style[edge_id]['show_text']= False
