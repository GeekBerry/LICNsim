#!/usr/bin/python3
# coding=utf-8


import os
# ======================================================================================================================
import sys


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


