# -*- coding: utf-8 -*-

"""
@author: cicada
@contact: 1713856662a@gmail.com
@file: maps.py
@time: 2019/5/5 下午2:09 
"""

# 解算软件的类型编号
CAE_APPLICATION_TYPE = (
    "SU2",
    "OpenFoam",
    "MOOSE"
)

SU2_SOLVE_CONFIG_MAP = {
    "InitialCondition": "init_cfg",  # su2的初始条件
    "BoundaryCondition": "bound_cfg",
    "Run": "parl_cfg"
}

# JSON映射到SU2配置文件
JSON_2_SU2CONFIG = {
    "writeInterval": "write_interval",
    "mesh_input_file": "mesh_input_file",
    "EXT_ITER": "EXT_ITER",
}

JSON_2_SLURMCONFIG = {
    "numProc": "total_core"
}

# 数据库映射到JSON
DB_2_JSON = {
    "solve": {
        "solve_id": "jobId",
        "solve_path": "solve_path",
        "mesh_path": "mesh_path",
        "username": "username",
        "solve_app": "solve_app",
        "solve_config": "solve_config",
        "launch_script": "launch_script",
        "create_time": "create_time"
    },
    "solve_status": {
        "solve_id": "jobId",
        "core_num": "coreNum",
        "slurm_id": "slurmId",
        "slurm_status": "slurmStatus",
        "total_step": "totalStep",
        "current_step": "currentStep",
        "log_file": "logFile",
        "error_file": "errorFile",
    },
    "solve_results": {

    },
    "solve_chart": {
        "solve_id": "jobId",
        "iteration_step": "iterationStep",
        "multi_fields": "multiFields",
    },
}


# 参数映射到数据库
ARGS_2_DB = {

}
