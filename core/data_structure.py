#!/usr/bin/python3
# coding=utf-8

# from common import logging
# from collections import deque

from core import clock, deque, Timer, top


# ======================================================================================================================
def EMPTY_FUNC(*args, **kwargs):
    pass


def DEBUG_FUNC(*args, **kwargs):
    raise NotImplementedError(f'args={args}, kwargs={kwargs}')


class Bind:
    def __init__(self, func=EMPTY_FUNC, *args):
        self.func = func
        self.args = args  # 注意, 没有进行拷贝

    def __bool__(self):
        return self.func is EMPTY_FUNC

    def clear(self):
        self.func = EMPTY_FUNC
        self.args = None

    def __call__(self, *args, **kwargs):
        return self.func(*self.args, *args, **kwargs)

    def __repr__(self):
        return f'Bind({self.func.__qualname__} {self.args})'


import traceback


class CallTable(dict):
    @staticmethod
    def printUnboundWarring(*args, **kwargs):
        stack_summary = traceback.extract_stack()
        item = stack_summary.format()[-3]  # -3: 经验值, 正好对应调用的位置
        print('UnboundWarring: 没有对应API函数\n', item, end='')
        print('参数:', args, kwargs, end='\n\n')
        pass

    def __getitem__(self, name):
        return self.setdefault(name, Bind(CallTable.printUnboundWarring))

    def __setitem__(self, name, func):
        callback = self.setdefault(name, Bind())
        callback.func = func

    def __delitem__(self, name):
        self[name] = CallTable.printUnboundWarring


# if __name__ == '__main__':
#     t= CallTable()
#     p= t['1']
#     t['1']= print
#     p(1,2,3)  # 打印:1 2 3

# ----------------------------------------------------------------------------------------------------------------------

class Announce:
    @staticmethod
    def printEmptyWarring(*args, **kwargs):
        stack_summary = traceback.extract_stack()
        item = stack_summary.format()[-3]  # -3: 经验值, 正好对应调用的位置
        print('EmptyWarring: 没有监听者\n', item, end='')
        print('参数:', args, kwargs, end='\n\n')

    def __init__(self, name=None):
        self._funcs = []

        if name:
            self.name = name

    def __len__(self):
        return len(self._funcs)

    def __iter__(self):
        return iter(self._funcs)

    def __call__(self, *args):
        # DEBUG
        # if hasattr(self, 'name'):
        #     print(f'{self.name} {args}')

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


class AnnounceTable(dict):
    def __getitem__(self, anno_name):
        if anno_name not in self:
            super().__setitem__(anno_name, Announce())
            # super().__setitem__( anno_name, Announce(f'AnnounceTable {id(self)} {anno_name}') ) # DEBUG
        return self.get(anno_name)

    def __setitem__(self, key, value):
        # 禁止直接修改 announce, 以免误写 announce_table['name'] = func 造成麻烦
        raise NotImplementedError


# ======================================================================================================================
def TupleClass(*fields):
    class __TupleClass:
        FIELDS = fields

        def __init__(self, *args):
            for k, v in zip(self.FIELDS, args):
                setattr(self, k, v)

        def __repr__(self):
            return f'{self.__class__.__name__}{self.__dict__}'

        def __iter__(self):
            return iter(self.__dict__.values())

    return __TupleClass


# if __name__ == '__main__':
#     Point= tupleClass('x', 'y')
#     p= Point(0.1, 0.2)
#     print(p.x, p.y)  # 0.1 0.2
#     print(*p)  # 0.1 0.2

# ======================================================================================================================
class descriptor:
    """
    用于代替对属性进行 @property 的 setter 和 getter 设置
    例如：
    class X:
        num = descriptor('a', 'var')
    相当于以下操作
    class X:
        @property
        def num(self):
            return self.a.var

        @num.setter
        def num(self, value):
            self.a.var= value
    """

    def __init__(self, attr, field):
        self.attr = attr
        self.field = field

    def __get__(self, obj, type=None):
        return getattr(getattr(obj, self.attr), self.field)

    def __set__(self, obj, val):
        return setattr(getattr(obj, self.attr), self.field, val)


# if __name__ == '__main__':
#     class A:
#         def __init__(self, var):
#             self.var= var
#
#     class X:
#         num = descriptor('a', 'var')
#         def __init__(self, a):
#             self.a= a
#
#     a= A(100)
#     x= X(a)
#
#     print(x.num)  # 100
#     x.num= 200
#     print(a.var)  # 200


def decorator(Type):  # 对象装饰器
    class Decorator:
        def __init__(self, inner):
            super().__setattr__('_inner', inner)

        # 批量定义重载函数
        rewrite_methods = set(dir(Type)) - set(dir(type))  # FIXME 如何找到 Type 所有自定义函数
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


# class DefaultDictDecorator(decorator(dict)):
#     def __init__(self, table, default_factory):
#         super().__init__(table)
#         self.default_factory = default_factory
#
#     def __getitem__(self, item):
#         try:
#             return super().__getitem__(item)
#         except KeyError:
#             default = self.default_factory()
#             self.__setitem__(item, default)
#             return default

# ======================================================================================================================
class Loop:
    def __init__(self, func, *args, delta=1, delay=0):
        self.timer = Timer(self.__step)
        self.bind = Bind(func, *args)
        self.delta = delta
        self.timer.timing(delay)

    def __step(self):
        self.bind()
        self.timer.timing(self.delta)


class TimeSet:
    def __init__(self, life_time):
        self.table = {}  # {key:del_time, ...}
        self.life_time = life_time

    def __contains__(self, item):
        return item in self.table

    def add(self, var):
        self.table[var] = clock.time
        clock.timing(self.life_time, self.checkDel, var)

    def discard(self, var):
        try:
            del self.table[var]
        except KeyError:
            pass

    def checkDel(self, var):
        add_time = self.table.get(var)
        if (add_time is not None) and (add_time + self.life_time <= clock.time):
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


class Buffer:
    pop = DEBUG_FUNC
    overflow = EMPTY_FUNC

    def __init__(self, rate, capacity):
        self.rate = rate
        self._rest = 0
        self._capacity = capacity

        self.queue = deque()
        self.last_check_time = None
        self.timer = Timer(self.check)

    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, value):
        assert value >= 0
        while len(self.queue) > value:
            self.overflow(*self.queue.pop())
        self._capacity = value

    @property
    def rest(self):
        return self._rest

    def append(self, *args):
        if len(self.queue) >= self._capacity:
            self.overflow(*args)
        else:
            self.queue.append(args)  # 保存参数是一个tuple
            self.check()

    def check(self):
        if self.last_check_time != clock.time:
            self.last_check_time = clock.time
            self._rest = self.rate  # 复位剩余处理

        while self.queue:
            if self._rest > 0:
                self._rest -= 1
                self.pop(*self.queue.popleft())  # 保存参数是一个tuple
            else:
                if not self.timer:  # 如果定时器没被启动过
                    self.timer.timing(1)  # 下一周期再进行检查
                break


from core.common import INF


class LeakBucket:
    Entry = TupleClass('size', 'rest', 'value')

    pop = DEBUG_FUNC
    overflow = EMPTY_FUNC

    def __init__(self, rate, capacity):
        self.rate = rate
        self._rest = rate
        self._occupy = 0
        self._last_reset_time = -INF  # -1 一个比0小的时间

        self._capacity = capacity
        self._size = 0
        self._queue = deque()

        self.timer = Timer(self.check)

    @property
    def capacity(self):
        return self._capacity

    @capacity.setter
    def capacity(self, value):
        assert value >= 0
        self._capacity = value
        self.limit()

    @property
    def size(self):
        return self._size

    def occupy(self):
        self.reset()
        return self._occupy

    def __iter__(self):
        return map(lambda entry: entry.value, self._queue)

    def append(self, value, size=1.0):
        self._size += size
        self._queue.append(self.Entry(size, size, value))
        self.limit()
        self.check()

    def limit(self):
        while self._size > self._capacity:
            size, rest, value = self._queue.pop()
            self._size -= size
            self.overflow(value)

    def check(self):
        self.reset()
        while self._queue:
            if self._rest >= top(self._queue).rest:
                size, rest, value = self._queue.popleft()
                self._size -= size
                self._rest -= rest
                self.pop(value)  # XXX 什么情况用 clock.timing(0, self.pop, value)
            else:
                if not self.timer:
                    top(self._queue).rest -= self._rest  # 消耗掉剩下的尺寸
                    self._rest = 0
                    self.timer.timing(1)  # 下一周期再进行检查
                break

    def reset(self):
        if self._last_reset_time != clock.time:
            if self._last_reset_time == clock.time - 1:
                self._occupy = self.rate - self._rest
            else:
                self._occupy = 0

            self._rest = self.rate
            self._last_reset_time = clock.time


# if __name__ == '__main__':
#     lb = LeakBucket(0.1, 5)
#     lb.pop = lambda value: print('pop', value)
#     lb.overflow = lambda value: print('overflow', value)
#
#     lb.append('A', size=0.3)
#     lb.append('B', size=0.7)
#
#     for i in range(11):
#         print('Time:', clock.time)
#         clock.step()

# if __name__ == '__main__':
#     lb = LeakBucket(2, 5)
#     lb.pop = lambda value: print('pop', value)
#     lb.overflow = lambda value: print('overflow', value)
#
#     print('Time:', clock.time)
#     lb.append('A', size=1)
#     lb.append('B', size=2)
#     lb.append('C', size=1)
#     lb.append('D', size=3)
#     clock.step()
#
#     print('Time:', clock.time)
#     clock.step()
#
#     print('Time:', clock.time)
#     clock.step()

# ---------------------  专用数据结构定义  ----------------------------


class Hardware:
    def __init__(self):
        self.api = CallTable()
        self.announces = AnnounceTable()
        self.units = {}

    def install(self, unit_name, unit) -> bool:
        if unit_name not in self.units:
            self.units[unit_name] = unit
            unit.install(self.announces, self.api)
            return True
        else:
            return False

    def uninstall(self, unit_name) -> bool:
        if unit_name in self.units:
            unit = self.units.pop(unit_name)
            unit.uninstall(self.announces, self.api)
            return True
        else:
            return False


class Unit:
    def install(self, announces, api):
        self.announces = announces
        self.api = api

    def uninstall(self, announces, api):
        self.announces = None
        self.api = None
