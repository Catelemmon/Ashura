# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: dbs.py
@time: 2019/4/25 上午11:39 
"""
from typing import List

from mysql import connector

from constants.maps import DB_2_JSON
from models.model import *
import traceback


class DB:

    # TODO 上下文管理器实现DB类

    def __init__(self):
        pass

    def write_solve(self, **kwargs):
        _session = DBsession()
        try:
            solve = Solve(
                solve_path=kwargs["work-path"],
                mesh_path=kwargs["mesh-file-name"],
                username=kwargs.get("username", "middleware"),
                solve_app=kwargs.get("solve-app", 0),
                launch_script=kwargs.get("launch_script"),
                solve_config=kwargs.get("solve-config", "{}"),
                create_time=datetime.now()
            )
            _session.add(solve)
            _session.commit()
            return solve.solve_id
        except Exception:
            traceback.print_exc()
            return -1
        finally:
            _session.close()

    def query_solve_path(self, solve_id):
        _session = DBsession()
        try:
            solve_path = _session.query(Solve).filter(Solve.solve_id == solve_id).first().solve_path
            return solve_path
        except Exception:
            traceback.print_exc()
            return None
        finally:
            _session.close()

    def write_solve_status(self, **kwargs):
        _session = DBsession()
        try:
            ss = SolveStatus(
                solve_id=kwargs["job_id"],
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
    def query_solve_status(cls, solve_id):
        _session = DBsession()
        try:
            solve_status = _session.query(SolveStatus).filter(SolveStatus.solve_id == solve_id).first()
            res_mapping = DB_2_JSON[SolveStatus.__tablename__]
            result = {}
            for param in res_mapping:
                result[res_mapping[param]] = getattr(solve_status, param)
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
            _session.query(SolveStatus).filter(SolveStatus.solve_id == solve_job_id).\
                update({SolveStatus.current_step: current_step})
            _session.commit()
        except Exception:
            traceback.print_exc()
        finally:
            _session.close()


class SlurmDB(object):

    def __init__(self):
        self.db = connector.connect(
            host="192.168.6.31",
            port=3306,
            user="slurm",
            password="123456",
            database="slurm_acct_db"
        )

    def query_job_status(self, slurm_id):
        cursor = self.db.cursor()
        cursor.execute(f"select state from slurm_acct_db.linux_job_table where id_job={slurm_id};")
        status = cursor.fetchone()[0]
        cursor.close()
        return status


