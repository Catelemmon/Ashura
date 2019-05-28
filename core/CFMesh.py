# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: CFMesh.py
@time: 2019/5/21 上午10:54 
"""
import shutil
from typing import Dict
from pathlib import Path

from configs import TEMPLATES_FILES_PATH
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
        shutil.copy(str(Path(TEMPLATES_FILES_PATH).joinpath('CFMeshDictTemp')),
                    str(Path(self.system_folder).joinpath("meshDict")))

    def ready_mesh_dir(self):
        # 准备mesh的工作目录
        self.foam = str(Path(self.mesh_dir).joinpath("case.foam"))
        Path(self.foam).touch(mode=0o600)  # 创建一个case.foam
        self._ready_system_folder()
        self._ready_control_dict()
        self.render_configs()

    def _ready_control_dict(self):
        shutil.copy(str(Path(TEMPLATES_FILES_PATH).joinpath('CFMesh_controlDictTemp')),
                    str(Path(self.system_folder).joinpath("controlDict")))

    def _ready_system_folder(self):
        self.system_folder = str(Path(self.mesh_dir).joinpath("system"))
        Path(self.system_folder).mkdir(mode=0o700, exist_ok=True)
        return self.system_folder

    @classmethod
    def _write_configs(cls, config_path, data):
        # TODO 实现写配置文件
        pass
