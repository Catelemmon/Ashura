# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: SolveOpt.py
@time: 2019/4/24 上午10:29 
"""
from importlib import import_module
from typing import Dict


class SolveOpt(object):

    # TODO 解算类待重构

    def __new__(cls, solve_dir, solve_app_type="SU2", **kwargs):

        mdl_name = class_name = solve_app_type + "SolveOpt"
        mdl = import_module(mdl_name, package="core")
        cls = getattr(mdl, class_name)
        self = cls._from_parts(kwargs)
        self.solve_type = solve_app_type
        self.solve_dir = solve_dir
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
        return kwargs

    def _init(self):
        self.commands_dict = None
        pass

    def get_commands_dict(self):
        # 返回执行的命令
        pass

    def ready_solve_dir(self, **kwargs):
        # 准备解算目录, 拷贝操作等
        pass

    def render_configs(self, parser=None, **solve_args):
        # 渲染配置文件
        pass

    @classmethod
    def _write_configs(cls, config_path, data):
        # 写配置文件
        pass

    def start_solve(self):
        # 单机版本
        pass

    def get_total_step(self):
        pass