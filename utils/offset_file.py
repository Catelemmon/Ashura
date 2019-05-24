# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: offset_file.py
@time: 2019/4/28 上午11:06 
"""


def def_end_func(end_line, **kwargs):
    param = kwargs
    return end_line is ""


def offset_file(file_obspath, offset=0, end_func=def_end_func, **kwargs):
    seek_file = open(file_obspath, encoding="utf-8", mode="r", errors="ignore")
    seek_file.seek(offset)
    while True:
        line = seek_file.readline()
        if end_func(line, **kwargs):
            break
        yield line.strip(), seek_file.tell()
