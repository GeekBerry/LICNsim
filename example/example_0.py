from unit.node import *
from unit.channel import *
from debug import *


node1 = ExampleNode()
node2 = ExampleNode()
channel12= Channel(None, None, rate= 100_000, delay= 1, loss= 0)
channel21= Channel(None, None, rate= 100_000, delay= 1, loss= 0)

node1.setOutChannel(2, channel12)
node1.setInChannel(2, channel21)

node2.setOutChannel(1, channel21)
node2.setInChannel(1, channel12)

print('---------------------')
node1.store(dp_A)
node2.ask(ip_A)

print('---------------------')
clock.step()

print('---------------------')
clock.step()

print('---------------------')
clock.step()

print('---------------------')
clock.step()
