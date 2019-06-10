# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: solve_flow.py
@time: 2019/4/25 上午10:21 
"""

import json
from multiprocessing import Process, ProcessError

from constants.maps import CAE_APPLICATION_TYPE, SU2_SOLVE_CONFIG_MAP, MONITOR_HANDLERS_CLASSES_MAP
from core.SolveOpt import SolveOpt
from dbs.db import DB, SlurmDB
from pathlib import Path
from monitor import Handlers
from monitor import DIR_MONITOR
from monitor.Handlers import SU2ResultHandler
from schedulers import Slurm

# TODO 封装成类 重构!!!
from utils.log_utils import get_logger, logger_dec

core_logger = get_logger("core")


class SolveController(object):

    def __init__(self, work_path, mesh_file_name, username, job_name, solve_config, solve_app=0):
        self.work_path = work_path
        self.mesh_file_name = mesh_file_name
        self.username = username
        self.job_name = job_name
        self.solve_app = solve_app
        self.solve_config = solve_config if isinstance(solve_config, dict) else json.loads(solve_config)
        self.core_num = 10
        self.launch_script = str(Path(work_path).joinpath("solve.sh"))

    def start_actions(self):
        core_logger.info(f"仿真信息写入数据库 | solve_app: {self.solve_app}"
                         f" | work_path: {self.work_path} | mesh_file_name: {self.mesh_file_name}"
                         f" | job_name: {self.job_name}")
        solve_id = DB.write_solve(work_path=self.work_path, mesh_file_name=self.mesh_file_name, username=self.username,
                                  solve_app=self.solve_app, launch_script=self.launch_script,
                                  solve_config=self.solve_config)
        if solve_id == -1:
            core_logger.info("写入数据库失败")
            return -1, "数据库写入失败"
        core_logger.info(f"创建进程执行仿真作业 | solve_id: {solve_id}")
        try:
            solve_pro = Process(target=self._asyc_solve, args=(solve_id,))
            solve_pro.start()
            core_logger.info(f"异步进行仿真 | solve_id: {solve_id}")
        except ProcessError:
            # TODO 更新solve的状态 数据库
            core_logger.exception(f"开启仿真进程失败 | solve_id: {solve_id}")
            return -1, "开启仿真进程失败"
        return solve_id, "sucess"

    def _easy_parse(self):
        arg_fields = self.solve_config["jobParams"]["args"]
        for field in arg_fields:
            name = field.get("name", None)
            if name == "Run":
                self.core_num = field["formSchema"]["value"]["CPU_NUM"]
                return

    @logger_dec(name="core")
    def _asyc_solve(self, solve_id):
        solve_app_type = CAE_APPLICATION_TYPE[self.solve_app]
        so = SolveOpt(self.work_path, solve_app_type=solve_app_type, mesh_file_path=self.mesh_file_name)
        so.ready_solve_dir(**self.solve_config)
        all_step = so.get_total_step()
        commands = so.get_commands_dict()
        slurm = Slurm()
        slurm_id = slurm.send_job(work_dir=self.work_path, total_core=self.core_num, username=self.username,
                                  job_name=self.job_name, **commands)
        log_file = str(Path(self.work_path).joinpath(f"{slurm_id}.out"))
        error_file = str(Path(self.work_path).joinpath(f"{slurm_id}.err"))
        DB.write_solve_status(
            job_id=solve_id,
            slurm_id=slurm_id,
            core_num=self.core_num,
            total_step=all_step,
            log_file=log_file,
            error_file=error_file
        )

        handler_cls = getattr(Handlers, MONITOR_HANDLERS_CLASSES_MAP[solve_app_type])
        m_pid = DIR_MONITOR.create_watcher_process(self.work_path, handler_cls(solve_id))  # 监控文件夹
        return None


def start_solve_actions(**params):
    solve_path = params["work-path"]
    launch_script = str(Path(solve_path).joinpath("solve.sh"))

    db = DB()
    job_id = db.write_solve(launch_script=launch_script, **params)  # 写入数据库
    if job_id == -1:
        return job_id, "写入数据库失败"
    excute_res = "创建仿真作业成功"

    # TODO: 开新的进程执行仿真操作
    mesh_file_name = params["mesh-file-name"]
    username = params["username"]
    solve_app_type = CAE_APPLICATION_TYPE[params["solve-app"]]
    solve_config = params["solve-config"]
    solve_config = json.loads(solve_config)
    job_name = params["job-name"]
    try:
        _start_solve(job_id, solve_path, mesh_file_name, username, job_name, solve_app_type, solve_config)
    except Exception:
        core_logger.exception("创建作业失败")
        excute_res = "创建作业失败"

    return job_id, excute_res


def _start_solve(job_id, solve_path, mesh_file_path, username, job_name, solve_app_type, solve_config):
    try:
        db = DB()
        so = SolveOpt(solve_dir=solve_path, solve_type=solve_app_type, mesh_file_path=mesh_file_path)
        so.ready_solve_dir(**solve_config)
        commands = so.get_commands_dict()
        total_core = None
        all_step = None
        options = solve_config["options"]
        for option_item in options:
            sub_options = option_item["option"]
            for sub_op in sub_options:
                if sub_op["name"] == "EXT_ITER":
                    all_step = sub_op["value"]
                if sub_op["name"] == "numProc":
                    total_core = sub_op["value"]
        if total_core <= 0:
            total_core = 10
        slurm = Slurm()
        slurm_id = slurm.send_job(work_dir=solve_path, total_core=total_core, username=username,
                                  job_name=job_name, **commands)
        log_file = str(Path(solve_path).joinpath(f"{slurm_id}.out"))
        error_file = str(Path(solve_path).joinpath(f"{slurm_id}.err"))
        db.write_solve_status(
            job_id=job_id,
            slurm_id=slurm_id,
            core_num=total_core,
            total_step=all_step,
            log_file=log_file,
            error_file=error_file
        )
        m_pid = DIR_MONITOR.create_watcher_process(solve_path, SU2ResultHandler(job_id))  # 监控文件夹
        return None
    except Exception:
        return "创建作业失败"


def stop_solve(solve_id):
    db = DB()
    slurm_id = db.query_solve_status(solve_id)["slurmId"]
    status = SlurmDB().query_job_status(slurm_id)
    if status is 0 or status is 1:
        solve_dir = DB().query_solve_path(solve_id)
        DIR_MONITOR.kill_watcher(solve_dir)
        Slurm.kill_job(slurm_id)
        core_logger.info(f"杀死杀死仿真作业 | slurm_id {slurm_id} | solve_id {solve_id}")
        return 0, "success"
    else:
        return 1, "the job has finished!"
