# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: AshuraServer.py
@time: 2019/4/19 下午2:56 
"""

from abc import abstractmethod
from pathlib import Path
from config import

class AshuraServer(object):

    def __new__(cls, ,hooks=[], **kwargs):
        # 构建不同的服务器 HTTP服务或者是rabbitMQ
        # hooks是为了启动其他的相关服务
        pass

    @classmethod
    def _parse(cls, server_type = ,hooks, **kwargs):
        self = object.__new__(cls)
        # 解析传进来的参数
        pass

    def _init(self):
        pass

    @abstractmethod
    def server(self):
        # TODO 运行服务器, 由子类实现
        pass

    def run_server(self):
        self.server()
        for hook in self.hooks:
            hook()
