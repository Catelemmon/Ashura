# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: solve_flow.py
@time: 2019/4/25 上午10:21 
"""
import json

from constants.maps import CAE_APPLICATION_TYPE
from core.SolveOpt import SolveOpt
from dbs.db import DB, SlurmDB
from pathlib import Path

from monitor import DIR_MONITOR
from monitor.Handlers import SU2ResultHandler
from schedulers import Slurm

# TODO 封装成类 重构!!!


def start_solve_actions(**params):

    solve_path = params["work-path"]
    launch_script = str(Path(solve_path).joinpath("solve.sh"))

    db = DB()
    job_id = db.write_solve(launch_script=launch_script, **params)  # 写入数据库
    if job_id == -1:
        return job_id, "写入数据库失败"
    excute_res = ""

    # TODO: 开新的进程执行仿真操作
    mesh_file_name = params["mesh-file-name"]
    username = params["username"]
    solve_app_type = CAE_APPLICATION_TYPE[params["solve-app"]]
    solve_config = params["solve-config"]
    solve_config = json.loads(solve_config)
    job_name = params["job-name"]
    _start_solve(job_id, solve_path, mesh_file_name, username, job_name, solve_app_type, solve_config)

    return job_id, excute_res


def _start_solve(job_id, solve_path, mesh_file_path, username, job_name, solve_app_type, solve_config):
    db = DB()
    so = SolveOpt(solve_dir=solve_path, solve_type=solve_app_type, mesh_file_path=mesh_file_path)
    so.ready_solve_dir(**solve_config)
    commands = so.get_commands_dict()
    slurm = Slurm()
    total_core = solve_config.get("numProc", 10)
    slurm_id = slurm.send_job(work_dir=solve_path, total_core=total_core, username=username,
                              job_name=job_name, **commands)
    log_file = str(Path(solve_path).joinpath(f"{slurm_id}.out"))
    error_file = str(Path(solve_path).joinpath(f"{slurm_id}.err"))
    db.write_solve_status(
        job_id=job_id,
        slurm_id=slurm_id,
        log_file=log_file,
        error_file=error_file
    )
    m_id = DIR_MONITOR.create_watcher_process(solve_path, SU2ResultHandler(job_id))  # 监控文件
    print(f"monitor process id is {m_id}")


def stop_solve(solve_id):
    db = DB()
    slurm_id = db.query_solve_status(solve_id)["slurmId"]
    status = SlurmDB().query_job_status(slurm_id)
    if status is 0 or status is 1:
        solve_dir = DB().query_solve_path(65)
        DIR_MONITOR.kill_watcher(solve_dir)
        Slurm.kill_job(slurm_id)
        return 0, "success"
    else:
        return -1, "the job has finished!"
