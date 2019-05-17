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


class Cad2VtmConverter(object):

    def __init__(self, ori_file, des_file, vf_file,
                 command="salome -t -w 1 -- python ./sub_cad2vtp.py {ori_file} {vf_file} {des_file}"):
        self.ori_file = ori_file
        self.des_file = des_file
        self.vf_file = vf_file
        if des_file:
            self.command = command.format(ori_file=self.ori_file, vf_file=self.vf_file, des_file=self.des_file)
        else:
            self.command = command.format(ori_file=self.ori_file, vf_file=self.vf_file)

    def start(self):
        try:
            output = subprocess.check_output(self.command.split(), cwd=os.path.dirname(os.path.abspath(__file__)))
            output = output.decode("utf-8")
            if re.search("all conversion successful", output):
                res = re.search("result json\|.+", output).group()
                return 0, json.loads(res.split("|")[1]), "cad转换成功"
            elif re.search("Error", output):
                convert_logger.critical("cad转换错误 | script")
                return 2, {}, "cad转换错误 | script"
        except subprocess.CalledProcessError:
            convert_logger.exception("cad转换错误 | salome")
            return 2, {}, "cad转换错误 | salome"
