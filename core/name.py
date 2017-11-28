
class Name(tuple):
    def __new__(cls, iterable=None):
        if iterable is None:
            return tuple.__new__(cls)
        if isinstance(iterable, str):
            return tuple.__new__(cls, iterable.split('/'))
        else:
            return tuple.__new__(cls, map(str, iterable))

    # @classmethod
    # def fromArgs(cls, *args):
    #     return Name(args)

    # @classmethod
    # def fromStr(cls, string):
    #     return Name(string.split('/'))

    def matchLength(self, other)->int:
        """
        找出共同前缀长度
        :param other:Name
        :return:int
        """
        match_len = 0
        for sge1, sge2 in zip(self, other):
            if sge1 == sge2:
                match_len += 1
            else:
                break
        return match_len

    def isPrefix(self, name):
        return self.matchLength(name) == len(self)

    def __str__(self):
        return '/'.join(map(str, self))


if __name__ == '__main__':
    name1= Name('A/1')
    name2= Name('A/1')
    print(name1.isPrefix(name2), name2.isPrefix(name1))  # True True

    name1= Name('A/1')
    name2= Name('A')
    print(name1.isPrefix(name2), name2.isPrefix(name1))  # False True

    name1= Name('A/1')
    name2= Name('B')
    print(name1.isPrefix(name2), name2.isPrefix(name1))  # False False

    name1= Name('')
    name2= Name('A')
    print(name1.isPrefix(name2), name2.isPrefix(name1))  # False False



# ----------------------------------------------------------------------------------------------------------------------
class NameTree:
    _value_count = 0  # 记录一个 NameTree 节点及所有子节点中, 有效节点数量; 在 'value' 增删时会更新

    def __init__(self, parent=None, key=None):
        self._parent = parent
        self.__key = key  # 自己在父节点中的键值
        self._children = dict()

    def __iter__(self):
        return iter(self._children.values())

    def forebears(self):  # 倒序遍历 Path. 包含自身, 包含根节点
        cur_node = self
        while cur_node:
            yield cur_node
            cur_node = cur_node._parent

    def descendants(self):  # 递归遍历自己和所有子节点 (先根遍历)
        yield self
        for child in self._children.values():
            for each in child.descendants():
                yield each

    @property
    def key(self):
        return self.__key

    def name(self):
        forebear_list = list(self.forebears())
        forebear_list.pop(-1)  # 不包含根节点
        return Name(  [ name_node.key for name_node in reversed(forebear_list) ]  )

    # -------------------------------------------------------------------------
    def access(self, name):
        cur_node = self
        for seg_key in name:
            if seg_key not in cur_node._children:
                cur_node._children[seg_key] = self.__class__(cur_node, seg_key)
            cur_node = cur_node._children[seg_key]
        return cur_node

    def get(self, name):
        cur_node = self
        for segment in name:
            cur_node = cur_node._children.get(segment)
            if cur_node is None:
                return None
        return cur_node

    def longest(self, name):  # 寻找最长前缀匹配的节点
        cur_node = self
        for segment in name:
            if segment in cur_node._children:
                cur_node = cur_node._children[segment]
            else:
                break
        return cur_node

    def discard(self, name):
        name_node = self.get(name)
        if name_node is not None:
            name_node.cutDown()

    # -------------------------------------------------------------------------
    def cutDown(self):  # 将节点从树上剪下
        if self._parent:
            del self._parent._children[self.key]
        return self

    def clear(self):
        self._parent = None
        self.__key = None
        self._children = {}

    # -------------------------------------------------------------------------
    def valueCount(self):
        return self._value_count

    def hasValue(self):
        return hasattr(self, 'value')

    def setValue(self, value):
        if not self.hasValue():  # 新增
            for each in self.forebears():
                each._value_count += 1
        setattr(self, 'value', value)

    def setDefaultValue(self, default=None):
        if not self.hasValue():
            self.setValue(default)
        return self.getValue()

    def getDefaultValue(self, default=None):
        if self.hasValue():
            return self.getValue()
        else:
            return default

    def getValue(self):
        return getattr(self, 'value')

    def delValue(self):
        delattr(self, 'value')

        cut_node = None
        for each in self.forebears():  # 注: forebears 包含自身
            each._value_count -= 1
            if each._value_count == 0:  # 找到最前一个 value_count 为 0 的祖先
                cut_node = each

        if cut_node is not None:
            cut_node.cutDown()
            cut_node.clear()

    # -------------------------------------------------------------------------
    def print(self, deep=0):  # DEBUG
        print('\t' * deep, f'{repr(self.key)}:{self.__dict__}')
        for each in self._children.values():
            each.print(deep + 1)

    # def __repr__(self):
    #     if self.hasValue():
    #         return f'{self.name()}:{self.value}'
    #     else:
    #         return str(self.name())


# if __name__ == '__main__':
#     nt= NameTree()
#     nt.access( Name('A/a/1') )
#     nt.access( Name('A/a/2') )
#     nt.access( Name('A/b') )
#
#     p= list( nt.descendants() )
#     print(p)

# if __name__ == '__main__':
#     nt= NameTree()
#
#     nt.access(Name('A/a/1'))
#     nt.access(Name(['A','a',2]))
#     nt.print()
#
#     print('--------------------------------')
#     p= nt.get(Name('A/a'))
#     print(p, p.name())  # <__main__.NameTree object at 0x000002A32ABE2978> A/a
#
#     p= nt.get(Name('A/a/3'))
#     print(p)  # None
#
#     p= nt.longest(Name('A/a/3'))
#     print(p, p.name())  # <__main__.NameTree object at 0x0000027F9CBF2978> A/a
#
#     # print('--------------------------------')
#     # for each in nt:
#     #     print(each, f'"{each.name()}"')
#
#     nt.discard( Name('A/a') )
#     nt.print()


# ----------------------------------------------------------------------------------------------------------------------
class NameTable:
    """
    依靠 NameTree.hasValue() 判断节点有效性
    """

    def __init__(self):
        self.name_tree = NameTree()

    def __contains__(self, name):
        node = self.name_tree.get(name)
        return (node is not None) and node.hasValue()

    def __len__(self):
        return self.name_tree.valueCount()

    def keys(self):
        for node in self.name_tree.descendants():
            if node.hasValue():
                yield node.name()

    def values(self):
        for name in self.keys():
            yield self.get(name)

    def items(self):
        for name in self.keys():
            yield name, self.get(name)

    # -------------------------------------------------------------------------
    def __getitem__(self, name):
        node = self.name_tree.get(name)
        try:
            return node.getValue()
        except AttributeError:
            raise KeyError(name)

    def __setitem__(self, name, value):
        self.name_tree.access(name).setValue(value)

    def __delitem__(self, name):
        node = self.name_tree.get(name)
        try:
            node.delValue()
        except AttributeError:
            raise KeyError(name)

    # -------------------------------------------------------------------------
    def get(self, name, default=None):
        try:
            return self.__getitem__(name)
        except KeyError:
            return default

    def setdefault(self, name, default=None):
        node = self.name_tree.access(name)
        return node.setDefaultValue(default)

    def discard(self, name):
        try:
            self.__delitem__(name)
        except KeyError:
            pass

    def pop(self, name):
        try:
            value = self.__getitem__(name)
        except KeyError:
            raise KeyError(name)
        else:
            self.__delitem__(name)
            return value

    # -------------------------------------------------------------------------
    def forebear(self, name) -> iter:  # 有效祖先生成器
        name_node = self.name_tree.longest(name)
        for pre_node in name_node.forebears():
            if pre_node.hasValue():
                yield pre_node.name()

    def descendant(self, name) -> iter:  # 有效子孙生成器 (先根序)
        name_node = self.name_tree.get(name)
        if name_node is not None:
            for pre_node in name_node.descendants():
                if pre_node.hasValue():
                    yield pre_node.name()
        else:
            raise StopIteration

    def __repr__(self):
        return str(dict(self.items()))

# if __name__ == '__main__':
#     t= NameTable()
#
#     t[('A',1)]= 1
#     p= t.descendantValues( ('A',) )
#     print( list(p) )


# if __name__ == '__main__':
#     t= NameTable()
#
#     t[ ('A',) ]= 1
#     t[ Name('A/1') ]= 10
#     t[ Name('A/1') ]= 10
#     print(t)  # {Name('A'): 1, Name('A/1'): 10}
#     t.name_tree.print()
#     """
#      None:{'_parent': None, '_NameTree__key': None, '_children': {'A': 'A'}, 'value_count': 2}
#          'A':{'_parent': None, '_NameTree__key': 'A', '_children': {'1': '1'}, 'value': 1, 'value_count': 2}
#              '1':{'_parent': 'A', '_NameTree__key': '1', '_children': {}, 'value': 10, 'value_count': 1}
#     """
#
#     a= t.get( Name('A/2') )
#     print(a)  # None
#     t.name_tree.print()
#     """
#      None:{'_parent': None, '_NameTree__key': None, '_children': {'A': 'A'}, 'value_count': 2}
#          'A':{'_parent': None, '_NameTree__key': 'A', '_children': {'1': '1'}, 'value': 1, 'value_count': 2}
#              '1':{'_parent': 'A', '_NameTree__key': '1', '_children': {}, 'value': 10, 'value_count': 1}
#     """
#
#     print(   list(  t.forebears( Name('A/1') )  )   )  # [10, 1]
#     print(   list(  t.descendants( Name('A/1') )  )   )  # [10]
#
#     del t[ Name(['A']) ]
#     print(t)  # {Name('A/1'): 10}
#     t.name_tree.print()
#     """
#      None:{'_parent': None, '_NameTree__key': None, '_children': {'A': 'A'}, 'value_count': 1}
#          'A':{'_parent': None, '_NameTree__key': 'A', '_children': {'1': '1'}, 'value_count': 1}
#              '1':{'_parent': 'A', '_NameTree__key': '1', '_children': {}, 'value': 10, 'value_count': 1}
#     """
#
#     del t[ Name('A/1') ]
#     print(t)  # {}
#     t.name_tree.print()  # None:{'_parent': None, '_NameTree__key': None, '_children': {}, 'value_count': 0}
