# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: FileMonitor.py
@time: 2019/4/28 上午10:11 
"""
import copy
import os
import signal
from multiprocessing import Process

from watchdog.observers import Observer


def start_observer(observer):
    observer.start()
    observer.join()


class WorkDirMonitor(object):

    def __init__(self):
        self.watchers = {}
        self.kill_count = 0

    def create_watcher_process(self, path, handler, start_observer_func=start_observer, **kwargs):
        # 创建文件夹监控
        is_recursive = kwargs.get("recursive", False)
        params = kwargs
        if "recursive" in params:
            params.pop("recursive")
        observer = Observer()
        observer.schedule(handler, path, recursive=is_recursive)
        watcher_p = Process(target=start_observer_func, args=(observer, ), kwargs=params)
        watcher_p.start()
        self.watchers[path] = watcher_p.pid
        return watcher_p.pid

    def kill_watcher(self, path):
        pid = self.watchers.get(path, -1)
        if pid is not -1:
            os.kill(pid, signal.SIGKILL)
            self.watchers.pop(path)
            self.kill_count += 1
            if self.kill_count >= 150:
                self.watchers = copy.deepcopy(self.watchers)




