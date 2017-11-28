#!/usr/bin/python3
#coding=utf-8

# from common import logging
from collections import deque
from core import Timer, clock, top

# ======================================================================================================================
def EMPTY_FUNC(*args, **kwargs):
    pass


class Bind:
    def __init__(self, func= EMPTY_FUNC, *args):
        self.func= func
        self.args= args  # 注意, 没有进行拷贝

    def __bool__(self):
        return self.func is EMPTY_FUNC

    def clear(self):
        self.func= EMPTY_FUNC
        self.args= None

    def __call__(self, *args, **kwargs):
        return self.func(*self.args, *args, **kwargs)

    def __repr__(self):
        return f'Bind({self.func.__qualname__} {self.args})'


import traceback


class CallTable(dict):
    @staticmethod
    def printUnboundWarring(*args, **kwargs):
        stack_summary= traceback.extract_stack()
        item= stack_summary.format()[-3]  # -3: 经验值, 正好对应调用的位置
        print('UnboundWarring: 没有对应API函数\n', item, end='')
        print('参数:', args, kwargs, end='\n\n')
        pass

    def __getitem__(self, name):
        return self.setdefault( name, Bind(CallTable.printUnboundWarring) )

    def __setitem__(self, name, func):
        callback= self.setdefault(name, Bind() )
        callback.func= func


# if __name__ == '__main__':
#     t= CallTable()
#     p= t['1']
#     t['1']= print
#     p(1,2,3)  # 打印:1 2 3

# ----------------------------------------------------------------------------------------------------------------------

class Announce:
    @staticmethod
    def printEmptyWarring(*args, **kwargs):
        stack_summary= traceback.extract_stack()
        item= stack_summary.format()[-3]  # -3: 经验值, 正好对应调用的位置
        print('EmptyWarring: 没有监听者\n', item, end='')
        print('参数:', args, kwargs, end='\n\n')

    def __init__(self):
        self._funcs= []

    def __len__(self):
        return len(self._funcs)

    def __iter__(self):
        return iter(self._funcs)

    def __call__(self, *args):
        if hasattr(self, 'name'):
            print(f'{self.name} {args}')

        # Debug 每次调用都打印
        for callback in self._funcs:
            callback(*args)

        # Debug 没有监听者时调用
        # if len(self._funcs) == 0:
        #     Announce.printEmptyWarring(*args)

    def prepend(self, func):
        self._funcs.insert(0, func)

    def append(self, func):
        self._funcs.append(func)

    def discard(self, func):
        try:
            self._funcs.remove(func)
        except ValueError:
            pass



class AnnounceTable(dict):  # 带 Log Debug 版
    def __getitem__(self, anno_name):
        if anno_name not in self:
            self[anno_name]= Announce()
            # self[anno_name].name= f'AnnounceTable {id(self)} {anno_name}'
        return self.get(anno_name)


# ======================================================================================================================
# def tupleClass(*fields):
#     class TupleClass:
#         FIELDS = fields
#
#         def __init__(self, *args):
#             for k, v in zip(self.FIELDS, args):
#                 setattr(self, k, v)
#
#         def __repr__(self):
#             return f'{self.__class__.__name__}{self.__dict__}'
#
#     return TupleClass


# if __name__ == '__main__':
#     Point= tupleClass('x', 'y')
#     p= Point(0.1, 0.2)
#     print(p.x, p.y)
#     print(p)


# ======================================================================================================================
def decorator(Type):  # 对象装饰器
    class Decorator:
        def __init__(self, inner):
            super().__setattr__('_inner', inner)

        # 批量定义重载函数
        rewrite_methods= set( dir(Type) ) - set( dir(type) )  # FIXME 如何找到 Type 所有自定义函数
        for method_name in rewrite_methods:
            exec(f'''
def {method_name}(self, *args, **kwargs):
    return self._inner.__class__.{method_name}(self._inner, *args, **kwargs)
''')  # 注意：利用 __class__ 来调用, 是实现嵌套中, 将部分处理交由上层而不会造成递归的关键

        def __getattr__(self, item):
            return getattr(self._inner, item)

        def __repr__(self):
            return f'{self.__class__.__name__}({ repr(self._inner) })'

    return Decorator

# if __name__ == '__main__':
#     class D( decorator(dict) ):
#         def __setitem__(self, key, value):
#             print('D.setitem', key, value)
#             super().__setitem__(key, value)
#
#     table= {1:100, 2:200}
#     decortor= D(table)
#
#     print( isinstance(decortor, dict) )  # False
#
#     decortor[3]= 300  # 打印: D.setitem 3 300
#     print(table)  # {1: 100, 2: 200, 3: 300} 注意table被修改了


class DefaultDictDecorator( decorator(dict) ):
    def __init__(self, table, default_factory):
        super().__init__(table)
        self.default_factory= default_factory

    def __getitem__(self, item):
        try:
            return super().__getitem__(item)
        except KeyError:
            default= self.default_factory()
            self.__setitem__(item, default)
            return default


class TimeSet:
    def __init__(self, life_time):
        self.table= {}  # {key:del_time, ...}
        self.life_time= life_time

    def __contains__(self, item):
        return item in self.table

    def add(self, var):
        self.table[var]= clock.time()
        clock.timing(self.life_time, self.checkDel, var)

    def discard(self, var):
        try:
            del self.table[var]
        except KeyError:
            pass

    def checkDel(self, var):
        add_time= self.table.get(var)
        if (add_time is not None) and ( add_time+self.life_time <= clock.time() ):
            del self.table[var]

    def __str__(self):
        return str(self.table)


# if __name__ == '__main__':
#     tset = TimeSet(2)
#
#     tset.add(1)
#     clock.step()
#
#     tset.add(2)
#     clock.step()
#
#     print(tset)  # {1: 0, 2: 1}
#     tset.add(1)
#
#     clock.step()
#     print(tset)  # {1:2, 2:1}
#
#     clock.step()
#     print(tset)  # {1:2}
#
#     clock.step()
#     print(tset)  # {}


# ---------------------  专用数据结构定义  ----------------------------

class Hardware:
    def __init__(self):
        self.api= CallTable()
        self.announces= AnnounceTable()
        self.units= {}

    def install(self, unit_name, unit):
        unit.install(self.announces, self.api)
        self.units[unit_name]= unit

    def uninstall(self, unit_name):
        unit= self.units[unit_name]
        unit.uninstall(self.announces, self.api)
        del self.units[unit_name]


class Unit:
    def install(self, announces, api):
        self.announces= announces
        self.api= api

    def uninstall(self, announces, api):
        # TODO 完整卸载
        # self.announces= None
        # self.api= None
        pass
