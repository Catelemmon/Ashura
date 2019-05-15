# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: model.py
@time: 2019/4/15 下午4:33 
"""


from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from sqlalchemy.orm import sessionmaker

ModelBase = declarative_base()


def now_func():
    return datetime.now()


class Solve(ModelBase):

    __tablename__ = "solve"

    solve_id = Column(Integer, primary_key=True, autoincrement=True)
    solve_path = Column(String(200), nullable=False)  # 仿真的工作路径
    mesh_path = Column(String(200), nullable=False)  # 网格文件的路径
    username = Column(String(20), default="middleware")  # 创建solve_job的用户
    solve_app = Column(Integer, default=0)  # 默认是su2
    solve_config = Column(JSON, nullable=False)  # json配置文件路径
    launch_script = Column(String(200), nullable=False)  # 启动脚本
    create_time = Column(DateTime, default=func.now())  # 作业的创建时间


class SolveStatus(ModelBase):

    __tablename__ = "solve_status"

    _id = Column(Integer, primary_key=True, autoincrement=True)
    solve_id = Column(Integer, nullable=False)  # solve_job的id
    core_num = Column(Integer, nullable=False)  # solve_job使用的cpu核数
    slurm_id = Column(Integer, nullable=False)  # 创建solve_job后slurm的id号
    slurm_status = Column(Integer, nullable=False)  # PENDING R FAILED COMPLETE CANCELED
    total_step = Column(Integer, nullable=False)  # 总共的步骤
    current_step = Column(Integer, nullable=False)  # 当前的步骤
    log_file = Column(String(200), nullable=False)  # 日志输出的文件
    error_file = Column(String(200), nullable=False)  # 错误输出的文件
    create_time = Column(DateTime, default=func.now())  # 作业的创建时间


class SolveResults(ModelBase):

    __tablename__ = "sovle_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    solve_id = Column(Integer, nullable=False)
    post_results = Column(JSON, nullable=False)  # 后处理的结果文件(兼容OpenFoam和SU2)
    create_time = Column(DateTime, default=func.now())  # 结果创建的时间


class SolveChart(ModelBase):

    __tablename__ = "solve_chart"

    _rsd_id = Column(Integer, primary_key=True, autoincrement=True)
    solve_id = Column(Integer, primary_key=True, )  # 作业的id
    iteration_step = Column(Integer, nullable=False)  # 迭代次数
    multi_fields = Column(JSON, nullable=False)  # 多个域中存储的值
    create_time = Column(DateTime, default=func.now())


class Convert(ModelBase):

    __tablename__ = "convert"

    convert_id = Column(Integer, primary_key=True, autoincrement=True)
    origin_path = Column(String(200), nullable=False)  # 源文件的路径
    output_dir = Column(String(200), nullable=False)  # 向哪个目录输出
    convert_type = Column(Integer, nullable=False)  # 转换的类型
    convert_status = Column(Integer, default=0, nullable=False)  # 转换状态 0 转换完成 1 正在转换 2 转换失败
    convert_infos = Column(JSON, default={})  # 转换的一些输出结果
    begin_time = Column(DateTime, default=func.now())  # 开始转换的时间
    end_time = Column(DateTime, default=func.now())  # 转换失败


# engine = create_engine("mysql+mysqlconnector://root:Cdlmt#2019!@127.0.0.1:3306/Ashura")
engine = create_engine("mysql+mysqlconnector://lmt:Lmt#2018@192.168.6.22:3306/fermat_cfd",
                       pool_size=10, pool_recycle=600, pool_timeout=30, pool_pre_ping=True)

DBsession = sessionmaker(bind=engine)
