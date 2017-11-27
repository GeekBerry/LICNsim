from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem

from gui.EdgeItem import EdgeItem
from gui.NodeItem import NodeItem

from debug import showCall


class NetScene(QGraphicsScene):
    SPACE_WIDTH = 200  # 留白宽度

    def __init__(self, parent, announces, api):
        super().__init__(parent)
        self.node_table = {}  # { node_id:node_item, ... }
        self.edge_table = {}  # { (src_id, dst_id):edge_item, ... }

        self.cache_pixmap= None
        self.background_item= QGraphicsPixmapItem()
        self.addItem(self.background_item)

        api['Scene.setBackgroundColor']= self.setBackgroundBrush
        api['Scene.setBackgroundPixmap']= self.setBackgroundPixmap
        api['Scene.setLayout']= self.setLayout
        api['Scene.renderNode']= self.renderNode
        api['Scene.renderEdge']= self.renderEdge

        announces['addICNNode'].append(self.addICNNode)
        announces['addICNChannel'].append(self.addICNChannel)

        self.announces = announces
        self.api= api

    def setLayout(self, layout):
        for node_id, (x,y) in layout.items():
            self.node_table[node_id].checkPos(x,y)
        self.adjustBounding()

    def addICNNode(self, node_id):
        node_item = NodeItem(node_id)
        # TODO 用 icn_node 的属性决定 node_item 的style
        node_item.call_backs['ItemPositionHasChanged'] = self._nodeItemPositionHasChanged
        node_item.call_backs['mousePressEvent'] = self._nodeMousePressEvent
        node_item.call_backs['mouseReleaseEvent'] = self._nodeMouseReleaseEvent
        node_item.call_backs['mouseDoubleClickEvent'] = self._nodeMouseDoubleClickEvent
        self.node_table[node_id] = node_item
        self.addItem(node_item)
        self.update()

    def addICNChannel(self, edge_id):
        edge_item = EdgeItem(edge_id)
        # TODO 用 icn_channel 的属性决定 edge_item 的 style
        edge_item.call_backs['mouseDoubleClickEvent'] = self._edgeMouseDoubleClickEvent

        src_id, dst_id= edge_id
        src_item = self.node_table[src_id]
        dst_item = self.node_table[dst_id]
        edge_item.adjust(src_item.pos(), dst_item.pos())
        self.edge_table[edge_id] = edge_item

        self.addItem(edge_item)
        self.update()

    def renderNode(self, node_id, style:dict):
        node_item = self.node_table[node_id]
        node_item.setStyle(style)

    def renderEdge(self, edge_id, style:dict):
        edge_item= self.edge_table[edge_id]
        edge_item.setStyle(style)

    # ------------------------------------------------------------------------------------------------------------------
    def setBackgroundPixmap(self, pixmap):
        if pixmap is None:
            self.background_item.hide()
        else:
            if self.cache_pixmap is not pixmap:
                self.cache_pixmap= pixmap
                self.background_item.setPixmap(pixmap)
                # 设置位置居中
                rect = self.background_item.boundingRect()
                self.background_item.setPos(-rect.center())
            self.background_item.show()

    def adjustBounding(self):
        self.setSceneRect(
            self.itemsBoundingRect().adjusted(
                -self.SPACE_WIDTH,
                -self.SPACE_WIDTH,
                self.SPACE_WIDTH,
                self.SPACE_WIDTH
            )
        )
        self.update()

    # ------------------------------------------------------------------------------------------------------------------
    def _nodeItemPositionHasChanged(self, src_id):
        """
        当一个节点位置变化时，调整与该节点链接的边
        :param src_id: 节点id
        :return: None
        """
        neighbor_table = self.api['Sim.graph']()  # 邻接表{node_id:{neighbor_id, ...}, }
        src_pos = self.node_table[src_id].pos()
        for dst_id in neighbor_table[src_id]:
            dst_pos = self.node_table[dst_id].pos()
            self.edge_table[(src_id, dst_id)].adjust(src_pos, dst_pos)
            self.edge_table[(dst_id, src_id)].adjust(dst_pos, src_pos)

    def _nodeMousePressEvent(self, node_id):
        pass

    def _nodeMouseReleaseEvent(self, node_id):
        node_item = self.node_table[node_id]
        pos= node_item.pos()
        pos= pos.x(), pos.y()
        self.announces['moveNode'](node_id, pos)

    def _nodeMouseDoubleClickEvent(self, node_id):
        self.announces['doubleClickNode'](node_id)

    def _edgeMouseDoubleClickEvent(self, edge_id):
        self.announces['doubleClickEdge'](edge_id)

    # 如果需要检测双击空白处功能，则启用该代码
    # def mouseDoubleClickEvent(self, event):
    #     super().mouseDoubleClickEvent(event)
    #     if not event.pos():  # XXX 场景在没有捕捉到Item时, event.pos()为QPointF(), 而非位置
    #         self.announces['SceneDoubleClick']()
