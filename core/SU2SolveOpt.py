# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: SU2SolveOpt.py
@time: 2019/5/6 上午11:25 
"""
import codecs
import copy
from pathlib import Path
from typing import Dict

from jinja2 import FileSystemLoader, Template

from configs import TEMPLATES_FILES_PATH
from constants.commands import SU2_COMMANDS
from core.SolveOpt import SolveOpt
from parsers.SU2Parser import SU2Parser


class SU2SolveOpt(SolveOpt):

    @classmethod
    def _from_parts(cls, kwargs, init=True):
        self = object.__new__(cls)
        pars: Dict = cls._parse(kwargs)
        self.options = kwargs
        if init:
            self._init(**pars)
        return self

    @classmethod
    def _parse(cls, kwargs: Dict):
        su2_cfg_name = kwargs.get("solve_cfg_name", "solve.cfg")
        su2_cfg_temp = kwargs.get("solve_cfg_temp", "su2cfg.cfg")  # su2配置文件的模板
        su2_mesh_file = kwargs.get("mesh_file_path", "su2_mesh.su2")
        return {
            "su2_cfg_name": su2_cfg_name,
            "su2_cfg_temp": su2_cfg_temp,
            "su2_mesh_file": su2_mesh_file,
        }

    def _init(self, **pars):
        self.commands_dict = copy.deepcopy(SU2_COMMANDS)
        for key in pars:
            setattr(self, key, pars[key])
            if key in self.options:
                self.options.pop(key)
        self._command_render(pars)

    def _command_render(self, pars):
        self.commands_dict["solve_command"] = self.commands_dict["solve_command"].format(**pars)
        self.commands_dict["post_orders"] = self.commands_dict["post_orders"].format(**pars)

    def get_commands_dict(self):
        return self.commands_dict

    def render_configs(self, parser=SU2Parser, **solve_args):
        render_args: Dict = parser.json_2_config(mesh_input_file=self.su2_mesh_file, **solve_args)
        loader = FileSystemLoader(str(TEMPLATES_FILES_PATH))
        tmp = Template(loader.get_source(None, self.su2_cfg_temp)[0])
        script_data = tmp.render(**render_args)
        return script_data

    @classmethod
    def _write_config(cls, config_path, data):
        with codecs.open(config_path, encoding="utf-8", mode="w") as config_obj:
            config_obj.write(data)

    def ready_solve_dir(self, **kwargs):
        script_data = self.render_configs(**kwargs)
        su2_config_path = Path(self.solve_dir).joinpath(self.su2_cfg_name)
        self._write_config(su2_config_path, script_data)

    def start_solve(self):
        pass
