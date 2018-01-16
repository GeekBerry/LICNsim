from core import *
from debug import *
from module import *
from unit.channel import *
from unit.node import ExampleNode

sim = Simulator()
sim.install('hub', HubModule())
sim.loadNodeAnnounce('inPacket', Bind(print, 'inPacket') )
sim.loadNodeAnnounce('outPacket', Bind(print, 'outPacket') )
sim.loadNodeAnnounce('csStore', Bind(print, 'csStore') )
sim.loadNodeAnnounce('csEvict', Bind(print, 'csEvict') )

# -----------------------------------------------------------------------------
node_d= ExampleNode()
node_i= ExampleNode()

sim.addICNNode('A', node_d)
sim.addICNNode('B', node_i)

sim.addICNEdge('A', 'B', Channel(INF, 1, 0.0))
sim.addICNEdge('B', 'A', Channel(INF, 1, 0.0))

node_d.store(dp_A)
node_i.ask(ip_A)

for i in range(5):
    print('Time:', i)
    clock.step()

