# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: SolveOpt.py
@time: 2019/4/24 上午10:29 
"""
from monitor import fm
from monitor.Handlers import SU2ResultHandler
from schedulers import Slurm


class SolveOpt(object):

    # TODO 解算类待重构

    def __new__(cls, **kwargs):

        self = object.__new__(cls)
        self.solve_path = kwargs["solve_path"]
        return self

    def excute_solveflow(self, call_schduler=None):
        # TODO 执行solve操作流
        # solve_config_res = self._write_config()
        # if solve_config_res:
        #     return solve_config_res
        # write_sd_res = self._write_scheduler_config()
        # if write_sd_res:
        #     return write_sd_res
        slurm_id = Slurm.send_job(self.solve_path)
        return slurm_id

    def _init_status(self):
        pass

    def _write_config(self):
        try:
            # do something
            return None
        except Exception:
            # logging
            return "写入解算器参数出错"

    def _write_scheduler_config(self):
        try:
            # do somthing
            # logging
            return None
        except Exception:
            return "写入scheduler参数出错"

    def _excute_solvescript(self):
        try:
            # do something
            slurm_id = 0
            return slurm_id
        except Exception:
            return "执行脚本出错"

    def _add_solve_monitor(self, handler):
        pass