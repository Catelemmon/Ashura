# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: SolveFlow.py
@time: 2019/4/25 上午10:21 
"""
from core.SolveOpt import SolveOpt
import subprocess

from dbs.db import DB
from core.SolveOpt import SolveOpt


def start_solve_actions(**params):

    job_id = DB.write_solve_to_db(params)
    if job_id == -1:
        return job_id, "写入数据库失败"

    so = SolveOpt(**params)
    excute_res = so.excute_solveflow()
    DB.write_solvestatus_to_db()
    return job_id, excute_res
