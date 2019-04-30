# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: solve_flow.py
@time: 2019/4/25 上午10:21 
"""
from core.SolveOpt import SolveOpt
from dbs.db import DB
from pathlib import Path

from monitor import fm
from monitor.Handlers import SU2ResultHandler
from schedulers import Slurm


def start_solve_actions(**params):

    solve_path = params["work-path"]
    launch_script = str(Path(solve_path).joinpath("solve.sh"))

    db = DB()
    job_id = db.write_solve(launch_script=launch_script, **params)  # 写入数据库
    if job_id == -1:
        return job_id, "写入数据库失败"
    excute_res = ""

    # TODO: 开新的进程执行仿真操作
    _start_solve(job_id, solve_path)

    return job_id, excute_res


def _start_solve(job_id, solve_path):
    db = DB()
    sp = SolveOpt(solve_path=solve_path, )
    slurm_id = sp.excute_solveflow()
    log_file = str(Path(solve_path).joinpath(f"{slurm_id}.out"))
    error_file = str(Path(solve_path).joinpath(f"{slurm_id}.err"))
    db.write_solve_status(
        job_id=job_id,
        slurm_id=slurm_id,
        log_file=log_file,
        error_file=error_file
    )
    fm.create_watcher_process(solve_path, SU2ResultHandler(job_id))
