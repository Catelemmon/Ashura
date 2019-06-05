# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: MeshOpt.py
@time: 19-3-28 上午11:06 
"""
import copy
from importlib import import_module
from typing import Dict

from constants.maps import MESH_APP
from utils.log_utils import get_logger


logger = get_logger(logger_name="core")


class MeshOpt:

    def __new__(cls, cad_file, mesh_dir, mesh_config: Dict, mesh_app=1, **kwargs):
        mdl_name, cls_name = MESH_APP[mesh_app], MESH_APP[mesh_app]
        mdl = import_module(mdl_name, package="core")
        cls: MeshOpt = getattr(mdl, cls_name)
        self = cls._from_parts(cad_file=cad_file, mesh_dir=mesh_dir,
                               mesh_config=mesh_config, mesh_app=mesh_app, **kwargs)
        return self

    @classmethod
    def _from_parts(cls, init=True, **kwargs):
        self = object.__new__(cls)
        pars: Dict = cls._parse(kwargs)
        self.options: Dict = copy.deepcopy(kwargs)
        for key in pars:
            setattr(self, key, pars[key])
            self.options.pop(key)
        if init:
            self._init()
        return self

    @classmethod
    def _parse(cls, kwargs: Dict):
        return kwargs

    def _init(self):
        pass

    def get_commands_dict(self):
        # 返回执行命令的字典
        pass

    def ready_mesh_dir(self, **kwargs):
        pass

    def render_configs(self, mesh_config: Dict, cad_name_config: Dict, parser=None, **mesh_args):
        pass

    @classmethod
    def _write_configs(cls, config_path, data):
        # 写配置文件
        pass

    def start_mesh(self):
        # 单机版
        pass
