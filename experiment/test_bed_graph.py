import networkx

test_bed_graph= networkx.Graph()

test_bed_graph.add_edge('BUPT', 'CNIC')
test_bed_graph.add_edge('BUPT', 'ANYANG')
test_bed_graph.add_edge('BUPT', 'PKUSZ')
test_bed_graph.add_edge('BUPT', 'KISTI')
test_bed_graph.add_edge('BUPT', 'UI')
test_bed_graph.add_edge('BUPT', 'TONGI')
test_bed_graph.add_edge('BUPT', 'SRRU')
test_bed_graph.add_edge('BUPT', 'WASEDA')

test_bed_graph.add_edge('CNIC', 'PKUSZ')
test_bed_graph.add_edge('CNIC', 'OSAKA')

test_bed_graph.add_edge('PKUSZ', 'MSU')
test_bed_graph.add_edge('PKUSZ', 'WASEDA')
test_bed_graph.add_edge('PKUSZ', 'ANYANG')
test_bed_graph.add_edge('PKUSZ', 'TONGI')
test_bed_graph.add_edge('PKUSZ', 'SRRU')
test_bed_graph.add_edge('PKUSZ', 'OSAKA')
test_bed_graph.add_edge('PKUSZ', 'PADUA')

test_bed_graph.add_edge('ANYANG', 'WASEDA')
test_bed_graph.add_edge('ANYANG', 'OSAKA')
test_bed_graph.add_edge('ANYANG', 'KISTI')
test_bed_graph.add_edge('ANYANG', 'TONGI')
test_bed_graph.add_edge('ANYANG', 'SRRU')
test_bed_graph.add_edge('ANYANG', 'MSU')

test_bed_graph.add_edge('KISTI', 'WASEDA')
test_bed_graph.add_edge('KISTI', 'CSU')
test_bed_graph.add_edge('KISTI', 'UI')

test_bed_graph.add_edge('UI', 'WASEDA')
test_bed_graph.add_edge('UI', 'UUM')
test_bed_graph.add_edge('UI', 'TONGI')
test_bed_graph.add_edge('UI', 'UFPA')
test_bed_graph.add_edge('UI', 'SRRU')

test_bed_graph.add_edge('SRRU', 'OSAKA')
test_bed_graph.add_edge('SRRU', 'MSU')
test_bed_graph.add_edge('SRRU', 'UUM')
test_bed_graph.add_edge('SRRU', 'CAIDA')

test_bed_graph.add_edge('TONGI', 'OSAKA')
test_bed_graph.add_edge('TONGI', 'WASEDA')
test_bed_graph.add_edge('TONGI', 'SRRU')

test_bed_graph.add_edge('OSAKA', 'WASEDA')
test_bed_graph.add_edge('OSAKA', 'UUM')
test_bed_graph.add_edge('OSAKA', 'GOETINGEN')

test_bed_graph.add_edge('WASEDA', 'UA')

test_bed_graph.add_edge('UUM', 'MSU')
test_bed_graph.add_edge('UUM', 'MUNBAI_AWS')

test_bed_graph.add_edge('UA', 'UM')
test_bed_graph.add_edge('UA', 'WU')
test_bed_graph.add_edge('UA', 'CSU')
test_bed_graph.add_edge('UA', 'REMAP')
test_bed_graph.add_edge('UA', 'CAIDA')

test_bed_graph.add_edge('CAIDA', 'UCI')
test_bed_graph.add_edge('CAIDA', 'UCLA')
test_bed_graph.add_edge('CAIDA', 'UFPA')

test_bed_graph.add_edge('UCLA', 'UCI')
test_bed_graph.add_edge('UCLA', 'REMAP')
test_bed_graph.add_edge('UCLA', 'CSU')
test_bed_graph.add_edge('UCLA', 'MSU')

test_bed_graph.add_edge('REMAP', 'UCI')
test_bed_graph.add_edge('REMAP', 'BYU')
test_bed_graph.add_edge('REMAP', 'CSU')

test_bed_graph.add_edge('BYU', 'UA')
test_bed_graph.add_edge('BYU', 'CSU')

test_bed_graph.add_edge('UM', 'WU')
test_bed_graph.add_edge('UM', 'MICH')
test_bed_graph.add_edge('UM', 'NEU')
test_bed_graph.add_edge('UM', 'UFPA')

test_bed_graph.add_edge('UIUC', 'WU')
test_bed_graph.add_edge('UIUC', 'CSU')
test_bed_graph.add_edge('UIUC', 'MICH')
test_bed_graph.add_edge('UIUC', 'NIST')
test_bed_graph.add_edge('UIUC', 'PADUA')

test_bed_graph.add_edge('MICH', 'CSU')
test_bed_graph.add_edge('MICH', 'NIST')
test_bed_graph.add_edge('MICH', 'NEU')
test_bed_graph.add_edge('MICH', 'LIP6')

test_bed_graph.add_edge('NEU', 'NIST')
test_bed_graph.add_edge('NEU', 'NTNU')

test_bed_graph.add_edge('URJC', 'LIP6')
test_bed_graph.add_edge('URJC', 'MINHO')
test_bed_graph.add_edge('URJC', 'PADUA')
test_bed_graph.add_edge('URJC', 'COPELABS')
test_bed_graph.add_edge('URJC', 'BASEL')
test_bed_graph.add_edge('URJC', 'WU')

test_bed_graph.add_edge('AFA', 'PADUA')
test_bed_graph.add_edge('AFA', 'BERN')
test_bed_graph.add_edge('AFA', 'COPELABS')
test_bed_graph.add_edge('AFA', 'MUNBAI_AWS')

test_bed_graph.add_edge('TNO', 'LIP6')
test_bed_graph.add_edge('TNO', 'GOETINGEN')
test_bed_graph.add_edge('TNO', 'MSU')
test_bed_graph.add_edge('TNO', 'BASEL')

test_bed_graph.add_edge('COPELABS', 'PADUA')
test_bed_graph.add_edge('COPELABS', 'MINHO')
test_bed_graph.add_edge('COPELABS', 'UFPA')
test_bed_graph.add_edge('COPELABS', 'LIP6')

test_bed_graph.add_edge('MINHO', 'PADUA')
test_bed_graph.add_edge('MINHO', 'BASEL')

test_bed_graph.add_edge('NTNU', 'LIP6')
test_bed_graph.add_edge('NTNU', 'BASEL')
test_bed_graph.add_edge('NTNU', 'GOETINGEN')
test_bed_graph.add_edge('NTNU', 'SYSTEMX')

test_bed_graph.add_edge('SYSTEMX', 'GOETINGEN')
test_bed_graph.add_edge('SYSTEMX', 'LIP6')
test_bed_graph.add_edge('SYSTEMX', 'BASEL')

test_bed_graph.add_edge('BASEL', 'LIP6')
test_bed_graph.add_edge('BASEL', 'GOETINGEN')
test_bed_graph.add_edge('BASEL', 'PADUA')
test_bed_graph.add_edge('BASEL', 'BERN')

test_bed_graph.add_edge('PADUA', 'GOETINGEN')


if __name__ == '__main__':
    for node in test_bed_graph.nodes():
        print(node)

    for edge in test_bed_graph.edges():
        print(edge)
