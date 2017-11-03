import networkx

from debug import *
from core import *
from module import *
from module.gui_module import GUIModule
from module.name_monitor import NameMonitor
from unit.channel import *
from unit.node import *

sim = SuperSimulator()

sim.install('name_monitor', NameMonitor())
sim.install('gui', GUIModule())

sim.loadNodeAnnounce('csStore', Bind(print, 'csStore'))
sim.loadNodeAnnounce('csEvict', Bind(print, 'csEvict'))
sim.loadNodeAnnounce('inPacket', Bind(print, 'inPacket'))
sim.loadNodeAnnounce('outPacket', Bind(print, 'outPacket'))

graph = networkx.grid_2d_graph(4, 4)
ask_id, *other_ids, store_id, store_id1 = sim.addGraph(graph, ExampleNode, OneStepChannel).values()

sim.getNode(store_id).store(dp_A)
sim.getNode(store_id1).store(dp_A1)
sim.getNode(ask_id).ask(ip_A)

sim.show()



