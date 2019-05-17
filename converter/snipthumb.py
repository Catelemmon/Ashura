# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: snipthumb.py
@time: 2019/5/16 上午10:19 
"""
import os
import subprocess

from configs import PVPYTHON_PATH
from utils.log_utils import get_logger

convert_logger = get_logger("convert")


class SnipThumb(object):

    def __init__(self,
                 vf_file, img_file,
                 command=f"{PVPYTHON_PATH} ./sub_snipthumb.py" + " {vf_file} {img_file}"):
        self.vf_file = vf_file
        self.img_file = img_file
        self.command = command.format(vf_file=vf_file, img_file=img_file)

    def start(self):
        try:
            subprocess.run(self.command.split(), cwd=os.path.dirname(os.path.abspath(__file__)))
            return 0
        except subprocess.CalledProcessError:
            convert_logger.exception(f"图片转换失败 | {self.vf_file}")
            return 1
