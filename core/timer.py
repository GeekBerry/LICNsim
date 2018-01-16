from collections import defaultdict, deque


class Event:
    def __init__(self, func=None, *args, **kwargs):
        self.func= func
        self.args= args
        self.kwargs= kwargs

    def __bool__(self):
        return self.func is not None

    def execute(self)->None:
        if self:
            func, args, kwargs= self.func, self.args, self.kwargs
            self.clear()  # XXX 要在func执行前清理, 以便执行中判断bool(event)为False
            func(*args, **kwargs)

    def clear(self):
        self.func= None
        self.args= ()
        self.kwargs= {}


class Clock:
    __instance= None

    def __new__(cls):  # 单例模式
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self._time= 0  # int 当前时间
        self._todo= defaultdict(deque)  # { time:deque( event,...), } 要被执行的事件列表

    @property
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

        event= Event(func, *args, **kwargs)
        self._todo[self._time+delay].append(event)
        return event


clock= Clock()  # 全局变量  XXX 是否要使用单例模式？


class Timer:
    def __init__(self, func):
        self.func= func
        self.event= Event()

    def __bool__(self):
        return bool(self.event)

    def timing(self, delay):
        self.event.clear()
        self.event= clock.timing(delay, self.func)

    def cancel(self):
        self.event.clear()

