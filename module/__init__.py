
class MoudleBase:
    @NotImplementedError
    def setup(self, sim):
        pass

from module.sim import Simulator
from module.hub_module import HubModule
from module.gui_module import GUIModule
from module.name_monitor import NameMonitor
from module.node_monitor import NodeMonitor
from module.node_monitor import EdgeMonitor
from module.log_module import LogMoudle




