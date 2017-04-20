#!/usr/bin/python3
#coding=utf-8

import types
def singleton(cls, *args, **kw):
    instance={}
    def _singleton():
        if cls not in instance:
            instance[cls]=cls(*args, **kw)
        return instance[cls]
    return _singleton

def objName(obj):  # TODO 整理重写
    if type(obj) == types.MethodType:
        addr= hex(id(obj.__self__))
        return f'{obj.__qualname__}<{addr}>'
    elif type(obj) == types.FunctionType:
        return obj.__qualname__
    elif isinstance(obj, type):
        return obj.__qualname__
    elif type(obj) == types.BuiltinFunctionType:
        return obj.__qualname__
    else:
        addr= hex(id(obj))
        return f'{obj.__class__.__qualname__}<{addr}>'

#=======================================================================================================================
import sys
def getSysKwargs()->dict:
    return dict([ part.split('=') for part in sys.argv[1:] ])

def setSysKwargs(**kwargs)->str:
    string= ''
    for k,v in kwargs.items():
        string += f'{k}={v} '
    return string

#=======================================================================================================================
from core.data_structure import CallTable, AnnounceTable

class Hardware:
    def __init__(self, name):
        self.name= name
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
        pass

    def uninstall(self, announces, api):
        pass

    def __str__(self):
        return objName(self)
