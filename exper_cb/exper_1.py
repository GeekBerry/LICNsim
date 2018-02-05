import networkx, time
from core import *
from debug import *
from exper_cb.modules import ReporterModule, ExperDBModule
from module import *
from unit import *

TIME = time.strftime("%Y%m%d_%H%M%S", time.localtime())

RATIO = 1000  # 单位 step/second
NAME = Name('P')
i_packet = Packet(NAME, Packet.INTEREST, 1)
d_packet = Packet(NAME, Packet.DATA, 100)

SIM_SECOND= 500

def main(graph_mode, lam, cs_mode, evict_mode, evict_time, normal):
    file_name= f'result/{TIME} {graph_mode} lam{lam} {cs_mode} cs_{evict_mode}{evict_time} normal_{normal} .txt'

    print(f'start:{file_name}')

    SourceNode = nodeFactory(
        cs_capacity=100,
        evict_mode='CONST',

        AppType=GuidedAppUnit,
        ForwardType=GuidedForwardUnit,
    )

    if cs_mode == 'LCE':
        ContentStoreType = ContentStoreUnit
        proba= None
    elif cs_mode == 'LCP':
        ContentStoreType = LCPContentStoreUnit
        proba= 0.5
    elif cs_mode == 'LCD':
        ContentStoreType = LCDContentStoreUnit
        proba= None
    else:
        raise ValueError(cs_mode)

    ExperNode = nodeFactory(
        cs_capacity=100,
        cs_probability= proba,
        evict_mode=evict_mode,
        evict_life_time=evict_time * RATIO,

        AppType=GuidedAppUnit,
        ForwardType=GuidedForwardUnit,
        ContentStoreType=ContentStoreType,
    )

    if graph_mode == 'grid':
        STORE_NODE = (50, 50)
        graph = networkx.grid_2d_graph(101, 101)
    elif graph_mode == 'ba':
        STORE_NODE = 0
        graph = networkx.barabasi_albert_graph(10000, 3)
    elif graph_mode == 'tree':
        STORE_NODE = 0
        graph = networkx.balanced_tree(3, 8)
    else:
        raise ValueError(graph_mode)

    sim = Simulator()
    sim.install('hub', HubModule())
    sim.install('track', StoreTrackModule())
    sim.install('db', ExperDBModule(RATIO))

    sim.createNode(STORE_NODE, SourceNode)
    sim.createGraph(graph, ExperNode, OneStepChannel)

    sim.node(STORE_NODE).store(d_packet)  # 储存数据包

    if normal:  # 设置符合正态分布的驱逐时间
        for node_id in sim.nodes():
            sim.node(node_id).units['evict'].life_time= int( numpy.random.normal(scale=1000, loc= evict_time*RATIO) )

    def uniformAsk(node_ids):
        node_id = random.choice(node_ids)
        sim.node(node_id).ask(i_packet.fission())

    Loop(uniformAsk, list(sim.nodes()), delta=RATIO // lam)
    sim.install('reporter', ReporterModule(STORE_NODE, NAME, RATIO, file_name) )

    for i in range( SIM_SECOND*RATIO + 1):
        clock.step()

    clock.clear()

    print(f'end:{file_name}')

