
class Name(tuple):
    def __new__(cls, iterable=None):
        if iterable is None:
            return tuple.__new__(cls)
        if isinstance(iterable, str):
            return tuple.__new__(cls, iterable.split('/'))
        else:
            return tuple.__new__(cls, map(str, iterable))

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

    def __repr__(self):
        return f"Name('{self}')"


if __name__ == '__main__' and 0:
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
    def __init__(self, parent=None, key=None):
        self._parent = parent
        self.__key = key  # 自己在父节点中的键值
        self._children = dict()
        self._value_count = 0  # 记录一个 NameTree 节点及所有子节点中, 有效节点数量; 在 'value' 增删时会更新
        # self.value 在setValue时添加, 被delValue时删除

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

    def getValue(self):
        return getattr(self, 'value')

    def delValue(self):  # 删除一个节点是, 会检查前面value_count为0的节点, 把整个空枝剪下
        delattr(self, 'value')

        cut_node = None  # 标记最前一个 value_count 为 0 的祖先节点
        for each in self.forebears():  # 注: forebears 包含自身
            each._value_count -= 1
            if each._value_count == 0:
                cut_node = each

        if cut_node is not None:
            cut_node.cutDown()
            cut_node.clear()

    # -------------------------------------------------------------------------
    def print(self, deep=0):  # XXX for DEBUG
        print('\t' * deep, f'{repr(self.key)}:{self.__dict__}')
        for each in self._children.values():
            each.print(deep + 1)


# ----------------------------------------------------------------------------------------------------------------------
class NameTable:
    """
    依靠 NameTree.hasValue() 判断节点有效性
    """

    def __init__(self, default_factory=None):
        self.root = NameTree()
        self._default_factory= default_factory

    def __contains__(self, name):
        node = self.root.get(name)
        return (node is not None) and node.hasValue()

    def __len__(self):
        return self.root.valueCount()

    def __iter__(self):
        return self.keys()

    def keys(self):
        for node in self.root.descendants():
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
        if self._default_factory is None:  # 没有默认值函数
            node = self.root.get(name)
            if node and node.hasValue():
                return node.getValue()
            else:
                raise KeyError(name)
        else:  # 有默认值函数
            node = self.root.access(name)
            if not node.hasValue():
                node.setValue( self._default_factory() )
            return node.getValue()

    def __setitem__(self, name, value):
        self.root.access(name).setValue(value)

    def __delitem__(self, name):
        node = self.root.get(name)
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
        node = self.root.access(name)
        if not node.hasValue():
            node.setValue(default)
        return node.getValue()

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
    def forebear(self, name) -> iter:  # 有效祖先(含自己)生成器
        name_node = self.root.longest(name)
        for pre_node in name_node.forebears():
            if pre_node.hasValue():
                yield pre_node.name()

    def descendant(self, name) -> iter:  # 有效子孙(含自己)生成器 (先根序)
        name_node = self.root.get(name)
        if name_node is not None:
            for pre_node in name_node.descendants():
                if pre_node.hasValue():
                    yield pre_node.name()
        else:
            raise StopIteration

    def __repr__(self):
        return str(dict(self.items()))


if __name__ == '__main__':
    table= NameTable()

    table[Name('A')] = None
    table[Name('A/a/1')] = None
    table[Name('A/a/2')] = None
    table[Name('B')] = None
    print(table)  # {Name('A'): None, Name('A/a/1'): None, Name('A/a/2'): None, Name('B'): None}

    p= list(  table.descendant( Name('A') )  )
    print(p)  # [Name('A'), Name('A/a/1'), Name('A/a/2')]

    p= list(  table.descendant( Name() )  )
    print(p)  # [Name('A'), Name('A/a/1'), Name('A/a/2'), Name('B')]

    del table[Name('A')]
    print(table)  # {Name('A/a/1'): None, Name('A/a/2'): None, Name('B'): None}