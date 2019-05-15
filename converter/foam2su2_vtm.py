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


class Foam2su2Converter(object):

    def __init__(self, foam_mesh_path,
                 output_su2_path,
                 command="/data/ParaView-5.6.0-osmesa-MPI-Linux-64bit/bin/pvpython ./sub_foam2su2_vtm.py"
                         " {foam_mesh_path} {output_su2_path}"):

        self.foam_mesh_path = foam_mesh_path
        self.output_su2_path = output_su2_path
        self.command = command.format(foam_mesh_path=self.foam_mesh_path, output_su2_path=self.output_su2_path)

    def start(self):
        output = subprocess.check_output(self.command.split(), cwd=os.path.dirname(os.path.abspath(__file__)))
        output = output.decode("utf-8")
        return self._parse_convert_output(output)

    @classmethod
    def _parse_convert_output(cls, output):
        if re.search("conversion vtm successful", output):
            res_data = re.sub("conversion vtm successful", "", output)
            return 0, json.loads(res_data), "SU2网格转换成功"
        else:
            return -1, "", "SU2网格转换失败"
