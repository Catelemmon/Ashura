# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: Slurm.py
@time: 2019/4/24 上午10:27 
"""
import re
import subprocess

from schedulers import Scheduler


class Slurm(Scheduler.Scheduler):

    def job_info(self):
        pass

    @classmethod
    def kill_job(cls):
        pass

    @classmethod
    def send_job(cls, work_dir):
        try:
            res = subprocess.check_output(['sbatch', f'{work_dir}/solve.sh'], cwd=work_dir)
            res = res.decode("utf-8")
            slurm_id = int(re.search("\d+", res).group())
            return slurm_id
        except subprocess.CalledProcessError:
            # logging
            return -1
        except AttributeError:
            # logging
            return -1

    def data_parse(self):
        pass