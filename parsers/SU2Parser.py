# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: SU2Parser.py
@time: 2019/4/30 上午10:03 
"""
import copy
from pathlib import Path

from utils.offset_file import offset_file, def_end_func


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
