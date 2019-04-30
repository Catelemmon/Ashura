# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: model.py
@time: 2019/4/15 下午4:33 
"""


from sqlalchemy import Column, String, Integer, DateTime, Float, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from sqlalchemy.orm import sessionmaker

ModelBase = declarative_base()


class Solve(ModelBase):

    __tablename__ = "solve"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String, nullable=False)  # 仿真的工作路径
    mesh_path = Column(String, nullable=False)  # 网格文件的路径
    user_name = Column(String, default="middleware")  # 创建solve_job的用户
    solve_app = Column(Integer, default=0)  # 默认是su2
    solve_config = Column(String, nullable=False)  # 配置文件路径
    launch_script = Column(String, nullable=False)  # 启动脚本
    create_time = Column(DateTime, default=datetime.now())  # 作业的创建时间


class SolveStatus(ModelBase):

    __tablename__ = "solve_status"

    id = Column(Integer, primary_key=True, autoincrement=True)
    solve_job_id = Column(Integer, nullable=False)  # solve_job的id
    core_num = Column(Integer, nullable=False)  # solve_job使用的cpu核数
    slurm_id = Column(Integer, nullable=False)  # 创建solve_job后slurm的id号
    slurm_status = Column(Integer, nullable=False)  # PENDING R FAILED COMPLETE CANCELED
    total_step = Column(Integer, nullable=False)  # 总共的步骤
    current_step = Column(Integer, nullable=False)  # 当前的步骤
    log_file = Column(String, nullable=False)  # 日志输出的文件
    error_file = Column(String, nullable=False)  # 错误输出的文件


class SolveResults(ModelBase):

    __tablename__ = "job_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, nullable=False)
    post_results = Column(JSON, nullable=False)  # 后处理的结果文件(兼容OpenFoam和SU2)
    create_time = Column(DateTime, default=datetime.now())  # 结果创建的时间


class SolveChart(ModelBase):

    __tablename__ = "job_chart"


    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, primary_key=True, )  # 作业的id
    iteration_step = Column(Integer, nullable=False)  # 迭代次数
    multi_fields = Column(JSON, nullable=False)  # 多个域中存储的值
    calc_time = Column(Float, nullable=True)  # 计算耗时
    capture_time = Column(DateTime, default=datetime.now(), nullable=False)  # 捕获时间
    output_time = Column(DateTime, default=datetime.now())  # 实际输出时间


class CadConvert(ModelBase):

    __tablename__ = "cad_convert"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cad_path = Column(String, nullable=False)  # cad 的路径
    cad_type = Column(String, nullable=False)  # cad 的文件类型
    target_path = Column(Integer, nullable=False)  # 目标文件的输出路径
    target_type = Column(Integer, nullable=False)  # 目标文件的类型
    convert_status = Column(Integer, nullable=False)  # 0 转换完成 1 正在转换 2 转换失败
    create_time = Column(DateTime, default=datetime.now())  # 创建时间
    covert_time = Column(String, nullable=True)  # 总共转换的时间


engine = create_engine("mysql+mysqlconnector://root:09170725@127.0.0.1:3306/Ashura")

DBsession = sessionmaker(bind=engine)
