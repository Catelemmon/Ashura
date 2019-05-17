# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: Slurm.py
@time: 2019/4/24 上午10:27 
"""
import codecs
import copy
import re
import subprocess

from jinja2 import FileSystemLoader, Template
from pathlib import Path
from configs import SCRIPTS_PATH, CORE_NUM_PER_NODE
from schedulers import Scheduler
from utils.log_utils import get_logger

scheduler_logger = get_logger("scheduler")


class Slurm(Scheduler.Scheduler):

    def __init__(self, **kwargs):
        self.core_per_node = CORE_NUM_PER_NODE
        self.param = kwargs

    def job_info(self):
        pass

    @classmethod
    def kill_job(cls, slurm_id):
        try:
            subprocess.run(["scancel", f"{slurm_id}"])
        except subprocess.CalledProcessError:
            # TODO logging
            return 1

    def send_job(self, work_dir, **kwargs):
        try:
            data = self._render_script(**kwargs)
            self._write_script(data, str(Path(work_dir).joinpath("solve.sh")))
            username = kwargs.get("username", "middleware")
            res = subprocess.check_output(['sbatch', '-A', f'{username}', 'solve.sh'], cwd=work_dir)
            res = res.decode("utf-8")
            slurm_id = int(re.search("\d+", res).group())
            return slurm_id
        except subprocess.CalledProcessError:
            scheduler_logger.exception("slurm创建作业失败")
            return 1
        except AttributeError:
            # logging
            scheduler_logger.exception(f"参数错误 | {str(kwargs)}")
            return 1

    def data_parse(self):
        pass

    def _render_script(self, total_core, temp_file="su2_batch_script.sh", **kwargs):
        # 渲染脚本
        loader = FileSystemLoader(str(SCRIPTS_PATH))
        total_node = total_core // self.core_per_node + 1
        param = copy.deepcopy(kwargs)
        tmp = Template(loader.get_source(None, temp_file)[0])
        script_data = tmp.render(core_per_node=self.core_per_node, total_node=total_node,
                                 total_core=total_core, **param)
        return script_data

    @classmethod
    def _write_script(cls, batch_data, script):
        try:
            with codecs.open(script, encoding="utf-8", mode="w") as sh_obj:
                sh_obj.write(batch_data)
        except PermissionError:
            scheduler_logger.exception("写slurm脚本错误")
