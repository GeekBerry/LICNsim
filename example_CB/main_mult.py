#!/usr/bin/python3
#coding=utf-8


# from core.common import timeProfile
# timeProfile('import example_CB.main')


import time
import itertools
import os
from core.common import setSysKwargs

def python(filename, **kwargs):
    os.system(f'python {filename} {setSysKwargs(**kwargs)}')
#-----------------------------------------------------------------------------------------------------------------------
date= time.strftime("%y%m%d%H%M%S", time.localtime())

graph_s= ['Grid']  # ['Grid', 'BA', 'Tree']
sim_second= 500
cs_mode_s= ['FIFO', 'LRU']
cs_time_s= [60, 80, 100]
numfunc_s= ['Fixed', 'Possion']
lambda_s= [60, 80, 100]
posfunc_s= ['Uniform']
repeat_s= range(0,1)

#-----------------------------------------------------------------------------------------------------------------------
experiment= []
for graph_name, cs_mode, cs_time ,numfunc, lam, posfunc, repeat in itertools.product(graph_s, cs_mode_s, cs_time_s, numfunc_s, lambda_s, posfunc_s, repeat_s):
    kwargs={}
    kwargs['date']= date
    kwargs['graph_name']= graph_name
    kwargs['sim_second']= sim_second
    kwargs['cs_mode']= cs_mode
    kwargs['cs_time']= cs_time
    kwargs['numfunc']= numfunc
    kwargs['lam']= lam
    kwargs['posfunc']= posfunc
    kwargs['repeat']= repeat
    experiment.append(kwargs)

#-----------------------------------------------------------------------------------------------------------------------
import multiprocessing

if __name__ == "__main__":
    print("Start")
    cpu_num= multiprocessing.cpu_count()
    pool = multiprocessing.Pool( processes= max(4, cpu_num) )

    for kwargs in experiment:
        pool.apply_async(func= python, args= ('main.py',), kwds= kwargs)

    pool.close()
    pool.join()   # 调用join之前，先调用close函数，否则会出错。执行完close后不会有新的进程加入到pool,join函数等待所有子进程结束
    print("End")

