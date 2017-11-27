import networkx

from core import *
from unit.node import *
from unit.channel import *
from module import *
from debug import *

sim = SuperSimulator()

sim.install('name_monitor', NameMonitor())
sim.install('node_monitor', NodeMonitor())
sim.install('log', LogMoudle())
sim.install('gui', GUIModule())

graph = networkx.random_regular_graph(3, 20)
# graph= networkx.grid_2d_graph(10,10)
node_map= sim.addGraph(graph, ExampleNode, OneStepChannel)

node_i, *_, node_d, node_d1 = node_map.values()

node_d.store(dp_A)
node_d1.store(dp_A1)
node_i.ask(ip_A)

sim.show()

# from experiment.test_bed_graph import test_bed_graph
#
# print(graph.nodes)
# print(test_bed_graph.nodes)
