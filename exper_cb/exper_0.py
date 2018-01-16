from core import *
from debug import *
from exper_cb.test_bed_graph import test_bed_graph
from module import *
from unit import *
# -----------------------------------------------------------------------------
from unit.channel import OneStepChannel

sim = Simulator()
sim.install('hub', HubModule())
sim.install('monitor', MonitorModule())
sim.install('gui', GUIModule())

sim.install('track', StoreTrackModule())

sim.install('log', LogModule())
sim.install('db', DBModule(10))
sim.install('statistics', StatisticsModule())

# -----------------------------------------------------------------------------

ExperNode = nodeFactory(
    cs_capacity=100,
    evict_mode='FIFO',
    evict_life_time=1000,

    AppType=GuidedAppUnit,
    ForwardType=GuidedForwardUnit,
)

i_packet = Packet(Name('P'), Packet.INTEREST, 1)
d_packet = Packet(Name('P'), Packet.DATA, 100)

# -----------------------------------------------------------------------------

STORE_NODE = 'BUPT'

sim.createGraph(test_bed_graph, ExperNode, OneStepChannel)

for node_id in test_bed_graph:
    sub_node_ids = [f'{node_id}_{i}' for i in range(4)]
    sim.createGraph({node_id: sub_node_ids}, ExperNode, OneStepChannel)

# -----------------------------------------------------------------------------

sim.node(STORE_NODE).store(d_packet)


def uniformAsk(node_ids):
    node_id = random.choice(node_ids)
    sim.node(node_id).ask(i_packet.fission())


Loop(uniformAsk, list(sim.nodes()), delta=10)

if __name__ == '__main__':
    sim.showGUI()

    # for i in range(1000):
    #     clock.step()

    print(sim.modules['db'].selectWhere())
