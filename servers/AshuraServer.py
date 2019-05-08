# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: AshuraServer.py
@time: 2019/4/19 下午2:56 
"""

from abc import abstractmethod
from importlib import import_module
from typing import Dict


class AshuraServer(object):

    def __new__(cls, server_type="HttpServer", hooks=(), **kwargs):
        # 构建不同的服务器 HTTP服务或者是rpc
        # hooks是为了启动其他的相关服务

        mdl = import_module(server_type, package="servers")
        cls = getattr(mdl, server_type)
        self = cls._from_parts(kwargs)
        self.hooks = hooks
        self.server_type = server_type
        return self

    @classmethod
    def _from_parts(cls, kwargs, init=True):
        self = object.__new__(cls)
        pars: Dict = cls._parse(kwargs)
        self.options = kwargs
        for key in pars:
            setattr(self, key, pars[key])
            self.options.pop(key)
        if init:
            self._init()
        return self

    @classmethod
    def _parse(cls, kwargs):
        # 处理参数
        return kwargs

    def _init(self):
        pass

    @abstractmethod
    def server(self, options):
        pass

    def run_server(self):
        self.server(self.options)
        for hook in self.hooks:
            hook()
