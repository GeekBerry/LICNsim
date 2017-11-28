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


from experiment.test_bed_graph import test_bed_graph

# graph = networkx.random_regular_graph(3, 20)
# graph= networkx.grid_2d_graph(10,10)
graph= test_bed_graph

node_map= sim.addGraph(graph, ExampleNode, OneStepChannel)

node_d= node_map['BUPT']
node_i= node_map['UCLA']

node_d.store(dp_A)
node_i.ask(ip_A)

sim.show()
