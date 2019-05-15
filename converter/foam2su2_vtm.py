# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: foam2su2_vtm.py
@time: 2019/5/14 下午2:09 
"""
import json
import os
import re
import subprocess
from configs import PVPYTHON_PATH


class Foam2su2Converter(object):

    def __init__(self, foam_mesh_path,
                 output_su2_path, vf_file,
                 command=f"{PVPYTHON_PATH} ./sub_foam2su2_vtm.py"
                         " {foam_mesh_path} {vf_file} {output_su2_path}"):

        self.foam_mesh_path = foam_mesh_path
        self.output_su2_path = output_su2_path
        self.vf_file = vf_file
        self.command = command.format(foam_mesh_path=self.foam_mesh_path, output_su2_path=self.output_su2_path,
                                      vf_file=self.vf_file)

    def start(self):
        try:
            output = subprocess.check_output(self.command.split(), cwd=os.path.dirname(os.path.abspath(__file__)))
            output = output.decode("utf-8")
            return self._parse_convert_output(output)
        except subprocess.CalledProcessError:
            return -1, {}, "foam mesh 转换错误 | paraview"
        except Exception:
            return -1, {}, "foam mesh参数解析失败 | _parse_convert_output"

    @classmethod
    def _parse_convert_output(cls, output):
        if re.search("conversion vtm successful", output):
            res_data = re.sub("conversion vtm successful", "", output)
            return 0, json.loads(res_data), "SU2网格转换成功"
        else:
            return -1, "", "SU2网格转换失败"
