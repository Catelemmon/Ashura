# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: build_box.py
@time: 2019/5/30 下午8:32 
"""
import re
import os
import subprocess
from typing import Tuple


from utils.log_utils import get_logger

convert_logger = get_logger("convert")


class BondingBoxCreator(object):

    def __init__(self, ori_stl: str, des_stl: str, vf_file: str, dia_point1: Tuple, dia_point2: Tuple,
                 command='/data/home/liuheng/software/salome/salome -t -w 1 -- python ./sub_build_box.py {ori_stl} {des_stl}'
                         ' {vf_file} "{dia_point1}" "{dia_point2}"'):
        self.dia_point2 = dia_point2
        self.dia_point1 = dia_point1
        if not ori_stl.endswith("stl"):
            raise ValueError(f"错误的错误模型 | {ori_stl}")
        if not vf_file.endswith("vtm"):
            raise ValueError(f"错误的可视化文件 | {vf_file}")
        self.vf_file = vf_file
        self.des_stl = des_stl
        self.ori_stl = ori_stl
        self.command = command.format(ori_stl=self.ori_stl, des_stl=self.des_stl, vf_file=self.vf_file,
                                      dia_point1=str(self.dia_point1).replace(" ", ""),
                                      dia_point2=str(self.dia_point2).replace(" ", ""))

    def start(self):
        convert_logger.info("执行生成box命令")
        try:
            output = subprocess.check_output(self.command.split(), cwd=os.path.dirname(os.path.abspath(__file__)))
        except subprocess.CalledProcessError:
            convert_logger.exception(f"创建生成box的子进程失败")
            return 2, "创建生成box的子进程失败"
        except PermissionError:
            convert_logger.exception(f"subprocess库权限不足")
            return 2, "subprocess库权限不足"
        output = output.decode("utf-8")
        if re.search('creat_box_successful', output):
            convert_logger.info('creat_box_successful')
            return 0, "box生成成功"
        elif re.search('vtm生成失败', output):
            convert_logger.info('vtm生成失败')
            return 2, "vtm生成失败"
        elif re.search('vtk生成失败', output):
            convert_logger.info('vtk生成失败')
            return 2, "vtk生成失败"
        elif re.search('stl,vtk生成失败', output):
            convert_logger.info('stl,vtk生成失败')
            return 2, "stl,vtk生成失败"
        else:
            convert_logger.info('未知错误')
            return 2, "未知错误"


if __name__ == '__main__':
    bbc = BondingBoxCreator("/data/home/liuheng/cadcases/AileM6_with_thick_TE.stl",
                            "/data/home/liuheng/cadcases/boxstl.stl",
                            "/data/home/liuheng/cadcases/vf.vtm",
                            (0, 0, 0), (25, 25, 25))
    bbc.start()
