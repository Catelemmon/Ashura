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
import json
from utils.log_utils import get_logger

db_logger = get_logger("db")


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
            db_logger.exception("db-function write_solve failed")
            return -1
        finally:
            _session.close()

    def query_solve_path(self, solve_id):
        _session = DBsession()
        try:
            solve_path = _session.query(Solve).filter(Solve.solve_id == solve_id).first().solve_path
            return solve_path
        except Exception:
            db_logger.exception("db-function query_solve_path failed")
            return None
        finally:
            _session.close()

    def write_solve_status(self, **kwargs):
        _session = DBsession()
        try:
            ss = SolveStatus(
                solve_id=kwargs["job_id"],
                core_num=kwargs["core_num"],
                slurm_id=kwargs["slurm_id"],
                slurm_status=0,
                total_step=kwargs["total_step"],
                current_step=0,
                log_file=kwargs["log_file"],
                error_file=kwargs["error_file"],
                create_time=datetime.now()
            )
            _session.add(ss)
            _session.commit()
            return 0
        except Exception:
            db_logger.exception("db-function write_solve failed")
            return -1
        finally:
            _session.close()

    @classmethod
    def query_solve_status(cls, solve_id):
        _session = DBsession()
        try:
            solve_status = _session.query(SolveStatus).filter(SolveStatus.solve_id == solve_id).first()
            if solve_status is None:
                return solve_status
            res_mapping = DB_2_JSON[SolveStatus.__tablename__]
            result = {}
            for attr in res_mapping:
                result[res_mapping[attr]] = getattr(solve_status, attr)
            return result
        except Exception:
            db_logger.exception("db-function query_solve_status failed")
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
            db_logger.exception("db-function query_activejob failed")
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
            db_logger.exception("db-function update_solve_current_step failed")
        finally:
            _session.close()

    @classmethod
    def write_solve_chart(cls, solve_job_id, iter_step, fields_json):
        _session = DBsession()
        try:
            res_col = SolveChart(
                solve_id=solve_job_id,
                iteration_step=iter_step,
                multi_fields=fields_json,
            )
            _session.add(res_col)
            _session.commit()
        except Exception:
            db_logger.exception("db-function write_solve_chart failed")
        finally:
            _session.close()

    @classmethod
    def query_solve_chart(cls, solve_job_id, begin=0):
        _session = DBsession()
        res_mapping = DB_2_JSON[SolveChart.__tablename__]
        try:
            solve_charts: List[SolveChart] = _session.query(SolveChart).filter(SolveChart.solve_id == solve_job_id,
                                                                                SolveChart.iteration_step >= begin).\
                order_by(SolveChart.iteration_step.asc()).limit(50)
            cols = []
            for chart_model in solve_charts:
                col = {}
                for attr in res_mapping:
                    col[res_mapping[attr]] = getattr(chart_model, attr)
                    col["datetime"] = str(getattr(chart_model, "create_time"))
                    if attr == "multi_fields":
                        col[res_mapping[attr]] = json.dumps(col[res_mapping[attr]])
                cols.append(col)
            return cols
        except Exception:
            db_logger.exception("db-function query_solve_chart failed")
        finally:
            _session.close()

    @classmethod
    def write_convert(cls, origin_file, des_file, vf_file, convert_type):
        _session = DBsession()
        convert_id = -1
        try:
            convert = Convert(
                origin_file=origin_file,
                des_file=des_file,
                vf_file=vf_file,
                convert_type=convert_type,
                convert_status=1,
            )
            _session.add(convert)
            _session.commit()
            convert_id = convert.convert_id
            return convert_id
        except Exception:
            db_logger.exception("db-function write_convert failed")
            return convert_id
        finally:
            _session.close()

    @classmethod
    def update_convert(cls, convert_id, convert_status, convert_infos):
        _session = DBsession()
        try:
            _session.query(Convert).filter(Convert.convert_id == convert_id).update({
                Convert.convert_status: convert_status,
                Convert.convert_infos: convert_infos,
                Convert.end_time: datetime.now()
            })
            _session.commit()
        except Exception:
            db_logger.exception("db-function update_convert failed")
        finally:
            _session.close()

    @classmethod
    def query_convert(cls, convert_id):
        _session = DBsession()
        try:
            convert = _session.query(Convert).filter(Convert.convert_id == convert_id).first()
            res_mapping = DB_2_JSON[Convert.__tablename__]
            res = {}
            for key in res_mapping:
                res[res_mapping[key]] = getattr(convert, key) if not key.endswith("time")\
                    else str(getattr(convert, key))
                if key == "convert_infos":
                    res[res_mapping[key]] = json.dumps(res[res_mapping[key]])
            return res
        except Exception:
            db_logger.exception("db-function query_convert failed")
            return None
        finally:
            _session.close()

    @classmethod
    def write_mesh(cls, meshing_path, cad_path, username, mesh_app, mesh_config, launch_script):
        _session = DBsession()
        mesh_id = -1
        try:
            mesh = Mesh(
                meshing_path=meshing_path,
                cad_path=cad_path,
                username=username,
                mesh_app=mesh_app,
                mesh_config=mesh_config,
                launch_script=launch_script
            )
            _session.add(mesh)
            _session.commit()
            mesh_id = mesh.mesh_id
            return mesh_id
        except Exception:
            db_logger.exception("db-function write_mesh failed")
            return mesh_id
        finally:
            _session.close()

    @classmethod
    def write_mesh_status(cls, mesh_id, core_num, slurm_id, log_file, error_file):
        _session = DBsession()
        try:
            ms = MeshStatus(
                mesh_id=mesh_id,
                core_num=core_num,
                slurm_id=slurm_id,
                slurm_status=0,
                log_file=log_file,
                error_file=error_file
            )
            _session.add(ms)
            _session.commit()
        except Exception:
            db_logger.exception("db-function write_mesh_status faild")
        finally:
            _session.close()

    @classmethod
    def update_mesh_status(cls, mesh_id, current_step):
        _session = DBsession()
        try:
            _session.query(MeshStatus).filter(MeshStatus.mesh_id == mesh_id).update({
                MeshStatus.current_step: current_step
            })
            _session.commit()
        except Exception:
            db_logger.exception("db-function update_mesh_status failed!")

    @classmethod
    def compete_mesh_step(cls, mesh_id):
        _session = DBsession()
        try:
            ms = _session.query(MeshStatus).filter(MeshStatus.mesh_id == mesh_id).first()
            ms.current_step = ms.total_step
            _session.commit()
        except Exception:
            db_logger.exception("db-function compete_mesh_step failed!")

    @classmethod
    def query_mesh_status(cls, mesh_id):
        _session = DBsession()
        try:
            ms = _session.query(MeshStatus).filter(MeshStatus.mesh_id == mesh_id).first()
            res_mapping = DB_2_JSON[MeshStatus.__tablename__]
            res = {}
            for attr in res_mapping:
                res[res_mapping[attr]] = getattr(ms, attr)
            return res
        except Exception:
            db_logger.exception("db-function query_mesh_status failed!")
            return {}
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
        try:

            cursor.execute(f"select state from slurm_acct_db.linux_job_table where id_job={slurm_id};")
            res = cursor.fetchone()
            if res:
                status = res[0]
            else:
                status = -2
            return status
        except Exception:
            db_logger.exception("SlurmDB-function query_job_status failed")
        finally:
            cursor.close()

    def query_active_job(self):
        cursor = self.db.cursor()
        try:
            cursor.execute()
        except Exception:
            pass
        finally:
            cursor.close()