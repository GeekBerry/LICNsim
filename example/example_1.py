import networkx

from core import *
from unit.node import *
from unit.channel import *
from module import *
from debug import *

sim = Simulator()
sim.install('hub', HubModule())
sim.install('name_monitor', NameMonitor())
sim.install('node_monitor', NodeMonitor())
sim.install('log', LogMoudle())
sim.install('gui', GUIModule())


# from experiment.test_bed_graph import test_bed_graph
# graph = networkx.random_regular_graph(3, 20)
# graph= networkx.grid_2d_graph(10,10)
# graph= test_bed_graph


sim.createGraph({'A':['B']}, RouterNodeBase, OneStepChannel)
sim.createGraph({'A':['a1', 'a2']}, ServerNodeBase, OneStepChannel)
sim.createGraph({'B':['b1', 'b2']}, ClientNodeBase, OneStepChannel)

node_d= sim.node('b1')
node_i= sim.node('a1')

node_d.store(dp_A)
node_i.ask(ip_A)

sim.show()
