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

    AppType= GuidedAppUnit,  #AppUnit,
    # InfoType= IOInfoUnit,
    ForwardType= GuidedForwardUnit,  # ShortestForwardUnit,
)


from exper_cb.test_bed_graph import test_bed_graph
# graph= test_bed_graph; cs_id= 'BUPT'

import networkx
# graph= networkx.grid_2d_graph(80, 160); cs_id= (0,0)
# graph= networkx.grid_2d_graph(5, 5); cs_id= (2,2)
# graph= networkx.balanced_tree(3,3); cs_id= 0
graph= networkx.barabasi_albert_graph(20,2); cs_id= 0

sim.createGraph(graph, NodeType, OneStepChannel)

#
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

if __name__ == '__main__' and 1:
    sim.showGUI()
    # prcfile('sim.showGUI()')

if __name__ == '__main__' and 0:
    for i in range(1_000):
        clock.step()

    sim.plotNames(ip_A.name, ip_B.name)
    sim.plotNodes('BUPT', 'UCLA')

if __name__ == '__main__' and 0:
    import time

    start = time.clock()
    for i in range(1_000):
        clock.step()
    end = time.clock()
    t= end - start
    print(clock.debug_count_event, t, clock.debug_count_event/t)


    """
    wuwuwu
    100 6999 0.5554927573202761 12599.624221499329
    200 7652 0.6142046002561807 12458.389267694187
    400 8692 0.7269610852256184 11956.623506610902
    800 11696 0.9945434643412691 11760.169785788887
    1600 15655 1.4880261192583557 10520.648661599153
    3200 26067 2.679414107488344 9728.619375089782
    6400 38377 4.834931383162682 7937.444600278151
    12800 72214 10.939928530199792 6600.957200099842
    
    youyouyou
    100 6937 0.7165969726443074 9680.476285577713
    200 7570 0.780713369924573 9696.260230219139
    400 8158 0.8715715994530243 9360.103065680145
    800 11466 1.255737850719881 9130.886668285779
    1600 16575 1.8500994105078574 8958.978045104137
    3200 22847 2.7140994657943422 8417.893407349135
    6400 37295 5.310220277580219 7023.249140428262
    12800 61940 11.574760397690106 5351.298676762322
    
    """
