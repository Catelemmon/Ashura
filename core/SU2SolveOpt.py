# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: SU2SolveOpt.py
@time: 2019/5/6 上午11:25 
"""
import codecs
import copy
import json
from pathlib import Path
from typing import Dict

from jinja2 import FileSystemLoader, Template

from configs import TEMPLATES_FILES_PATH
from constants.commands import SU2_COMMANDS
from core.SolveOpt import SolveOpt
from parsers.SU2Parser import su2_json_parser
from utils.log_utils import default_logger, get_logger

core_logger = get_logger("core")


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

    @default_logger(name="core")
    def render_configs(self, parser=su2_json_parser, **solve_args):
        render_args: Dict = su2_json_parser(**solve_args)
        self.total_step = render_args["EXT_NUMBER"]
        render_args["mesh_input_file"] = self.su2_mesh_file
        if render_args is {}:
            raise ValueError("参数解析失败")
        try:
            loader = FileSystemLoader(str(TEMPLATES_FILES_PATH))
            tmp = Template(loader.get_source(None, self.su2_cfg_temp)[0])
            script_data = tmp.render(**render_args)
        except Exception:
            raise
        return script_data

    @classmethod
    def _write_config(cls, config_path, data):
        try:
            with codecs.open(config_path, encoding="utf-8", mode="w") as config_obj:
                config_obj.write(data)
        except Exception:
            core_logger.exception(f"仿真配置文件写入异常 | {config_path}")
            
    def ready_solve_dir(self, **kwargs):
        script_data = self.render_configs(**kwargs)
        su2_config_path = Path(self.solve_dir).joinpath(self.su2_cfg_name)
        self._write_config(su2_config_path, script_data)
        return script_data

    def start_solve(self):
        pass

    def get_total_step(self):
        return self.total_step


if __name__ == '__main__':
    so = SolveOpt("/home/cicada/workspace/su2_work_path/test_render", solve_app_type="SU2", mesh_file_path="fake-m6")
    config_json = """
    {
    "jobParams": {
        "args": [
            {
                "name": "material",
                "label": "材料属性",
                "formSchema": {
                    "value": {
                        "R": "287.058",
                        "gamma": "1.4",
                        "density": {
                            "value": "STANDARD_AIR",
                            "options": [
                                {
                                    "label": "标准气体",
                                    "value": "STANDARD_AIR"
                                },
                                {
                                    "label": "理想气体",
                                    "value": "IDEAL_GAS"
                                },
                                {
                                    "label": "VW_GAS",
                                    "value": "VW_GAS"
                                },
                                {
                                    "label": "PR_GAS",
                                    "value": "PR_GAS"
                                }
                            ]
                        },
                        "material": {
                            "value": "air",
                            "options": [
                                {
                                    "label": "空气",
                                    "value": "air"
                                }
                            ]
                        }
                    }
                }
            },
            {
                "name": "ics",
                "label": "初始条件",
                "formSchema": {
                    "value": {
                        "AOA": "3.06",
                        "Mach": "0.1",
                        "slider": "0",
                        "Reynolds": "11.72E6",
                        "temperature": "288.15",
                        "Reynolds_length": "0.64607"
                    }
                }
            },
            {
                "name": "bcs",
                "label": "边界条件",
                "formSchema": {
                    "value": {
                        "wall": {
                            "items": [
                                "Face_2",
                                "Face_3",
                                "Face_4",
                                "Face_5",
                                "Face_6",
                                "Face_7",
                                "Face_8"
                            ]
                        },
                        "far_bc": {
                            "items": [
                                "Face_1",
                                "Face_11",
                                "Face_12",
                                "Face_13",
                                "Face_14"
                            ]
                        },
                        "symmetric": {
                            "items": [
                                "Face_10"
                            ]
                        }
                    }
                }
            },
            {
                "name": "solve_setup",
                "label": "求解设置",
                "formSchema": {
                    "value": {
                        "CFL": "1",
                        "scheme": {
                            "value": "WEIGHTED_LEAST_SQUARES",
                            "options": [
                                {
                                    "label": "格林高斯",
                                    "value": "GREEN_GAUSS"
                                },
                                {
                                    "label": "加权最小二乘法",
                                    "value": "WEIGHTED_LEAST_SQUARES"
                                }
                            ]
                        }
                    }
                }
            },
            {
                "name": "Run",
                "label": "运行",
                "formSchema": {
                    "value": {
                        "CPU_NUM": "2",
                        "EXT_NUMBER": "120",
                        "SAVE_RESULT": "0",
                        "SAVE_HISTORY": "0"
                    }
                }
            }
        ]
    }
}
    """
    config_obj = json.loads(config_json)
    so.ready_solve_dir(**config_obj)