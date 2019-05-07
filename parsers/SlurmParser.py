# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: SlurmParser.py
@time: 2019/5/6 下午5:52 
"""
from constants.maps import JSON_2_SLURMCONFIG


class SlurmParser(object):

    # TODO 待重构

    @classmethod
    def json_2_config(cls, **batch_args):
        # TODO 添加异常处理
        res = {}
        for key in JSON_2_SLURMCONFIG:
            res[JSON_2_SLURMCONFIG[key]] = batch_args
        return res
