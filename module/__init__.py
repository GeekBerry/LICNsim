
class ModuleBase:
    @NotImplementedError
    def setup(self, sim):
        pass

from module.sim import Simulator
from module.hub_module import HubModule
from module.gui_module import GUIModule
from module.monitor_module import MonitorModule
# from module.name_monitor import NameMonitor
# from module.node_monitor import NodeMonitor
# from module.edge_monitor import EdgeMonitor
from module.log_module import LogModule

from module.store_track_module import StoreTrackModule
from module.loss_module import LossMonitor
from module.db_module import DBModule
from statistics_module import StatisticsModule




