from core import *
from debug import *
from module import *
from unit import *

from unit.channel import OneStepChannel
from unit.node import nodeFactory

sim = Simulator()
sim.install('hub', HubModule())

sim.install('track', StoreTrackModule())
# sim.install('loss', LossMonitor())
sim.install('log', LogModule())
sim.install('monitor', MonitorModule())
sim.install('gui', GUIModule())

sim.install('db', DBModule(10))
sim.install('statistics', StatisticsModule())

# ----------------------------------------------------------------------------------------------------------------------
NodeType = nodeFactory(
    node_type='router',

    recv_rate=1,
    recv_capacity=INF,
    nonce_life_time=100_000,

    cs_capacity= 500,
    replace_mode= 'FIFO',
    # evict_mode=None,  # 'CONST', 'FIFO', 'LRU', 'GEOMETRIC'
    # evict_life_time=None,

    # AppType=AppUnit,
    # InfoType= IOInfoUnit,
    ForwardType= ShortestForwardUnit,
)


from exper_cb.test_bed_graph import test_bed_graph
graph= test_bed_graph

sim.createGraph(graph, NodeType, OneStepChannel)

cs_id= 'BUPT'
sim.node(cs_id).units['cs'].capacity = 1000
sim.node(cs_id).store(dp_A)
sim.node(cs_id).store(dp_B)


def uniformAsk(node_ids, packet):
    # if random.random() < 0.1:
    #     node_id = random.choice(node_ids)
    #     sim.node(node_id).ask(packet.fission())

    if random.random() < math.exp(-clock.time/1000):
        node_id = random.choice(node_ids)
        sim.node(node_id).ask(packet.fission())


Loop(uniformAsk, list(sim.nodes()), ip_A)
Loop(uniformAsk, list(sim.nodes()), ip_B)

if __name__ == '__main__' and 0:
    sim.showGUI()
    # prcfile('sim.showGUI()')

if __name__ == '__main__' and 1:
    for i in range(1_000):
        clock.step()

    sim.plotNames(ip_A.name, ip_B.name)
    sim.plotNodes('BUPT', 'UCLA')

if __name__ == '__main__' and 0:
    import time

    start = time.clock()
    for i in range(2_000):
        clock.step()
    end = time.clock()
    print(end - start)
