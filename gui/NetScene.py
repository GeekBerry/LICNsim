from random import randint

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtWidgets import QGraphicsScene

from gui.NodeItem import NodeItem
from gui.EdgeItem import EdgeItem

from debug import showCall


# ----------------------------------------------------------------------------------------------------------------------
class NetScene(QGraphicsScene):
    @staticmethod
    def layoutPosition(neibor_table, pos_table, ratio):
        for node_id, node_pos in pos_table.items():
            force = QPointF(0.0, 0.0)
            weight = len(neibor_table[node_id])  # 邻居数量

            for other_id, other_pos in pos_table.items():
                vec= other_pos - node_pos
                vls= vec.x()*vec.x() + vec.y()*vec.y()  # vector_length_square

                if 0 < vls < 4*ratio:  # vec.length() 小于 4*ratio才计算斥力; '4'来自于经验
                    force -= (vec/vls) * ratio  # 空间中节点间为排斥力

                if other_id in neibor_table[node_id]:
                    force += vec/weight  # 连接的节点间为吸引力

            pos_table[node_id]= node_pos + force * 0.4  # force系数不能为1, 否则无法收敛; 0.4来自于经验,不会变化太快

    AREA_SIZE= 1000
    EDGE_LEN= 80  # 默认边长度
    NODE_SIZE= 0.5  # 默认Node大小
    SPACE_WIDTH= 200

    def __init__(self):
        super().__init__()
        self.node_table= {}  # { node_id:node_item, ... }
        self.edge_table= {}  # { (src_id, dst_id):edge_item, ... }

    def install(self, announces, api):
        self.announces= announces
        self.api= api

        announces['playSteps'].append(self.playSteps)
        announces['addICNNode'].append(self.addICNNodeEvent)
        announces['addICNChannel'].append(self.addICNChannelEvent)
        announces['painterUpdated'].append(self.painterUpdated)

    def painterUpdated(self, painter):
        if painter is self.api['Painter.currentPainter']():
            self.refresh()

    def addICNNodeEvent(self, node_id, icn_node):
        node_item= NodeItem(node_id)
        # TODO 用 icn_node 的属性决定 node_item 的style
        node_item.setPos( randint(0, self.AREA_SIZE), randint(0, self.AREA_SIZE) )
        node_item.setSize( self.NODE_SIZE )

        node_item.call_backs['ItemPositionHasChanged']= self._nodeMoved
        node_item.call_backs['mousePressEvent']= self._nodeMousePressEvent
        node_item.call_backs['mouseDoubleClickEvent']= self._nodeMouseDoubleClickEvent
        self.node_table[node_id]= node_item

        self.addItem(node_item)
        self.update()

    def addICNChannelEvent(self, src_id, dst_id, icn_channel):
        edge_item= EdgeItem(src_id, dst_id)
        # TODO 用 icn_channel 的属性决定 edge_item 的 style
        edge_item.call_backs['mouseDoubleClickEvent']= self._edgeMouseDoubleClickEvent

        src_item= self.node_table[src_id]
        dst_item= self.node_table[dst_id]
        edge_item.adjust( src_item.pos(), dst_item.pos() )
        self.edge_table[ (src_id, dst_id) ]= edge_item

        self.addItem(edge_item)
        self.update()

    # ------------------------------------------------------------------------------------------------------------------
    def playSteps(self, steps):
        self.refresh()

    def refresh(self):
        painter= self.api['Painter.currentPainter']()
        if painter is None:  # DEBUG
            return

        style_dict= painter.getStyleDict()
        if 'back_ground_color' in style_dict:
            self.setBackgroundBrush( style_dict['back_ground_color'] )

        if 'node_style' in style_dict:
            node_style= style_dict['node_style']
            assert isinstance(node_style, dict)

            for node_id, entry in node_style.items():
                ui_node= self.node_table[node_id]
                ui_node.setSize( entry['size'] )
                ui_node.setColor( entry['color'] )
                ui_node.setText( entry['text'] )
                if entry['show_text']:
                    ui_node.showText()
                else:
                    ui_node.hideText()
                ui_node.update()

        if 'edge_style' in style_dict:
            edge_style= style_dict['edge_style']
            assert isinstance(edge_style, dict)

            for (src_id, dst_id), entry in edge_style.items():
                ui_edge= self.edge_table[ (src_id, dst_id) ]
                ui_edge.setWidth( entry['width'] )
                ui_edge.setColor( entry['color'] )
                ui_edge.setText( entry['text'] )
                if entry['show_text']:
                    ui_edge.showText()
                else:
                    ui_edge.hideText()
                ui_edge.update()

    # ------------------------------------------------------------------------------------------------------------------
    @showCall
    def _nodeMouseDoubleClickEvent(self, node_id):
        self.announces['NodeDoubleClick'](node_id)

    def _nodeMousePressEvent(self, node_id):
        self.announces['NodeMousePress'](node_id)

    def _edgeMouseDoubleClickEvent(self, src_id, dst_id):
        self.announces['EdgeDoubleClick'](src_id, dst_id)

    # def mouseDoubleClickEvent(self, event):
    #     super().mouseDoubleClickEvent(event)
    #     if not event.pos():  # XXX 场景在没有捕捉到Item时, event.pos()为QPointF(), 而非位置
    #         self.announces['SceneDoubleClick']()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_P:
            self._nodesLayout(10)
        else: super().keyPressEvent(event)

    # ------------------------------------------------------------------------------------------------------------------
    def _nodeMoved(self, src_id):
        neibor_table= self.api['Topo.neiborTable']()

        src_pos= self.node_table[src_id].pos()
        for dst_id in neibor_table[src_id]:
            dst_pos= self.node_table[dst_id].pos()
            self.edge_table[ (src_id, dst_id) ].adjust(src_pos, dst_pos)
            self.edge_table[ (dst_id, src_id) ].adjust(dst_pos, src_pos)

    # ------------------------------------------------------------------------------------------------------------------
    def _nodesLayout(self, times):
        # TODO 当携带地理位置信息时, 针对地理位置信息 layout

        neibor_table= self.api['Topo.neiborTable']()
        position_table= { node_id:self.node_table[node_id].pos()
            for node_id in neibor_table.nodes()
        }

        for i in range(0, times):
            # XXX 根据经验, ratio 为 self.EDGE_LEN * self.EDGE_LEN 时, 点之间距离大致为 self.EDGE_LEN
            self.layoutPosition(neibor_table, position_table, self.EDGE_LEN * self.EDGE_LEN)

        for node_id, node_pos in position_table.items():
            self.node_table[node_id].setPos(node_pos)

        self.setSceneRect( self.itemsBoundingRect().adjusted(-self.SPACE_WIDTH, -self.SPACE_WIDTH, self.SPACE_WIDTH, self.SPACE_WIDTH) )
        self.update()


