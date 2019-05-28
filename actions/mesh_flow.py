# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: mesh_flow.py
@time: 2019/4/25 上午10:21 
"""
from pathlib import Path
from typing import Dict

from core.MeshOpt import MeshOpt
from dbs import DB, SlurmDB
from monitor import DIR_MONITOR
from monitor.Handlers import CFMeshResultHandler
from schedulers import Slurm
from utils.log_utils import get_logger

core_logger = get_logger("core")

# TODO 需要添加参数解析类


class MeshControler(object):

    def __init__(self,
                 work_path, cad_file_name, username, mesh_name, mesh_config, mesh_app=1,
                 ):
        self.work_path = work_path
        self.cad_file_name = cad_file_name
        self.username = username
        self.mesh_name = mesh_name
        self.mesh_app = mesh_app
        self.mesh_config: Dict = mesh_config
        self.core_num = 10
        self.lanuch_script = Path(self.work_path).joinpath("meshing.sh")

    def start_actions(self):
        core_logger.info(f"划分网格信息写入数据库 | mesh_APP: {self.mesh_app}"
                         f" | work_path: {self.work_path} | cad:name: {self.cad_file_name}"
                         f" | mesh_name: {self.mesh_name}")
        mesh_id = DB.write_mesh(meshing_path=self.work_path, cad_path=self.cad_file_name, username=self.username,
                                mesh_app=self.mesh_app, mesh_config=self.mesh_config,
                                launch_script=str(self.lanuch_script))
        # TODO 从这以后都是异步操作 生成网格结束后,还要转化出vtm和su2
        mo = MeshOpt(cad_file=self.cad_file_name, mesh_dir=self.work_path,
                     mesh_config=self.mesh_config, mesh_app=self.mesh_app)
        mo.ready_mesh_dir(**self.mesh_config)
        command_dict = mo.get_commands_dict()
        slurm = Slurm()
        slurm_id = slurm.send_job(self.work_path, launch_script=self.lanuch_script,
                                  username=self.username, total_core=10,
                                  temp_file="cfmesh_batch_script.sh", job_name=self.mesh_name, **command_dict)
        log_file = str(Path(self.work_path).joinpath(f"{slurm_id}.out"))
        err_file = str(Path(self.work_path).joinpath(f"{slurm_id}.err"))
        DB.write_mesh_status(mesh_id, core_num=self.core_num, slurm_id=slurm_id,
                             log_file=log_file, error_file=err_file)
        # 开启文件夹监控程序
        DIR_MONITOR.create_watcher_process(self.work_path, CFMeshResultHandler(mesh_id,
                                                                               (r'.*{slurm_id}\.out'
                                                                                .format(slurm_id=slurm_id),)))
        return mesh_id

    @classmethod
    def stop_actions(cls, mesh_id):
        ms = DB.query_mesh_status(mesh_id)
        if ms is None:
            pass
        slurm_id = ms["slurmId"]
        status = SlurmDB().query_job_status(slurm_id)
        if status is 0 or status is 1:
            mesh_dir = DB().query_mesh_dir(mesh_id)
            if mesh_dir is not None:
                DIR_MONITOR.kill_watcher(mesh_dir)
                Slurm.kill_job(slurm_id)
                core_logger.info(f"杀死网格作业 | slurm_id: {slurm_id} | mesh_id: {mesh_id}")
                return 0, "success"
            else:
                return 2, "查询网格错误"
        else:
            return 1, "mesh job has finished!"
