from collections import defaultdict, deque


class Handle:
    def __init__(self, func=None, *args, **kwargs):
        self.func= func
        self.args= args
        self.kwargs= kwargs

    def __bool__(self):
        return self.func is not None

    def execute(self)->None:
        func, args, kwargs= self.func, self.args, self.kwargs
        self.clear()  # XXX 要在func执行前清理, 以便执行中判断bool(handle)为False
        func(*args, **kwargs)

    def clear(self):
        self.func= None
        self.args= ()
        self.kwargs= {}


class Clock:
    def __init__(self):
        self._time= 0  # int 当前时间
        self._todo= defaultdict(deque)  # { _time:deque( Handle,...), } 要被执行的事件列表
        self._executing= False

    def __bool__(self):
        return bool(self._todo)

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
    def timing(self, delay, func, *args, **kwargs):
        assert isinstance(delay, int)  # delay 必须int型
        assert delay >= 0  # delay 设置必须大于等于0

        handle= Handle(func, *args, **kwargs)
        self._todo[self._time+delay].append(handle)
        return handle


clock= Clock()  # 全局变量


class Timer:
    def __init__(self, func):
        self.func= func
        self.handle= Handle()
        self._exe_time= None

    def __bool__(self):
        return bool(self.handle)

    @property
    def exe_time(self):
        return self._exe_time

    def timing(self, delay, *args):
        self.handle.clear()
        self.handle= clock.timing(delay, self.func, *args)
        self.__exe_time= clock.time() + delay

    def cancel(self):
        self.handle.clear()

    def __repr__(self):
        return f'Timer({self._exe_time}: {self.func})'


# if __name__ == '__main__':
#     def selftiming():
#         print('Second')
#         clock.timing(0, print, 'Fourth', end='#')
#
#     clock.timing(1, selftiming)
#     clock.timing(1, print, 'Third')
#
#     clock.step()
#     clock.step()

