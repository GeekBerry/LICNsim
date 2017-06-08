
from debug import showCall


class Name(str):
    def __init__(self, *args, **kwargs):
        self.__segments= self.split('/')

    def __len__(self):
        return len(self.__segments)

    def __iter__(self):
        return iter(self.__segments)


# ----------------------------------------------------------------------------------------------------------------------
class NameTree:
    def __init__(self, parent=None, key=None):
        self.parent= parent
        self.__key= key
        self.children= {}

    def __iter__(self):  # 递归遍历自己和所有子节点
        yield self
        for child in self.children.values():
            for each in child:
                yield each

    @property
    def key(self):
        return self.__key

    def name(self):
        cur_node= self
        reverse_list= []
        while cur_node.parent:
            reverse_list.append( str(cur_node.key) )
            cur_node= cur_node.parent
        return Name( '/'.join(reverse_list[::-1]) )

    def access(self, name):
        cur_node= self
        for segment in name:
            if segment not in cur_node.children:
                cur_node.children[segment]= self.__class__(cur_node, segment)
            cur_node= cur_node.children[segment]
        return cur_node

    def get(self, name):
        cur_node= self
        for segment in name:
            cur_node= cur_node.children.get(segment, None)
            if cur_node is None:
                return None
        return cur_node

    def longest(self, name):  # 寻找最长前缀匹配的节点
        cur_node= self
        for segment in name:
            if segment in cur_node.children:
                cur_node= cur_node.children[segment]
            else:
                break
        return cur_node

    def print(self, deep= 0):  # DEBUG
        print('\t' * deep, f'{repr(self.key)}:{self}')
        for each in self.children.values():
            each.print(deep+1)


if __name__ == '__main__':
    nt= NameTree()

    nt.access(Name('/A/a/1'))
    nt.print()

    print('--------------------------------')
    p= nt.get(Name('/A/a'))
    print(p, p.name())

    p= nt.get(Name('/A/a/2'))
    print(p)

    p= nt.longest(Name('/A/a/2'))
    print(p, p.name())

    print('--------------------------------')
    for each in nt:
        print(each, f'"{each.name()}"')

    print('--------------------------------')
    for each in nt.access(Name('')):
        print(each, f'"{each.name()}"')

