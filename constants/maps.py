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
    "BoundaryCondition": "bound_cfg",  # 边界条件
    "Run": "parl_cfg"  # 并行配置
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
    "convert": {
        "convert_id": "convertId",
        "origin_file": "originFile",
        "des_file": "desFile",
        "vf_file": "vfFile",
        "convert_type": "convertType",
        "convert_status": "convertStatus",
        "convert_infos": "convertInfos",
        "begin_time": "beginTime",
        "end_time": "endTime"
    }
}


# 参数映射到数据库
ARGS_2_DB = {

}

CONVERT_CLASSES = [
    ("cad2vtm", "Cad2VtmConverter"),
    ("foam2su2_vtm", "Foam2su2Converter")
]