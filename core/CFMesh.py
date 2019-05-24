# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: CFMesh.py
@time: 2019/5/21 上午10:54 
"""
from typing import Dict

from core import MeshOpt


class CFMesh(MeshOpt):

    # cfmesh对3D网格的操作

    def _init(self, **pars):
        self._render_command()

    def _render_command(self):
        self.command_dict = {"mesh_command": "cartesianMesh"}

    def get_commands_dict(self):
        return self.command_dict

    def render_configs(self, parser=None, **mesh_args):
        # TODO 实现cfmesh的配置文件的渲染
        pass

    def ready_mesh_dir(self):
        # TODO 实现准备mesh的文件夹
        pass

    @classmethod
    def _write_configs(cls, config_path, data):
        # TODO 实现写配置文件
        pass