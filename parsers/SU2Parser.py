    # -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: SU2Parser.py
@time: 2019/4/30 上午10:03 
"""
import copy
import json
from typing import Dict

from constants.maps import JSON_2_SU2CONFIG
from utils.log_utils import get_logger
from utils.offset_file import offset_file, def_end_func


parser_logger = get_logger(logger_name="parser")


class SU2Parser(object):

    # TODO: 待重构

    def __init__(self, res_file, offset=0):
        self.res_file = res_file

    def res_parse(self, res_dict_tmp, keys, offset=0, end_func=def_end_func):
        line_gen = offset_file(self.res_file, offset=offset, end_func=end_func)
        results = []
        result_pos = 0
        for line, pos in line_gen:
            result = copy.deepcopy(res_dict_tmp)
            for i, value in enumerate(line.split(",")):
                result[keys[i]] = value.strip()
            results.append(result)
            result_pos = pos
        return results, result_pos

    def parse_first_line(self):
        # 构造结果模板
        res_dict_tmp = {}
        with open(self.res_file, mode="r", encoding="utf-8") as f_obj:
            first_line = f_obj.readline()  # 只读取第一行
            keys = [key[1:-1] for key in first_line.split(",")]
            for key in keys:
                res_dict_tmp[key] = None
            first_line_offset = f_obj.tell()
            return res_dict_tmp, keys, first_line_offset


def _material_config(material_config: Dict):
    res = {}
    for key in material_config:
        if isinstance(material_config[key], Dict):
            if "density" == key:
                res[key] = material_config[key]["value"]
        else:
            res[key] = material_config[key]
    return res


def _init_config(init_config: Dict):
    return init_config


def _boundary_config(bound_config: Dict):
    res = {}
    for bound in bound_config:
        if bound == "far_bc":
            values = str(tuple(bound_config[bound]["items"])).replace("'", "")
            res["far_bc"] = values
        if bound == "wall":
            values = []
            for item in bound_config[bound]["items"]:
                values.append(item)
                values.append("0.0")
            res["wall"] = str(tuple(values)).replace("'", "")
        if bound == "symmetric":
            values = str(tuple(bound_config[bound]["items"])).replace("'", "")
            res["symmetric"] = values
    return res


def _solve_setup(setup_config: Dict):
    res = {"scheme": setup_config["scheme"]["value"], "CFL": setup_config["CFL"]}
    return res


def _run_config(run_config: Dict):
    res = copy.deepcopy(run_config)
    res.pop("CPU_NUM")
    return res


PARSE_FUNCS = {
    "material": _material_config,
    "ics": _init_config,
    "bcs": _boundary_config,
    "solve_setup": _solve_setup,
    "Run": _run_config
}


def su2_json_parser(**solve_args):
    args = solve_args["jobParams"]["args"]
    res = {}
    for arg_dict in args:
        parse_func = PARSE_FUNCS[arg_dict["name"]]
        sub_res = parse_func(arg_dict["formSchema"]["value"])
        res.update(sub_res)
    mapping_res = {}
    for map_key in JSON_2_SU2CONFIG:
        mapping_res[JSON_2_SU2CONFIG[map_key]] = res[map_key]
    return mapping_res


if __name__ == '__main__':
    json_s = """
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
    json_obj = json.loads(json_s)
    print(su2_json_parser(**json_obj))
