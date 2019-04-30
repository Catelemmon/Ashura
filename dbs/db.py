# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: dbs.py
@time: 2019/4/25 上午11:39 
"""
from typing import List

from sqlalchemy import update

from models.model import *
import traceback


class DB:

    def __init__(self):
        pass

    def write_solve(self, **kwargs):
        _session = DBsession()
        try:
            solve = Solve(
                solve_path=kwargs["work-path"],
                mesh_path=kwargs["mesh-file-path"],
                username=kwargs.get("username", "middleware"),
                solve_app=kwargs.get("solve-app", 0),
                launch_script=kwargs.get("launch_script"),
                solve_config=kwargs.get("solve-config", "{}"),
                create_time=datetime.now()
            )
            _session.add(solve)
            _session.commit()
            job_id = solve.id
            return job_id
        except Exception:
            traceback.print_exc()
            return -1
        finally:
            _session.close()

    def write_solve_status(self, **kwargs):
        _session = DBsession()
        try:
            ss = SolveStatus(
                solve_job_id=kwargs["job_id"],
                core_num=0,
                slurm_id=kwargs["slurm_id"],
                slurm_status=0,
                total_step=0,
                current_step=0,
                log_file=kwargs["log_file"],
                error_file=kwargs["error_file"],
                create_time=datetime.now()
            )
            _session.add(ss)
            _session.commit()
            _session.close()
            return 0
        except Exception:
            traceback.print_exc()
            return -1
        finally:
            _session.close()

    @classmethod
    def query_solve_status(cls, job_id):
        _session = DBsession()
        try:
            solve_status = _session.query(SolveStatus).filter(SolveStatus.solve_job_id == job_id).first()
            # TODO 解析查询的结果
            result = {}
            params = ["solve_job_id", "core_num", "slurm_id",
                      "slurm_status", "total_step", "current_step",
                      "log_file", "error_file"]
            for param in params:
                result[param] = getattr(solve_status, param)
            return result
        except Exception:
            traceback.print_exc()
            return None
        finally:
            _session.close()


    @classmethod
    def query_activejob(cls):
        # 查询活动的作业
        _session = DBsession()
        try:
            unactive_job_ids = _session.query(SolveStatus).filter(SolveStatus.slurm_status == 1).all()
            return unactive_job_ids
        except Exception:
            traceback.print_exc()
            return None
        finally:
            _session.close()

    @classmethod
    def update_unactivejob(cls, slurm_ids: List):
        # 更新
        pass

    @classmethod
    def query_slurm_jobstatus(cls, slurm_ids: List):
        pass

    @classmethod
    def update_solve_current_step(cls, solve_job_id, current_step):
        _session = DBsession()
        try:
            _session.query(SolveStatus).filter(SolveStatus.solve_job_id == solve_job_id).\
                update({SolveStatus.current_step: current_step})
            _session.commit()
        except Exception:
            traceback.print_exc()
        finally:
            _session.close()
