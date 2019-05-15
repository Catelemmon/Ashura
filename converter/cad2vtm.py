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


class Cad2VtmConverter(object):

    def __init__(self, src_file, output_path,
                 command="salome -t -w 1 -- python ./sub_cad2vtp.py {src_path}　{output_path}"):
        self.src_file = src_file
        self.output_path = output_path
        self.command = command.format(src_path=self.src_file, output_path=self.output_path)

    def start(self):
        try:
            output = subprocess.check_output(self.command.split(), cwd=os.path.dirname(os.path.abspath(__file__)))
            output = output.decode("utf-8")
            if re.search("all conversion successful", output):
                # TODO logging
                res = re.search("result json\|.+", output).group()
                return 0, json.loads(res.split("|")[1]), "cad转换成功"
            elif re.search("Error", output):
                # logging
                return -1, "", "cad转换错误 | script"
        except subprocess.CalledProcessError:
            # logging
            return -1, "", "cad转换错误 | salome"
