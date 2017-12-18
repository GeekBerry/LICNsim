import networkx

from core import *
from debug import *
from module import *
from module.guide_module import GuideModule
from module.loss_module import LossMonitor
from module.db_module import DBModule
from statistics_module import StatisticsModule
from unit.node import *
from debug import prcfile

sim = Simulator()
sim.install('hub', HubModule())

sim.install('guide', GuideModule())
# sim.install('loss', LossMonitor())
sim.install('log', LogModule())

sim.install('name_monitor', NameMonitor())
sim.install('node_monitor', NodeMonitor())
sim.install('edge_monitor', EdgeMonitor())
sim.install('gui', GUIModule())

sim.install('db', DBModule(10))
sim.install('statistics', StatisticsModule())

# ----------------------------------------------------------------------------------------------------------------------
NodeType = nodeFactory(
    cs_capacity=500,
    replace_mode='FIFO',
    # evict_mode='GEOMETRIC',
    # evict_life_time=100,
    ForwardType=GuidedForwardUnit
)

graph = networkx.grid_2d_graph(5, 5)
sim.createGraph(graph, NodeType, OneStepChannel)

# 设置物理位置
# for node_id in sim.nodes():
#     x, y = node_id
#     sim.node(node_id).pos = x * 100, y * 100

sim.node((2, 2)).units['cs'].capacity = 1000
sim.node((2, 2)).store(dp_A)
sim.node((2, 2)).store(dp_B)

import math


def uniformAsk(node_ids, packet):
    if random.random() < math.exp(-clock.time / 1000):
        node_ids = (0, 0), (4, 4), (0, 4), (4, 0)
        node_id = random.choice(node_ids)
        sim.node(node_id).ask(packet.fission())

        # if random.random() < 0.1:
        #     node_id = random.choice(node_ids)
        #     sim.node(node_id).ask(packet.fission())

        # if random.random() < math.exp(-clock.time/1000):
        #     node_id = random.choice(node_ids)
        #     sim.node(node_id).ask(packet.fission())


Loop(uniformAsk, list(sim.nodes()), ip_A)
Loop(uniformAsk, list(sim.nodes()), ip_B)

if __name__ == '__main__' and 1:
    sim.showGUI()
    # prcfile('sim.showGUI()')

if __name__ == '__main__' and 0:
    for i in range(1_000):
        clock.step()

    sim.plotNames(ip_A.name, ip_B.name)
    sim.plotNodes((0, 0), (2, 2))
    sim.showPlot()

if __name__ == '__main__' and 0:
    import time

    start = time.clock()
    for i in range(2_000):
        clock.step()
    end = time.clock()
    print(end - start, clock.debug_count_event)
