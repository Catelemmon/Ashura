# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: models.py
@time: 2019/4/15 下午4:33 
"""

from models import db


class Job(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path = db.Column()  # 所属路径
    owner = db.Column()  # 所属者
    uuid = db.Column()  # 暂定
    config = db.Column()  # 配置文件
    config_path = db.Column()  # 配置文件的路径 json.config
    mesh_path = db.Column()  # mesh的路径
    mesh_type = db.Column()  # mesh的类型
    solver_type = db.Column()  # 解算器的类型
    status = db.Column()  # 状态 正在执行 挂起 报错
    outfile = db.Column()  #
    core = db.Column()
    slurm_id = db.Column()
    create_time = db.Column()


class JobChart(db.Model):
    id = db.Column()
    job_id = db.Column()
    iteration_step = db.Column()  # 迭代次数
    residual = db.Column()  # 残差
    multi_field = db.Column()  # 多个域中存储的值
    capture_time = db.Column()
    output_time = db.Column()





class Mesh(db.Model):
    id = db.Column()
    path = db.Column()
    mesh = db.Column()
    status = db.Column()




