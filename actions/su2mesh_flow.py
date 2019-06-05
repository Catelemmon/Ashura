# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: su2mesh_flow.py
@time: 2019/5/27 下午7:18 
"""
import time
from multiprocessing import Process, ProcessError
from pathlib import Path
from typing import Dict

from actions.convert_flow import ConvertControler
from core.MeshOpt import MeshOpt
from dbs import DB, SlurmDB
from monitor import DIR_MONITOR
from monitor.Handlers import CFMeshResultHandler
from schedulers import Slurm
from utils.log_utils import get_logger

core_logger = get_logger("core")


# TODO 需要添加参数解析类
# TODO 打日志


class SU2MeshControler(object):

    def __init__(self,
                 work_path, cad_file_path, vf_path, thumb_path, username, mesh_name, mesh_config, mesh_app=1,
                 ):
        self.work_path = work_path
        self.cad_file_path = cad_file_path
        self.cad_name = Path(cad_file_path).name
        self.vf_path = vf_path
        self.thumb_path = thumb_path
        self.des_path = str(Path(work_path).joinpath(Path(self.cad_file_path).name.split(".")[0] + ".su2"))
        self.username = username
        self.mesh_name = mesh_name
        self.mesh_app = mesh_app
        self.mesh_config: Dict = mesh_config
        self.core_num = 10
        self.lanuch_script = Path(self.work_path).joinpath("meshing.sh")

    def start_actions(self):
        core_logger.info(f"划分网格信息写入数据库 | mesh_app: {self.mesh_app}"
                         f" | work_path: {self.work_path} | cad:name: {self.cad_file_path}"
                         f" | mesh_name: {self.mesh_name}")
        mesh_id = DB.write_mesh(meshing_path=self.work_path, cad_path=self.cad_file_path, username=self.username,
                                mesh_app=self.mesh_app, mesh_config=self.mesh_config,
                                launch_script=str(self.lanuch_script))
        core_logger.info(f"异步进行网格的划分 | mesh_id: {mesh_id}")
        try:
            mc_process = Process(target=self._asyc_mesh, args=(mesh_id,))
            mc_process.start()
            core_logger.info(f"异步mesh_convert进程开始 | pid: {mc_process.pid} | mesh_id: {mesh_id}")
        except ProcessError:
            # TODO 更新数据库
            core_logger.exception(f"开启转换进程失败 | mesh_id: {mesh_id}")
            return 1, "开启网格进程失败"
        return mesh_id, "success!"

    def _easily_parse(self):
        for single_arg in self.mesh_config["meshParams"]["args"]:
            name = single_arg.get("name", None)
            if name == "processors_number":
                self.num_proc = single_arg["formSchema"]["value"]["processorsNumber"]["processorsNumber"]
                return

    def _asyc_mesh(self, mesh_id):
        self._easily_parse()
        mo = MeshOpt(cad_file=self.cad_file_path, mesh_dir=self.work_path,
                     mesh_config=self.mesh_config, mesh_app=self.mesh_app)
        mo.ready_mesh_dir()
        command_dict = mo.get_commands_dict()
        slurm = Slurm()
        slurm_id = slurm.send_job(self.work_path, launch_script=self.lanuch_script,
                                  username=self.username, total_core=self.num_proc,
                                  temp_file="cfmesh_batch_script.sh", job_name=self.mesh_name, **command_dict)
        log_file = str(Path(self.work_path).joinpath(f"{slurm_id}.out"))
        err_file = str(Path(self.work_path).joinpath(f"{slurm_id}.err"))
        DB.write_mesh_status(mesh_id, core_num=self.core_num, slurm_id=slurm_id,
                             log_file=log_file, error_file=err_file)
        # 开启文件夹监控程序
        core_logger.info(f"开始监控 | mesh_id: {mesh_id}")
        DIR_MONITOR.create_watcher_process(self.work_path, CFMeshResultHandler(mesh_id,
                                                                               (r'.*{slurm_id}\.out'
                                                                                .format(slurm_id=slurm_id),)))
        # 阻塞住这个进程, 直到进行转换
        while True:
            state = SlurmDB().query_job_status(slurm_id)
            if state == 3:
                break
            if state in (4, 5):
                # TODO 生成网格被中断保存
                return None
            time.sleep(10)
        # TODO  添加异常处理
        ori_file = str(Path(self.work_path).joinpath("case.foam"))

        try:

            cc = ConvertControler(ori_file=ori_file, des_file=self.des_path,
                                  vf_file=self.vf_path, thumb_path=self.thumb_path, convert_type=1)
        except Exception:
            core_logger.exception("创建ConvertControler失败")
            raise ValueError("创建ConvertControler失败")
        core_logger.info("SU2MeshControler开始进行转换")
        cv_id = cc.start_actions()[0]
        print(cv_id)
        DB.write_mesh_convert(mesh_id, cv_id)
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
