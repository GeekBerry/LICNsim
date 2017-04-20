#!/usr/bin/python3
#coding=utf-8

from collections import defaultdict, deque

NoneFunc= lambda:None
class Handle:
    def __init__(self, func=NoneFunc, *args, **kwargs):
        self.func= func
        self.args= args
        self.kwargs= kwargs

    def __bool__(self):
        return self.func is not NoneFunc

    def execute(self)->None:
        # print(__file__, f'[{clock.time()}] {repr(self.func)}')  # DEBUG
        self.func(*self.args, **self.kwargs)
        self.clear()

    def clear(self):
        self.func= NoneFunc
        self.args= ()
        self.kwargs= {}


class Clock:
    def __init__(self):
        self._time= 0  # int 当前时间
        self._todo= defaultdict(deque)  # { _time:deque( Handle,...), } 要被执行的事件列表
        self._executing= False

    def time(self):
        return self._time

    def step(self):
        if self._time in self._todo:
            queue= self._todo[self._time]
            while queue:  # 特别的, 能在遍历时添加
                queue.popleft().execute()
            del self._todo[self._time]
        self._time += 1

    def clear(self):
        self._time= 0
        self._todo.clear()

    #--------------------------------------------------------------------------
    def timing(self, delay, func, *args, __to_head__=False, **kwargs):
        if not isinstance(delay, int):
            raise TypeError("delay 必须int型")
        if delay < 0:
            raise KeyError("delay 设置必须大于等于0")

        handle= Handle(func, *args, **kwargs)
        if __to_head__:
            self._todo[self._time+delay].appendleft(handle)
        else:
            self._todo[self._time+delay].append(handle)
        return handle




class Timer:
    def __init__(self, func, *args, **kwargs):
        self.func= func
        self.args= args
        self.kwargs= kwargs
        self.handle= Handle()

    def __bool__(self):
        return bool(self.handle)

    def timing(self, delay, __to_head__= False):
        self.handle.clear()
        self.handle= clock.timing(delay, self.func, *self.args, **self.kwargs, __to_head__=__to_head__)

    def cancel(self):
        self.handle.clear()

clock= Clock()


if __name__ == '__main__':
    def selftiming():
        print('Second')
        clock.timing(0, print, 'Fourth', end='#')

    clock.timing(1, selftiming)
    clock.timing(1, print, 'Third')
    clock.timing(1, print, 'First', __to_head__=True)

    clock.step()
    clock.step()

