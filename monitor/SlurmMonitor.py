# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: SlurmMonitor.py
@time: 2019/4/29 上午10:24 
"""

import sched
import time


def slurm_query_func(handlers=[]):
    pass


class SlurmMonitor(object):

    def __init__(self, query_func, time_interval=10, *args, **kwargs):
        self.handlers = []
        self.time_interval = time_interval  # 多长时间监控数据库一次
        self.query_func = query_func
        self._sceduler = sched.scheduler(time.time, delayfunc=time.sleep)

    def add_handler(self, func, *args, **kwargs):
        self.handlers.append((func, args, kwargs))  # 查询数据库后调用的操作

    def start(self):
        pass


