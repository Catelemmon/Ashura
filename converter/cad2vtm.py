# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: cad2vtm.py
@time: 2019/5/14 上午10:17 
"""
import json
import os
import re
import subprocess

from utils.log_utils import get_logger

convert_logger = get_logger("convert")

POSTFIX = (
    "stp", "brep", "iges"
)


class Cad2VtmConverter(object):

    def __init__(self, ori_file, des_file, vf_file,
                 command="salome -t -w 1 -- python ./sub_cad2vtp.py {ori_file} {vf_file} {des_file}"):
        self.ori_file: str = ori_file
        flag = True
        for postfix in POSTFIX:
            if self.ori_file.endswith(postfix):
                flag = False
        if flag:
            convert_logger.info(f"错误的模型文件 | {self.ori_file}")
            raise ValueError(f"错误的模型文件 | {self.ori_file}")
        self.des_file = des_file
        self.vf_file = vf_file
        if des_file:
            self.command = command.format(ori_file=self.ori_file, vf_file=self.vf_file, des_file=self.des_file)
        else:
            self.command = command.format(ori_file=self.ori_file, vf_file=self.vf_file)
        convert_logger.info(f"初始化模型转换类成功")

    def start(self):
        try:
            convert_logger.info("执行cad转换命令")
            output = subprocess.check_output(self.command.split(), cwd=os.path.dirname(os.path.abspath(__file__)))
            output = output.decode("utf-8")
            if re.search("all conversion successful", output):
                res = re.search("result json\|.+", output).group()
                return 0, json.loads(res.split("|")[1]), "cad转换成功"
            elif re.search("Error", output):
                convert_logger.critical("cad转换错误 | script")
                return 2, {}, "cad转换错误 | script"
            else:
                convert_logger.critical("脚本执行结果未捕获,转换失败 | script")
                return 2, {}, "脚本执行结果未捕获,转换失败 | script"
        except subprocess.CalledProcessError:
            convert_logger.exception("cad转换错误 | salome")
            return 2, {}, "cad转换错误 | salome"
        except Exception:
            convert_logger.exception("cad转换失败 | 未知错误")
            return 2, {}, "cad转换失败 | 未知错误"
