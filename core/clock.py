#!/usr/bin/python3
#coding=utf-8

class Clock:
    class ID:#定时器id
        def __init__(self, time= None, index= None):
            self._time= time
            self._index= index

        def __bool__(self):
            return self._time is not None

        def clear(self):
            self._time= None
            self._index= None

        def getTime(self):
            return self._time

        def getIndex(self):
            return self._index


    def __init__(self):
        self.__time= 0  # int 当前时间
        self.__todo= {} #{ _time:[ CallBack,...], } 要被执行的事件列表

    def __bool__(self):
        return len(self.__todo) > 0

    def time(self):
        return self.__time

    def timing(self, delay, func):  # -> Clock.CallBack 或 None
        """
        设置定时执行函数
        :param delay 执行时间，从当前时间起的step数
        :param func 要执行的函数, 无参数
        """
        if not isinstance(delay, int):
            raise TypeError("delay 必须int型")
        if delay < 0:
            raise KeyError("delay 设置必须大于等于0")

        functions= self.__todo.setdefault( self.__time+delay, [] )
        functions.append(func)
        return Clock.ID( self.__time+delay, len(functions)-1 )  # 在键为self.__time+delay的列表中第len(functions)-1项

    def cancel(self, clock_id):  # 会修改id
        if type(clock_id) == Clock.ID \
        and clock_id.getTime() in self.__todo\
        and 0<= clock_id.getIndex() < len( self.__todo[clock_id.getTime()] ):
            self.__todo[clock_id.getTime()][clock_id.getIndex()]= None
            clock_id.clear()

    def step(self):
        if self.__time in self.__todo:
            for func in self.__todo[self.__time]:  # 列表遍历时可追加
                if func:  # 如果func有效(没被cancel等)
                    func()  # 执行, 一定为无参数类型
            del self.__todo[self.__time] # 删除此时间事件, 不能再之前直接用pop
        self.__time += 1  # 时间片自增


    def clear(self):
        self.__time= 0
        self.__todo= {}




class Timer: #管理callback
    def __init__(self, func, *args):
        self._func= func
        self._args= args
        self._timeid= Clock.ID()

    def __bool__(self):
        return bool(self._timeid)

    def timing(self, time):# 定时或重新定时
        clock.cancel(self._timeid)
        self._timeid= clock.timing(time, self._execute)

    def cancel(self):
        clock.cancel(self._timeid)

    def _execute(self):
        self._timeid.clear() #清空操作必须放到执行前, 以免执行中对_timeid进行定时后又被清空
        self._func(*self._args) #执行

    def __del__(self):
        self.cancel()

    def __repr__(self):
        return "[%d] %s %s"%(self._timeid.getTime(), self._func, self._args)

clock= Clock()
