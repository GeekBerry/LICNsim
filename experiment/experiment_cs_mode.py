import time
import networkx

from debug import *
from experiment import *
from module import *
from unit.channel import *
from algorithm.graph_algo import graphApproximateDiameter

DATE= time.strftime("%Y%m%d%H%M%S", time.localtime())

GRAPH_NAME= 'BA'

if GRAPH_NAME == 'Grid':
    graph = networkx.grid_2d_graph(100, 100)
    DATA_NODE = (50, 50)
    DIAMETER = 200
elif GRAPH_NAME == 'BA':
    graph = networkx.barabasi_albert_graph(10000, 3)
    DATA_NODE = 0
    DIAMETER = graphApproximateDiameter(graph)
elif GRAPH_NAME == 'Tree':
    graph= networkx.balanced_tree(3, 8)
    DATA_NODE = 0
    DIAMETER = 16
else:
    raise TypeError


cs_type= 'LCE'  # LCE, LCP, LCD
evict_mode = 'FIFO'  # FIFO, LRU, RANDOM, GEOMETRIC

lam = 100
cs_time = 100


# for lam in (20,40,60,80,100):
for cs_time in (20,40,60,80,100):
    SECOND = DIAMETER * lam
    SIM_STEP = 500 * SECOND

    NodeType= NodeFactor(cs_type= cs_type, p=0.5, cs_time=cs_time * SECOND, evict_mode= evict_mode)
    file_name = f'result/C. {GRAPH_NAME} 直径{DIAMETER} lam{lam} {evict_mode}{cs_time} {cs_type} {DATE}.txt'

    sim = SuperSimulator()
    sim.install('cs_track', StoreTrackMoudle(ip_A.name))
    sim.install('db', LogMoudle())
    sim.install('reporter', ReporterModule(sim.modules['db'].db_table, SECOND, file_name))

    node_map = sim.addGraph(graph, NodeType, OneStepChannel)
    sim.getNode(node_map[DATA_NODE]).setEvictMode('CONST')
    sim.getNode(node_map[DATA_NODE]).insert(dp_A)

    sim.install('asker', AskMoudle(ip_A, PossionAsk(1), UniformDistribute(sim.nodes()), delta=DIAMETER))  # DEBUG 版本， 期望能动态配置

    for i in range(SIM_STEP + 1):
        clock.step()

    clock.clear()
    print('\n\n')



