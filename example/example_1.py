import networkx

from core import *
from unit.node import *
from unit.channel import *
from module import *
from module.loss_module import LossMonitor
from debug import *

sim = Simulator()
sim.install('hub', HubModule())
sim.install('loss', LossMonitor())

sim.install('name_monitor', NameMonitor())
sim.install('node_monitor', NodeMonitor())
sim.install('log', LogModule())
sim.install('gui', GUIModule())

# from experiment.test_bed_graph import test_bed_graph
# graph = networkx.random_regular_graph(3, 20)
# graph= networkx.grid_2d_graph(10,10)
# graph= test_bed_graph


sim.createGraph({'A':['B']}, nodeFactory(node_type='router', cs_capacity= 1000), channelFactor(channel_type='wired'))
sim.createGraph({'A':['s1', 's2']}, nodeFactory(node_type='server', cs_capacity= 1000), channelFactor(channel_type='wired'))
sim.createGraph({'B':['c1', 'c2']}, nodeFactory(node_type='client'), channelFactor(channel_type='wireless'))

sim.node('A').pos= (0, 0)
sim.node('B').pos= (500, 0)

sim.node('s1').pos= (0, 500)
sim.node('s2').pos= (0, -500)

sim.node('c1').pos= (500, 500)
sim.node('c2').pos= (500, -500)

sim.node('s1').store(dp_A)
sim.node('c1').ask(ip_A)

sim.showGUI()
