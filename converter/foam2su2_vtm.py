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
from typing import List

from configs import PVPYTHON_PATH
from utils.log_utils import get_logger
from pathlib import Path

convert_logger = get_logger("convert")


class Foam2su2Converter(object):

    def __init__(self, foam_mesh_path,
                 output_su2_path, vf_file,
                 command=f"{PVPYTHON_PATH} ./sub_foam2su2_vtm.py"
                 " {foam_mesh_path} {output_su2_path} {vf_file}"):

        if foam_mesh_path.endswith(".zip"):
            self.foamcase_zip: str = foam_mesh_path
            self.foam_mesh_path = foam_mesh_path.split(".")[0] + "/case.foam"
        else:
            self.foam_mesh_path = foam_mesh_path
        self.output_su2_path = output_su2_path
        self.vf_file = vf_file
        self.command = command

    def start(self):
        try:

            code, res, msg = self._ready_foam_case()
            if code != 0:
                return code, res, msg
            self.command = self.command.format(foam_mesh_path=self.foam_mesh_path, output_su2_path=self.output_su2_path,
                                               vf_file=self.vf_file)
            output = subprocess.check_output(self.command.split(), cwd=os.path.dirname(os.path.abspath(__file__)))
            output = output.decode("utf-8")
            return self._parse_convert_output(output)
        except subprocess.CalledProcessError:
            convert_logger.exception("foam mesh 转换错误 | paraview")
            return 2, {}, "foam mesh 转换错误 | paraview"
        except Exception:
            convert_logger.exception("foam mesh参数解析失败 | _parse_convert_output")
            return 2, {}, "foam mesh参数解析失败 | _parse_convert_output"

    @classmethod
    def _parse_convert_output(cls, output):
        if re.search("conversion vtm successful", output):
            res_data = re.sub("conversion vtm successful", "", output)
            return 0, json.loads(res_data), "SU2网格转换成功"
        else:
            return 2, {}, "SU2网格转换失败"

    def _ready_foam_case(self):
        unzip_dir = str(Path(self.foamcase_zip).parent)  # 执行unzip命令的目录
        zip_name = str(Path(self.foamcase_zip).name)  # zip包的名字
        zip_ouput_dir = Path(self.foamcase_zip).name.split(".")[0]  # zip输出到什么的文件夹

        try:
            _ = subprocess.check_output(["unzip", "-o", f"{zip_name}", "-d", f"{zip_ouput_dir}"], cwd=unzip_dir)
            foam_path = None
            for root, dirs, files in os.walk(Path(unzip_dir).joinpath(zip_ouput_dir)):
                for sf in files:
                    if sf.endswith(".foam"):
                        foam_path = Path(root).joinpath(sf)
                        break
            if foam_path:
                self.foam_mesh_path = str(foam_path)
                return 0, {}, ""
            else:
                return 2, {}, "错误的openfoam案例包"
        except subprocess.CalledProcessError:
            convert_logger.exception("解压openfoam算例包失败")
            return 2, {}, "解压openfoam算例包失败"


if __name__ == '__main__':
    print(Foam2su2Converter(
        "/share/home/fermat/temp/2709dfc4-f172-450b-95ef-934ca913a875.zip",
        "/share/home/fermat/web/16/mesh/a05490a8-778a-49de-b9d1-070a3d63e3ba.su2",
        "/share/home/fermat/web/16/vtm/a05490a8-778a-49de-b9d1-070a3d63e3ba.vtm"
    ).start())
