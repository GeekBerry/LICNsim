from core import Hardware


class NodeBase(Hardware):
    def __init__(self):
        super().__init__()
        self.node_type = 'router'
        self.pos = (0, 0)


