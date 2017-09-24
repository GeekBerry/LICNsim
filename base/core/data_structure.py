#!/usr/bin/python3
#coding=utf-8

from debug import showCall
from common import logging
from collections import deque, defaultdict
from base.core import Timer, clock


def top(iterable):
    """
    iterable 中有 None 和 StopIteration 将无法区别, 请分清使用场景
    :param iterable:
    :return: None or Any
    """
    try:
        return next(iter(iterable))
    except StopIteration:
        return None


def setLimitedSub(set_obj, iterable, limit:int):
    for each in iterable:
        if len(set_obj) > limit:
            set_obj.discard(each)
        else: return

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
        self.callbacks= []

    def __len__(self):
        return len(self.callbacks)

    def __iter__(self):
        return iter(self.callbacks)

    def __call__(self, *args):
        for callback in self.callbacks:
            callback(*args)

        # if len(self.callbacks) == 0:
        #     Announce.printEmptyWarring(*args)

    def pushHead(self, func):
        self.callbacks.insert(0, func)

    def append(self, func):
        self.callbacks.append(func)

    def discard(self, func):
        try:
            self.callbacks.remove(func)
        except ValueError:
            pass


class AnnounceTable(defaultdict):  # 不带Log版
    def __init__(self):
        super().__init__(Announce)


# ======================================================================================================================
def tupleClass(*fields):
    class TupleClass:
        FIELDS = fields

        def __init__(self, *args):
            for k, v in zip(self.FIELDS, args):
                setattr(self, k, v)

        def __repr__(self):
            return f'{self.__class__.__name__}{self.__dict__}'

    return TupleClass


# if __name__ == '__main__':
#     Point= tupleClass('x', 'y')
#     p= Point(0.1, 0.2)
#     print(p.x, p.y)
#     print(p)


# ======================================================================================================================
def decorator(Type):  # 对象装饰器  FIXME 测试, 用例
    class Decorator:
        def __init__(self, inner):
            super().__setattr__('_inner', inner)

        # 批量定义重载函数
        rewrite_methods= set( dir(Type) ) - set( dir(type) )  # FIXME 如何找到 Type 所有自定义函数
        for method_name in rewrite_methods:
            exec(f'''
def {method_name}(self, *args, **kwargs):
    return self._inner.__class__.{method_name}(self._inner, *args, **kwargs)
''')  # XXX 利用 __class__ 来调用, 是实现嵌套中, 将部分处理交由上层而不会造成递归的关键; 见(BaseDictDecorator)

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
#     print(isinstance(decortor, dict))  # False
#
#     decortor[3]= 300  # print: D.setitem 3 300
#     print(table) # {1: 100, 2: 200, 3: 300} 注意table被修改了


# ----------------------------------------------------------------------------------------------------------------------
class BaseDictDecorator(decorator(dict)):
    def __init__(self, table):
        super().__init__(table)

        assert hasattr(table, '__setitem__') and hasattr(table, '__getitem__') and hasattr(table, '__delitem__')
        try:  # 链接处理链
            table.__delitem__ = self.__delitem__  # 内部可能会引起状态变化的量, 交由外部处理
            table.__setitem__ = self.__setitem__  # 内部可能会引起状态变化的量, 交由外部处理
            table.__getitem__ = self.__getitem__  # 内部可能会引起状态变化的量, 交由外部处理
        except AttributeError:
            pass

    # 约定 get(item) 函数不会引起状态变化

    def setdefault(self, key, default=None):  # 利用链接过的函数实现, 减少状态可变子类的函数重载量
        try:
            return self.__getitem__(key)
        except KeyError:
            self.__setitem__(key, default)
            return default

    def pop(self, key):  # 利用链接过的函数实现, 减少状态可变子类的函数重载量
        value= self.__getitem__(key)
        self.__delitem__(key)
        return value

    # 一些不用的, 但会引起 dict 变化的重载
    def update(self): raise NotImplementedError

    def popitem(self): raise NotImplementedError


class SizeDictDecorator(BaseDictDecorator):
    size_evict_call_back= EMPTY_FUNC

    def __init__(self, table, max_size, set_trigger= True, get_trigger= False):
        super().__init__(table)
        self.max_size= max_size
        self.set_trigger= set_trigger
        self.get_trigger= get_trigger

        self.key_queue= deque(self.keys())  # deque(key1, ...)  排在前面的先删除
        self.limit()

    def setMaxSize(self, value):
        self.max_size= value

    def setSizeEvictCallback(self, func):
        self.size_evict_call_back= func

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if key not in self.key_queue:
            self.key_queue.append(key)
            self.limit()
        elif self.set_trigger:  # move to end
            self.key_queue.remove(key)
            self.key_queue.append(key)

    def __getitem__(self, key):
        value= super().__getitem__(key)
        if self.get_trigger:  # move to end
            self.key_queue.remove(key)
            self.key_queue.append(key)
        return value

    def __delitem__(self, key):
        super().__delitem__(key)
        self.key_queue.remove(key)

    def limit(self):
        while len(self) > self.max_size:
            key= top(self.key_queue)
            self.size_evict_call_back(key)
            self.__delitem__(key)


# if __name__ == '__main__':
#     d = {1: 100, 2:200, 3:300}
#
#     t1= SizeDictDecorator(d, 2)
#     t1.delete_call_back= lambda *args: print('evict', *args)
#
#     print(d)  # {2: 200, 3: 300}
#
#     t1[4]= 400  # evict 2 200
#     print(d)  # {3: 300, 4: 400}
#
#     del t1[3]  # evict 3 300
#     print(d)  # {4: 400}


class TimeDictDecorator(BaseDictDecorator):
    time_evict_call_back= EMPTY_FUNC

    def __init__(self, table, life_time, set_trigger= True, get_trigger= False):
        super().__init__(table)
        self.life_time= life_time
        self.set_trigger= set_trigger
        self.get_trigger= get_trigger

        self.timer= Timer(self.flush)
        self.info= dict.fromkeys( table.keys(), clock.time() )  # XXX 在 python 3.6 及中, dict是有序的
        self.timer.timing(self.life_time)

    def setLifeTime(self, value):
        self.life_time= value

    def setTimeEvictCallback(self, func):
        self.time_evict_call_back= func

    def __getitem__(self, key):
        value= super().__getitem__(key)
        if self.get_trigger:
            del self.info[key]  # XXX 在 python 3.6 及中, dict是有序的
            self.info[key]= clock.time() + self.life_time
        return value

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if key not in self.info:
            self.info[key]= clock.time() + self.life_time
        elif self.set_trigger:
            del self.info[key]  # XXX 在 python 3.6 及中, dict是有序的
            self.info[key]= clock.time() + self.life_time

        if not self.timer:
            self.timer.timing(self.life_time)

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.info[key]

    def flush(self):
        cur_time= clock.time()

        del_keys= []
        for key, dead_time in self.info.items():
            if dead_time <= cur_time:
                del_keys.append(key)
            else:
                # self.timer.timing(self.life_time)     # 方案1: 条目最大生存时长而 2*self.life_time-1
                self.timer.timing(dead_time - cur_time)  # 方案2: 删除更及时, 操作更频繁
                break

        for key in del_keys:
            self.time_evict_call_back(key)
            self.__delitem__(key)

# if __name__ == '__main__':
#     d = {1: 100, 2:200, 3:300}
#
#     t1= TimeDictDecorator(d, 2)
#     print(d)  # {1: 100, 2: 200, 3: 300}
#
#     clock.step()
#     clock.step()
#     p= t1[3]
#     print(d)  # {1: 100, 2: 200, 3: 300}
#
#     clock.step()
#     print(d)  # {3: 300}


class DefaultDictDecorator(BaseDictDecorator):
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


# if __name__ == '__main__':
#     t= {}
#     t1= DefaultDictDecorator(t, int)
#
#     print(t1['A'])  # 0
#     print(t)  # {'A': 0}


# if __name__ == '__main__':
#     d = {1: 100, 2:200, 3:300}
#     t1= SizeDictDecorator(d, 2)
#     t2= TimeDictDecorator(t1, 2)
#
#     print(clock.time(), d, t1.key_queue, t2.info)  # 0 {2: 200, 3: 300} deque([2, 3]) {2: 0, 3: 0}
#
#     clock.step()
#     p= t2[3]
#     print(clock.time(), d, t1.key_queue, t2.info)  # 1 {2: 200, 3: 300} deque([2, 3]) {2: 0, 3: 3}
#
#     clock.step()
#     t2[4]= 400
#     print(clock.time(), d, t1.key_queue, t2.info)  # 2 {3: 300, 4: 400} deque([3, 4]) {3: 3, 4: 4}
#
#     clock.step()
#     t2[4]= 4000
#     print(clock.time(), d, t1.key_queue, t2.info)  # 3 {3: 300, 4: 4000} deque([3, 4]) {3: 3, 4: 5}
#
#     clock.step()
#     clock.step()
#     print(clock.time(), d, t1.key_queue, t2.info)  # 5 {4: 4000} deque([4]) {4: 5}
#
#     clock.step()
#     print(clock.time(), d, t1.key_queue, t2.info)  # 6 {} deque([]) {}
#
#     clock.step()
#     t2[1]= 1000
#     print(clock.time(), d, t1.key_queue, t2.info)  # 7 {1: 1000} deque([1]) {1: 9}

