from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem

from gui.EdgeItem import EdgeItem
from gui.NodeItem import NodeItem

from debug import showCall


class NetScene(QGraphicsScene):
    SPACE_WIDTH = 200  # 留白宽度

    def __init__(self, parent, announces, api):
        super().__init__(parent)
        self.announces = announces
        self.api = api

        api['Scene.setBackgroundColor'] = self.setBackgroundBrush
        api['Scene.setBackgroundPixmap'] = self.setBackgroundPixmap
        api['Scene.setLayout'] = self.setLayout
        api['Scene.renderNode'] = self.renderNode
        api['Scene.renderEdge'] = self.renderEdge
        api['Scene.selectedNode'] = lambda: self.selected_node

        announces['addICNNode'].append(self.addICNNode)
        announces['addICNEdge'].append(self.addICNEdge)

        self.node_table = {}  # { node_id:node_item, ... }
        self.edge_table = {}  # { edge_id:edge_item, ... }

        self.cache_pixmap = None
        self.background_item = QGraphicsPixmapItem()
        self.addItem(self.background_item)

        self.selected_node = None

    def setLayout(self, layout):
        """
        设置场景中节点的位置
        :param layout: {node_id:(x,y), ...}
        :return: None
        """
        for node_id, (x, y) in layout.items():
            self.node_table[node_id].checkPos(x, y)
        self.adjustBounding()

    def addICNNode(self, node_id):
        node_item = NodeItem(node_id)
        node_item.press_callback = self.pressNode
        node_item.release_callback = self.releaseNode
        node_item.double_click_callback = self.announces['doubleClickNode']
        node_item.move_callback = self.moveNode

        self.node_table[node_id] = node_item
        self.addItem(node_item)
        self.update()

    def addICNEdge(self, edge_id):
        edge_item = EdgeItem(edge_id)
        edge_item.double_click_callback = self.announces['doubleClickEdge']

        src_id, dst_id = edge_id
        src_item = self.node_table[src_id]
        dst_item = self.node_table[dst_id]
        edge_item.adjust(src_item.pos(), dst_item.pos())

        self.edge_table[edge_id] = edge_item
        self.addItem(edge_item)
        self.update()

    def renderNode(self, node_id, style: dict):
        self.node_table[node_id].setStyle(style)

    def renderEdge(self, edge_id, style: dict):
        self.edge_table[edge_id].setStyle(style)

    # ------------------------------------------------------------------------------------------------------------------
    def setBackgroundPixmap(self, pixmap):
        if pixmap is None:
            self.background_item.hide()
        else:
            if self.cache_pixmap is not pixmap:
                self.cache_pixmap = pixmap
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
    def pressNode(self, node_id):
        self.selected_node= node_id
        self.announces['selectedNode'](self.selected_node)

    def moveNode(self, src_id):
        """
        当一个节点位置变化时，调整与该节点链接的边
        :param src_id: 节点id
        :return: None
        """
        graph = self.api['Sim.graph']()  # 邻接表{node_id:{neighbor_id, ...}, }
        src_pos = self.node_table[src_id].pos()
        for dst_id in graph[src_id]:
            dst_pos = self.node_table[dst_id].pos()
            self.edge_table[(src_id, dst_id)].adjust(src_pos, dst_pos)
            self.edge_table[(dst_id, src_id)].adjust(dst_pos, src_pos)

    def releaseNode(self, node_id):
        node_item = self.node_table[node_id]
        pos = node_item.pos()
        pos = pos.x(), pos.y()
        self.announces['sceneNodeMoved'](node_id, pos)
