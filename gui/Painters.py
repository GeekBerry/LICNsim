from collections import defaultdict

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from core import threshold, normalizeINF, strPercent
from debug import showCall
from gui.common import HotColor, DeepColor


class Painter:
    """
    style_dict
    {
        'back_ground_color':背景颜色,

        'node_style':
        {
            node_id:
            {
                'size':     float节点尺寸(0.0~1.0),
                'color':    节点颜色,
                'text':     str,
                'show_text':bool,
            },
            ...
        },

        'edge_style':
        {
            (src_id, dst_id):
            {
                'width':    float(0.0~1.0),
                'color':    线条颜色,
                'text':     str,
                'show_text':bool
            },
            ...
        },
    }
    """

    def __init__(self):
        self.back_ground_color= Qt.white
        self.node_style= defaultdict( lambda:{'size':0.5, 'color':Qt.white, 'text':'', 'show_text':False} )
        self.edge_style= defaultdict( lambda:{'width': 0.0, 'color':Qt.lightGray, 'text':'', 'show_text':False} )

    def install(self, announces, api):
        self.announces= announces
        self.api= api

    def getStyleDict(self, node_ids, edge_ids)->dict:
        self._calculate(node_ids, edge_ids)
        return {
            'back_ground_color': self.back_ground_color,
            'node_style': self.node_style,
            'edge_style': self.edge_style
        }

    @NotImplementedError
    def _calculate(self, node_ids, edge_ids):
        # XXX 粗暴的进行全盘渲染, TODO cache
        pass

# ======================================================================================================================

class PropertyPainter(Painter):
    @showCall
    def _calculate(self, node_ids, edge_ids):  # FIXME 将计算与渲染分离
        # 计算, 绘制, 渲染节点
        for node_id in node_ids:
            icn_node= self.api['Sim.getNode'](node_id)
            text= ''

            # SIZE
            cs_unit= icn_node.units.get('cs', None)
            if cs_unit is not None:
                capacity= cs_unit.capacity
                text+= f'CS 容量{capacity}\n'
            else:
                capacity= 0.0

            self.node_style[node_id]['text']= text
            self.node_style[node_id]['size']= normalizeINF(capacity)

        # 计算, 绘制, 渲染边
        for src_id, dst_id in edge_ids:
            icn_edge= self.api['Sim.getEdge'](src_id, dst_id)
            assert icn_edge is not None  # DEBUG

            self.edge_style[ (src_id, dst_id) ]['width']= normalizeINF(icn_edge.rate)
            text = f'速率 {icn_edge.rate}\n'

            color= HotColor( threshold(0.0, icn_edge.delay/100, 1.0) )
            text += f'延迟 {icn_edge.delay}\n'

            color= DeepColor( 0.1+0.9*(1-icn_edge.loss), color)  # 0.1+0.9*loss 避免loss为0 时无颜色显示
            text += f'丢包率 {strPercent(icn_edge.loss)}'

            self.edge_style[ (src_id, dst_id) ]['color']= color
            self.edge_style[ (src_id, dst_id) ]['show_text']= True
            self.edge_style[ (src_id, dst_id) ]['text']= text


# ======================================================================================================================
from core import Name


class NameStorePainter(Painter):
    EMPTY_COLOR= Qt.lightGray

    STORE_COLOR= QColor(255, 0, 0)
    WEAK_STORE_COLOR= QColor(255, 200, 200)

    PEND_COLOR= QColor(0, 255, 0)
    WEAK_PEND_COLOR= QColor(200, 255, 200)

    TRANSFER_COLOR= QColor(0, 0, 255)
    WEAK_TRANSFER_COLOR= QColor(200, 200, 255)

    def __init__(self):
        super().__init__()
        self.back_ground_color= QColor(255, 240, 240)
        self.show_name= Name()

    def install(self, announces, api):
        super().install(announces, api)
        announces['selectedName'].append(self.selectedName)

    def selectedName(self, name):
        if name != self.show_name:
            self.show_name= name
            self.announces['updatePainter'](self)

    def _calculate(self, node_ids, edge_ids):  # FIXME 将计算与渲染分离  TODO
        name_table= self.api['NameMonitor.table']()

        node_dict= dict.fromkeys(node_ids, self.EMPTY_COLOR)
        edge_dict= dict.fromkeys(edge_ids, self.EMPTY_COLOR)

        for sub_name in name_table.forebear(self.show_name):
            record = name_table[sub_name]
            for node_id in record.pending:
                node_dict[node_id] = self.PEND_COLOR if (sub_name == self.show_name) else self.WEAK_PEND_COLOR

            for edge_id in record.transfer:
                edge_dict[edge_id]= self.TRANSFER_COLOR if  (sub_name == self.show_name) else self.WEAK_TRANSFER_COLOR

        for sub_name in name_table.descendant(self.show_name):
            record= name_table[sub_name]
            for node_id in record.store:
                node_dict[node_id]= self.STORE_COLOR if (sub_name == self.show_name) else self.WEAK_STORE_COLOR

            for edge_id in record.transfer:
                edge_dict[edge_id]= self.TRANSFER_COLOR if (sub_name == self.show_name) else self.WEAK_TRANSFER_COLOR

        # ---------------------------------------------------------------------
        for node_id, color in node_dict.items():
            self.node_style[node_id]['color']= color

        for edge_id, color in edge_dict.items():
            self.edge_style[edge_id]['color']= color
            self.edge_style[edge_id]['show_text']= False if (color is self.EMPTY_COLOR) else True



# ======================================================================================================================
# from module import NodeHitMonitor
# from core import strPercent
#
#
# class NodeHitPainter(Painter):
#     def getStyleDict(self)->dict:
#         self._calculate( self.api['Topo.nodeIds'](), self.api['Topo.edgeIds']() )
#         return {
#             'back_ground_color': QColor(240, 255, 240),
#             'node_style': self.node_style,
#             'edge_style': self.edge_style
#         }
#
#     def _calculate(self, node_ids, edge_ids):  # FIXME 将计算与渲染分离
#         for node_id in node_ids:
#             record= self.api['Monitor.getNodeHitRecord'](node_id)
#             assert isinstance(record, NodeHitMonitor.Record)
#
#             ratio= record.ratio
#             if ratio is None:
#                 color= Qt.lightGray
#                 text= '无访问记录'
#             else:
#                 color= HotColor(ratio)
#                 text= f'命中率: {strPercent(ratio)}'
#
#             self.node_style[node_id]['color']= color
#             self.node_style[node_id]['text']= text
#             # self.node_style[node_id]['show_text']= True  # XXX 是否需要?
#
#         for edge_id in edge_ids:
#             self.edge_style[edge_id]['color']= Qt.lightGray
#             self.edge_style[edge_id]['text']= ''
#             self.edge_style[edge_id]['show_text']= False
