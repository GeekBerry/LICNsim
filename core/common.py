#!/usr/bin/python3
# coding=utf-8




def singleton(cls, *args, **kw):
    instance={}

    def _singleton():
        if cls not in instance:
            instance[cls]=cls(*args, **kw)
        return instance[cls]
    return _singleton


def strPercent(value):
    return '%0.2f%%'%( value*100 )
# ======================================================================================================================
import sys
import os


def getFileClass(path):
    folder, file_name= os.path.dirname(path), os.path.basename(path)
    module_name, suffix= os.path.splitext(file_name)

    if suffix == '.py':
        sys.path.insert(0, folder)
        module= __import__(module_name)
        return [ value for value in module.__dict__.values() if isinstance(value, type) ]
    else:
        return []

def getSysKwargs()->dict:
    return dict([ part.split('=') for part in sys.argv[1:] ])


def setSysKwargs(**kwargs)->str:
    string= ''
    for k,v in kwargs.items():
        string += f'{k}={v} '
    return string

# ======================================================================================================================
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
        # self.announces= None
        # self.api= None
        pass


