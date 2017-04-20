#!/usr/bin/python3
#coding=utf-8

import inspect
class LabelTable:
    class Reference:
        def __init__(self, callback):
            self.callback= callback

        def __repr__(self):
            return self

        def __str__(self):
            return ''.join( str(each) for each in self.callback() )


    def __init__(self):
        self.table= {}

    def clear(self):
        self.table.clear()

    def __getitem__(self, obj):
        if id(obj) not in self.table:
            self.table[ id(obj) ]= self._defaultLable(obj)
        return self.Reference(  lambda: self.table[ id(obj) ]  )

    def __setitem__(self, obj, value):  # value:( str| LabelTable.Reference, ...)
        if type(value) is str:
            self.table[ id(obj) ]= value,
        elif type(value) is tuple:
            contents= []
            for each in value:  # 将参数字符化
                if type(each) is LabelTable.Reference:# 标签直接储存
                    contents.append(each)
                else:  # 用字符串记录以免储存引用
                    contents.append( str(each) )
            self.table[ id(obj) ]= contents
        else:
            raise TypeError("value must be str or tuple")

    def __delitem__(self, obj):
        if id(obj) in self.table:
            del self.table[ id(obj) ]

    def _defaultLable(self, obj):
        if inspect.ismethod(obj):
            return self[obj.__self__], obj.__name__ # (obj name, methon name, )
        elif inspect.isbuiltin(obj) or inspect.isfunction(obj):
            return obj.__qualname__,
        else:
            return "%s<%X>"%( obj.__class__.__qualname__, id(obj) ),


class NoLabelTable:
    def __setitem__(self, obj, value):
        pass

    def __getitem__(self, obj):
        return ""

    def __delitem__(self, key):
        pass

    def clear(self):
        pass

#=======================================================================================================================
class Logger:
    class LEVEL:
        NOLOG= 0
        ERROR= 1
        WARING= 2
        INFO= 3
        DEBUG= 4
        TRACK= 5

    def __init__(self, level):
        self.level= level
        # self.file= open('log.md', 'w')

    def __del__(self):
        # self.file.close()
        pass

    def track(self, *content):
        if self.level >= Logger.LEVEL.TRACK :
            self.__log('TRACK', *content)


    def debug(self, *content):
        if self.level >= Logger.LEVEL.DEBUG :
            self.__log('DEBUG', *content)


    def info(self, *content):
        if self.level >= Logger.LEVEL.INFO :
            self.__log('INFO', *content)


    def waring(self, *content):
        if self.level >= Logger.LEVEL.WARING :
            self.__log('WARING', *content)


    def error(self, *content):
        if self.level >= Logger.LEVEL.ERROR :
            self.__log('ERROR', *content)


    def __log(self, level, *content):
        from core.clock import clock
        import time
        data= {}
        data['level']= level
        data['step']= clock.time()
        data['file']= inspect.stack()[2][1]
        data['line']= inspect.stack()[2][2]
        data['function']= inspect.stack()[2][3]
        data['_time']= time.clock()
        data['table']= ' '.join( str(each) for each in content )

        # 打印
        print("[%s]\t(%08d) <%f>: \"%s\\%d\\%s\""%\
            ( data['level'], data['step'], data['_time'], data['file'], data['line'], data['function'])  )
        print('\t', data['table'], '\n')



